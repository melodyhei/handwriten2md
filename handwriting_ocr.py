import os
import base64
import json
import requests
from typing import Optional, Tuple, List, Dict
from dotenv import load_dotenv
from PIL import Image
import io
import time
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure API keys
BAIDU_API_KEY = os.getenv('BAIDU_API_KEY')
BAIDU_SECRET_KEY = os.getenv('BAIDU_SECRET_KEY')

def compress_image(image_path: str, max_size_mb: float = 4.0) -> Optional[bytes]:
    """
    压缩图片到指定大小以下
    
    Args:
        image_path: 图片路径
        max_size_mb: 最大文件大小（MB）
        
    Returns:
        压缩后的图片数据（bytes）或 None（如果压缩失败）
    """
    try:
        # 打开图片
        with Image.open(image_path) as img:
            # 转换为RGB模式（如果是RGBA）
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # 计算初始大小
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=95)
            size = output.tell()
            
            # 如果图片已经小于限制，直接返回
            if size <= max_size_mb * 1024 * 1024:
                return output.getvalue()
            
            # 计算需要的压缩比例
            ratio = (max_size_mb * 1024 * 1024) / size
            quality = int(95 * ratio)
            
            # 重新压缩
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=max(quality, 60))
            
            return output.getvalue()
            
    except Exception as e:
        print(f"图片压缩失败: {str(e)}")
        return None

class BaiduOCR:
    """百度OCR API封装类"""
    
    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.access_token = self._get_access_token()
        
    def _get_access_token(self) -> str:
        """获取百度API访问令牌"""
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }
        response = requests.post(url, params=params)
        return response.json()["access_token"]
    
    def recognize_handwriting(self, image_path: str) -> Tuple[bool, str]:
        """
        识别手写文字
        
        Args:
            image_path: 图片路径
            
        Returns:
            (success, text): 成功标志和识别文本
        """
        try:
            # 压缩图片
            compressed_image = compress_image(image_path)
            if compressed_image is None:
                return False, "图片压缩失败"
            
            # 转换为base64
            image = base64.b64encode(compressed_image).decode('utf-8')
            
            # 调用百度OCR API
            url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/handwriting?access_token={self.access_token}"
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = {"image": image}
            
            response = requests.post(url, headers=headers, data=data)
            result = response.json()
            
            if 'error_code' in result:
                return False, f"OCR识别失败: {result['error_msg']}"
            
            # 提取识别文本
            text = '\n'.join([word['words'] for word in result['words_result']])
            return True, text
            
        except Exception as e:
            return False, f"OCR处理出错: {str(e)}"

def get_processed_images(output_dir: str) -> Dict[str, str]:
    """
    获取已处理的图片记录
    
    Args:
        output_dir: 输出目录
        
    Returns:
        已处理图片的字典 {图片名: 处理时间}
    """
    processed_file = os.path.join(output_dir, "processed_images.json")
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
    processed_file = os.path.join(output_dir, "processed_images.json")
    processed_images = get_processed_images(output_dir)
    processed_images[image_name] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(processed_file, 'w', encoding='utf-8') as f:
        json.dump(processed_images, f, ensure_ascii=False, indent=2)

def format_markdown(image_name: str, text: str) -> str:
    """
    将文本格式化为Markdown格式
    
    Args:
        image_name: 图片名称
        text: 文本内容
        
    Returns:
        Markdown格式的文本
    """
    return f"""## {image_name}

{text}

---

"""

def main():
    """主函数示例"""
    # 检查环境变量
    required_vars = ['BAIDU_API_KEY', 'BAIDU_SECRET_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"错误: 缺少必要的环境变量: {', '.join(missing_vars)}")
        return
    
    # 设置输入输出路径
    results_dir = "png_images"
    output_dir = "output"
    ocr_output_file = os.path.join(output_dir, "ocr_results.md")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 检查results目录是否存在
    if not os.path.exists(results_dir):
        print(f"错误: {results_dir} 目录不存在！")
        return
    
    # 获取已处理的图片
    processed_images = get_processed_images(output_dir)
    
    # 获取所有图片文件并按名称排序
    image_files = [f for f in os.listdir(results_dir) 
                  if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    image_files.sort()  # 按文件名排序
    
    # 过滤出未处理的图片
    new_images = [f for f in image_files if f not in processed_images]
    
    if not new_images:
        print("没有新的图片需要处理！")
        return
    
    print(f"找到 {len(new_images)} 个新图片文件，开始处理...")
    
    # 打开输出文件（追加模式）
    with open(ocr_output_file, 'a', encoding='utf-8') as ocr_file:
        # 处理每个图片
        for i, image_file in enumerate(new_images, 1):
            image_path = os.path.join(results_dir, image_file)
            print(f"\n处理第 {i}/{len(new_images)} 个文件: {image_file}")
            
            # OCR识别
            print("正在进行OCR识别...")
            success, text = ocr_text_from_image(image_path)
            if not success:
                error_msg = f"OCR识别失败: {text}"
                print(error_msg)
                ocr_file.write(format_markdown(image_file, error_msg))
                continue
            
            print("OCR识别结果:")
            print("-" * 50)
            print(text)
            print("-" * 50)
            
            # 保存OCR结果
            ocr_file.write(format_markdown(image_file, text))
            
            # 记录已处理的图片
            save_processed_image(output_dir, image_file)
            
            # 添加短暂延迟，避免API限制
            time.sleep(1)
    
    print(f"\n处理完成！")
    print(f"OCR结果已保存到: {ocr_output_file}")
    print("\n下一步：")
    print("1. 检查 ocr_results.md 文件")
    print("2. 运行 gpt_organize.py 来整理和连接文本")

if __name__ == "__main__":
    main() 