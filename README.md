# MCP Chat with File System Access
MCP Chat is a command-line interface application that enables interactive chat capabilities with AI models through the Anthropic API. The application supports file system operations with controlled access to explicitly allowed directories, video conversion capabilities, and extensible tool integrations via the MCP architecture.

## MCP Specification
github.com/modelcontextprotocol/modelcontextprotocol
* Defines how MCP clients and servers should behave
* Defines all the different valid message types (Typescript)

## Prerequisites
- Python 3.10+
- Anthropic API Key
- FFmpeg (for video conversion features)

## Setup
_You must have FFmpeg already installed to convert a video file_. To install FFmpeg on macOS run:
```bash
brew install ffmpeg
```

### Step 1: Configure the environment variables
1. Copy the `.env.example` file to create a new `.env` file:
```bash
cp .env.example .env
```
2. Edit the `.env` file and set your environment variables:
```bash
CLAUDE_MODEL="claude-sonnet-4-5"  # Or your preferred Claude model
ANTHROPIC_API_KEY=""  # Enter your Anthropic API secret key
```

### Step 2: Install dependencies
#### Setup with uv
[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver.
1. Install uv, if not already installed:
```bash
pip install uv
```
2. Install dependencies:
```bash
uv sync
```

### Step 3: Run the project
When running the project, pass one or more directories that the MCP server is allowed to access. The server enforces that policy explicitly instead of using the deprecated roots capability.

```bash
uv run main.py <allowed_dir1> [allowed_dir2] [allowed_dir3] ...
```

Examples:
```bash
# Single directory
uv run main.py /Users/you/Downloads

# Multiple directories
uv run main.py /Users/you/Downloads /Volumes/media /Users/you/Documents

# Current directory
uv run main.py .
```

## Features
### File System Access
The server can only access files and directories within the explicitly configured allowed paths. This provides security by limiting file system access to approved locations.

### Available Tools
- **list_allowed_directories**: List the directories currently configured as allowed for the server
- **read_dir**: Read contents of a directory (must be inside an allowed path)
- **convert_video**: Convert MP4 videos to other formats (avi, mov, webm, mkv, gif)

### Video Conversion
The video conversion tool uses FFmpeg to convert MP4 files to various formats:
- Standard video formats: AVI, MOV, WebM, MKV
- GIF conversion with optimized settings
- Medium quality preset for balanced file size and quality
