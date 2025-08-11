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

1. Make sure you have Python 3.12 installed
2. Set up your configuration in a `.env` file in the samples directory (copy from `.env.example`)

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

1. Navigate to the samples directory:
```bash
cd samples
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or if you're using the main project's dependencies:
```bash
# From the root directory
pip install -e .
```

## Usage

Run the application:
```bash
python app.py
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

### ShipmentTrackingPlugin

This plugin implements the core functionality for tracking packages:

- **track_package()**: Main function that accepts tracking ID and optional date filters
- **_call_real_api()**: Makes HTTP requests to actual tracking APIs
- **_simulate_api_response()**: Simulates the Demo Shipment Tracker API responses for demo purposes

### ShipmentTrackingAgent

The main agent class that orchestrates the conversation:

- **setup_kernel()**: Configures Semantic Kernel with AI services and plugins
- **chat()**: Processes user messages and returns responses
- **reset_conversation()**: Resets the chat history

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

You can extend this application by:

1. **Adding more API endpoints**: Implement additional tracking functions
2. **Adding filters**: Implement content filters for security and compliance  
3. **Adding memory**: Store conversation history and user preferences
4. **Adding authentication**: Secure access to tracking information
5. **Adding multiple agents**: Create specialized agents for different types of queries
6. **Custom authentication**: Modify headers for your specific API authentication requirements

## Architecture Notes

This application follows the single agent pattern demonstrated in the workshop:

- Uses Semantic Kernel's automatic function calling capabilities
- Implements a single plugin with focused functionality
- Maintains conversation state through ChatHistory
- Provides a natural language interface for complex API interactions
- Supports both development (simulated) and production (real API) modes

The agent automatically determines when to call the tracking function based on user queries, making it easy to ask questions like "Where is my package?" without needing to specify exact function calls.

## Troubleshooting

### Common Issues

1. **API Key Authentication**: If you get 401/403 errors, check that your API key is correct and the authentication format matches your API's requirements.

2. **Network Timeouts**: If requests are timing out, your API might be slow. Consider increasing the timeout in `_call_real_api()`.

3. **URL Configuration**: Ensure your `SHIPMENT_API_BASE_URL` includes the correct protocol (https://) and domain.

4. **Missing Dependencies**: If you get import errors, ensure all dependencies are installed with `pip install -r requirements.txt`.

### Debug Mode

The application prints configuration information when starting:
- Base URL being used
- Whether simulation mode is enabled  
- Whether an API key is configured

Check these values if you're having connection issues.
