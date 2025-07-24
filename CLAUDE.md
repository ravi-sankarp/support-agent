# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **SolidWorks Support Agent** - a specialized AI agent that provides SolidWorks CAD software support using the Perplexity API for real-time technical assistance. The project is built with Python using Poetry for dependency management and includes both a command-line interface and a Streamlit web UI.

## Code Architecture

### Core Components

1. **`src/agent.py`** - Core business logic (UI-agnostic)
   - `SolidWorksAgentCore` - Main agent class with session management
   - `ChatSession`, `ChatMessage`, `AgentResponse` - Data models
   - `MessageType`, `ResponseType` - Enums for message/response classification

2. **`src/perplexity_helper.py`** - Perplexity API integration
   - `PerplexityHelper` - API client with SolidWorks-specific prompt formatting
   - Handles model switching, connection testing, error handling
   - Domain filtering for SolidWorks-specific sources

3. **`src/steamlit_ui.py`** - Streamlit web interface
   - Pure UI layer that uses `SolidWorksAgentCore`
   - Session state management, chat interface rendering
   - Sidebar controls for model switching and session management


### Architecture Pattern

The project follows a **layered architecture**:
- **UI Layer**: Streamlit interface (`steamlit_ui.py`)
- **Business Logic Layer**: Agent core (`agent.py`) 
- **Integration Layer**: Perplexity API client (`perplexity_helper.py`)

This separation allows the core business logic to be reused across different UIs (CLI, web, API, etc.).

### Key Design Decisions

- **Session Management**: Multi-session support with session state persistence
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Source Requirements**: Responses must include SolidWorks documentation sources
- **Context Validation**: Agent asks for clarification when queries lack sufficient context
- **Model Flexibility**: Support for switching between Perplexity models (sonar-pro, sonar)
