# 手写文字识别与优化程序

这个程序使用百度OCR API和OpenAI GPT API来实现手写文字的识别和优化。它可以：
1. 从图片中提取手写文字
2. 使用GPT-4对提取的文字进行优化和润色

## 环境要求

- Python 3.7+
- 百度OCR API密钥
- OpenAI API密钥

## 安装

1. 克隆或下载此仓库
2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 配置

1. 创建 `.env` 文件，添加以下环境变量：
```
BAIDU_API_KEY=你的百度API密钥
BAIDU_SECRET_KEY=你的百度Secret密钥
OPENAI_API_KEY=你的OpenAI API密钥
```

## 使用方法

1. 将需要识别的图片放在程序目录下
2. 修改 `handwriting_ocr.py` 中的 `image_path` 变量为你的图片路径
3. 运行程序：
```bash
python handwriting_ocr.py
```

## 程序结构

- `handwriting_ocr.py`: 主程序文件
- `requirements.txt`: 依赖包列表
- `.env`: 环境变量配置文件（需要自行创建）

## 主要功能

1. OCR识别：
   - 使用百度OCR API进行手写文字识别
   - 支持JPG/PNG格式图片
   - 包含基本的错误处理

2. 文本优化：
   - 使用GPT-4进行文本优化
   - 自动修复错别字
   - 优化语言表达
   - 补全缺失内容

## 注意事项

- 确保图片清晰度较高，以提高识别准确率
- API调用可能产生费用，请注意使用频率
- 建议在使用前先测试小量图片 