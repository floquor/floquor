from node_basic import BaseDataNode
from app import app
from dataclasses import dataclass
from typing import Iterator
from node_basic import NodeOutput
from openai import OpenAI
import string


@dataclass
class ChatMessage:
    role: str
    content: str


@app.node_def("LLM.AppendToChatMessageList")
class AppendToChatMessageListNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "Append to Chat Message List",
            "category": "LLM",
            "execution": "DATA",
            "inputs": [
                {"name": "message_list", "type": "list<chat_message>"},
                {
                    "name": "role",
                    "type": "str",
                    "widget": "str_select",
                    "options": {
                        "default": "user",
                        "choices": ["user", "assistant", "system"],
                    },
                },
                {"name": "content", "type": "str", "widget": "str_multiline"},
            ],
            "outputs": [{"name": "message_list", "type": "list<chat_message>"}],
        }

    def get_data(
        self, controller, role: str, content: str, message_list: list[ChatMessage] = []
    ) -> dict[str, any]:
        return {"message_list": message_list + [{"role": role, "content": content}]}


@app.node_def("LLM.OpenAIChatCompletionNode")
class OpenAIChatCompletionNode:
    @classmethod
    def meta(cls):
        return {
            "title": "OpenAI Chat Completion",
            "category": "LLM",
            "inputs": [
                {
                    "name": "api_key",
                    "type": "str",
                    "options": {"default": "", "multiline": False},
                },
                {
                    "name": "base_url",
                    "type": "str",
                    "options": {
                        "default": "https://api.deepseek.com",
                        "multiline": False,
                    },
                },
                {
                    "name": "model",
                    "type": "str",
                    "options": {"default": "deepseek-chat"},
                },
                {"name": "messages", "type": "list<chat_message>"},
                {"name": "temperature", "type": "float", "options": {"default": 0.7}},
                {"name": "max_tokens", "type": "int", "options": {"default": 1000}},
            ],
            "outputs": [
                {"name": "role", "type": "str"},
                {"name": "content", "type": "str"},
                {"name": "on_content_part", "type": "route"},
                {"name": "content_part", "type": "str"},
            ],
            "display": [{"name": "outputing", "type": "text"}],
        }

    def execute(
        self,
        controller,
        api_key: str,
        base_url: str,
        model: str,
        messages: list[ChatMessage],
        temperature: float,
        max_tokens: int,
    ) -> Iterator[NodeOutput]:
        client = OpenAI(api_key=api_key, base_url=base_url if base_url else None)

        response_text = ""
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        controller.send_event("display", {"outputing": ""})
        for chunk in completion:
            if chunk.choices and chunk.choices[0].delta.content:
                content_part = chunk.choices[0].delta.content
                response_text += content_part
                controller.send_event("append", {"outputing": content_part})
                yield NodeOutput(
                    execution_pin="on_content_part", data={"content_part": content_part}
                )
        yield NodeOutput(
            execution_pin=None, data={"role": "assistant", "content": response_text}
        )


@app.node_def("LLM.PromptTemplateNode")
class PromptTemplateNode(BaseDataNode):
    @classmethod
    def meta(cls) -> dict[str, any]:
        return {
            "title": "Prompt Template",
            "category": "LLM",
            "execution": "DATA",
            "inputs": [
                {"name": "template", "type": "str", "widget": "str_multiline"},
                {"name": "variables", "type": "dict<str, str>"},
            ],
            "outputs": [{"name": "prompt", "type": "str"}],
        }

    def get_data(
        self, controller, template: str, variables: dict[str, str]
    ) -> dict[str, any]:
        return {"prompt": string.Template(template).safe_substitute(variables)}
