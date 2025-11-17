校园哈基米关爱平台 - 协作指南

Hi 朋友！欢迎加入「校园哈基米关爱平台」项目。

这是一个使用 Python (FastAPI) + 原生 JavaScript 搭建的 Web 应用，用于记录和展示校园流浪猫的信息。这份文档会告诉你怎么在 5 分钟内把项目跑起来并开始协作。

🛠️ 必备工具 (Prerequisites)

在开始之前，请确保你的电脑上安装了：

Git: 点击下载 (用于拉取代码)

Python 3.8+: 点击下载 (用于运行后端和前端)

🚀 5 分钟启动项目 (Quick Start)

我们必须同时运行两个服务：

后端服务 (在 8000 端口，提供 API 数据)

前端服务 (在 5500 端口，提供网页)

你需要**打开两个黑窗口（终端）**来分别启动它们。

第 1 步：获取代码 (Clone)

打开第 1 个终端，把代码从 GitHub "克隆"到你的电脑上。

# 1. 克隆仓库
git clone [https://github.com/433-love/campus-project.git](https://github.com/433-love/campus-project.git)

# 2. 进入项目目录
cd campus-project


第 2 步：启动后端 (Backend @ Port 8000)

在第 1 个终端里 (接着上一步)，我们来启动后端。

# 3. 安装后端依赖 (根据 requirements.txt)
py -3 -m pip install --user -r requirements.txt

# 4. (重要) 安装图片上传插件
py -3 -m pip install --user python-multipart

# 5. (重要) 手动创建 uploads 文件夹
# 在你的项目根目录 (campus-project) 下，手动新建一个名为 uploads 的文件夹
# (这是为了让上报轨迹功能可以保存图片)

# 6. 启动后端！
py -3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000


启动成功后，你会看到 Uvicorn running on http://127.0.0.1:8000。
保持这个终端开着，不要关！

第 3 步：启动前端 (Frontend @ Port 5500)

打开一个全新的、第 2 个终端。

# 1. (在新终端里) 同样先进入项目目录
# (把 D:\path\to 换成你自己的路径)
cd D:\path\to\campus-project

# 2. 进入 frontend 目录
cd frontend

# 3. 启动前端服务
py -3 -m http.server 5500


启动成功后，你会看到 Serving HTTP on :: port 5500。
也保持这个终端开着，不要关！

第 4 步：访问！

你现在有两个服务在运行了。打开你的浏览器 (Chrome, Edge 等)，访问：

http://localhost:5500

你应该能看到项目的主页，并且能看到（或添加）猫咪列表了！

🤝 重点！如何协作 (Git Workflow)

我们都（在 main 分支上）协作，所以必须遵守规则，避免代码冲突。

规则 1：开始干活前，先拉取 (Pull)

在你每天开始写代码之前，永远先运行这行命令，来获取其他人最新的代码：

git pull origin main


规则 2：提交你的修改 (Add & Commit)

当你完成了一个小功能（比如改了个 Bug，加了个按钮）：

# 1. 添加你修改过的文件 ('.' 代表所有)
git add .

# 2. "提交"你的修改，并写清楚你干了啥
git commit -m "【修复】修复了首页无法显示图片的 Bug"
# (这个 -m "..." 里的信息一定要写清楚！)


规则 3：推送你的代码 (Push)

提交后，把你的代码推送回 GitHub，分享给所有人：

git push origin main


总结一下就是：git pull -> (写代码) -> git add . -> git commit -m "..." -> git push

📁 项目文件速查表

文件/目录

一句话说明

backend/main.py

FastAPI 总入口，所有 /api/* 路由都在这里

backend/models.py

数据库表结构（User、Cat、SightingLog…）

backend/schemas.py

请求/响应的数据格式（Pydantic 模型）

backend/database.py

连接数据库（默认 SQLite）

requirements.txt

后端依赖清单

frontend/index.html

前端单页应用外壳

frontend/styles.css

全局样式

frontend/app.js

前端核心逻辑：纯原生 JS 写的单页路由 & API 调用

uploads/

(需手动创建) 用户上传图片存放目录

## 🐾 新功能：宠物追踪系统

平台现在支持使用外设（GPS、RFID、Bluetooth 等）进行宠物追踪！

### 功能特点

- **设备管理**：注册和管理多种类型的追踪设备
- **实时追踪**：记录宠物的位置信息和移动轨迹
- **电量监控**：查看设备电量状态
- **历史记录**：查看完整的追踪历史

### 使用方法

1. 在"追踪"标签页注册新设备
2. 填写设备类型（GPS/RFID/Bluetooth）、名称和序列号
3. 关联到特定猫咪
4. 上报位置数据
5. 查看追踪历史

### API 端点

- `POST /api/tracking/devices` - 注册追踪设备
- `GET /api/tracking/devices` - 获取设备列表
- `GET /api/tracking/devices/{device_id}` - 获取设备详情
- `PUT /api/tracking/devices/{device_id}` - 更新设备信息
- `DELETE /api/tracking/devices/{device_id}` - 删除设备
- `POST /api/tracking/logs` - 上报位置数据
- `GET /api/cats/{cat_id}/tracking` - 获取猫咪追踪历史
- `GET /api/tracking/devices/{device_id}/logs` - 获取设备追踪记录
