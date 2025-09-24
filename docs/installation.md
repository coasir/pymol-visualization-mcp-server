# Installation Guide

This guide will walk you through the complete installation and setup process for the PyMOL Visualization MCP Server.

## Prerequisites

### System Requirements
- **Operating System**: macOS, Linux, or Windows
- **Python**: Version 3.8 or higher
- **PyMOL**: Latest stable version
- **Claude Desktop**: Latest version

### Check Your Python Version
```bash
python --version
# or
python3 --version
```

## Installation Steps

### 1. Install PyMOL

#### Option A: Using Conda (Recommended)
```bash
conda install -c conda-forge pymol-open-source
```

#### Option B: Using Package Manager

**macOS (with Homebrew):**
```bash
brew install pymol
```

**Ubuntu/Debian:**
```bash
sudo apt-get install pymol
```

#### Option C: Commercial Version
Download from [PyMOL.org](https://pymol.org/) if you have a license.

### 2. Clone and Setup Repository

```bash
# Clone the repository
git clone https://github.com/coasir/pymol-visualization-mcp-server.git
cd pymol-visualization-mcp-server

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Setup PyMOL-MCP Server

**Critical Requirement**: You must set up the PyMOL-MCP bridge first:

1. **Clone molecule-mcp repository**:
   ```bash
   git clone https://github.com/ChatMol/molecule-mcp.git
   cd molecule-mcp
   ```

2. **Install molecule-mcp dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Follow molecule-mcp setup instructions** from their repository

### 4. Configure Claude Desktop

#### Step 4.1: Locate Configuration File
1. Open Claude Desktop
2. Go to **Settings** → **Developer** → **Edit Config**
3. This opens `claude_desktop_config.json`

#### Step 4.2: Add Both MCP Servers

You need to configure **both** servers in your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pymol": {
      "command": "/usr/bin/mcp",
      "args": [
        "run",
        "/full/path/to/molecule-mcp/pymol_server.py"
      ]
    },
    "pymol-visualization": {
      "command": "/usr/bin/python3",
      "args": [
        "/full/path/to/pymol-visualization-mcp-server/server/804vis_en.py"
      ],
      "env": {}
    }
  }
}
```

#### Step 4.3: Update Paths

**Find your paths:**
```bash
# Find MCP executable path
which mcp
# Example output: /usr/bin/mcp or /Library/Frameworks/Python.framework/Versions/3.12/bin/mcp

# Find Python path
which python3
# Example output: /usr/bin/python3

# Get full paths to repositories
pwd  # Run this in molecule-mcp directory
pwd  # Run this in pymol-visualization-mcp-server directory
```

**Update the configuration with your actual paths:**
- Replace `/usr/bin/mcp` with your MCP executable path
- Replace `/full/path/to/molecule-mcp/pymol_server.py` with actual path
- Replace `/usr/bin/python3` with your Python path
- Replace `/full/path/to/pymol-visualization-mcp-server/server/804vis_en.py` with actual path

### 4. Verify Installation

#### Test PyMOL Remote Mode
```bash
pymol -R
```
You should see PyMOL start with remote control enabled.

#### Test MCP Server
1. Restart Claude Desktop
2. In a new chat, look for "pymol-visualization" in the tools menu
3. You should see two templates:
   - `single_component_analysis`
   - `multi_component_analysis`

## Troubleshooting Installation

### Common Issues

#### PyMOL Not Found
```bash
# Check if PyMOL is in PATH
pymol --help

# If not found, add to PATH or use full path
export PATH=$PATH:/path/to/pymol/bin
```

#### Python Path Issues
```bash
# Use absolute path in configuration
which python3
# Copy this exact path to claude_desktop_config.json
```

#### Permission Issues
```bash
# Make script executable
chmod +x server/804vis_en.py
```

#### Claude Desktop Not Recognizing Server
1. Check JSON syntax in configuration file
2. Ensure paths are correct and absolute
3. Restart Claude Desktop completely
4. Check Claude Desktop logs for errors

### Validation Tests

#### Test 1: Basic Functionality
Try running a simple single-component analysis:
- Structure: `1xyz` (any valid PDB ID)
- Key_residues: `1,10,20`

#### Test 2: Multi-Component Analysis
Try running with a known PPI structure:
- Structure: `1bd2`
- Components: `receptor:A+B+C,ligand:D+E`

## Next Steps

Once installation is complete:
1. Read the [Usage Guide](usage.md)
2. Try the example cases
3. Explore advanced features

## Getting Help

If you encounter issues:
1. Check the [Troubleshooting Guide](troubleshooting.md)
2. Verify all paths in configuration
3. Test PyMOL independently
4. Open an issue on GitHub with:
   - Operating system
   - Python version
   - PyMOL version
   - Error messages
   - Configuration file content
