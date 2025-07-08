# PDF/JPG互转工具

本项目是一个简单易用的**PDF转图片（JPG）、图片（JPG）转PDF**桌面工具，基于Python开发，支持图形界面操作，支持批量文件处理与图片排序，适合日常办公、资料归档等场景。

## 功能特性

- **PDF转JPG**  
  - 支持批量选择PDF文件
  - 可自定义输出分辨率（DPI）
  - 自动在原PDF同目录下新建文件夹输出图片

- **JPG转PDF**  
  - 支持批量选择图片（JPG）
  - 支持图片顺序调整（上移、下移），按顺序合成PDF
  - 合成PDF自动输出到图片所在目录

- **进度条动画反馈**  
  - 长任务有明显进度动画，不怕假死

- **大图片防炸弹兼容**  
  - 自动解除Pillow像素限制，支持超大图片、PDF转换

- **自带Poppler**  
  - 无需额外系统依赖，开箱即用

- **版权信息**  
  - 右下角显示：灯火通明（济宁）网络有限公司

## 使用方法

### 1. 下载和运行

- 直接下载 [Releases](https://github.com/lanbing1989/pdf_jpg_converter/releases) 中的 exe 文件（推荐）
- 或自行源码运行（需安装Python、依赖库和poppler）

### 2. 图形界面使用指引

- 启动后，选择“PDF转JPG”或“JPG转PDF”标签页
- 点击“选择PDF”或“选择JPG”，批量添加文件
- 如需调整图片顺序，可用“上移”“下移”按钮
- 设置DPI（如需），点击“开始转换”
- 转换结果将在源文件夹下生成（PDF转图片为pdf同名文件夹，图片转PDF为合并输出.pdf）

### 3. 源码运行（开发者/自定义用户）

1. 安装依赖  
   ```
   pip install pillow pdf2image
   ```
2. 下载poppler并解压到项目同级目录（需包含 poppler/bin）
3. 运行主程序  
   ```
   python pdf_jpg_converter_app_copyright.py
   ```

### 4. 打包EXE（开发者参考）

本工具已适配PyInstaller，poppler会一并打包，无需额外配置：

```
pyinstaller --noconfirm --onefile --add-data "poppler;poppler" pdf_jpg_converter_app_copyright.py
```
详见项目内相关说明。

---

## 截图

![主界面](screenshot.png)

---

## 常见问题

- **转换报错/图片过大**  
  已自动解除Pillow像素限制，极大图片依然可能耗时较久，请耐心等待进度条动画完成。

- **poppler相关问题**  
  exe版本自带poppler，源码运行请确保poppler/bin正确放置。

- **其它问题反馈/建议**  
  欢迎在[Issue](https://github.com/lanbing1989/pdf_jpg_converter/issues)区留言。

---

## 版权信息

> 灯火通明（济宁）网络有限公司 版权所有

---

## License

本项目仅供学习交流。请勿用于商业用途。
