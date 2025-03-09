from node_basic import BaseDataNode, NodeOutput
from app import app
from typing import Iterator


# For data nodes, inherit from BaseDataNode and implement meta and get_data function
# 对于一般的数据节点， 继承BaseDataNode， 实现meta和get_data函数即可
# The node ID for HelloExampleNode, must be unique, recommended format is "YourPluginName.NodeName"
# HelloExampleNode 是节点的ID,必须唯一,建议格式为"你的插件名.节点名"
@app.node_def("Demo.HelloExampleNode")
class HelloExampleNode(BaseDataNode):

    # Node metadata
    # 节点的元数据
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            # The title of the node displayed in the UI and in the menu.
            # 节点显示在UI上的标题，以及菜单里的名称
            "title": "Hello Example",
            # The default execution mode of the node. TRIGGERED: execute when triggered, DATA: execute when other nodes need its output data, DATA_ONCE: same as DATA but only execute once
            # 节点的默认执行方式。TRIGGERED: 触发时执行，DATA：其它节点需要它的输出数据时执行，DATA_ONCE：同DATA，但只执行一次
            "execution": "DATA",
            # The category of the node displayed in the menu. If it contains "/", it represents multi-level categories.
            # 显示在菜单中的节点的分类。如果带了"/"，则表示多级分类
            "category": "Demo",
            # Node inputs, basic types are str, int, float, bool. You can also define your own types. "*" means accepting any type.
            # 节点的输入, 基本类型有str, int, float, bool。 你也可以定义自己的类型。 "*" 表示接受任何类型
            "inputs": [{"name": "value", "type": "str", "options": {"default": ""}}],
            # Node outputs
            # 节点的输出
            "outputs": [{"name": "value", "type": "str"}],
        }

    # get_data returns a dictionary representing the output data of the node
    # get_data返回的是一个字典，表示节点的输出数据
    def get_data(self, controller, value: str) -> dict[str, any]:
        # Set the output "value" to "Hello, " + value
        # 将输出"value"设置为"Hello, " + value
        return {"value": "Hello, " + value}


# If the node has route outputs, you need to implement meta and execute functions.
# 如果节点有路由输出，则需要实现meta和execute函数
@app.node_def("Demo.CustomRouteExampleNode")
class CustomRouteExampleNode:
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "Custom Route Example",
            "category": "Demo",
            "inputs": [
                {
                    "name": "input1",
                    "type": "int",
                },
                {
                    "name": "input2",
                    "type": "str",
                    "widget": "str_select",
                    "options": {
                        "default": "one",
                        "choices": ["one", "two", "three"],
                    },
                },
            ],
            "outputs": [
                # "route" is a special output type that represents a route output.
                # "route" 是一种特殊的输出类型，表示路由输出
                {"name": "positive", "type": "route"},
                {"name": "zero", "type": "route"},
                {"name": "negative", "type": "route"},
                {"name": "value", "type": "int"},
            ],
            # Components used to display output in the frontend. Currently, type only supports "text".
            # 用于在前端显示输出的组件。目前type暂时只支持text。
            "display": [
                {"name": "tip1", "type": "text"},
                {"name": "tip2", "type": "text"},
            ],
        }

    # The function "execute" returns an iterator
    # execute返回的是一个迭代器
    def execute(self, controller, input1: int, input2: str) -> Iterator[NodeOutput]:
        if input1 > 0:
            # Send display event to the frontend.
            # 向前端发送显示事件
            controller.send_event(
                "display", {"tip1": "positive", "tip2": f"You choosed {input2}."}
            )
            # Set the output "value" to 1 and route to "positive".
            # 把输出"value"设置为1，并向"positive"路由
            yield NodeOutput(execution_pin="positive", data={"value": 1})
        elif input1 == 0:
            controller.send_event(
                "display", {"tip1": "zero", "tip2": f"You choosed {input2}."}
            )
            yield NodeOutput(execution_pin="zero", data={"value": 0})
        else:
            controller.send_event(
                "display", {"tip1": "negative", "tip2": f"You choosed {input2}."}
            )
            yield NodeOutput(execution_pin="negative", data={"value": -1})
