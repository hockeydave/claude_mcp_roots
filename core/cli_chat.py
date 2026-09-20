from typing import Any, Awaitable, Callable, List, cast

from anthropic.types import MessageParam
from mcp.types import Prompt, PromptMessage

from core.chat import Chat
from core.claude import Claude
from mcp_client import MCPClient


class CliChat(Chat):
    def __init__(
        self,
        doc_client: MCPClient,
        clients: dict[str, MCPClient],
        claude_service: Claude,
    ):
        super().__init__(clients=clients, claude_service=claude_service)
        self.doc_client: MCPClient = doc_client

    async def list_prompts(self) -> list[Prompt]:
        return await self.doc_client.list_prompts()

    async def get_prompt(
        self, command: str, doc_id: str
    ) -> list[PromptMessage]:
        get_prompt = cast(
            Callable[[str, dict[str, str]], Awaitable[list[PromptMessage]]],
            getattr(self.doc_client, "get_prompt"),
        )
        return await get_prompt(command, {"doc_id": doc_id})

    async def _process_query(self, query: str):
        self.messages.append({"role": "user", "content": query})


def _field_value(obj: Any, key: str) -> Any:
    if isinstance(obj, dict):
        return cast(dict[str, Any], obj).get(key)
    return getattr(obj, key, None)


def convert_prompt_message_to_message_param(
    prompt_message: "PromptMessage",
) -> MessageParam:
    role = "user" if prompt_message.role == "user" else "assistant"
    content: Any = prompt_message.content

    if isinstance(content, dict):
        content_dict = cast(dict[str, Any], content)
        content_type = _field_value(content_dict, "type")
        if content_type == "text":
            return cast(
                MessageParam,
                {"role": role, "content": str(_field_value(content_dict, "text") or "")},
            )
    elif hasattr(content, "__dict__"):
        content_obj = content
        content_type = _field_value(content_obj, "type")
        if content_type == "text":
            return cast(
                MessageParam,
                {"role": role, "content": str(_field_value(content_obj, "text") or "")},
            )

    if isinstance(content, list):
        text_blocks: list[dict[str, str]] = []
        items = cast(list[Any], content)
        for item in items:
            if isinstance(item, dict):
                item_dict = cast(dict[str, Any], item)
                if _field_value(item_dict, "type") == "text":
                    text_blocks.append(
                        {"type": "text", "text": str(_field_value(item_dict, "text") or "")}
                    )
            elif hasattr(item, "__dict__"):
                item_obj = item
                if _field_value(item_obj, "type") == "text":
                    text_blocks.append(
                        {"type": "text", "text": str(_field_value(item_obj, "text") or "")}
                    )
        if text_blocks:
            return cast(
                MessageParam,
                {"role": role, "content": text_blocks},
            )

    return cast(MessageParam, {"role": role, "content": ""})


def convert_prompt_messages_to_message_params(
    prompt_messages: List[PromptMessage],
) -> List[MessageParam]:
    return [
        convert_prompt_message_to_message_param(msg) for msg in prompt_messages
    ]
