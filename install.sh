#!/bin/bash
# Mail Command Extractor MCP Server Installation Script

set -e

echo "🚀 Mail Command Extractor MCP Server Installation"
echo "================================================"

INSTALL_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
echo "📁 Installation directory: $INSTALL_DIR"

# Check Python
python3 --version || {
    echo "❌ Python 3 is required"
    exit 1
}

# Install dependencies (if requirements.txt exists)
if [ -f "$INSTALL_DIR/requirements.txt" ]; then
    pip3 install -r "$INSTALL_DIR/requirements.txt" || {
        echo "⚠️ Failed to install dependencies, continuing..."
    }
fi

# Make scripts executable
chmod +x "$INSTALL_DIR/mcp_server.py"
chmod +x "$INSTALL_DIR/test_mail_command_extractor.py"

# Test server
echo "🧪 Testing MCP server..."
cd "$INSTALL_DIR"
python3 mcp_server.py --test || {
    echo "❌ Server test failed"
    exit 1
}

# Run skill tests
echo "🧪 Running skill tests..."
python3 test_mail_command_extractor.py || {
    echo "❌ Skill tests failed"
    exit 1
}

# Generate MCP configuration
MCP_CONFIG_DIR="$HOME/.config/mcp"
mkdir -p "$MCP_CONFIG_DIR"
sed "s|/path/to/skill|$INSTALL_DIR|g" "$INSTALL_DIR/mcp_config.json" > "$MCP_CONFIG_DIR/mail-command-extractor.json"

# Update Claude Desktop config
CLAUDE_CONFIG="$INSTALL_DIR/claude_desktop_config.json"
sed -i.bak "s|/path/to/skill|$INSTALL_DIR|g" "$CLAUDE_CONFIG" 2>/dev/null || {
    # macOS sed syntax
    sed -i '' "s|/path/to/skill|$INSTALL_DIR|g" "$CLAUDE_CONFIG"
}

echo "✅ Installation completed!"
echo "📋 Next steps:"
echo "1. Configure local settings: cp mail_command_extractor_config_example.json mail_command_extractor_config_local.json"
echo "2. Edit local config: nano mail_command_extractor_config_local.json"
echo "3. Test configuration: python3 test_mail_command_extractor.py"  
echo "4. MCP config saved to: $MCP_CONFIG_DIR/mail-command-extractor.json"
echo "5. Claude Desktop config: $CLAUDE_CONFIG"
echo "6. Add to your AI agent's MCP settings"

echo ""
echo "🔧 Manual Setup for Claude Desktop:"
echo "   Copy the contents of claude_desktop_config.json to your Claude Desktop configuration"