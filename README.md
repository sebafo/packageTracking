# Shipment Tracking Agent Sample

This sample application demonstrates how to create a conversational AI agent using Semantic Kernel that can answer shipment tracking questions by calling the Demo Shipment Tracker API.

## Features

- **Single Agent Architecture**: Built as a single conversational agent following the pattern from the workshop
- **Function Calling**: Uses Semantic Kernel's automatic function calling to interact with the tracking API
- **Natural Language Interface**: Users can ask tracking questions in natural language
- **Configurable API**: Can use either simulated responses or real API calls
- **Real HTTP Integration**: Supports calling actual REST APIs with authentication

## Setup

### Prerequisites

1. Make sure you have Python 3.13+ installed
2. [uv](https://github.com/astral-sh/uv) (recommended for dependency management)
3. Set up your configuration in a `.env` file (copy from `.env.example`)

### Configuration

Copy the `.env.example` file to `.env` and configure your settings:

```bash
# Azure OpenAI Configuration (required)
AZURE_OPENAI_ENDPOINT=your-endpoint-here
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=your-chat-deployment-name
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=your-embedding-deployment-name

# Shipment API Configuration
SHIPMENT_API_BASE_URL=https://your-actual-api-domain.com
SHIPMENT_API_KEY=your_api_key_here  # Optional, for authenticated APIs
USE_SIMULATED_API=false  # Set to true for demo mode, false for real API
```

### Installation

Install dependencies using uv:

```bash
# Install dependencies from pyproject.toml
uv sync

# Alternatively, if you don't have a lockfile:
uv pip install -r pyproject.toml
```

Dependencies are automatically managed by uv for reproducible installs.

## Usage

Run the application using uv:
```bash
# Basic usage
uv run src/app.py

# Show help
uv run src/app.py --help

# Enable verbose logging for debugging
uv run src/app.py --verbose
```

You can also run it from the project root using the main entry point:
```bash
# Alternative entry point
uv run main.py
```

### Example Conversations

Try these example queries:

- `"Track package PKG123456789"`
- `"What's the status of my shipment PKG987654321?"`
- `"Can you help me track my package?"`
- `"Where is my package PKG123456789 right now?"`
- `"When was my package PKG123456789 last updated?"`

### Sample Tracking IDs (Simulation Mode)

When `USE_SIMULATED_API=true`, the app includes these sample tracking IDs:

- `PKG123456789` - Returns a detailed package with multiple status updates (Electronics from Munich to Paris)
- Any other tracking ID starting with `PKG` - Returns a generic delivered package
- Invalid tracking IDs - Returns appropriate error messages

## Code Structure

The application has been restructured into a modular architecture for better maintainability and reusability:

### 📁 Project Structure

```
src/
├── __init__.py              # Package initialization
├── main.py                  # Main entrypoint with interactive session
├── agent.py                 # Core ShipmentTrackingAgent class
├── config.py                # Configuration management
├── utils/                   # Utility modules
│   ├── __init__.py
│   ├── logging_config.py    # Logging setup and configuration
│   └── spinner.py           # Spinner animation utility / not used in this version
├── filters/                 # Semantic Kernel filters
│   ├── __init__.py
│   └── verbose_function_filter.py  # Function call logging
└── plugins/                 # Semantic Kernel plugins
    ├── __init__.py
    └── shipment_tracking_plugin.py  # API integration and simulation
```

### Core Components

#### `config.py` - Configuration Management
Centralized configuration class that:
- Loads environment variables from `.env` file
- Validates required configuration
- Provides configuration validation methods

#### `agent.py` - ShipmentTrackingAgent
The main agent class that orchestrates the conversation:
- **setup_kernel()**: Configures Semantic Kernel with AI services and plugins
- **chat()**: Processes user messages and returns responses
- **reset_conversation()**: Resets the chat history

#### `plugins/shipment_tracking_plugin.py` - ShipmentTrackingPlugin
This plugin implements the core functionality for tracking packages:
- **track_package()**: Main function that accepts tracking ID and optional date filters
- **get_current_date_and_time()**: Provides current timestamp for date-based queries
- **_call_real_api()**: Makes HTTP requests to actual tracking APIs
- **_simulate_api_response()**: Simulates API responses for demo purposes

#### `utils/` - Utility Modules
- **logging_config.py**: Logging setup with verbose mode support
- **spinner.py**: Console spinner animation for better UX

#### `filters/` - Function Call Filters
- **verbose_function_filter.py**: Detailed logging of function invocations for debugging

#### `main.py` - Command Line Interface
Handles user interaction:
- Command-line argument parsing
- Interactive chat session management
- Welcome messages and help text
- Error handling and graceful shutdown

## API Integration

The application supports both simulated and real API integration:

### Real API Mode (`USE_SIMULATED_API=false`)

When configured for real API calls, the application:

1. Makes HTTP GET requests to the configured `SHIPMENT_API_BASE_URL`
2. Includes authentication headers if `SHIPMENT_API_KEY` is provided
3. Handles common HTTP status codes (200, 404, etc.)
4. Includes proper error handling for network issues and timeouts
5. Supports query parameters for tracking ID and date filters

### API Authentication

The application supports multiple authentication methods that can be configured:

```python
# Bearer token (default)
headers["Authorization"] = f"Bearer {self.api_key}"

# Alternative formats (uncomment as needed):
# headers["X-API-Key"] = self.api_key
# headers["Authorization"] = f"ApiKey {self.api_key}"
```

### Error Handling

The application includes comprehensive error handling:

- **Network errors**: Connection issues, DNS failures
- **Timeouts**: 30-second timeout for API calls
- **HTTP errors**: Non-200 status codes with detailed error messages
- **Package not found**: 404 responses handled gracefully
- **API key issues**: Authentication failures

## Real API Integration Example

To integrate with your actual tracking API:

1. Set the correct base URL in your `.env` file:
```bash
SHIPMENT_API_BASE_URL=https://api.yourshipper.com
```

2. Add your API key if required:
```bash
SHIPMENT_API_KEY=your_actual_api_key
```

3. Disable simulation mode:
```bash
USE_SIMULATED_API=false
```

4. Ensure your API follows the expected request/response format or modify the plugin accordingly.

## Extending the Application

The modular structure makes it easy to extend the application:

1. **Adding new plugins**: Create new plugin classes in the `plugins/` directory
2. **Adding new utilities**: Add utility functions to the `utils/` package
3. **Adding new filters**: Implement custom filters in the `filters/` package
4. **Custom configuration**: Extend the `Config` class for new environment variables
5. **Multiple agents**: Create specialized agents by extending the base agent class
6. **Custom authentication**: Modify the plugin's API authentication methods

### Example: Adding a New Plugin

```python
# src/plugins/new_plugin.py
from semantic_kernel.functions import kernel_function

class NewPlugin:
    @kernel_function
    async def new_function(self, param: str) -> dict:
        # Your implementation here
        return {"result": "success"}
```

### Example: Adding a New Utility

```python
# src/utils/new_utility.py
def new_helper_function():
    # Your utility function here
    pass
```

## Architecture Notes

This application follows a modular single agent pattern with the following principles:

- **Modular Design**: Each component has a single responsibility and can be tested independently
- **Semantic Kernel Integration**: Uses automatic function calling capabilities
- **Configuration Management**: Centralized environment variable handling with validation
- **Separation of Concerns**: Clear separation between CLI, agent logic, plugins, and utilities
- **Maintainable Structure**: Easy to extend, test, and debug individual components
- **Natural Language Interface**: Provides intuitive conversation flow for complex API interactions
- **Dual Mode Support**: Both development (simulated) and production (real API) modes

The agent automatically determines when to call the tracking function based on user queries, making it easy to ask questions like "Where is my package?" without needing to specify exact function calls.

### Benefits of the Modular Structure

1. **🧱 Testability**: Each module can be unit tested independently
2. **🔄 Reusability**: Components can be imported and used in other projects
3. **📖 Maintainability**: Easier to locate and fix issues
4. **⚙️ Extensibility**: Simple to add new features without touching existing code
5. **🔍 Debugging**: Verbose logging and clear separation make debugging easier

## Troubleshooting

### Common Issues

1. **API Key Authentication**: If you get 401/403 errors, check that your API key is correct and the authentication format matches your API's requirements.

2. **Network Timeouts**: If requests are timing out, your API might be slow. Consider increasing the timeout in `_call_real_api()`.

3. **URL Configuration**: Ensure your `SHIPMENT_API_BASE_URL` includes the correct protocol (https://) and domain.

4. **Missing Dependencies**: Dependencies are managed by uv. If you encounter import errors, try:
   ```bash
   # Sync dependencies from lockfile
   uv sync
   
   # Or install from pyproject.toml
   uv pip install -r pyproject.toml
   ```

5. **Module Import Issues**: Ensure you're running the application from the project root directory using `uv run src/app.py`

### Verbose Debug Mode

Enable verbose logging to see detailed function call information:
```bash
uv run src/app.py --verbose
```

This will show:
- 📦 Function calls with parameters
- 🔧 LLM requests and responses  
- 📝 Detailed execution logs
- 💾 Logs saved to 'semantic_kernel_debug.log'

## About uv

[uv](https://github.com/astral-sh/uv) is a fast, modern Python package and project manager. It replaces tools like `pip`, `pip-tools`, `pipx`, `poetry`, and `virtualenv`, and is recommended for reproducible, efficient dependency management in this project.

- See [uv documentation](https://docs.astral.sh/uv/) for more details.
