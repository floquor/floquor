from graph import GraphData, GraphExecutor


class App:
    def __init__(self):
        self.node_defs = {}

    def node_def(self, id: str):
        def decorator(node_class):
            self.register_node(id, node_class)
            return node_class

        return decorator

    def register_node(self, id: str, node_class):
        if not hasattr(node_class, "meta"):
            raise ValueError(f"Node type {id} is missing meta method")
        self.node_defs[id] = (node_class, node_class.meta())

    def execute_graph(self, graph: GraphData, progress_callback=lambda x: None):
        executor = GraphExecutor(self.node_defs, graph)
        executor.execute(progress_callback)


app = App()
