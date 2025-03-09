from typing import Iterator
from app import app
from node_basic import BaseDataNode, NodeOutput, Reference, FetchInputsRequest, NoInput
from types import SimpleNamespace

TOP_CATEGORY = "Basic/"


@app.node_def("StartNode")
class StartNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "Start",
            "category": "_",
            "no_trigger": True,
            "inputs": [],
            "outputs": [],
        }

    def get_data(self, controller) -> dict[str, any]:
        return {}


@app.node_def("IntNode")
class IntNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "Int",
            "execution": "DATA_ONCE",
            "category": TOP_CATEGORY + "Primitive",
            "inputs": [{"name": "value", "type": "int"}],
            "outputs": [{"name": "value", "type": "int"}],
        }

    def get_data(self, controller, value: int) -> dict[str, any]:
        return {"value": value}


@app.node_def("FloatNode")
class FloatNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "Float",
            "execution": "DATA_ONCE",
            "category": TOP_CATEGORY + "Primitive",
            "inputs": [{"name": "value", "type": "float"}],
            "outputs": [{"name": "value", "type": "float"}],
        }

    def get_data(self, controller, value: float) -> dict[str, any]:
        return {"value": value}


@app.node_def("BoolNode")
class BoolNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "Bool",
            "execution": "DATA_ONCE",
            "category": TOP_CATEGORY + "Primitive",
            "inputs": [{"name": "value", "type": "bool"}],
            "outputs": [{"name": "value", "type": "bool"}],
        }

    def get_data(self, controller, value: bool) -> dict[str, any]:
        return {"value": value}


@app.node_def("StringNode")
class StringNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "String",
            "execution": "DATA_ONCE",
            "category": TOP_CATEGORY + "Primitive",
            "inputs": [{"name": "value", "type": "str"}],
            "outputs": [{"name": "value", "type": "str"}],
        }

    def get_data(self, controller, value: str) -> dict[str, any]:
        return {"value": value}


@app.node_def("StingMultilineNode")
class StingMultilineNode(StringNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "String (Multiline)",
            "execution": "DATA_ONCE",
            "category": TOP_CATEGORY + "Primitive",
            "inputs": [{"name": "value", "type": "str", "widget": "str_multiline"}],
            "outputs": [{"name": "value", "type": "str"}],
        }


@app.node_def("NoneNode")
class NoneNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "None",
            "execution": "DATA_ONCE",
            "category": TOP_CATEGORY + "Primitive",
            "inputs": [],
            "outputs": [{"name": "value", "type": "*"}],
        }

    def get_data(self, controller) -> dict[str, any]:
        return {"value": None}


@app.node_def("ConvertToIntNode")
class ConvertToIntNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "Convert To Int",
            "execution": "DATA",
            "category": TOP_CATEGORY + "Convert",
            "inputs": [{"name": "value", "type": "*"}],
            "outputs": [{"name": "value", "type": "int"}],
        }

    def get_data(self, controller, value: int) -> dict[str, any]:
        return {"value": int(value)}


@app.node_def("ConvertToFloatNode")
class ConvertToFloatNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "Convert To Float",
            "execution": "DATA",
            "category": TOP_CATEGORY + "Convert",
            "inputs": [{"name": "value", "type": "*"}],
            "outputs": [{"name": "value", "type": "float"}],
        }

    def get_data(self, controller, value: int) -> dict[str, any]:
        return {"value": float(value)}


@app.node_def("ConvertToStringNode")
class ConvertToStringNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "Convert To String",
            "execution": "DATA",
            "category": TOP_CATEGORY + "Convert",
            "inputs": [{"name": "value", "type": "*"}],
            "outputs": [{"name": "value", "type": "str"}],
        }

    def get_data(self, controller, value: int) -> dict[str, any]:
        return {"value": str(value)}


