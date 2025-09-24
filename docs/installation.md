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
git clone https://github.com/yourusername/pymol-visualization-mcp-server.git
cd pymol-visualization-mcp-server

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Configure Claude Desktop

#### Step 3.1: Locate Configuration File
1. Open Claude Desktop
2. Go to **Settings** → **Developer** → **Edit Config**
3. This opens `claude_desktop_config.json`

#### Step 3.2: Add MCP Server Configuration

Copy the example configuration from `config/claude_desktop_config_example.json`:

```json
{
  "mcpServers": {
    "pymol-visualization": {
      "command": "/usr/bin/python3",
      "args": ["/full/path/to/pymol-visualization-mcp-server/server/804vis_en.py"],
      "env": {}
    }
  }
}
```

#### Step 3.3: Update Paths

**Find your Python path:**
```bash
which python3
# Example output: /usr/bin/python3
```

**Get full script path:**
```bash
pwd
# From inside the cloned repository
# Example: /Users/username/pymol-visualization-mcp-server
```

**Update the configuration:**
- Replace `/usr/bin/python3` with your Python path
- Replace the args path with your full script path

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
