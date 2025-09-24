# Usage Guide

This guide explains how to use the PyMOL Visualization MCP Server for protein structure analysis and visualization.

## Quick Start

### 1. Launch PyMOL in Remote Mode
Before using the MCP server, start PyMOL with remote control:
```bash
pymol -R
```

### 2. Access Tools in Claude Desktop
1. Open Claude Desktop
2. Start a new conversation
3. Click the "+" button to add tools
4. Select "Add from pymol-visualization"
5. Choose your analysis template

## Analysis Templates

### Single Component Analysis

**Purpose**: Highlight and analyze specific residues in a single protein structure.

**When to Use**:
- Studying active site residues
- Highlighting mutation sites
- Analyzing binding pockets
- Examining structural motifs

**Parameters**:
- `Structure*` (Required): PDB ID (e.g., `1xyz`) or file path
- `Key_residues*` (Required): Comma-separated residue numbers
  - Simple format: `57,102,145`
  - Chain-specific: `A:57,B:102,C:145`
- `Distance_pairs` (Optional): Atom pair distance measurements
  - Format: `57:CA-102:CA,145:CB-200:CB`

**Example Usage**:
```
Structure: 9def
Key_residues: 99,17,142,37
Distance_pairs: 99:CA-17:CA
```

### Multi-Component Analysis

**Purpose**: Analyze protein-protein or protein-ligand interaction interfaces.

**When to Use**:
- Studying protein complexes
- Analyzing binding interfaces
- Examining receptor-ligand interactions
- Investigating protein-protein interactions (PPIs)

**Parameters**:
- `Structure*` (Required): PDB ID or file path
- `Components*` (Required): Define molecular components
  - Format: `receptor:CHAIN_LIST,ligand:CHAIN_LIST`
  - Example: `receptor:A+B+C,ligand:D+E`
- `Key_residues` (Optional): Specific residues to highlight
  - Format: `A:57,B:102`
- `Distance_pairs` (Optional): Distance measurements between components

**Example Usage**:
```
Structure: 1bd2
Components: receptor:A+B+C,ligand:D+E
Key_residues: A:100,D:50
Distance_pairs: A:100:CA-D:50:CA
```

## Step-by-Step Workflow

### For Single Component Analysis

1. **Prepare Structure**
   - Ensure you have a PDB ID or local PDB file
   - Identify residues of interest

2. **Launch Analysis**
   - Select `single_component_analysis` template
   - Fill required parameters
   - Click "Add prompt" and send

3. **Monitor Progress**
   - Script loads and processes structure
   - Initial rendering appears in PyMOL
   - Wait for confirmation prompt

4. **Review and Adjust**
   - Check initial visualization
   - Confirm to continue or request adjustments
   - Script applies final rendering settings

5. **Save Results**
   - Remember to save images at pause points
   - Use PyMOL's save functions for publication-quality output

### For Multi-Component Analysis

1. **Define Components**
   - Identify receptor and ligand chains
   - Plan component groupings

2. **Launch Analysis**
   - Select `multi_component_analysis` template
   - Define components using chain notation
   - Specify any key residues

3. **Interface Detection**
   - Script automatically identifies interface residues
   - Calculates inter-molecular distances
   - Applies distinct coloring

4. **Review Results**
   - Check interface highlighting
   - Verify distance measurements
   - Confirm visualization quality

## Advanced Features

### Residue Selection Syntax

**Basic Numbers**: `1,5,10,20`
**Chain-Specific**: `A:1,A:5,B:10,B:20`
**Ranges**: `1-10,20-30` (if supported)

### Distance Measurement Syntax

**Atom Specification**: `RESIDUE:ATOM-RESIDUE:ATOM`
- `100:CA-200:CA` (alpha carbons)
- `100:CB-200:CB` (beta carbons)
- `100:N-200:O` (specific atoms)

### Component Definition Syntax

**Single Chain**: `receptor:A,ligand:B`
**Multiple Chains**: `receptor:A+B+C,ligand:D+E+F`
**Complex Example**: `protein:A+B,dna:C+D,ligand:E`

## Best Practices

### Input Preparation

1. **PDB Structure Quality**
   - Use high-resolution structures when possible
   - Check for missing residues or atoms
   - Verify chain assignments

2. **Residue Numbering**
   - Use original PDB numbering
   - Avoid insertion codes if possible
   - Double-check chain identifiers

3. **File Paths**
   - Use absolute paths for local files
   - Ensure files are accessible to PyMOL

### Visualization Optimization

1. **Image Quality**
   - Save at high resolution for publication
   - Use ray tracing for final images
   - Consider lighting and angles

2. **Color Schemes**
   - Default colors are optimized for clarity
   - Customize if needed for specific requirements
   - Maintain consistency across related figures

3. **Annotations**
   - Use distance measurements judiciously
   - Label important features
   - Keep annotations clear and readable

### Common Workflows

#### Active Site Analysis
```
Template: single_component_analysis
Structure: [enzyme PDB]
Key_residues: [catalytic residues]
Distance_pairs: [substrate binding distances]
```

#### Binding Interface Study
```
Template: multi_component_analysis
Structure: [complex PDB]
Components: protein:A,ligand:B
Distance_pairs: [key binding distances]
```

#### Mutation Effect Visualization
```
Template: single_component_analysis
Structure: [wild-type PDB]
Key_residues: [mutation sites + surrounding]
Distance_pairs: [structural impact measurements]
```

## Troubleshooting Usage

### Common Issues

1. **Structure Not Loading**
   - Verify PDB ID is valid
   - Check internet connection for PDB download
   - Ensure file path is correct for local files

2. **Residue Selection Errors**
   - Check residue numbering in PDB
   - Verify chain identifiers
   - Remove amino acid letters from residue specifications

3. **Component Definition Issues**
   - Ensure chains exist in structure
   - Use correct chain identifiers
   - Check for proper syntax (A+B+C, not A,B,C)

4. **Distance Measurement Problems**
   - Verify atom names exist
   - Check residue numbers are valid
   - Ensure proper syntax (CA not Ca)

### Performance Tips

1. **Large Structures**
   - Focus on relevant regions
   - Consider reducing surface detail
   - Use representative chains for symmetric complexes

2. **Multiple Analyses**
   - Clear PyMOL between runs if needed
   - Save intermediate states
   - Use consistent naming conventions

## Output and Saving

### Image Export
```python
# In PyMOL command line
ray 1200, 1200  # High resolution rendering
png filename.png, dpi=300  # Publication quality
```

### Session Saving
```python
save session.pse  # Complete session
save scene.pml    # Commands only
```

## Next Steps

- Explore example cases in `/examples/`
- Customize rendering parameters
- Integrate with publication workflows
- Advanced PyMOL scripting for specific needs