@app.node_def("ForLoopNode")
class ForLoopNode:
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "For Loop",
            "category": TOP_CATEGORY + "Control Flow",
            "inputs": [
                {"name": "start", "type": "int", "options": {"default": 0}},
                {"name": "end", "type": "int", "options": {"default": 3}},
                {"name": "step", "type": "int", "options": {"default": 1}},
            ],
            "outputs": [
                {"name": "item", "type": "int"},
                {"name": "body", "type": "route"},
            ],
        }

    def execute(
        self, controller, start: int, end: int, step: int
    ) -> Iterator[NodeOutput]:
        for i in range(start, end, step):
            yield NodeOutput(execution_pin="body", data={"item": i})


@app.node_def("ForEachNode")
class ForEachNode:
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "For Each",
            "category": TOP_CATEGORY + "Control Flow",
            "inputs": [
                {"name": "items", "type": "list<T>"},
            ],
            "outputs": [
                {"name": "item", "type": "T"},
                {"name": "body", "type": "route"},
            ],
            "generic_types": ["T"],
        }

    def execute(self, controller, items: list) -> Iterator[NodeOutput]:
        for item in items:
            yield NodeOutput(execution_pin="body", data={"item": item})


@app.node_def("WhileLoopNode")
class WhileLoopNode:
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "While Loop",
            "category": TOP_CATEGORY + "Control Flow",
            "inputs": [
                {"name": "condition", "type": "bool", "lazy": True},
            ],
            "outputs": [
                {"name": "body", "type": "route"},
            ],
        }

    def execute(self, controller) -> Iterator[NodeOutput]:
        while True:
            (condition,) = yield FetchInputsRequest(input_pins=["condition"])
            if not condition:
                break
            yield NodeOutput(execution_pin="body", data={})


@app.node_def("IfNode")
class IfNode:
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "If",
            "category": TOP_CATEGORY + "Control Flow",
            "inputs": [
                {"name": "condition", "type": "bool"},
            ],
            "outputs": [
                {"name": "if", "type": "route"},
                {"name": "else", "type": "route"},
            ],
        }

    def execute(self, controller, condition: bool) -> Iterator[NodeOutput]:
        if condition:
            yield NodeOutput(execution_pin="if", data={})
        else:
            yield NodeOutput(execution_pin="else", data={})


@app.node_def("PrintNode")
class PrintNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "Print",
            "category": TOP_CATEGORY + "Output",
            "inputs": [
                {"name": "value", "type": "*"},
            ],
            "outputs": [
                {"name": "value", "type": "*"},
            ],
        }

    def get_data(self, controller, value: int) -> dict[str, any]:
        print(value)
        return {"value": value}


@app.node_def("AddIntNode")
class AddIntNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "Add Int",
            "category": TOP_CATEGORY + "Math",
            "execution": "DATA",
            "inputs": [
                {"name": "a", "type": "int"},
                {"name": "b", "type": "int"},
            ],
            "outputs": [
                {"name": "result", "type": "int"},
            ],
        }

    def get_data(self, controller, a: int, b: int) -> dict[str, any]:
        return {"result": a + b}


@app.node_def("MathOperationNode")
class MathOperationNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "Math Operation",
            "category": TOP_CATEGORY + "Math",
            "execution": "DATA",
            "inputs": [
                {"name": "a", "type": "*"},
                {"name": "b", "type": "*"},
                {
                    "name": "operator",
                    "type": "str",
                    "widget": "str_select",
                    "options": {
                        "default": "+",
                        "choices": ["+", "-", "*", "/", "%", "**"],
                    },
                },
            ],
            "outputs": [
                {"name": "result", "type": "*"},
            ],
        }

    def get_data(self, controller, a: any, b: any, operator: str) -> dict[str, any]:
        return {"result": eval(f"{a} {operator} {b}")}


