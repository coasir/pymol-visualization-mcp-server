#!/usr/bin/env python3

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    GetPromptResult,
    Prompt,
    PromptArgument,
    TextContent,
    PromptMessage,
)

server = Server("pymol-visualizer")

# Concise system prompt
VISUALIZATION_PROMPT = """
You are the PyMOL protein structure visualization expert. Intelligently perform visualization analysis based on user needs.

# Target structure: {structure}
# Analysis type: {analysis_type}
# User specification: {user_input}

# Execution strategy:

## Phase 1: Environment preparation and structure loading
Launch PyMOL and establish a clean working environment. Load target structure (use fetch command to get PDB or load local file).
Basic cleanup: Remove solvent molecules, water molecules and other interfering substances.
Set background: white and opaque.

## Phase 2: User-specified component processing
{user_instructions}

## Phase 3: Visualization scheme implementation
Choose main representation method based on analysis goals: cartoon shows overall folding, surface displays molecular shape, sticks show atomic details.
Stick mode displays key atoms
Color key residues by element: run_pymol_command("util.cbaw key_residues")
Only single component analysis requires this step (grayscale setting): Apply grayscale spectrum to all Cα atoms except key residues: run_pymol_command("spectrum count, white_gray70, name ca and not key_residues")
Represent key residue Cα atoms as colored spheres with radius 0.3, each key residue's Cα atom uses different colors, distinguished from existing colors in structure and background color (avoid red, blue, gray)

Set initial viewing angle: Choose observation angle and zoom scale that can show the overall protein.

## Phase 4: Publication-quality rendering optimization

Professional rendering settings:
    - run_pymol_command("set ray_trace_mode, 1")
    - run_pymol_command("set ray_trace_gain, 0.05")
    - run_pymol_command("set ray_trace_depth_factor, 1")
    - run_pymol_command("set ray_trace_disco_factor, 1")
    - run_pymol_command("set specular, 0")
    - run_pymol_command("set ambient, 0.8")
    - run_pymol_command("set cartoon_side_chain_helper, on")
    - run_pymol_command("set valence, off")
    - run_pymol_command("set ray_shadow, off")
    - run_pymol_command("set reflect, 0.5")
    - run_pymol_command("set stick_radius, 0.25")
    - run_pymol_command("hide labels")
    - run_pymol_command("ray")

🛑 **Pause point**: Rendering optimization and ray completed, tell user they can save the first basic visualization image, then input 'continue' to proceed with detailed scientific analysis.

## Phase 5: In-depth scientific analysis (continue after user confirmation)
{analysis_focus}

## Phase 6: Measurement and annotation
If single component analysis: Only show key residues, protein backbone transparency set to 65%
If multi-component analysis: Show interface residues, hide all surface display, cartoon protein backbone transparency set to 85%
*If user performed distance measurement, display residues at both ends of distance in stick mode

## Phase 7: Final optimization and output
Adjust to optimal display angle: Consider symmetry and visibility of important features.
Perform final quality check: Ensure all key information is clearly visible, color scheme is reasonable, no technical errors.

# Important principles:
- Strictly execute according to user-specified residues/chains, do not speculate on your own
- Ensure output meets publication quality standards
- Pause at key nodes and wait for user confirmation before continuing
- Fix errors promptly when encountered

# Error handling strategy:
- **Detection failure**: When PyMOL returns "Invalid selection name" error, immediately rebuild that selection set
- **Automatic recovery**: When encountering selection set errors, do not ask user, directly recreate and continue execution
- **State maintenance**: When rebuilding selection sets, restore all previous attributes (color, display mode, etc.)
- **Process continuity**: Ensure error fixes do not interrupt overall visualization process

# Technical best practices:
- **Precise selection syntax**: Use "chain A and resi 65" instead of "resi 65" to avoid cross-chain residue confusion
- **Script block integrity**: Key calculations must be completed in single Python block to ensure variables are available throughout the entire process
- **Coordinate access method**: Use cmd.iterate_state instead of cmd.iterate to get atomic coordinates

"""

@server.list_prompts()
async def list_prompts() -> list[Prompt]:
    """Available analysis templates"""
    return [
        Prompt(
            name="single_component_analysis",
            description="Single component residue analysis",
            arguments=[
                PromptArgument(name="structure", description="PDB ID or file path", required=True),
                PromptArgument(name="key_residues", description="Key residues (e.g., 57,102 or A:57,B:102, optional)", required=False),
                PromptArgument(name="distance_pairs", description="Distance pairs (e.g., 57:CA-102:CA)", required=False)
            ]
        ),
        Prompt(
            name="multi_component_analysis", 
            description="Receptor-ligand interaction analysis",
            arguments=[
                PromptArgument(name="structure", description="PDB ID or file path", required=True),
                PromptArgument(name="key_residues", description="Key residues (e.g., 57,102 or A:57,B:102, optional)", required=False),
                PromptArgument(name="components", description="Component definition (e.g., receptor:A+B+C,ligand:D+E)", required=True),
                PromptArgument(name="distance_pairs", description="Distance pairs (e.g., 57:CA-102:CA)", required=False)
            ]
        )
    ]

