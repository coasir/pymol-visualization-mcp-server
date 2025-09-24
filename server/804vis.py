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

# 简洁的系统提示
VISUALIZATION_PROMPT = """
You are the PyMOL protein structure visualization expert. Intelligently perform visualization analysis based on user needs.

# 目标结构：{structure}
# 分析类型：{analysis_type}
# 用户指定：{user_input}

# 执行策略：

## 第一阶段：环境准备与结构加载
启动PyMOL并建立清洁的工作环境。加载目标结构（使用fetch命令获取PDB或load本地文件）。
Basic cleanup:移除溶剂分子、水分子和其他干扰物。
Set background： white并且opaque .

## 第二阶段：用户指定组件处理
{user_instructions}

## 第三阶段：可视化方案实施
根据分析目标选择主要表示方法：cartoon展示整体折叠，surface显示分子形状，sticks展示原子细节。
棍棒模式展示关键原子
Color key residues by element: run_pymol_command("util.cbaw key_residues")
仅单组分分析需进行此步（灰度设置）：Apply grayscale spectrum to all Cα atoms except key residues: run_pymol_command("spectrum count, white_gray70, name ca and not key_residues")
以半径为0.3的彩色球体表示key residue的Cα原子，每个key residue的Cα atom用不同颜色表示，并和结构中已有的颜色以及背景颜色区分开（避免红色蓝色灰色）

设置初始视角：选择能展示整体蛋白的观察角度和缩放比例。

## 第四阶段：论文质量渲染优化

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

🛑 **暂停点**：渲染优化和ray完成，告诉用户可以保存第一张基础可视化图片，然后输入'continue'继续详细科学分析。

## 第五阶段：深度科学分析（用户确认后继续）
{analysis_focus}

## 第六阶段：测量与标注
如果是单组分分析：仅展示关键残基，蛋白主链透明度设为65%
如果是多组分分析：展示界面残基，隐藏所有表面显示，卡通蛋白主链透明度设为85%
*如用户进行了对测距，距离两端的residue以棍棒模式体现

## 第七阶段：最终优化与输出
调整到最佳展示视角：考虑对称性、重要特征可见性。
进行最终质量检查：确认所有关键信息清晰可见、颜色方案合理、无技术错误。

# 重要原则：
- 严格按用户指定的残基/链执行，不要自行推测
- 确保输出达到论文发表质量标准
- 在关键节点暂停等待用户确认再继续
- 遇到报错及时修正

# 错误处理策略：
- **检测失效**：当PyMOL返回"Invalid selection name"错误时，立即重建该选择集
- **自动恢复**：遇到选择集错误时，不要询问用户，直接重新创建并继续执行
- **状态保持**：重建选择集时要恢复之前的所有属性（颜色、显示模式等）
- **流程连续性**：确保错误修复不中断整体可视化流程

# 技术最佳实践：
- **精确选择语法**：使用"chain A and resi 65"而不是"resi 65"来避免跨链残基混淆
- **脚本块完整性**：关键计算必须在单个Python块中完成，确保变量在整个流程中可用
- **坐标访问方法**：使用cmd.iterate_state而非cmd.iterate来获取原子坐标

"""

@server.list_prompts()
async def list_prompts() -> list[Prompt]:
    """可用分析模板"""
    return [
        Prompt(
            name="single_component_analysis",
            description="单组分残基分析",
            arguments=[
                PromptArgument(name="structure", description="PDB ID或文件路径", required=True),
                PromptArgument(name="key_residues", description="关键残基（如57,102或A:57,B:102，可选）", required=False),
                PromptArgument(name="distance_pairs", description="测距对（如57:CA-102:CA）", required=False)
            ]
        ),
        Prompt(
            name="multi_component_analysis", 
            description="受体配体相互作用分析",
            arguments=[
                PromptArgument(name="structure", description="PDB ID或文件路径", required=True),
                PromptArgument(name="key_residues", description="关键残基（如57,102或A:57,B:102，可选）", required=False),
                PromptArgument(name="components", description="组分定义（如receptor:A+B+C,ligand:D+E）", required=True),
                PromptArgument(name="distance_pairs", description="测距对（如57:CA-102:CA）", required=False)
            ]
        )
    ]