@app.node_def("CompareNode")
class CompareNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "Compare",
            "category": TOP_CATEGORY + "Logic",
            "execution": "DATA",
            "inputs": [
                {
                    "name": "operator",
                    "type": "str",
                    "widget": "str_select",
                    "options": {
                        "default": "==",
                        "choices": ["==", "!=", ">", ">=", "<", "<="],
                    },
                },
                {"name": "a", "type": "T"},
                {"name": "b", "type": "T"},
            ],
            "outputs": [
                {"name": "result", "type": "bool"},
            ],
            "generic_types": ["T"],
        }

    def get_data(self, controller, operator: str, a: any, b: any) -> dict[str, any]:
        return {"result": eval(f"{a} {operator} {b}")}


@app.node_def("DefineVariableNode")
class DefineVariableNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "Define Variable",
            "category": TOP_CATEGORY + "Variable",
            "inputs": [{"name": "initial_value", "type": "T"}],
            "outputs": [{"name": "variable", "type": "ref<T>"}],
            "generic_types": ["T"],
        }

    def get_data(self, controller, initial_value: any) -> dict[str, any]:
        return {"variable": Reference(initial_value)}


@app.node_def("SetVariableNode")
class SetVariableNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "Set Variable",
            "category": TOP_CATEGORY + "Variable",
            "inputs": [
                {"name": "variable", "type": "ref<T>"},
                {"name": "value", "type": "T"},
            ],
            "outputs": [{"name": "variable", "type": "ref<T>"}],
            "generic_types": ["T"],
        }

    def get_data(self, controller, variable: Reference, value: any) -> dict[str, any]:
        variable.value = value
        return {"variable": variable}


@app.node_def("GetVariableNode")
class GetVariableNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "Get Variable",
            "execution": "DATA",
            "category": TOP_CATEGORY + "Variable",
            "inputs": [{"name": "variable", "type": "ref<T>"}],
            "outputs": [{"name": "value", "type": "T"}],
            "generic_types": ["T"],
        }

    def get_data(self, controller, variable: Reference) -> dict[str, any]:
        return {"value": variable.value}


@app.node_def("DisplayAsTextNode")
class DisplayAsTextNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "Display As Text",
            "category": TOP_CATEGORY + "Output",
            "inputs": [
                {"name": "value", "type": "*"},
                {"name": "append", "type": "bool", "options": {"default": False}},
            ],
            "outputs": [{"name": "value", "type": "*"}],
            "display": [{"name": "value", "type": "text"}],
        }

    def get_data(self, controller, value: any, append: bool) -> dict[str, any]:
        controller.send_event("append" if append else "display", {"value": str(value)})
        return {"value": value}


@app.node_def("ExecutePythonScriptNode")
class ExecutePythonScriptNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "Execute Python Script",
            "category": TOP_CATEGORY + "Script",
            "inputs": [
                {"name": "script", "type": "str", "widget": "str_multiline"},
                {"name": "input", "type": "*"},
                {
                    "name": "output_name",
                    "type": "str",
                    "options": {"default": "result"},
                },
            ],
            "outputs": [{"name": "result", "type": "*"}],
        }

    def get_data(
        self,
        controller,
        script: str,
        input: any = None,
        output_name: str = "result",
    ) -> dict[str, any]:
        locals_dict = {}
        input_dict = {"input": input}
        try:
            exec(script, input_dict, locals_dict)
        except SystemExit as e:
            pass
        return {"result": locals_dict.get(output_name, None)}


@app.node_def("PythonEvalNode")
class PythonEvalNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "Python Eval",
            "category": TOP_CATEGORY + "Script",
            "inputs": [
                {"name": "expression", "type": "str"},
                {"name": "input", "type": "*"},
            ],
            "outputs": [{"name": "result", "type": "*"}],
        }

    def get_data(
        self,
        controller,
        expression: str,
        input: any = None,
    ) -> dict[str, any]:
        locals_dict = {}
        input_dict = {"input": input}
        try:
            return {"result": eval(expression, input_dict, locals_dict)}
        except SystemExit as e:
            raise Exception("You should not use exit() in the eval script")


