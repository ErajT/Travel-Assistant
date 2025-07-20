# 🌦️ MCP Travel Assistant Server Integration with Claude Code

This project integrates a **Travel Assistant Server** into Claude Code using the MCP (Modular Command Protocol) configuration.

## ⚙️ Setup Instructions

Follow the steps below to set up and run the Travel Assistant server through Claude Code.

### 1. ✅ Configure Claude Code

Add the following snippet to your Claude Code configuration file (usually found in the settings):
json
{
  "mcpServers": {
    "weather": {
      "command": "uv",
      "args": [
        "--directory",
        "your-directory//mcp-server",
        "run",
        "server.py"
      ]
    }
  }
}

Replace "your-directory//mcp-server" with the actual path to your MCP server directory.

> 📝 This configuration tells Claude Code how to run your Travel Assistant server using uv (such as uvicorn) and the correct project path.

### 2. 🔐 Set Up Environment Variables

In order for the server to authenticate with the backend, you need to provide credentials securely.

1. In the root of your project, create a file named .env.
2. Add the following lines to store your **Client ID** and **Client Secret** obtained from **Amaneus**:

CLIENT_ID=your-client-id-here
CLIENT_SECRET=your-client-secret-here

### 3. ⚡ Set Up the Environment Using uv
To prepare your Python environment and install dependencies, use uv:

Make sure you have uv installed. If not, install it by running:

curl -Ls https://astral.sh/uv/install.sh | sh

Create a virtual environment named .venv in your project root:

uv venv .venv

Activate the virtual environment:

On Windows:
.venv\Scripts\activate

Install all required dependencies from requirements.txt:

uv pip install -r requirements.txt

### 4. 🚀 Running the Server
Once everything is configured:

Claude Code will automatically detect and run the Travel Assistant MCP server when it's needed, using the MCP configuration you set up earlier.

Make sure your virtual environment is activated and your .env file is present before running Claude Code or using the assistant feature.
