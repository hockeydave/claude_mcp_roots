import json
import os
from pathlib import Path

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from core.video_converter import VideoConverter

mcp = MCPServer("VidsMCP", log_level="ERROR")


def get_allowed_roots() -> list[Path]:
    raw = os.getenv("ALLOWED_ROOTS", "[]")
    try:
        values = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return [Path(value).expanduser().resolve() for value in values if value]


def is_path_allowed(requested_path: Path) -> bool:
    requested_path = requested_path.resolve()
    if not requested_path.exists():
        return False
    if requested_path.is_file():
        requested_path = requested_path.parent
    for root in get_allowed_roots():
        try:
            requested_path.relative_to(root)
            return True
        except ValueError:
            continue
    return False


@mcp.tool()
async def convert_video(
    input_path: str = Field(description="Path to the input MP4 file"),
    format: str = Field(description="Output format (e.g. 'mov')"),
):
    """Convert an MP4 video file to another format using ffmpeg."""
    input_file = VideoConverter.validate_input(input_path)
    if not is_path_allowed(input_file):
        raise ValueError(f"Access to path is not allowed: {input_path}")
    return await VideoConverter.convert(input_path, format)


@mcp.tool()
async def list_allowed_directories() -> list[str]:
    """List the explicitly allowed directories configured for this server."""
    return [str(path) for path in get_allowed_roots()]


@mcp.tool()
async def read_dir(
    path: str = Field(description="Path to a directory to read"),
):
    """Read directory contents for an explicit path inside an allowed directory."""
    requested_path = Path(path).expanduser().resolve()
    if not is_path_allowed(requested_path):
        raise ValueError("Error: can only read directories within an allowed root")
    return [entry.name for entry in requested_path.iterdir()]


if __name__ == "__main__":
    mcp.run(transport="stdio")
