🌦️ MCP Travel Assistant Server Integration with Claude Code
This project integrates a Travel Assistant Server into Claude Code using the MCP (Modular Command Protocol) configuration.

⚙️ Setup Instructions
Follow the steps below to set up and run the Travel Assistant server through Claude Code.

1. ✅ Configure Claude Code
Add the following snippet to your Claude Code configuration file (usually found in the settings):

JSON:
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

This configuration tells Claude Code how to run your Travel Assistant server using uv (e.g., uvicorn) and the correct project path.

2. 🔐 Set Up Environment Variables
To authenticate the server with the backend securely:

In the root of your project, create a file named .env.

Add the following lines:

.env:

CLIENT_ID=your-client-id-here
CLIENT_SECRET=your-client-secret-here

Replace your-client-id-here and your-client-secret-here with the actual credentials obtained from Amaneus.

⚡ Set Up the Environment Using uv
To prepare your Python environment and install dependencies:

✅ Install uv (if not already installed)
curl -Ls https://astral.sh/uv/install.sh | sh

🛠️ Create a Virtual Environment
uv venv .venv

🔄 Activate the Virtual Environment
On Windows:

.venv\Scripts\activate

On macOS/Linux:

source .venv/bin/activate

📦 Install Dependencies
Make sure requirements.txt exists in your root directory, then run:

uv pip install -r requirements.txt

🚀 Running the Server
Once everything is configured:

Claude Code will automatically detect and run the Travel Assistant MCP server using the configuration you added.

Ensure:

Your virtual environment is activated.

Your .env file exists and contains valid credentials.

You're now ready to use the Travel Assistant within Claude Code! ✈️💬
