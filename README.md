# 手写笔记转 Markdown

这个项目可以将手写笔记图片转换为结构化的 Markdown 文档。它使用百度 OCR API 进行文字识别，并使用 GPT API 进行文本整理。

## 功能特点

- 支持 HEIC 格式图片自动转换为 PNG
- 使用百度 OCR API 进行手写文字识别
- 使用 GPT API 进行文本整理和连接
- 自动跳过已处理的图片，避免重复处理
- 生成结构化的 Markdown 文档
- 支持批量处理多张图片

## 目录结构

```
.
├── heic_images/     # 存放原始 HEIC 图片
├── png_images/      # 存放转换后的 PNG 图片
├── output/          # 存放处理结果
│   ├── ocr_results.md        # OCR 识别结果
│   ├── organized_text.md     # 整理后的文本
│   └── organized_images.json # 已处理图片记录
├── process_all.py   # 主处理脚本
├── handwriting_ocr.py # OCR 处理脚本
└── gpt_organize.py  # GPT 文本整理脚本
```

## 使用说明

1. 环境准备：
   ```bash
   # 创建虚拟环境
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # 或
   .venv\Scripts\activate  # Windows

   # 安装依赖
   pip install -r requirements.txt
   ```

2. 配置环境变量：
   创建 `.env` 文件并添加以下配置：
   ```
   BAIDU_API_KEY=你的百度OCR API Key
   BAIDU_SECRET_KEY=你的百度OCR Secret Key
   OPENAI_API_KEY=你的OpenAI API Key
   ```

3. 使用步骤：
   - 将 HEIC 格式的图片放入 `heic_images` 目录
   - 运行处理脚本：`python process_all.py`
   - 查看结果：
     - OCR 结果：`output/ocr_results.md`
     - 整理后的文本：`output/organized_text.md`

## 处理记录

- 系统会自动记录已处理的图片，避免重复处理
- 处理记录保存在 `output/organized_images.json` 文件中
- 每次运行只会处理新的、未处理过的图片
- 已处理的图片结果会被保留，不会被覆盖

## 成本分析

### OCR 成本（百度 OCR API）
- 免费额度：每天 1000 次
- 超出免费额度：0.005元/次
- 每张图片消耗：1 次调用

### GPT API 成本
- 模型：GPT-3.5-turbo
- 价格：
  - 输入：$0.0015/1K tokens
  - 输出：$0.002/1K tokens
- 每张图片消耗：
  - 输入：约 100-200 tokens
  - 输出：约 50-100 tokens
  - 总成本：约 $0.0003-0.0005/图片

## 注意事项

1. 图片处理：
   - 支持 HEIC 和 PNG 格式
   - 建议图片清晰度适中，避免过大或过小
   - 建议保持图片方向正确

2. 文本处理：
   - OCR 结果会保存在 `ocr_results.md` 中
   - 整理后的文本会保存在 `organized_text.md` 中
   - 已处理的图片记录在 `organized_images.json` 中

3. 成本控制：
   - 系统会自动跳过已处理的图片，避免重复消耗 API 额度
   - 可以通过查看 `organized_images.json` 了解已处理的图片

## 常见问题

1. 图片未被处理：
   - 检查图片是否已存在于 `organized_images.json` 中
   - 检查图片格式是否正确（HEIC 或 PNG）
   - 检查图片是否放在正确的目录中

2. API 调用失败：
   - 检查 API 密钥是否正确配置
   - 检查网络连接是否正常
   - 检查 API 调用额度是否已用完

## 贡献

欢迎提交 Issue 和 Pull Request 来帮助改进这个项目。

## 许可证

MIT License 