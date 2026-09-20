from core.claude import Claude
from mcp_client import MCPClient
from core.tools import ToolManager
from anthropic.types import Message, MessageParam
from typing import Any, Awaitable, Callable, Protocol, cast


class ChatStreamProvider(Protocol):
    chat_stream: Callable[..., Awaitable[Message]]


class ChatProvider(Protocol):
    chat: Callable[..., Awaitable[Message]]


class MessageManager(Protocol):
    def add_assistant_message(
        self, messages: list[MessageParam], message: Message
    ) -> None: ...

    def add_user_message(
        self, messages: list[MessageParam], message: Any
    ) -> None: ...


class Chat:
    def __init__(self, claude_service: Claude, clients: dict[str, MCPClient]):
        self.claude_service: Claude = claude_service
        self.clients: dict[str, MCPClient] = clients
        self.messages: list[MessageParam] = []
    async def _process_query(self, query: str):
        self.messages.append({"role": "user", "content": query})
    async def run(
        self,
        query: str,
        stream: bool = False,
        on_event: Callable[..., Any] | None = None,
    ) -> str:
        final_text_response = ""
        await self._process_query(query)
        while True:
            if stream and on_event:
                chat_stream = cast(ChatStreamProvider, self.claude_service).chat_stream
                response = await chat_stream(
                    messages=self.messages,
                    tools=await ToolManager.get_all_tools(self.clients),
                    on_event=on_event,
                )
            else:
                chat = cast(ChatProvider, self.claude_service).chat
                response = await chat(
                    messages=self.messages,
                    tools=await ToolManager.get_all_tools(self.clients),
                )
            cast(MessageManager, self.claude_service).add_assistant_message(
                self.messages, response
            )
            if response.stop_reason == "tool_use":
                if not stream:
                    print(self.claude_service.text_from_message(response))
                tool_result_parts = await ToolManager.execute_tool_requests(
                    self.clients, response
                )
                cast(MessageManager, self.claude_service).add_user_message(
                    self.messages, tool_result_parts
                )
            else:
                final_text_response = self.claude_service.text_from_message(
                    response
                )
                break
        return final_text_response