@app.node_def("SetObjectPropertyNode")
class SetObjectPropertyNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "Set Object Property",
            "category": TOP_CATEGORY + "Object",
            "execution": "DATA",
            "inputs": [
                {"name": "object", "type": "*"},
                {"name": "property", "type": "str"},
                {"name": "value", "type": "*"},
            ],
            "outputs": [{"name": "object", "type": "*"}],
        }

    def get_data(
        self, controller, property: str, value: any, object: any = None
    ) -> dict[str, any]:
        if object is None:
            object = SimpleNamespace()
        setattr(object, property, value)
        return {"object": object}


@app.node_def("GetObjectPropertyNode")
class GetObjectPropertyNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "Get Object Property",
            "category": TOP_CATEGORY + "Object",
            "execution": "DATA",
            "inputs": [
                {"name": "object", "type": "*"},
                {"name": "property", "type": "str"},
            ],
            "outputs": [{"name": "value", "type": "*"}],
        }

    def get_data(self, controller, object: any, property: str) -> dict[str, any]:
        return {"value": getattr(object, property)}


@app.node_def("EmptyListNode")
class EmptyListNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "Empty List",
            "category": TOP_CATEGORY + "Collection",
            "execution": "DATA_ONCE",
            "inputs": [],
            "outputs": [{"name": "list", "type": "list<*>"}],
        }

    def get_data(self, controller) -> dict[str, any]:
        return {"list": []}


@app.node_def("ListNode")
class ListNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "List",
            "category": TOP_CATEGORY + "Collection",
            "execution": "DATA",
            "inputs": [
                {"name": "last_list", "type": "list<T>"},
                {"name": "item_0", "type": "T"},
                {"name": "item_1", "type": "T"},
                {"name": "item_2", "type": "T"},
                {"name": "item_3", "type": "T"},
                {"name": "item_4", "type": "T"},
            ],
            "outputs": [{"name": "list", "type": "list<T>"}],
            "generic_types": ["T"],
        }

    def get_data(
        self,
        controller,
        item_0: any = NoInput(),
        item_1: any = NoInput(),
        item_2: any = NoInput(),
        item_3: any = NoInput(),
        item_4: any = NoInput(),
        last_list: list | None = None,
    ) -> dict[str, any]:
        result = []
        if not isinstance(item_0, NoInput):
            result.append(item_0)
        if not isinstance(item_1, NoInput):
            result.append(item_1)
        if not isinstance(item_2, NoInput):
            result.append(item_2)
        if not isinstance(item_3, NoInput):
            result.append(item_3)
        if not isinstance(item_4, NoInput):
            result.append(item_4)
        if last_list is not None:
            result = last_list + result
        return {"list": result}


@app.node_def("AppendToListNode")
class AppendToListNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "Append To List",
            "category": TOP_CATEGORY + "Collection",
            "execution": "DATA",
            "inputs": [
                {"name": "list", "type": "list<T>"},
                {"name": "item", "type": "T"},
            ],
            "outputs": [{"name": "list", "type": "list<T>"}],
            "generic_types": ["T"],
        }

    def get_data(
        self, controller, item: any, list: list | None = None
    ) -> dict[str, any]:
        if list is None:
            list = []
        return {"list": list + [item]}


@app.node_def("GetListItemNode")
class GetListItemNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "Get List Item",
            "category": TOP_CATEGORY + "Collection",
            "execution": "DATA",
            "inputs": [
                {"name": "list", "type": "list<T>"},
                {"name": "index", "type": "int"},
            ],
            "outputs": [{"name": "item", "type": "T"}],
            "generic_types": ["T"],
        }

    def get_data(self, controller, list: list, index: int) -> dict[str, any]:
        return {"item": list[index]}


