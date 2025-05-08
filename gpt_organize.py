import os
from openai import OpenAI
from dotenv import load_dotenv
import re
import json
from typing import List, Dict, Tuple
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure OpenAI
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url="https://api.openai.com/v1"
)

def get_processed_images(output_dir: str) -> Dict[str, str]:
    """
    获取已处理的图片记录
    
    Args:
        output_dir: 输出目录
        
    Returns:
        已处理图片的字典 {图片名: 处理时间}
    """
    processed_file = os.path.join(output_dir, "organized_images.json")
    if os.path.exists(processed_file):
        with open(processed_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_processed_image(output_dir: str, image_name: str):
    """
    记录已处理的图片
    
    Args:
        output_dir: 输出目录
        image_name: 图片名称
    """
    processed_file = os.path.join(output_dir, "organized_images.json")
    processed_images = get_processed_images(output_dir)
    processed_images[image_name] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(processed_file, 'w', encoding='utf-8') as f:
        json.dump(processed_images, f, ensure_ascii=False, indent=2)

def read_ocr_results(file_path: str) -> List[Dict[str, str]]:
    """
    读取OCR结果文件
    
    Args:
        file_path: OCR结果文件路径
        
    Returns:
        包含图片名称和文本的列表
    """
    results = []
    current_image = None
    current_text = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            # 检查是否是新的图片标题
            if line.startswith('## '):
                # 保存之前的图片结果
                if current_image and current_text:
                    results.append({
                        'image': current_image,
                        'text': '\n'.join(current_text)
                    })
                # 开始新的图片
                current_image = line[3:].strip()
                current_text = []
            elif not line.startswith('---'):
                current_text.append(line)
    
    # 保存最后一个图片的结果
    if current_image and current_text:
        results.append({
            'image': current_image,
            'text': '\n'.join(current_text)
        })
    
    return results

def organize_text_with_gpt(texts: List[Dict[str, str]]) -> str:
    """
    使用GPT整理和连接文本
    
    Args:
        texts: 文本列表，每个元素包含图片名称和文本
        
    Returns:
        整理后的文本
    """
    # 检查API密钥
    if not os.getenv('OPENAI_API_KEY'):
        return "GPT处理失败: 未找到OPENAI_API_KEY环境变量"
    
    # 构建提示词
    prompt = """请帮我整理和连接以下多张图片的OCR识别文本。这些文本可能来自同一篇文章的不同部分。
请：
1. 删除多余的空格和换行
2. 修正明显的错别字
3. 将不同图片的文本自然地连接起来
4. 保持原文的主要意思
5. 如果发现文本属于不同的文章，请用分隔符分开

原始文本：
"""
    
    # 添加所有文本
    for item in texts:
        prompt += f"\n--- 来自图片 {item['image']} ---\n"
        prompt += item['text'] + "\n"
    
    prompt += "\n请整理后的文本："
    
    try:
        # 调用API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # 使用更经济的模型，如果需要可以改回gpt-4
            messages=[
                {"role": "system", "content": "你是一个专业的中文文本整理助手，擅长处理OCR识别后的文本，能够识别和连接同一篇文章的不同部分。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        
        # 提取回复内容
        organized_text = response.choices[0].message.content.strip()
        if not organized_text:
            return "GPT处理失败: 返回的文本为空"
        
        return organized_text
        
    except Exception as e:
        error_msg = str(e)
        print(f"GPT API调用出错: {error_msg}")  # 打印详细错误信息以便调试
        return f"GPT处理失败: {error_msg}"

def append_to_organized_text(output_file: str, new_text: str):
    """
    将新整理的文本追加到已整理的文件中
    
    Args:
        output_file: 输出文件路径
        new_text: 新整理的文本
    """
    # 如果文件不存在，创建新文件
    if not os.path.exists(output_file):
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 整理后的文本\n\n")
    
    # 追加新文本
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write("\n" + new_text + "\n")

def clear_processing_history(output_dir: str):
    """
    清除处理历史记录
    
    Args:
        output_dir: 输出目录
    """
    processed_file = os.path.join(output_dir, "organized_images.json")
    if os.path.exists(processed_file):
        os.remove(processed_file)
        print("已清除处理历史记录")

def main():
    """主函数"""
    # 设置文件路径
    output_dir = "output"
    ocr_file = os.path.join(output_dir, "ocr_results.md")
    output_file = os.path.join(output_dir, "organized_text.md")
    
    # 检查OCR结果文件是否存在
    if not os.path.exists(ocr_file):
        print(f"错误: OCR结果文件 {ocr_file} 不存在！")
        return
    
    print("开始整理文本...")
    
    # 清除处理历史
    clear_processing_history(output_dir)
    
    # 读取OCR结果
    print("1. 读取OCR结果...")
    all_texts = read_ocr_results(ocr_file)
    if not all_texts:
        print("没有找到OCR结果！")
        return
    
    print(f"找到 {len(all_texts)} 个文本片段需要整理")
    
    # 使用GPT整理文本
    print("2. 使用GPT整理和连接文本...")
    organized_text = organize_text_with_gpt(all_texts)
    
    # 保存结果
    print("3. 保存整理后的文本...")
    # 清空原有文件内容
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 整理后的文本\n\n")
    # 追加新文本
    append_to_organized_text(output_file, organized_text)
    
    # 记录已处理的图片
    for text in all_texts:
        save_processed_image(output_dir, text['image'])
    
    print(f"\n处理完成！")
    print(f"整理后的文本已保存到: {output_file}")
    print(f"已处理 {len(all_texts)} 个文本片段")

if __name__ == "__main__":
    main() 