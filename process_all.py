import os
import subprocess
import time
from datetime import datetime

def setup_directories():
    """创建必要的目录"""
    directories = ['heic_images', 'png_images', 'output']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    return directories

def convert_heic_to_png():
    """转换HEIC图片为PNG格式"""
    print("\n1. 开始转换HEIC图片为PNG格式...")
    
    # 检查是否有HEIC图片
    heic_files = [f for f in os.listdir('heic_images') if f.lower().endswith('.heic')]
    if not heic_files:
        print("没有找到HEIC图片，跳过转换步骤")
        return
    
    # 运行转换脚本
    try:
        subprocess.run(['python', 'heic2png.py'], check=True)
        print("HEIC图片转换完成！")
    except subprocess.CalledProcessError as e:
        print(f"转换过程中出错: {e}")
        return False
    
    return True

def process_images():
    """处理PNG图片并提取文本"""
    print("\n2. 开始处理图片并提取文本...")
    
    # 运行OCR处理脚本
    try:
        subprocess.run(['python', 'handwriting_ocr.py'], check=True)
        print("OCR处理完成！")
    except subprocess.CalledProcessError as e:
        print(f"OCR处理过程中出错: {e}")
        return False
    
    # 运行GPT整理脚本
    try:
        subprocess.run(['python', 'gpt_organize.py'], check=True)
        print("GPT整理完成！")
    except subprocess.CalledProcessError as e:
        print(f"GPT整理过程中出错: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("=== 开始处理流程 ===")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 设置目录
    print("\n0. 检查并创建必要的目录...")
    setup_directories()
    
    # 2. 转换HEIC图片
    if not convert_heic_to_png():
        print("HEIC转换失败，程序终止")
        return
    
    # 3. 处理图片和文本
    if not process_images():
        print("处理失败，程序终止")
        return
    
    print("\n=== 处理完成 ===")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n处理结果保存在以下位置：")
    print("- OCR结果: output/ocr_results.md")
    print("- 整理后的文本: output/organized_text.md")
    print("\n使用说明：")
    print("1. 将新的HEIC图片放入 heic_images 目录")
    print("2. 运行此程序：python process_all.py")
    print("3. 程序会自动完成转换、OCR识别和文本整理")

if __name__ == "__main__":
    main() 