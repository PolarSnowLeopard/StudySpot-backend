# 自习室预约系统后端

这是一个基于Flask的自习室预约系统后端API服务。

## 技术栈

- Python 3.10
- Flask 2.2.3
- Flask-SQLAlchemy
- Flask-JWT-Extended
- Flask-RESTX (API文档)
- MySQL/SQLite

## 项目结构

```
├── app                     # 应用主目录
│   ├── api                 # REST API和Swagger文档
│   ├── controllers         # 控制器层，处理HTTP请求
│   ├── models              # 数据模型层
│   ├── schemas             # 数据验证模式
│   ├── services            # 业务逻辑服务层
│   ├── tests               # 测试目录
│   │   ├── integration     # 集成测试
│   │   └── unit            # 单元测试
│   └── utils               # 工具函数
├── config.py               # 配置文件
├── migrations              # 数据库迁移文件
├── requirements.txt        # 项目依赖
├── init_db.py              # 数据库初始化脚本
└── run.py                  # 应用入口
```

## 安装与配置

1. 克隆项目到本地

2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖

```bash
pip install -r requirements.txt
```

4. 配置环境变量

复制`.env.example`文件为`.env`，并根据需要修改配置：

```bash
cp .env.example .env
```

5. 配置数据库连接

### 开发环境数据库配置

编辑`.env`文件中的`DATABASE_URL`变量，设置为您的实际MySQL数据库连接信息：

```
DATABASE_URL=mysql+pymysql://用户名:密码@服务器地址:端口/数据库名
```

例如：
```
DATABASE_URL=mysql+pymysql://study_admin:secure_password@db.example.com:3306/study_room_dev
```

### 测试环境数据库配置

测试环境默认使用SQLite内存数据库，无需额外配置：

```
DATABASE_TEST_URL=sqlite:///:memory:
```

6. 创建MySQL数据库

在开发环境的MySQL服务器上创建数据库：

```sql
CREATE DATABASE study_room_dev;
GRANT ALL PRIVILEGES ON study_room_dev.* TO '您的用户名'@'%' IDENTIFIED BY '您的密码';
FLUSH PRIVILEGES;
```

7. 初始化数据库

有两种方式初始化数据库：

### 方式一：使用数据库迁移工具（推荐用于生产环境）

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 方式二：使用提供的初始化脚本（推荐用于开发环境）

```bash
python init_db.py
```

这将创建所有必要的表结构并添加以下默认用户：
- 管理员账号: admin / admin123
- 学生账号: student1 / password123

**注意**：请在生产环境中修改这些默认密码！

## 运行项目

```bash
python run.py
```

或使用Flask命令：

```bash
flask run
```

## API文档

项目集成了Swagger文档，运行项目后可以通过以下地址访问：

```
http://localhost:5000/api/docs
```

### 认证接口

#### 登录

- **URL**: `/api/auth/login`
- **方法**: `POST`
- **请求体**:
  ```json
  {
    "username": "string",  // 用户名/学号
    "password": "string",  // 密码
    "role": "string"       // 角色：student或admin
  }
  ```
- **响应**:
  ```json
  {
    "code": 0,
    "message": "登录成功",
    "data": {
      "token": "string",
      "userId": "string",
      "role": "string",
      "name": "string",
      "avatar": "string"
    }
  }
  ```

#### 登出

- **URL**: `/api/auth/logout`
- **方法**: `POST`
- **响应**:
  ```json
  {
    "code": 0,
    "message": "登出成功"
  }
  ```

## 测试

运行单元测试（使用SQLite内存数据库）：

```bash
pytest app/tests/unit
```

运行集成测试（使用SQLite内存数据库）：

```bash
pytest app/tests/integration
```

运行所有测试：

```bash
pytest
``` 