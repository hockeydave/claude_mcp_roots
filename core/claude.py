from typing import Any, Awaitable, Callable, cast

from anthropic import AsyncAnthropic
from anthropic.types import Message


class Claude:
    def __init__(self, model: str):
        self.client = AsyncAnthropic()
        self.model = model

    def add_user_message(self, messages: list[dict[str, Any]], message: Any):
        user_message: dict[str, Any] = {
            "role": "user",
            "content": message.content
            if isinstance(message, Message)
            else message,
        }
        messages.append(user_message)

    def add_assistant_message(
        self, messages: list[dict[str, Any]], message: Any
    ) -> None:
        assistant_message: dict[str, Any] = {
            "role": "assistant",
            "content": message.content
            if isinstance(message, Message)
            else message,
        }
        messages.append(assistant_message)

    def text_from_message(self, message: Message):
        return "".join(
            [block.text for block in message.content if block.type == "text"]
        )

    async def chat(
        self,
        messages: list[dict[str, Any]],
        system: str | None = None,
        stop_sequences: list[str] | None = None,
        tools: list[dict[str, Any]] | None = None,
        thinking: bool = False,
        thinking_budget: int = 1024,
    ) -> Message:
        params: dict[str, Any] = {
            "model": self.model,
            "max_tokens": 8000,
            "messages": messages,
            "stop_sequences": stop_sequences or [],
        }
        if thinking:
            params["thinking"] = {
                "type": "enabled",
                "budget_tokens": thinking_budget,
            }
        if tools:
            params["tools"] = tools
        if system:
            params["system"] = system
        message = cast(Message, await self.client.messages.create(**params))
        return message

    async def chat_stream(
        self,
        messages: list[dict[str, Any]],
        system: str | None = None,
        temperature: float = 1.0,
        stop_sequences: list[str] | None = None,
        tools: list[dict[str, Any]] | None = None,
        thinking: bool = False,
        thinking_budget: int = 1024,
        on_event: Callable[[Any], Awaitable[None]] | None = None,
    ) -> Message:
        # The current Anthropic stream API does not accept a `temperature` keyword.
        # Keep the parameter for compatibility, but do not forward it to the SDK.
        params: dict[str, Any] = {
            "model": self.model,
            "max_tokens": 8000,
            "messages": messages,
            "stop_sequences": stop_sequences or [],
        }
        if thinking:
            params["thinking"] = {
                "type": "enabled",
                "budget_tokens": thinking_budget,
            }
        if tools:
            params["tools"] = tools
        if system:
            params["system"] = system

        stream: Any = self.client.messages.stream(**params)
        async with stream as stream_handle:
            if on_event is not None:
                async for event in stream_handle:
                    await on_event(event)
            else:
                async for _event in stream_handle:
                    pass

        return await stream_handle.get_final_message()
