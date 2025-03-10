from dataclasses import dataclass
from enum import Enum
import json
from typing import Iterator
from node_basic import NodeOutput, FetchInputsRequest


class NodeExecutionType(Enum):
    TRIGGERED = "triggered"  # 只有被其它节点触发时执行
    DATA = "data"  # 每次其它下游节点需要数据时，执行，不缓存结果
    DATA_ONCE = "data_once"  # 其它下游节点需要数据时，执行一次，缓存结果，以后即使上游变化，也不再执行，直接返回缓存结果


@dataclass
class GraphNodeData:
    id: str
    node_type: str
    execution_type: NodeExecutionType
    inputs: dict[str, any]  # 固定的输入，不包含其它节点连入的输入


@dataclass
class GraphDataEdgeData:
    source_id: str
    source_pin: str
    target_id: str
    target_pin: str


@dataclass
class GraphRouteEdgeData:
    source_id: str
    source_pin: str
    target_id: str


@dataclass
class GraphData:
    nodes: list[GraphNodeData]
    edges: list[GraphDataEdgeData]
    route_edges: list[GraphRouteEdgeData]


# 从json中解析GraphData
def parse_graph_data(graph_data: str) -> GraphData:
    data = json.loads(graph_data)

    # 解析节点
    nodes = []
    for node_data in data["nodes"]:
        node = GraphNodeData(
            id=node_data["id"],
            node_type=node_data["node_type"],
            execution_type=NodeExecutionType(node_data["execution_type"].lower()),
            inputs=node_data["inputs"],
        )
        nodes.append(node)

    # 解析数据边
    edges = []
    for edge_data in data["edges"]:
        edge = GraphDataEdgeData(
            source_id=edge_data["source_id"],
            source_pin=edge_data["source_pin"],
            target_id=edge_data["target_id"],
            target_pin=edge_data["target_pin"],
        )
        edges.append(edge)

    # 解析路由边
    route_edges = []
    for route_edge_data in data["route_edges"]:
        route_edge = GraphRouteEdgeData(
            source_id=route_edge_data["source_id"],
            source_pin=route_edge_data["source_pin"],
            target_id=route_edge_data["target_id"],
        )
        route_edges.append(route_edge)

    return GraphData(nodes=nodes, edges=edges, route_edges=route_edges)


@dataclass
class NodeInstance:
    """节点实例的运行时信息"""

    instance: any  # 节点实例
    node_data: GraphNodeData  # 节点定义数据
    output_cache: dict[str, any]  # 输出值的缓存
    output_version: int  # 输出值的版本号


@dataclass
class Controller:
    send_event: lambda event, data: None


@dataclass
class ExpandTask:
    node_instance: NodeInstance
    input_pins: list[str] = None


@dataclass
class ExecuteTask:
    node_instance: NodeInstance


@dataclass
class IterateNextTask:
    node_instance: NodeInstance
    iterator: Iterator[NodeOutput | FetchInputsRequest]
    recollect_input_pins: list[str] = None