@app.node_def("SetListItemNode")
class SetListItemNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "Set List Item",
            "category": TOP_CATEGORY + "Collection",
            "execution": "DATA",
            "inputs": [
                {"name": "list", "type": "list<T>"},
                {"name": "index", "type": "int"},
                {"name": "item", "type": "T"},
            ],
            "outputs": [{"name": "list", "type": "list<T>"}],
            "generic_types": ["T"],
        }

    def get_data(self, controller, list: list, index: int, item: any) -> dict[str, any]:
        list[index] = item
        return {"list": list}


@app.node_def("EmptyDictNode")
class EmptyDictNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "Empty Dict",
            "category": TOP_CATEGORY + "Collection",
            "execution": "DATA_ONCE",
            "inputs": [],
            "outputs": [{"name": "dict", "type": "dict<*,*>"}],
        }

    def get_data(self, controller) -> dict[str, any]:
        return {"dict": {}}


@app.node_def("PutToDictNode")
class PutToDictNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "Put To Dict",
            "category": TOP_CATEGORY + "Collection",
            "execution": "DATA",
            "inputs": [
                {"name": "dict", "type": "dict<T,R>"},
                {"name": "key", "type": "T"},
                {"name": "value", "type": "R"},
            ],
            "outputs": [{"name": "dict", "type": "dict<T,R>"}],
            "generic_types": ["T", "R"],
        }

    def get_data(
        self, controller, key: any, value: any, dict: dict | None = None
    ) -> dict[str, any]:
        if dict is None:
            dict = {}
        dict[key] = value
        return {"dict": dict}


@app.node_def("GetFromDictNode")
class GetFromDictNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "Get From Dict",
            "category": TOP_CATEGORY + "Collection",
            "execution": "DATA",
            "inputs": [
                {"name": "dict", "type": "dict<T,R>"},
                {"name": "key", "type": "T"},
            ],
            "outputs": [{"name": "value", "type": "R"}],
            "generic_types": ["T", "R"],
        }

    def get_data(self, controller, dict: dict, key: any) -> dict[str, any]:
        return {"value": dict[key]}


@app.node_def("StringKeyDictNode")
class StringKeyDictNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "String Key Dict",
            "category": TOP_CATEGORY + "Collection",
            "execution": "DATA",
            "inputs": [
                {"name": "last_dict", "type": "dict<str,T>"},
                {"name": "key_0", "type": "str"},
                {"name": "value_0", "type": "T"},
                {"name": "key_1", "type": "str"},
                {"name": "value_1", "type": "T"},
                {"name": "key_2", "type": "str"},
                {"name": "value_2", "type": "T"},
                {"name": "key_3", "type": "str"},
                {"name": "value_3", "type": "T"},
                {"name": "key_4", "type": "str"},
                {"name": "value_4", "type": "T"},
            ],
            "outputs": [{"name": "dict", "type": "dict<str,T>"}],
            "generic_types": ["T"],
        }

    def get_data(
        self,
        controller,
        last_dict: dict | None = None,
        key_0: str = "",
        value_0: any = NoInput(),
        key_1: str = "",
        value_1: any = NoInput(),
        key_2: str = "",
        value_2: any = NoInput(),
        key_3: str = "",
        value_3: any = NoInput(),
        key_4: str = "",
        value_4: any = NoInput(),
    ) -> dict[str, any]:
        if last_dict is None:
            result_dict = {}
        else:
            result_dict = dict(last_dict)
        if not isinstance(value_0, NoInput):
            result_dict[key_0] = value_0
        if not isinstance(value_1, NoInput):
            result_dict[key_1] = value_1
        if not isinstance(value_2, NoInput):
            result_dict[key_2] = value_2
        if not isinstance(value_3, NoInput):
            result_dict[key_3] = value_3
        if not isinstance(value_4, NoInput):
            result_dict[key_4] = value_4
        return {"dict": result_dict}