@server.get_prompt()
async def get_prompt(name: str, arguments: dict | None = None) -> GetPromptResult:
    """生成可视化提示"""
    
    if name == "single_component_analysis":
        structure = arguments.get("structure", "")
        key_residues = arguments.get("key_residues", "")
        distance_pairs = arguments.get("distance_pairs", "")
        
        if not key_residues:
            raise ValueError("单组分分析需要指定key_residues参数")
        
        # 构建用户输入描述
        user_specs = [f"关键残基: {key_residues}"]
        if distance_pairs:
            user_specs.append(f"距离测量: {distance_pairs}")
        
        user_input = ", ".join(user_specs)
        
        user_instructions = f"""识别并选择用户指定的关键残基：{key_residues}。
创建名为'key_residues'的选择集包含所有指定残基。
支持跨链格式（如A:57表示A链第57号残基）和同链格式（如57,102,195）。

重要显示控制：
- 执行hide everything确保清洁起始状态
- 仅显示关键残基：show sticks, key_residues
- 先对关键残基按原子类型着色：util.cbaw key_residues
- 然后为每个关键残基的C原子分配独特颜色（如forest、deeppurple、gold、teal等，避免与红蓝冲突）
- 确保O=红色、N=蓝色、S=黄色等标准原子色保持不变
- 每个关键残基的Cα原子用0.3半径球体表示，颜色与该残基的C原子颜色一致。"""
        
        analysis_focus = f"""聚焦关键残基的结构特征和相互作用：

**蛋白主链优化显示**（暂停点后执行）：
- 设置蛋白主链为统一深灰色：color gray40, {structure}
- 设置蛋白主链透明度65%：set cartoon_transparency, 0.65, {structure}

严格控制显示内容：
- 蛋白主链透明度设为65%，颜色为gray40
- 关键残基使用高对比度、美观的配色方案
- 确保每个残基在视觉上完全可区分
- 确保关键残基完全可见：set transparency, 0.0, key_residues
如用户提供了距离测量对，执行精确的原子间距离测量。
注意：不显示氢键和氢键距离标签，也不显示残基标签。"""
        
        system_content = VISUALIZATION_PROMPT.format(
            structure=structure,
            analysis_type="单组分残基分析",
            user_input=user_input,
            user_instructions=user_instructions,
            analysis_focus=analysis_focus
        )
        
        return GetPromptResult(
            description=f"PyMOL单组分分析: {structure}",
            messages=[PromptMessage(role="user", content=TextContent(type="text", text=system_content))]
        )
    
    elif name == "multi_component_analysis":
        structure = arguments.get("structure", "")
        key_residues = arguments.get("key_residues", "")
        components = arguments.get("components", "")
        distance_pairs = arguments.get("distance_pairs", "")
        
        if not components:
            raise ValueError("多组分分析需要指定components参数")
        
        # 验证receptor和ligand格式
        if "receptor:" not in components or "ligand:" not in components:
            raise ValueError("组分定义必须使用receptor:chains,ligand:chains格式")
        
        # 构建用户输入描述
        user_specs = [f"组分划分: {components}"]
        if key_residues:
            user_specs.append(f"关键残基: {key_residues}")
        if distance_pairs:
            user_specs.append(f"距离测量: {distance_pairs}")
        
        user_input = ", ".join(user_specs)
        
        # 解析受体配体组分
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
        
        user_instructions = f"""按用户指定划分受体配体组分：
创建受体组分包含链{receptor_chains}，使用marine颜色着色
创建配体组分包含链{ligand_chains}，使用orange颜色着色
为每个组分创建独立的PyMOL对象，使用不同颜色区分。
为每个组分显示半透明表面：执行show surface命令，然后设置transparency为0.85。

使用精确的cmd.iterate_state方法识别界面相互作用残基：
1. 使用cmd.iterate_state获取受体和配体的所有原子坐标和信息到字典：
   - 创建receptor_atoms和ligand_atoms字典存储原子信息
   - 使用cmd.iterate_state(1, "receptor", "store_receptor_atom(model, chain, resi, name, x, y, z)")
   - 使用cmd.iterate_state(1, "ligand", "store_ligand_atom(model, chain, resi, name, x, y, z)")

2. 计算所有受体-配体原子间距离：
   - 遍历所有受体原子和配体原子对
   - 计算欧几里得距离：sqrt((x1-x2)² + (y1-y2)² + (z1-z2)²)
   - 存储距离信息包含残基号、原子名、链信息

3. 识别最近的残基和原子对：
   - 按距离排序所有原子对
   - 选择前10个最近的原子对
   - 提取涉及的残基号到receptor_interface_resi和ligand_interface_resi列表

4. 创建精确的界面残基选择集：
   - 使用"chain X and resi Y"格式而非简单resi号来精确选择界面残基
   - 避免选择其他链上的同号残基

5. 绘制最近原子对之间的距离线：
   - 对前10个最近的原子对使用cmd.distance()绘制距离线
   - 在同一Python脚本块中完成所有操作以避免变量作用域问题

重要技术要点：
- **精确残基选择**：使用"chain X and resi Y"格式而非简单的resi号，避免选择其他链上的同号残基
- **变量持久性**：必须在同一Python脚本块中完成所有操作（原子提取、距离计算、选择集创建、距离线绘制），避免变量作用域丢失问题

界面残基用sticks显示，按原子类型着色，受体C原子=cyan，配体C原子=lightorange

受体配体界面残基区分着色方案：
- 首先对所有界面残基按原子类型着色：util.cbaw receptor_interface 和 util.cbaw ligand_interface
- 然后单独修改碳原子颜色以区分受体配体：
  - 受体界面残基的C原子：cyan
  - 配体界面残基的C原子：lightorange
- 保持其他原子的标准颜色：N=蓝色，O=红色，S=黄色等
{('然后识别并选择用户指定的关键残基：' + key_residues + '。' if key_residues else '')}
{('创建名为\'key_residues\'的选择集包含所有指定残基。' if key_residues else '')}
{('支持跨链格式（如A:57表示A链第57号残基）和同链格式（如57,102,195）。' if key_residues else '')}
{('\n关键残基特殊着色：\n- 先对关键残基按原子类型着色：util.cbaw key_residues\n- 然后为每个关键残基的C原子分配独特颜色（避免与界面残基的cyan/lightorange冲突）\n- 保持O=红色、N=蓝色、S=黄色等标准原子色不变\n- 每个关键残基的Cα原子用0.3半径球体表示，颜色与该残基的C原子颜色一致。' if key_residues else '')}
{('专注于界面相互作用分析，重点展示受体配体间的精确原子级别PPI界面区域。' if not key_residues else '')}"""
        
        analysis_focus = f"""受体配体相互作用的PPI分析：
展示受体和配体的整体结构：每个组分使用cartoon表示。
设置背景结构透明度为85%以突出界面区域。
{('突出显示关键残基：使用sticks表示显示关键残基的侧链，spheres表示Cα原子。' if key_residues else '')}
设置除{('关键残基和' if key_residues else '')}界面相互作用残基外的结构部分透明度为85%以突出重点区域。
界面相互作用残基的透明度不调整，保持完全可见。
分析受体配体相互作用：重点分析受体结合口袋与配体的界面相互作用模式。
显示精确的原子间距离：展示最近的10个原子对之间的距离线，提供定量的相互作用信息。
测量重要距离：特别关注受体配体界面残基间距离，识别关键的相互作用。
如用户提供了距离测量对，执行精确的原子间距离测量，特别是跨受体配体测量。
注意：隐藏所有标签。"""
        
        system_content = VISUALIZATION_PROMPT.format(
            structure=structure,
            analysis_type="受体配体相互作用分析",
            user_input=user_input,
            user_instructions=user_instructions,
            analysis_focus=analysis_focus
        )
        
        return GetPromptResult(
            description=f"PyMOL受体配体分析: {structure}",
            messages=[PromptMessage(role="user", content=TextContent(type="text", text=system_content))]
        )
    
    else:
        raise ValueError(f"未知prompt: {name}")

async def main():
    """启动MCP服务器"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
