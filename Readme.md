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

### 1. Install Poetry (if not already installed)
```bash
# macOS/Linux
curl -sSL https://install.python-poetry.org | python3 -

# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# Or via pip
pip install poetry
```

### 2. Clone and Setup
```bash
# Clone the project
git clone <repository-url>
cd beacon-support-agent

# Install dependencies
poetry install
```

### 3. Setup Environment Variables
Create a `.env` file and add your Perplexity API key:
```bash
PERPLEXITY_API_KEY=your_actual_api_key_here
```

### 4. Get Your Perplexity API Key
1. Go to [Perplexity API Settings](https://www.perplexity.ai/settings/api)
2. Create an account or sign in
3. Generate a new API key
4. Copy and paste it into your `.env` file

### 5. Run the Agent

#### Web Interface (Streamlit)
```bash
# Launch web UI
poetry run solidworks-streamlit

# Or manually
poetry run streamlit run src/streamlit_ui.py
```

#### Command Line Interface
```bash
# Launch CLI
poetry run solidworks-agent
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

## 🔧 Usage

### Web Interface
The Streamlit web interface provides:
- 💬 **Chat Interface**: Interactive conversation with session management
- 🔄 **Model Switching**: Toggle between sonar-pro and sonar models
- 📊 **Session Management**: Create, switch, and clear conversation sessions
- 📱 **Responsive Design**: Works on desktop and mobile devices

### Command Line Interface
The CLI provides a terminal-based chat experience with the same core functionality.

### Example Questions
- "SolidWorks crashes when opening large assemblies"
- "How to create parametric configurations in SolidWorks"
- "Best practices for SolidWorks simulation mesh settings"
- "Troubleshoot SolidWorks PDM vault connection issues"
- "How to optimize SolidWorks performance for large models"

### Key Behaviors
- ✅ **SolidWorks-Only**: Exclusively answers SolidWorks-related questions
- ❌ **Polite Rejection**: Redirects non-SolidWorks queries appropriately
- 🔍 **Real-time Search**: Uses current web information for accurate answers
- 📚 **Source Citations**: All responses include relevant documentation sources
- 🤖 **Context Aware**: Asks for clarification when queries lack sufficient detail

## 🏗️ Architecture

The project follows a **layered architecture** pattern:

- **UI Layer**: `streamlit_ui.py` - Pure presentation logic
- **Business Logic Layer**: `agent.py` - Core agent functionality, UI-agnostic
- **Integration Layer**: `perplexity_helper.py` - External API communication

This separation enables easy extension to additional interfaces (API, desktop app, etc.).

## 🛠️ Development

### Poetry Commands
```bash
# Install all dependencies (including dev dependencies)
poetry install

# Run linting and formatting
poetry run black src/
poetry run flake8 src/
poetry run mypy src/

# Run tests
poetry run pytest
```

### Environment Variables
```bash
# .env file
PERPLEXITY_API_KEY=your_key_here
PERPLEXITY_MODEL=sonar-pro      # Optional: default model (sonar-pro or sonar)
DEBUG=false                     # Optional: enable debug logging
```

## 📊 Available Models

- **sonar-pro**: Advanced model with comprehensive search capabilities and higher accuracy
- **sonar**: Lightweight model for simpler queries with faster response times

## 🔒 Security & Best Practices

- 🔐 **Never commit your `.env` file** to version control
- 🔑 **Keep your API key secure** and rotate it regularly
- 📁 **Use .gitignore**: The `.env` file is automatically ignored by git
- 🛡️ **Input Validation**: All user inputs are validated and sanitized
- 🚫 **Domain Restrictions**: Responses are filtered to SolidWorks-relevant sources only

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and run tests: `poetry run pytest`
4. Format code: `poetry run black src/`
5. Submit a pull request

## 📄 License

[Add your license information here]
