# Smart Email Client - AI-Enhanced Email Management System

[![CircleCI](https://circleci.com/gh/your-username/smart-email-client.svg?style=shield)](https://circleci.com/gh/your-username/smart-email-client)
[![Coverage](https://img.shields.io/badge/coverage-85%2B%25-brightgreen)](https://circleci.com/gh/your-username/smart-email-client)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A professional-grade email client system showcasing component-based architecture, dependency injection, and AI-powered email analysis. Built with modern Python practices and comprehensive testing strategies.

## 🏗️ Architecture Overview

This project demonstrates enterprise-level software engineering practices through a sophisticated email client with AI-enhanced features:

```
smart-email-client/
├── src/                           # Component packages (uv workspace)
│   ├── email_client_api/         # Abstract email service protocols
│   ├── email_message/            # Email message data models  
│   ├── gmail_message_impl/       # Gmail-specific message parsing
│   ├── gmail_client_impl/        # Gmail API service implementation
│   └── email_analytics/          # AI-powered email analysis
├── tests/                        # Integration and E2E tests
│   ├── integration/              # Component interaction tests
│   └── e2e/                      # Full system workflow tests
├── .circleci/                    # Professional CI/CD pipeline
└── main.py                       # Demonstration application
```

### 🎯 Core Design Principles

- **Protocol-Based Architecture**: Abstract interfaces separate from concrete implementations
- **Dependency Injection**: Runtime implementation binding for maximum flexibility
- **AI Integration**: Intelligent email analysis without external API dependencies
- **Test-Driven Development**: Comprehensive testing at unit, integration, and E2E levels
- **Production-Ready Tooling**: Professional CI/CD, type safety, and code quality

## ✨ Key Features

### 📧 Core Email Operations
- **Gmail API Integration**: Full OAuth2 authentication with multiple modes
- **CRUD Operations**: Read, delete, mark read/unread with robust error handling
- **Advanced Search**: Gmail query syntax support with intelligent filtering
- **Message Threading**: Conversation tracking and thread management

### 🤖 AI-Powered Analysis
- **Priority Scoring**: Intelligent email prioritization based on content and metadata
- **Sentiment Analysis**: Emotion detection using advanced keyword algorithms
- **Content Categorization**: Automatic classification (work, personal, promotional, etc.)
- **Spam Detection**: Multi-factor spam probability assessment
- **Response Suggestions**: AI recommendations for emails requiring responses

### 📊 Productivity Insights
- **Communication Patterns**: Analysis of email habits and peak activity times
- **Response Efficiency**: Metrics on email processing and response times
- **Productivity Recommendations**: AI-generated suggestions for inbox optimization
- **Email Overload Assessment**: Risk analysis and management strategies

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- Gmail API credentials (see setup instructions below)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/smart-email-client.git
   cd smart-email-client
   ```

2. **Install uv package manager:**
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Windows (PowerShell)
   irm https://astral.sh/uv/install.ps1 | iex
   ```

3. **Set up the development environment:**
   ```bash
   # Create virtual environment and install all dependencies
   uv sync --all-packages --dev
   
   # Activate virtual environment
   source .venv/bin/activate  # macOS/Linux
   # or
   .venv\Scripts\Activate.ps1  # Windows
   ```

### Gmail API Setup

1. **Enable Gmail API in Google Cloud Console:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable the Gmail API
   - Create OAuth 2.0 credentials for desktop application

2. **Download credentials:**
   - Download the `credentials.json` file
   - Place it in the project root directory

3. **For CI/CD environments (optional):**
   ```bash
   export GMAIL_CLIENT_ID="your_client_id"
   export GMAIL_CLIENT_SECRET="your_client_secret" 
   export GMAIL_REFRESH_TOKEN="your_refresh_token"
   ```

### First Run

```bash
# Run the smart email client demonstration
python main.py
```

This will:
- Perform interactive OAuth2 authentication (first time only)
- Demonstrate all core features with your actual Gmail data
- Show AI analysis results and productivity insights

## 🧪 Development Workflow

### Running Tests

```bash
# Run all unit tests with coverage
pytest src/ -m "unit" --cov=src --cov-report=term-missing

# Run integration tests (CI-compatible)
pytest src/ tests/ -m "integration and not local_credentials" -v

# Run full test suite
pytest --cov=src --cov-report=html

# Run specific component tests
pytest src/email_analytics/tests/ -v
```

### Code Quality

```bash
# Linting and formatting
ruff check .                 # Check for issues
ruff check . --fix          # Auto-fix issues
ruff format .               # Apply formatting

# Type checking
mypy src/ --explicit-package-bases

# Security scanning
uv pip check                # Vulnerability scan
```

### Documentation

```bash
# Generate and serve documentation (if MkDocs is configured)
mkdocs serve
```

## 🏭 Production Deployment

### CI/CD Pipeline

The project includes a comprehensive CircleCI configuration with:

- **Quality Gates**: Linting, type checking, security scanning
- **Multi-Level Testing**: Unit, integration, and E2E test suites
- **Coverage Reporting**: Automated coverage tracking with 85% threshold
- **Branch-Specific Workflows**: Enhanced validation for main/develop branches
- **Artifact Management**: Test results, coverage reports, and build summaries

### Environment Configuration

For production deployment:

1. **Set environment variables:**
   ```bash
   GMAIL_CLIENT_ID=your_production_client_id
   GMAIL_CLIENT_SECRET=your_production_client_secret
   GMAIL_REFRESH_TOKEN=your_production_refresh_token
   ```

2. **Deploy using your preferred method:**
   - Docker containerization
   - Serverless functions (AWS Lambda, Google Cloud Functions)
   - Traditional server deployment

## 📁 Component Deep Dive

### Email Client API (`src/email_client_api/`)
- **Purpose**: Abstract protocols defining email service contracts
- **Key Features**: Runtime-checkable protocols, factory pattern, type safety
- **Dependencies**: None (pure protocol definitions)

### Email Message (`src/email_message/`)
- **Purpose**: Email message data models and parsing contracts
- **Key Features**: Rich metadata support, extensible properties, protocol compliance
- **Dependencies**: None (pure protocol definitions)

### Gmail Message Implementation (`src/gmail_message_impl/`)
- **Purpose**: Gmail-specific message parsing and data extraction  
- **Key Features**: Gmail API response parsing, metadata extraction, error handling
- **Dependencies**: `email_message`, `google-api-python-client`

### Gmail Client Implementation (`src/gmail_client_impl/`)
- **Purpose**: Gmail API service implementation with full CRUD operations
- **Key Features**: OAuth2 authentication, comprehensive error handling, rate limiting
- **Dependencies**: `email_client_api`, `gmail_message_impl`, Google API libraries

### Email Analytics (`src/email_analytics/`)
- **Purpose**: AI-powered email analysis and productivity insights
- **Key Features**: Priority scoring, sentiment analysis, pattern recognition, recommendations
- **Dependencies**: `email_message`, `email_client_api`

## 🧪 Testing Strategy

### Test Categories

- **Unit Tests** (`src/*/tests/`): Fast, isolated component testing with mocks
- **Integration Tests** (`tests/integration/`): Component interaction validation
- **End-to-End Tests** (`tests/e2e/`): Full system workflow testing
- **CI/CD Tests**: Automated testing compatible with headless environments

### Test Markers

```python
@pytest.mark.unit              # Fast unit tests
@pytest.mark.integration       # Integration tests  
@pytest.mark.e2e              # End-to-end tests
@pytest.mark.circleci         # CI/CD compatible
@pytest.mark.local_credentials # Requires local auth files
```

## 🤝 Contributing

1. **Fork the repository** and create a feature branch
2. **Follow the coding standards**: Use ruff for formatting and linting
3. **Write comprehensive tests**: Maintain 85%+ coverage
4. **Update documentation**: Keep README and docstrings current
5. **Submit a pull request** with clear description of changes

### Development Standards

- **Type Safety**: Full mypy compliance in strict mode
- **Code Quality**: Ruff linting with comprehensive rule set
- **Test Coverage**: Minimum 85% with meaningful test cases
- **Documentation**: Professional-grade docstrings and README

## 📊 Performance Metrics

- **Build Time**: Complete CI pipeline under 10 minutes
- **Test Coverage**: 85%+ with comprehensive test suites
- **Type Safety**: 100% mypy compliance in strict mode
- **Code Quality**: Zero ruff violations with professional standards

## 🔧 Troubleshooting

### Common Issues

**Authentication Errors:**
- Ensure `credentials.json` is in project root
- Check Gmail API is enabled in Google Cloud Console
- Verify OAuth consent screen is configured

**Import Errors:**
- Run `uv sync --all-packages --dev` to ensure all dependencies are installed
- Activate virtual environment before running commands

**Test Failures:**
- Use `pytest src/ tests/ -m "not local_credentials"` for CI-compatible testing
- Ensure environment variables are set for integration tests

### Getting Help

- **Issues**: Report bugs and feature requests on GitHub Issues
- **Documentation**: Check inline docstrings and code comments
- **Examples**: Review `main.py` for comprehensive usage examples

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gmail API**: For comprehensive email service integration
- **Python Community**: For excellent tooling (uv, ruff, mypy, pytest)
- **Component Architecture**: Inspired by enterprise software engineering practices

---

**Built with ❤️ using modern Python practices and professional software engineering standards.**