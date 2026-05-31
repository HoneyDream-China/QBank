# 宝宝定制刷题系统

一个全栈刷题练习系统，支持 Web 应用和桌面应用两种使用方式。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 (Composition API), Vue Router 4, Pinia, Axios, Element Plus, Vite 5 |
| 后端 | Python 3.12+, FastAPI, SQLAlchemy 2.0, Pydantic v2, JWT 认证 |
| 数据库 | SQLite (Web 端) / JSON 文件 (桌面端) |
| 桌面端 | Python tkinter + PyInstaller 打包 |

## 项目结构

```
├── main.py                   # 桌面应用入口
├── questions.json            # 题库数据
├── frontend/                 # Vue 3 前端
│   ├── src/
│   │   ├── views/            # 页面组件
│   │   ├── components/       # 通用组件
│   │   ├── router/           # 路由定义
│   │   ├── stores/           # Pinia 状态管理
│   │   └── api/              # Axios 请求封装
│   ├── package.json
│   └── vite.config.js
├── backend/                  # FastAPI 后端
│   ├── app/
│   │   ├── routers/          # API 路由
│   │   ├── models/           # SQLAlchemy 模型
│   │   ├── schemas/          # Pydantic 数据校验
│   │   ├── utils/            # JWT、依赖注入
│   │   └── services/         # PDF 提取等
│   └── requirements.txt
└── dist/                     # 桌面应用打包产物
    └── main.exe
```

## 环境要求

- **Node.js** >= 18
- **Python** >= 3.12
- **pip**

## 快速开始 (Web 应用)

### 1. 启动后端

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

后端运行在 `http://localhost:8000`，API 文档在 `http://localhost:8000/docs`。

### 2. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端运行在 `http://localhost:5173`，API 请求自动代理到后端 `localhost:8000`。

### 3. 打开浏览器

访问 `http://localhost:5173`，注册账号或使用默认管理员账号登录：

- **管理员**: `admin` / `admin123`

## 快速开始 (桌面应用)

### 直接运行

```bash
pip install tkinter

# 需要题库文件
python main.py
```

### 使用打包好的 exe

直接双击 `dist/main.exe` 运行（确保同目录下有 `questions.json` 题库文件）。

### 重新打包

```bash
pip install pyinstaller
pyinstaller main.spec
```

## 生产构建 (Web 应用)

```bash
cd frontend
npm run build
```

构建产物在 `frontend/dist/`，可部署到任意静态文件服务器，或由 FastAPI 后端直接托管。

## 配置说明

主要配置在 `backend/app/config.py`：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `SECRET_KEY` | `quiz-system-secret-key-change-in-production` | JWT 签名密钥，生产环境务必修改 |
| `DEFAULT_ADMIN_USERNAME` | `admin` | 默认管理员用户名 |
| `DEFAULT_ADMIN_PASSWORD` | `admin123` | 默认管理员密码，生产环境务必修改 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` (24小时) | Token 过期时间 |
| `DATABASE_URL` | `sqlite:///./quiz.db` | SQLite 数据库路径 |

## 功能概览

- 用户注册/登录 (JWT 认证)
- 选择题库进行练习
- 随机刷题 / 考试模式
- 错题本管理
- 答题历史与进度统计
- 管理员面板：题库管理、题目增删改、PDF 批量导入、用户管理

## 云服务器部署（让其他人通过网址访问）

### 第一步：准备云服务器

任意云厂商均可，最低配置 1 核 1G 即可运行：

- [阿里云 ECS](https://ecs.console.aliyun.com) / [腾讯云 CVM](https://console.cloud.tencent.com/cvm) / [华为云 ECS](https://console.huaweicloud.com/ecm)
- 操作系统选择 **Ubuntu 22.04** 或 **CentOS 7+**
- 购买后记住 **公网 IP**（例如 `123.45.67.89`）

### 第二步：连接到服务器

```bash
# 本地终端执行，root 换成你的服务器用户名
ssh root@你的服务器公网IP
```

### 第三步：安装 Docker

```bash
# Ubuntu 一键安装
curl -fsSL https://get.docker.com | bash

# 启动 Docker 并设为开机自启
systemctl enable docker --now

# 验证安装
docker --version
```

### 第四步：上传项目

**方式一：Git 克隆（推荐）**

先把项目推送到 GitHub/Gitee 私有仓库，然后在服务器上：

```bash
git clone https://github.com/你的用户名/你的仓库.git
cd 你的仓库
```

**方式二：直接上传**

在本地项目目录执行（替换 IP）：

```bash
# 打包并上传到服务器
tar -czf quiz.tar.gz --exclude='node_modules' --exclude='venv' --exclude='__pycache__' --exclude='.git' .
scp quiz.tar.gz root@你的服务器IP:/root/
```

然后在服务器上解压：

```bash
cd /root
tar -xzf quiz.tar.gz -C /root/quiz
cd /root/quiz
```

### 第五步：配置并启动

```bash
# 1. 复制环境变量文件
cp .env.example .env

# 2. 编辑 .env，务必修改下面三项
nano .env
#   SECRET_KEY=改成随机字符串（可用 openssl rand -hex 32 生成）
#   DEFAULT_ADMIN_PASSWORD=改成强密码
#   PORT=80

# 3. 构建并启动
docker compose up -d

# 4. 导入题库（仅首次）
docker compose exec app python init_data.py
```

### 第六步：开放防火墙端口

**云厂商安全组（控制台操作）：**

在云服务器控制台的「安全组」或「防火墙」中，添加入方向规则：

| 协议 | 端口 | 来源 |
|------|------|------|
| TCP | 80 | 0.0.0.0/0 |

**服务器系统防火墙：**

```bash
# Ubuntu
ufw allow 80/tcp

# CentOS
firewall-cmd --add-port=80/tcp --permanent
firewall-cmd --reload
```

### 第七步：验证

浏览器访问 `http://你的服务器公网IP`，能打开登录页面即部署成功。

默认管理员：`admin` / `.env` 中设置的 `DEFAULT_ADMIN_PASSWORD`。

### 绑定域名（可选）

如果有域名，在 DNS 控制台添加一条 **A 记录**，将域名指向服务器公网 IP：

| 主机记录 | 记录类型 | 记录值 |
|----------|----------|--------|
| `@`（或 `quiz`） | A | 你的服务器 IP |

等待 DNS 生效后，即可通过域名访问。

### 日常维护

```bash
# 查看运行状态
docker compose ps

# 查看日志
docker compose logs -f app

# 更新代码后重新部署
git pull
docker compose up -d --build

# 停止服务
docker compose down
```

数据存储在 Docker volume 中，`docker compose down` 不会丢失。
