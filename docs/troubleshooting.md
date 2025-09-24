# Troubleshooting Guide

This guide helps you resolve common issues when using the PyMOL Visualization MCP Server.

## Installation Issues

### PyMOL Not Found

**Symptoms**:
- `command not found: pymol`
- `PyMOL executable not found`

**Solutions**:
1. **Check Installation**:
   ```bash
   which pymol
   pymol --version
   ```

2. **Install PyMOL**:
   ```bash
   # Using conda (recommended)
   conda install -c conda-forge pymol-open-source
   
   # Using homebrew (macOS)
   brew install pymol
   ```

3. **Add to PATH**:
   ```bash
   export PATH=$PATH:/path/to/pymol/bin
   # Add to ~/.bashrc or ~/.zshrc for persistence
   ```

### Python Path Issues

**Symptoms**:
- MCP server not starting
- `Python interpreter not found`

**Solutions**:
1. **Find Python Path**:
   ```bash
   which python3
   which python
   ```

2. **Update Configuration**:
   ```json
   {
     "mcpServers": {
       "pymol-visualization": {
         "command": "/usr/bin/python3",  // Use actual path
         "args": ["/full/path/to/server/804vis_en.py"],
         "env": {}
       }
     }
   }
   ```

3. **Test Python Script**:
   ```bash
   python3 server/804vis_en.py --help
   ```

### MCP Server Not Recognized

**Symptoms**:
- Tool not appearing in Claude Desktop
- "Server failed to start" errors

**Solutions**:
1. **Validate JSON Configuration**:
   ```bash
   # Check JSON syntax
   python3 -m json.tool claude_desktop_config.json
   ```

2. **Check File Permissions**:
   ```bash
   chmod +x server/804vis_en.py
   ls -la server/
   ```

3. **Restart Claude Desktop**:
   - Completely quit and restart application
   - Clear cache if necessary

4. **Check Logs**:
   - Look for error messages in Claude Desktop
   - Check system console for additional details

## Runtime Issues

### PyMOL Remote Mode Problems

**Symptoms**:
- PyMOL starts but doesn't respond to commands
- "Connection refused" errors

**Solutions**:
1. **Launch with Remote Flag**:
   ```bash
   pymol -R
   # or
   /full/path/to/pymol -R
   ```

2. **Check Port Availability**:
   ```bash
   lsof -i :9123  # Default PyMOL remote port
   ```

3. **Alternative Launch Methods**:
   ```bash
   # With specific port
   pymol -R -p 9124
   
   # With verbose output
   pymol -R -v
   ```

### Structure Loading Failures

**Symptoms**:
- "PDB not found" errors
- Structure doesn't appear in PyMOL

**Solutions**:
1. **Verify PDB ID**:
   ```bash
   # Test PDB download
   wget https://files.rcsb.org/download/1XYZ.pdb
   ```

2. **Check Internet Connection**:
   - Ensure internet access for PDB downloads
   - Try alternative PDB servers

3. **Use Local Files**:
   ```bash
   # Provide full path to local PDB file
   Structure: /full/path/to/structure.pdb
   ```

4. **File Format Issues**:
   - Ensure PDB format compliance
   - Check for special characters in path
   - Use standard PDB extensions (.pdb, .ent)

### Residue Selection Problems

**Symptoms**:
- "Residue not found" warnings
- Incorrect residue highlighting

**Solutions**:
1. **Check Residue Numbering**:
   ```python
   # In PyMOL
   load 1xyz.pdb
   show sequence
   select resi 100  # Test specific residue
   ```

2. **Verify Chain Identifiers**:
   ```python
   # List all chains
   cmd.get_chains('all')
   ```

3. **Handle Insertion Codes**:
   ```
   # Use full residue specification
   A:100A instead of A:100
   ```

4. **Remove Amino Acid Letters**:
   ```
   # Incorrect: T99, H17
   # Correct: 99, 17
   ```

### Distance Measurement Issues

**Symptoms**:
- Distance calculations fail
- Incorrect atom selections

**Solutions**:
1. **Check Atom Names**:
   ```python
   # In PyMOL
   select resi 100
   show sticks
   # Verify atom names (CA, CB, N, O, etc.)
   ```

2. **Correct Syntax**:
   ```
   # Correct format
   100:CA-200:CA
   
   # Common mistakes
   100:Ca-200:Ca  # Wrong case
   100-CA-200-CA  # Wrong separator
   ```

3. **Verify Residue Existence**:
   - Ensure both residues exist in structure
   - Check for missing atoms

