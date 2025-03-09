from dataclasses import dataclass
from typing import Iterator


@dataclass
class NodeOutput:
    execution_pin: str
    data: dict[str, any]


@dataclass
class FetchInputsRequest:
    input_pins: list[str]


@dataclass
class Reference:
    value: any


# 用于区分节点是没有输入还是输入了None
@dataclass
class NoInput:
    pass


class BaseDataNode:
    def execute(self, controller, **kwargs) -> Iterator[NodeOutput]:
        yield NodeOutput(
            execution_pin=None, data=self.get_data(controller=controller, **kwargs)
        )

    def get_data(self, controller, **kwargs) -> dict[str, any]:
        raise NotImplementedError(
            "get_data() is not implemented for {self.__class__.__name__}"
        )
