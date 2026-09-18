# media_tool- PyQt6多媒体工具箱
图片 / GIF / 视频 AI增强、AI抠图桌面工具

## ✨ 功能清单
- 图片增强：高清修复，支持透明PNG（保留Alpha通道，不会变黑底）
- GIF逐帧增强：带进度显示，支持中断任务
- 视频增强：逐帧推理处理
- AI抠图：u2net模型抠除背景
- 自动设备检测：优先GPU，无独显自动切CPU推理

## 📁 项目目录结构
media_tool-/
├── components/ # 公共组件
├── core/ # 核心推理、模型封装
├── windows/ # PyQt 界面页面（图片增强页面在这里）
├── main.py # 程序入口
├── requirements.txt # python 依赖
└── .gitignore # 忽略 venv、模型、输出缓存
plaintext

## 🛠️ 环境部署（Windows）
### 1. 创建虚拟环境
```powershell
# 创建虚拟环境
python -m venv venv
# 激活虚拟环境
venv\Scripts\activate
2. 安装依赖
powershell
pip install -r requirements.txt
3. 准备模型文件
⚠️ 模型文件不会上传 GitHub，需要手动放到 models/ 文件夹
需要模型：
realesr-animevideov3-x2.param
realesr-animevideov3-x2.bin
路径：media_tool-/models/
4. 启动软件
powershell
python main.py
📌 使用说明
导入素材：支持 png/jpg/gif/mp4
选择增强倍率，开启高清增强
点击处理，底部查看实时进度
可随时中断正在执行的任务
处理完成后导出文件