@server.get_prompt()
async def get_prompt(name: str, arguments: dict | None = None) -> GetPromptResult:
    """Generate visualization prompt"""
    
    if name == "single_component_analysis":
        structure = arguments.get("structure", "")
        key_residues = arguments.get("key_residues", "")
        distance_pairs = arguments.get("distance_pairs", "")
        
        if not key_residues:
            raise ValueError("Single component analysis requires key_residues parameter")
        
        # Build user input description
        user_specs = [f"Key residues: {key_residues}"]
        if distance_pairs:
            user_specs.append(f"Distance measurement: {distance_pairs}")
        
        user_input = ", ".join(user_specs)
        
        user_instructions = f"""Identify and select user-specified key residues: {key_residues}.
Create selection set named 'key_residues' containing all specified residues.
Support cross-chain format (e.g., A:57 means residue 57 on chain A) and same-chain format (e.g., 57,102,195).

Important display control:
- Execute hide everything to ensure clean starting state
- Only show key residues: show sticks, key_residues
- First color key residues by atom type: util.cbaw key_residues
- Then assign unique colors to C atoms of each key residue (e.g., forest, deeppurple, gold, teal, etc., avoid conflicts with red and blue)
- Ensure O=red, N=blue, S=yellow and other standard atom colors remain unchanged
- Each key residue's Cα atom represented as 0.3 radius sphere, color consistent with that residue's C atom color."""
        
        analysis_focus = f"""Focus on structural features and interactions of key residues:

**Protein backbone optimized display** (execute after pause point):
- Set protein backbone to uniform dark gray: color gray40, {structure}
- Set protein backbone transparency 65%: set cartoon_transparency, 0.65, {structure}

Strictly control displayed content:
- Protein backbone transparency set to 65%, color as gray40
- Key residues use high contrast, aesthetically pleasing color scheme
- Ensure each residue is completely visually distinguishable
- Ensure key residues are completely visible: set transparency, 0.0, key_residues
If user provided distance measurement pairs, perform precise inter-atomic distance measurements.
Note: Do not display hydrogen bonds and hydrogen bond distance labels, also do not display residue labels."""
        
        system_content = VISUALIZATION_PROMPT.format(
            structure=structure,
            analysis_type="Single component residue analysis",
            user_input=user_input,
            user_instructions=user_instructions,
            analysis_focus=analysis_focus
        )
        
        return GetPromptResult(
            description=f"PyMOL single component analysis: {structure}",
            messages=[PromptMessage(role="user", content=TextContent(type="text", text=system_content))]
        )
    
    elif name == "multi_component_analysis":
        structure = arguments.get("structure", "")
        key_residues = arguments.get("key_residues", "")
        components = arguments.get("components", "")
        distance_pairs = arguments.get("distance_pairs", "")
        
        if not components:
            raise ValueError("Multi-component analysis requires components parameter")
        
        # Validate receptor and ligand format
        if "receptor:" not in components or "ligand:" not in components:
            raise ValueError("Component definition must use receptor:chains,ligand:chains format")
        
        # Build user input description
        user_specs = [f"Component division: {components}"]
        if key_residues:
            user_specs.append(f"Key residues: {key_residues}")
        if distance_pairs:
            user_specs.append(f"Distance measurement: {distance_pairs}")
        
        user_input = ", ".join(user_specs)
        
        # Parse receptor ligand components
        comp_parts = components.split(',')
        receptor_chains = ""
        ligand_chains = ""
        
        for comp_def in comp_parts:
            if ':' in comp_def:
                comp_name, chains = comp_def.split(':', 1)
                comp_name = comp_name.strip()
                if comp_name == "receptor":
                    receptor_chains = chains.strip()
                elif comp_name == "ligand":
                    ligand_chains = chains.strip()
        
        user_instructions = f"""Divide receptor-ligand components according to user specification:
Create receptor component containing chains {receptor_chains}, color with marine
Create ligand component containing chains {ligand_chains}, color with orange
Create independent PyMOL objects for each component, use different colors to distinguish.
Show semi-transparent surface for each component: execute show surface command, then set transparency to 0.85.

Use precise cmd.iterate_state method to identify interface interaction residues:
1. Use cmd.iterate_state to get all atomic coordinates and information of receptor and ligand into dictionaries:
   - Create receptor_atoms and ligand_atoms dictionaries to store atomic information
   - Use cmd.iterate_state(1, "receptor", "store_receptor_atom(model, chain, resi, name, x, y, z)")
   - Use cmd.iterate_state(1, "ligand", "store_ligand_atom(model, chain, resi, name, x, y, z)")

2. Calculate distances between all receptor-ligand atom pairs:
   - Iterate through all receptor atom and ligand atom pairs
   - Calculate Euclidean distance: sqrt((x1-x2)² + (y1-y2)² + (z1-z2)²)
   - Store distance information including residue number, atom name, chain information

3. Identify closest residue and atom pairs:
   - Sort all atom pairs by distance
   - Select top 10 closest atom pairs
   - Extract involved residue numbers to receptor_interface_resi and ligand_interface_resi lists

4. Create precise interface residue selection sets:
   - Use "chain X and resi Y" format instead of simple resi numbers to precisely select interface residues
   - Avoid selecting same-numbered residues on other chains

5. Draw distance lines between closest atom pairs:
   - Use cmd.distance() to draw distance lines for top 10 closest atom pairs
   - Complete all operations in the same Python script block to avoid variable scope issues

Important technical points:
- **Precise residue selection**: Use "chain X and resi Y" format instead of simple resi numbers, avoid selecting same-numbered residues on other chains
- **Variable persistence**: Must complete all operations (atom extraction, distance calculation, selection set creation, distance line drawing) in the same Python script block to avoid variable scope loss issues

Interface residues displayed as sticks, colored by atom type, receptor C atoms=cyan, ligand C atoms=lightorange

Receptor-ligand interface residue differentiation coloring scheme:
- First color all interface residues by atom type: util.cbaw receptor_interface and util.cbaw ligand_interface
- Then separately modify carbon atom colors to distinguish receptor-ligand:
  - Receptor interface residue C atoms: cyan
  - Ligand interface residue C atoms: lightorange
- Maintain standard colors for other atoms: N=blue, O=red, S=yellow, etc.
{('Then identify and select user-specified key residues: ' + key_residues + '.' if key_residues else '')}
{('Create selection set named \'key_residues\' containing all specified residues.' if key_residues else '')}
{('Support cross-chain format (e.g., A:57 means residue 57 on chain A) and same-chain format (e.g., 57,102,195).' if key_residues else '')}
{('\nKey residue special coloring:\n- First color key residues by atom type: util.cbaw key_residues\n- Then assign unique colors to C atoms of each key residue (avoid conflicts with interface residue cyan/lightorange)\n- Maintain O=red, N=blue, S=yellow and other standard atom colors unchanged\n- Each key residue\'s Cα atom represented as 0.3 radius sphere, color consistent with that residue\'s C atom color.' if key_residues else '')}
{('Focus on interface interaction analysis, emphasize precise atomic-level PPI interface regions between receptor and ligand.' if not key_residues else '')}"""
        
        analysis_focus = f"""Receptor-ligand interaction PPI analysis:
Show overall structure of receptor and ligand: each component uses cartoon representation.
Set background structure transparency to 85% to highlight interface regions.
{('Highlight key residues: use sticks representation to show key residue side chains, spheres to represent Cα atoms.' if key_residues else '')}
Set transparency of structural parts except {('key residues and ' if key_residues else '')}interface interaction residues to 85% to highlight key regions.
Transparency of interface interaction residues is not adjusted, kept fully visible.
Analyze receptor-ligand interactions: focus on analyzing interface interaction patterns between receptor binding pocket and ligand.
Show precise inter-atomic distances: display distance lines between the closest 10 atom pairs, providing quantitative interaction information.
Measure important distances: pay special attention to distances between receptor-ligand interface residues, identify key interactions.
If user provided distance measurement pairs, perform precise inter-atomic distance measurements, especially cross receptor-ligand measurements.
Note: Hide all labels."""
        
        system_content = VISUALIZATION_PROMPT.format(
            structure=structure,
            analysis_type="Receptor-ligand interaction analysis",
            user_input=user_input,
            user_instructions=user_instructions,
            analysis_focus=analysis_focus
        )
        
        return GetPromptResult(
            description=f"PyMOL receptor-ligand analysis: {structure}",
            messages=[PromptMessage(role="user", content=TextContent(type="text", text=system_content))]
        )
    
    else:
        raise ValueError(f"Unknown prompt: {name}")

async def main():
    """Start MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