## Common Error Messages

### "No module named 'mcp'"

**Solution**:
```bash
pip install mcp>=1.0.0
```

### "No module named 'pymol_mcp'" or PyMOL-MCP Issues

**Solution**:
```bash
# Install the PyMOL-MCP bridge
pip install pymol-mcp

# Or reinstall if already installed
pip uninstall pymol-mcp
pip install pymol-mcp
```

**Additional Resources**:
- [ChatMol/molecule-mcp Repository](https://github.com/ChatMol/molecule-mcp)
- Check the molecule-mcp documentation for specific configuration issues

### "Permission denied"

**Solution**:
```bash
chmod +x server/804vis_en.py
# or run with python3 explicitly
python3 server/804vis_en.py
```

### "JSON decode error"

**Solution**:
1. Validate JSON syntax in configuration
2. Remove trailing commas
3. Check for proper quotes and brackets

### "Connection timeout"

**Solutions**:
1. Ensure PyMOL is running with -R flag
2. Check firewall settings
3. Try different port numbers

## Performance Issues

### Slow Structure Loading

**Solutions**:
1. Use local PDB files when possible
2. Check internet connection speed
3. Consider structure complexity

### Memory Issues with Large Structures

**Solutions**:
1. Reduce surface quality
2. Focus on specific regions
3. Use representative chains for symmetric structures

### Rendering Performance

**Solutions**:
1. Adjust ray tracing settings
2. Reduce image resolution for previews
3. Use faster rendering modes during development

## Advanced Troubleshooting

### Debug Mode

**Enable Verbose Output**:
```bash
# Run server with debug flags
python3 -v server/804vis_en.py

# PyMOL verbose mode
pymol -R -v
```

### Log Analysis

**Check System Logs**:
```bash
# macOS
console app or tail -f /var/log/system.log

# Linux
journalctl -f
tail -f /var/log/syslog
```

### Network Diagnostics

**Test Connectivity**:
```bash
# Test PyMOL remote port
telnet localhost 9123

# Test PDB server
ping rcsb.org
curl -I https://files.rcsb.org/download/1xyz.pdb
```

## Getting Help

### Before Seeking Help

1. **Collect Information**:
   - Operating system and version
   - Python version (`python3 --version`)
   - PyMOL version (`pymol --version`)
   - MCP version (`pip show mcp`)
   - Error messages (complete text)

2. **Try Basic Tests**:
   - Can PyMOL start normally?
   - Can Python run the script directly?
   - Is the configuration file valid JSON?

3. **Check Recent Changes**:
   - Did it work before?
   - What changed since it last worked?
   - New installations or updates?

### Where to Get Help

1. **GitHub Issues**:
   - Search existing issues first
   - Provide detailed information
   - Include configuration files (remove sensitive paths)

2. **Documentation**:
   - Review installation guide
   - Check usage examples
   - Compare with working configurations

3. **Community Resources**:
   - PyMOL forums and documentation
   - MCP protocol documentation
   - Claude Desktop support

### Issue Report Template

```markdown
**Environment**:
- OS: [macOS/Linux/Windows + version]
- Python: [version]
- PyMOL: [version]
- MCP: [version]

**Problem Description**:
[Detailed description of the issue]

**Steps to Reproduce**:
1. [First step]
2. [Second step]
3. [Third step]

**Expected Behavior**:
[What should happen]

**Actual Behavior**:
[What actually happens]

**Error Messages**:
```
[Paste complete error messages here]
```

**Configuration**:
```json
[Paste relevant configuration, remove sensitive paths]
```

**Additional Context**:
[Any other relevant information]
```

## Preventive Measures

### Regular Maintenance

1. **Keep Software Updated**:
   - Update PyMOL regularly
   - Update Python packages
   - Update Claude Desktop

2. **Backup Configurations**:
   - Save working configurations
   - Document custom modifications
   - Version control your setups

3. **Test After Updates**:
   - Verify functionality after updates
   - Test with simple cases first
   - Have rollback plans

### Best Practices

1. **Use Virtual Environments**:
   ```bash
   python3 -m venv pymol-mcp-env
   source pymol-mcp-env/bin/activate
   pip install -r requirements.txt
   ```

2. **Standardize Paths**:
   - Use absolute paths in configurations
   - Avoid spaces in directory names
   - Use consistent naming conventions

3. **Document Customizations**:
   - Keep notes of configuration changes
   - Document any local modifications
   - Maintain setup procedures
