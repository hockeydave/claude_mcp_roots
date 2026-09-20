from __future__ import annotations

import json
from contextlib import AsyncExitStack
from types import TracebackType
from typing import Any, Optional

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client


class MCPClient:
    def __init__(
        self,
        command: str,
        args: list[str],
        env: Optional[dict[str, str]] = None,
        allowed_roots: Optional[list[str]] = None,
    ):
        self._command = command
        self._args = args
        self._env = env
        self._allowed_roots = allowed_roots or []
        self._session: Optional[ClientSession] = None
        self._exit_stack: AsyncExitStack = AsyncExitStack()

    async def connect(self):
        server_params = StdioServerParameters(
            command=self._command,
            args=self._args,
            env=self._env,
        )
        stdio_transport = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        _stdio, _write = stdio_transport
        self._session = await self._exit_stack.enter_async_context(
            ClientSession(_stdio, _write)
        )
        await self._session.initialize()
    def session(self) -> ClientSession:
        if self._session is None:
            raise ConnectionError(
                "Client session not initialized or cache not populated. Call connect_to_server first."
            )
        return self._session
    async def list_tools(self) -> list[types.Tool]:
        result = await self.session().list_tools()
        return result.tools
    async def call_tool(
        self, tool_name: str, tool_input: dict[str, Any] | None
    ) -> types.CallToolResult | None:
        return await self.session().call_tool(tool_name, tool_input)

    async def list_prompts(self) -> list[types.Prompt]:
        result = await self.session().list_prompts()
        return result.prompts

    async def get_prompt(
        self, prompt_name: str, args: dict[str, str]
    ) -> list[Any]:
        result = await self.session().get_prompt(prompt_name, args)
        return result.messages

    async def read_resource(self, uri: str) -> Any:
        result = await self.session().read_resource(uri)
        resource = result.contents[0]
        if isinstance(resource, types.TextResourceContents):
            mime_type = getattr(resource, "mimeType", None)
            if mime_type == "application/json":
                return json.loads(resource.text)
            return resource.text
        return resource

    async def cleanup(self) -> None:
        await self._exit_stack.aclose()
        self._session = None

    async def __aenter__(self) -> "MCPClient":
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.cleanup()
