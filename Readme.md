# SolidWorks Support Agent

A specialized AI agent for SolidWorks CAD software support using Perplexity API for real-time technical assistance. Available as both a command-line interface and web application.

## ✨ Features

- 🎯 **SolidWorks-Specialized**: Focused exclusively on SolidWorks CAD software support
- 🌐 **Real-time Information**: Uses Perplexity API for current technical knowledge
- 💬 **Multi-Session Support**: Manage multiple conversation sessions
- 🖥️ **Dual Interface**: Command-line and web UI options
- 📚 **Source-backed Responses**: All answers include relevant documentation sources
- 🔄 **Model Flexibility**: Switch between Perplexity models (sonar-pro, sonar)

## 🚀 Quick Setup

### Prerequisites
- Python 3.9+ (excluding 3.9.7)
- [Poetry](https://python-poetry.org/docs/#installation) for dependency management


#### Web Interface (Streamlit)
```bash
poetry run streamlit run src/streamlit_ui.py
```


## 📁 Project Structure
```
beacon-support-agent/
├── src/
│   ├── agent.py              # Core business logic (UI-agnostic)
│   ├── perplexity_helper.py  # Perplexity API integration
│   └── streamlit_ui.py        # Streamlit web interface
├── pyproject.toml            # Poetry configuration & dependencies
├── poetry.lock               # Dependency lock file (auto-generated)
├── CLAUDE.md                 # Development guidelines
├── .gitignore                # Git ignore patterns
├── .env                      # Environment variables (create this)
└── README.md                 # This file
```

## 🏗️ Architecture

The project follows a **layered architecture** pattern:

- **UI Layer**: `streamlit_ui.py` - Pure presentation logic
- **Business Logic Layer**: `agent.py` - Core agent functionality, UI-agnostic
- **Integration Layer**: `perplexity_helper.py` - External API communication

This separation enables easy extension to additional interfaces (API, desktop app, etc.).

### Environment Variables
```bash
# .env file
PERPLEXITY_API_KEY=your_key_here
PERPLEXITY_MODEL=sonar-pro      # Optional: default model (sonar-pro or sonar)
DEBUG=false                     # Optional: enable debug logging
```