class GraphExecutor:
    def __init__(self, node_defs: dict[str, tuple[any, dict]], graph: GraphData):
        self.node_defs = node_defs
        self.graph = graph
        self.id_to_node_data = {node.id: node for node in graph.nodes}
        self.node_instances: dict[str, NodeInstance] = {}  # id -> NodeInstance
        self.data_inputs = self._build_data_inputs()
        self.data_dependencies = self._build_data_dependencies()
        self.routes = self._build_routes()

    def _build_data_inputs(
        self,
    ) -> dict[
        str, dict[str, (str, str, bool)]
    ]:  # target_id -> target_pin -> (source_id, source_pin)
        """构造节点输入表"""
        inputs = {}
        for edge in self.graph.edges:
            if edge.target_id not in inputs:
                inputs[edge.target_id] = {}

            inputs[edge.target_id][edge.target_pin] = (edge.source_id, edge.source_pin)
        return inputs

    def _build_data_dependencies(
        self,
    ) -> dict[str, set[str]]:  # target_id -> set[source_id]
        """构造节点数据依赖表"""
        dependencies = {node.id: set() for node in self.graph.nodes}
        for edge in self.graph.edges:
            # 获取目标节点的元数据
            target_node_data = self.id_to_node_data[edge.target_id]
            _, target_node_meta = self.node_defs[target_node_data.node_type]

            # 检查input pin是否为lazy
            input_is_lazy = False
            for input_meta in target_node_meta.get("inputs", []):
                if input_meta["name"] == edge.target_pin:
                    if input_meta.get("lazy", False):
                        input_is_lazy = True

            if not input_is_lazy:
                dependencies[edge.target_id].add(edge.source_id)
        return dependencies

    def _build_routes(
        self,
    ) -> dict[str, dict[str, str]]:  # source_id -> source_pin -> target_id
        """构造节点路由表"""
        routes = {
            node.id: {}
            for node in self.graph.nodes
            if node.execution_type == NodeExecutionType.TRIGGERED
        }
        for edge in self.graph.route_edges:
            if edge.source_id not in routes:
                raise ValueError(
                    f"node {edge.source_id} is a data node, but has route edges"
                )
            routes[edge.source_id][edge.source_pin] = edge.target_id
        return routes

    def _get_execution_order(
        self, target_node_id: str, pins: list[str] | None = None
    ) -> list[str]:
        """使用拓扑排序确定执行顺序"""
        result = []
        visited = set()
        processing = set()

        def visit(node_id: str, pins: list[str] | None = None):
            if node_id in processing:
                raise ValueError(f"检测到循环依赖，包含节点: {node_id}")
            if node_id in visited:
                return
            if (
                self.id_to_node_data[node_id].execution_type
                == NodeExecutionType.DATA_ONCE
                and self._get_node_instance(node_id).output_cache is not None
            ):
                return
            processing.add(node_id)
            if pins is None:
                dependencies = self.data_dependencies.get(node_id, set())
            else:
                dependencies = set()
                for pin in pins:
                    data_inputs = self.data_inputs.get(node_id, None)
                    if data_inputs is None:
                        continue
                    source_id, _ = data_inputs.get(pin, (None, None))
                    if source_id is None:
                        continue
                    dependencies.add(source_id)
            for dep_id in dependencies:
                if (
                    self.id_to_node_data[dep_id].execution_type
                    == NodeExecutionType.TRIGGERED
                ):
                    continue
                visit(dep_id)
            processing.remove(node_id)
            visited.add(node_id)
            result.append(node_id)

        visit(target_node_id, pins)
        return result

    def _get_node_instance(self, node_id: str) -> NodeInstance:
        """获取或创建节点实例"""
        if node_id not in self.node_instances:
            node_data = self.id_to_node_data[node_id]
            node_class, _ = self.node_defs[node_data.node_type]
            self.node_instances[node_id] = NodeInstance(
                instance=node_class(),
                node_data=node_data,
                output_cache=None,
                output_version=0,
            )
        return self.node_instances[node_id]

    def _collect_inputs_on_pins(self, node_id: str, pins: list[str]) -> dict[str, any]:
        result = {}
        pins_set = set(pins)
        node_data = self.id_to_node_data[node_id]
        if node_data.inputs:
            for key, value in node_data.inputs.items():
                if key in pins_set:
                    result[key] = value
        inputs = self.data_inputs.get(node_id, {})
        for target_pin, (source_id, source_pin) in inputs.items():
            node_instance = self._get_node_instance(source_id)
            if not target_pin in pins_set:
                continue
            if node_instance.output_cache is None:
                raise ValueError(
                    f"node {node_id} depends on node {source_id}, but node {source_id} has not been executed yet."
                )
            result[target_pin] = node_instance.output_cache[source_pin]
        return result

    def _collect_inputs(self, node_id: str) -> dict[str, any]:
        node_data = self.id_to_node_data[node_id]
        _, node_meta = self.node_defs[node_data.node_type]
        pins = []
        node_inputs = node_meta.get("inputs")
        if node_inputs is not None:
            for input_meta in node_inputs:
                name = input_meta["name"]
                if name is not None and not input_meta.get("lazy", False):
                    pins.append(name)
        return self._collect_inputs_on_pins(node_id, pins)

    def _get_route_targets(self, node_id: str, pin: str) -> list[str]:
        """获取路由边的目标节点"""
        return [
            edge.target_id
            for edge in self.graph.route_edges
            if edge.source_id == node_id and edge.source_pin == pin
        ]

    def _follow_route(self, node_instance, execution_pin, task_stack):
        """根据路由和执行引脚，将下一个节点添加到任务栈中"""
        routes = self.routes.get(node_instance.node_data.id, None)
        if routes is not None:
            target_node_id = routes.get(execution_pin, None)
            if target_node_id is not None:
                next_instance = self._get_node_instance(target_node_id)
                task_stack.append(ExpandTask(node_instance=next_instance))

    def execute(self, progress_callback=lambda x: None):
        """执行整个图"""
        task_stack = []
        task_stack.append(ExpandTask(node_instance=self._get_node_instance("start")))
        while len(task_stack) > 0:
            next_task = task_stack.pop()
            match next_task:
                case ExpandTask(node_instance, input_pins):
                    execution_order = self._get_execution_order(
                        node_instance.node_data.id, input_pins
                    )
                    if input_pins is not None:  # 说明节点本身已经执行过了，不需要再执行
                        execution_order = execution_order[:-1]
                    for node_id in reversed(execution_order):
                        task_stack.append(
                            ExecuteTask(node_instance=self._get_node_instance(node_id))
                        )
                case ExecuteTask(node_instance):
                    inputs = self._collect_inputs(node_instance.node_data.id)
                    controller = Controller(
                        send_event=lambda event, data: progress_callback(
                            {
                                "event": event,
                                "node_id": node_instance.node_data.id,
                                "data": data,
                            }
                        ),
                    )
                    outputs_iterator = node_instance.instance.execute(
                        controller=controller, **inputs
                    )
                    task_stack.append(
                        IterateNextTask(
                            node_instance=node_instance, iterator=outputs_iterator
                        )
                    )
                case IterateNextTask(
                    node_instance, outputs_iterator, recollect_input_pins
                ):
                    progress_callback(
                        {"event": "execute_node", "node_id": node_instance.node_data.id}
                    )
                    execution_pin = "_"
                    recollected_inputs = None
                    if recollect_input_pins is not None:
                        collected_inputs = self._collect_inputs_on_pins(
                            node_instance.node_data.id, recollect_input_pins
                        )
                        recollected_inputs = map(
                            lambda pin: collected_inputs[pin], recollect_input_pins
                        )
                    try:
                        output = outputs_iterator.send(recollected_inputs)
                    except StopIteration:
                        output = None
                    except Exception as e:
                        progress_callback(
                            {
                                "event": "execute_node_error",
                                "node_id": node_instance.node_data.id,
                                "node_error": repr(e),
                            }
                        )
                        raise e
                    match output:
                        case NodeOutput():
                            node_instance.output_cache = output.data
                            node_instance.output_version += 1
                            if output.execution_pin is not None:
                                execution_pin = output.execution_pin
                            if execution_pin != "_":
                                task_stack.append(
                                    IterateNextTask(
                                        node_instance=node_instance,
                                        iterator=outputs_iterator,
                                    )
                                )
                            self._follow_route(node_instance, execution_pin, task_stack)
                        case FetchInputsRequest(input_pins):
                            task_stack.append(
                                IterateNextTask(
                                    node_instance=node_instance,
                                    iterator=outputs_iterator,
                                    recollect_input_pins=input_pins,
                                )
                            )
                            task_stack.append(
                                ExpandTask(
                                    node_instance=node_instance, input_pins=input_pins
                                )
                            )
                        case None:
                            self._follow_route(node_instance, execution_pin, task_stack)
        progress_callback({"event": "finish"})
