# 在线考试系统

《数据库原理实践》课程设计项目——在线考试系统的设计与实现。

## 项目简介

本系统面向学校考试场景，为管理员、教师、学生三类角色提供服务：

- **管理员**：维护学生与教师的基本信息；
- **教师**：维护试题库（选择题/填空题）、组卷、安排考试、成绩统计与卷面分析；
- **学生**：在线限时考试、自动评阅结果查看、成绩查询。

详细需求见 [docs/01-需求分析.md](docs/01-需求分析.md)。

## 技术栈

- 数据库：MySQL 8.x（InnoDB / utf8mb4）
- 后端：Python 3.10 + Flask（RESTful API，Flask-SQLAlchemy + JWT）
- 前端：Vue 3 + Vite（前后端分离 SPA，Pinia + Vue Router + Axios）

## 目录结构

```
online-examination-system/
├── README.md                  # 项目说明
├── .gitignore
├── docs/                      # 课程设计各阶段文档
│   ├── 01-需求分析.md          # 功能模块图、数据流图、数据字典
│   └── assets/                # 文档配图（E-R 图等）
├── sql/                       # 数据库脚本
│   ├── 01_schema.sql          # 建库建表 DDL（11 张表）
│   └── 02_seed.sql            # 演示数据
└── src/
    ├── backend/               # Flask 后端
    │   ├── run.py             # 启动入口
    │   ├── requirements.txt
    │   ├── .env.example       # 环境变量模板
    │   └── app/
    │       ├── __init__.py    # 应用工厂、错误处理
    │       ├── config.py      # 配置
    │       ├── extensions.py  # db / jwt / cors
    │       ├── models.py      # ORM 模型（对应数据字典）
    │       ├── cli.py         # init-db / seed 命令
    │       ├── api/           # 按模块划分的蓝图
    │       └── utils/         # 鉴权装饰器、统一响应
    └── frontend/              # Vue 3 前端
        ├── package.json
        ├── vite.config.js     # /api 代理到后端
        └── src/
            ├── api/           # axios 封装
            ├── stores/        # Pinia 鉴权状态
            ├── router/        # 路由与角色守卫
            ├── layouts/       # 主布局
            └── views/         # 各角色页面
```

## 快速开始

### 1. 初始化数据库

```bash
# 方式 A：直接用 SQL 脚本（推荐，含演示数据）
mysql -u root -p < sql/01_schema.sql
mysql -u root -p online_exam < sql/02_seed.sql
```

```bash
# 方式 B：用后端 ORM 命令建表并写入演示数据
cd src/backend
.venv\Scripts\activate           # Windows；macOS/Linux: source .venv/bin/activate
flask --app run.py init-db
flask --app run.py seed
```

### 2. 启动后端

```bash
cd src/backend
copy .env.example .env           # 修改 DATABASE_URL 中的用户名/密码
.venv\Scripts\python.exe run.py  # 默认 http://127.0.0.1:5000
```

### 3. 启动前端

```bash
cd src/frontend
npm install
npm run dev                      # 默认 http://127.0.0.1:5173
```

## 演示账号（密码均为 `123456`）

| 角色 | 用户名 |
| --- | --- |
| 管理员 | `admin` |
| 教师 | `teacher1`、`teacher2` |
| 学生 | `stu0001` ~ `stu0006` |

## 接口约定

所有接口以 `/api` 为前缀，统一返回 `{ code, msg, data }`（`code=0` 表示成功）。
登录成功后返回 JWT，前端通过 `Authorization: Bearer <token>` 携带；后端按角色（admin/teacher/student）进行访问控制。

| 模块 | 主要接口 |
| --- | --- |
| 登录 | `POST /api/auth/login`、`GET /api/auth/me` |
| 用户管理 | `/api/students`、`/api/teachers`、`/api/courses`、`/api/me` |
| 试题管理 | `GET/POST/PUT/DELETE /api/questions` |
| 组卷 | `GET/POST/PUT/DELETE /api/papers` |
| 考试安排 | `GET/POST /api/exams` |
| 在线考试 | `GET /api/exams/{id}/paper`、`POST /api/exams/{id}/submit`、`GET /api/exams/{id}/result` |
| 成绩统计 | `GET /api/stats/scores`、`GET /api/stats/knowledge` |
| 成绩查询 | `GET /api/scores/mine`、`GET /api/scores` |

## 课程进度安排（2026 秋季学期）

| 节点 | 任务 | 状态 |
| --- | --- | --- |
| 9.10 | 确定选题（在线考试系统） | ✅ |
| 9.15 | 确定分工、需求分析、概念结构设计 | 🔄 需求分析初稿完成，概念设计进行中 |
| 10.15 | 逻辑/物理结构设计、数据库实施、系统开发与测试 | 🔄 工程骨架与建库脚本已就绪 |
| 第 13 周周末 | 验收与答辩（系统演示 + PPT 汇报） | ⬜ |

## 组员与分工

（待补充：组长/组员姓名、学号、分工）
