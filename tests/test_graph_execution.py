import unittest
import nodes
from app import app
from graph import parse_graph_data
import io
import sys


class TestGraphExecution(unittest.TestCase):
    def setUp(self):
        # 捕获标准输出
        self.captured_output = io.StringIO()
        sys.stdout = self.captured_output

    def tearDown(self):
        # 恢复标准输出
        sys.stdout = sys.__stdout__

    def test_accumulator_graph(self):
        """测试累加器图的执行

        这个测试用例验证了一个简单的累加器图的执行过程：
        1. 使用ForLoopNode遍历1到5的数字
        2. 使用一个变量存储累加结果
        3. 在每次循环中将当前数字加到累加结果中
        4. 最后打印最终结果（应该是15）
        """
        graph_json = """
        {
            "nodes": [
                {
                    "id": "start",
                    "node_type": "StartNode",
                    "execution_type": "TRIGGERED",
                    "inputs": {}
                },
                {
                    "id": "loop1",
                    "node_type": "ForLoopNode",
                    "execution_type": "TRIGGERED",
                    "inputs": {
                        "start": 1,
                        "end": 6,
                        "step": 1
                    }
                },
                {
                    "id": "define1",
                    "node_type": "DefineIntVariableNode",
                    "execution_type": "DATA_ONCE",
                    "inputs": {
                        "initial_value": 0
                    }
                },
                {
                    "id": "get1",
                    "node_type": "GetVariableNode",
                    "execution_type": "DATA",
                    "inputs": {}
                },
                {
                    "id": "get2",
                    "node_type": "GetVariableNode",
                    "execution_type": "DATA",
                    "inputs": {}
                },
                {
                    "id": "add1",
                    "node_type": "AddNode",
                    "execution_type": "DATA",
                    "inputs": {}
                },
                {
                    "id": "set1",
                    "node_type": "SetVariableNode",
                    "execution_type": "TRIGGERED",
                    "inputs": {}
                },
                {
                    "id": "print1",
                    "node_type": "PrintNode",
                    "execution_type": "TRIGGERED",
                    "inputs": {}
                }
            ],
            "edges": [
                {
                    "source_id": "loop1",
                    "source_pin": "item",
                    "target_id": "add1",
                    "target_pin": "a"
                },
                {
                    "source_id": "define1",
                    "source_pin": "variable",
                    "target_id": "get1",
                    "target_pin": "variable"
                },
                {
                    "source_id": "define1",
                    "source_pin": "variable",
                    "target_id": "get2",
                    "target_pin": "variable"
                },
                {
                    "source_id": "define1",
                    "source_pin": "variable",
                    "target_id": "set1",
                    "target_pin": "variable"
                },
                {
                    "source_id": "get1",
                    "source_pin": "value",
                    "target_id": "add1",
                    "target_pin": "b"
                },
                {
                    "source_id": "add1",
                    "source_pin": "result",
                    "target_id": "set1",
                    "target_pin": "value"
                },
                {
                    "source_id": "get2",
                    "source_pin": "value",
                    "target_id": "print1",
                    "target_pin": "value"
                }
            ],
            "route_edges": [
                {
                    "source_id": "start",
                    "source_pin": "_",
                    "target_id": "loop1"
                },
                {
                    "source_id": "loop1",
                    "source_pin": "body",
                    "target_id": "set1"
                },
                {
                    "source_id": "loop1",
                    "source_pin": "_",
                    "target_id": "print1"
                }
            ]
        }
        """
        graph = parse_graph_data(graph_json)
        app.execute_graph(graph)

        # 验证输出结果
        output = self.captured_output.getvalue().strip()
        self.assertEqual(output, "15")  # 1+2+3+4+5=15


if __name__ == "__main__":
    unittest.main()
