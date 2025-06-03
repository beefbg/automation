import zipfile
import xml.etree.ElementTree as ET
import re

def xmind_to_markdown(xmind_file, md_file):
    """
    将XMind文件转换为Markdown格式
    :param xmind_file: 输入的XMind文件路径
    :param md_file: 输出的Markdown文件路径
    """
    # 提取XMind内容（XMind本质是zip压缩包）
    with zipfile.ZipFile(xmind_file, 'r') as z:
        # 从压缩包中读取content.xml
        with z.open('content.xml') as xml_file:
            tree = ET.parse(xml_file)
    
    root = tree.getroot()
    
    # 定义XMind的XML命名空间
    ns = {
        'x': 'urn:xmind:xmap:xmlns:content:2.0',
        'a': 'http://www.w3.org/2005/Atom'
    }
    
    # 查找所有sheet（画布）
    sheets = root.findall('.//x:sheet', ns)
    if not sheets:
        raise ValueError("未找到有效的思维导图内容")
    
    markdown_content = ""
    
    for sheet in sheets:
        # 获取画布标题
        title_elem = sheet.find('.//x:title', ns)
        sheet_title = title_elem.text if title_elem is not None else "Untitled"
        markdown_content += f"# {sheet_title}\n\n"
        
        # 查找中心主题
        root_topic = sheet.find('.//x:topic', ns)
        if root_topic is None:
            continue
        
        # 递归处理主题树
        def process_topic(topic, level=0):
            content = ""
            
            # 提取主题文本
            title_elem = topic.find('x:title', ns)
            title = title_elem.text if title_elem is not None else ""
            
            # 清理特殊字符
            title = re.sub(r'[\r\n]+', ' ', title).strip()
            
            # 添加Markdown列表项
            indent = "  " * (level - 1) if level > 0 else ""
            prefix = "- " if level > 0 else f"## {title}\n"
            
            if level > 0:
                content += f"{indent}{prefix}{title}\n"
            
            # 处理子主题
            children = topic.find('x:children/x:topics/x:topic', ns)
            if children is not None:
                for child in topic.findall('x:children/x:topics/x:topic', ns):
                    content += process_topic(child, level + 1)
            
            return content
        
        # 从中心主题的下一级开始处理
        for main_topic in root_topic.findall('x:children/x:topics/x:topic', ns):
            markdown_content += process_topic(main_topic, level=1)
        
        markdown_content += "\n"
    
    # 写入Markdown文件
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

if __name__ == "__main__":
    # 使用示例
    xmind_to_markdown("input.xmind", "output.md")
    print("转换完成！")