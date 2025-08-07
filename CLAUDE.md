# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

- **Development server**: `uvicorn main:app --reload` - runs FastAPI server with auto-reload
- **Install dependencies**: `uv add <package>` - uses uv for dependency management
- **Run tests**: No test files found yet - create tests directory and add pytest configuration
- **Linting**: Use `ruff check .` or `mypy main.py` for type checking

## Architecture

This is a simple FastAPI application with:
- **Entry point**: `main.py` - contains FastAPI app instance and basic routes
- **Current routes**:
  - `GET /` - returns `{"Hello": "World"}`
  - `GET /items/{item_id}` - returns item with optional query parameter `q`
- **Dependencies**: 
  - FastAPI 0.116.1+ (web framework)
  - uvicorn 0.35.0+ (ASGI server)
  - httpx 0.27.0+ (async-compatible HTTP client for making external API calls)
- **Python**: Requires Python 3.13+

## Project Setup

- Uses `uv` for package management (see `pyproject.toml`)
- Has SonarQube configuration ready (`sonar-project.properties`)
- Currently minimal structure - extend from `main.py` as needed