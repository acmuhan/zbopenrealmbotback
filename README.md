# ZBProxy 管理 API

这是一个用于管理 ZBProxy 配置和控制其运行状态的 Python API 服务。

## 🚀 功能特性

- 📝 **配置管理**: 读取、修改、保存 ZBProxy 配置文件
- 🎮 **进程控制**: 启动、停止、重启 ZBProxy 进程
- 🔧 **服务管理**: 添加、删除服务配置
- 🌐 **出站管理**: 添加、删除出站配置
- 📊 **状态监控**: 实时查看 ZBProxy 运行状态、CPU和内存使用情况
- 📋 **日志管理**: 自动捕获ZBProxy输出到out.log，支持日志查看和清理
- 🔍 **日志跟踪**: 支持实时查看日志尾部，监控程序运行状态
- 🔒 **权限管理**: 自动修复可执行文件权限
- 🐧 **Linux 网络**: 自动设置 Linux 系统的 IP 路由

## 📦 安装依赖

```bash
pip install -r requirements.txt
```

## 🏃 运行服务

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动。

## 📖 API 文档

启动服务后，访问以下地址查看完整的 API 文档：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 主要 API 端点

### 配置管理

#### 获取完整配置
```http
GET /config
```

#### 获取指定路径的配置值
```http
GET /config/{path}
```
例如: `GET /config/Log.Level`

#### 更新配置值
```http
PUT /config
```
请求体:
```json
{
    "path": "Log.Level",
    "value": "info"
}
```

#### 添加服务配置
```http
POST /config/service
```
请求体:
```json
{
    "Name": "MyService",
    "Listen": 25566,
    "IPAccess": {"Mode": ""},
    "Outbound": {"Type": ""}
}
```

#### 删除服务配置
```http
DELETE /config/service/{service_name}
```

#### 添加出站配置
```http
POST /config/outbound
```
请求体:
```json
{
    "Name": "MyOutbound",
    "TargetAddress": "example.com",
    "TargetPort": 25565
}
```

#### 删除出站配置
```http
DELETE /config/outbound/{outbound_name}
```

### 进程控制

#### 获取 ZBProxy 状态
```http
GET /status
```

#### 启动 ZBProxy
```http
POST /start
```

#### 停止 ZBProxy
```http
POST /stop
```

#### 重启 ZBProxy
```http
POST /restart
```

#### 修复可执行文件权限
```http
POST /fix-permissions
```

修复ZBProxy可执行文件的执行权限，将权限设置为755（rwxr-xr-x）。

### 日志管理

#### 获取日志和状态监控
```http
GET /logs
```

此接口不仅返回日志文件内容，还包含ZBProxy的详细运行状态：
- ZBProxy进程状态（运行/停止）
- 进程ID和运行时间
- CPU使用率和内存占用
- 自动读取out.log文件（ZBProxy的标准输出）

#### 清理日志文件
```http
POST /logs/clear
```

清空所有日志文件的内容（保留文件，只清空内容）。

#### 获取指定日志文件的最后N行
```http
GET /logs/tail/{filename}?lines=50
```

支持的文件名：`out.log`, `zbproxy.log`, `error.log`, `access.log`
- `filename`: 日志文件名
- `lines`: 返回的行数（默认50行）

### Linux 网络配置

#### 执行 Linux IP 路由设置
```http
POST /dolinuxip
```

此接口会执行一个 bash 脚本来自动获取 Anchor IP 并设置默认路由。
- 仅在 Linux 系统上可用
- 需要 root 权限
- 会自动获取 DigitalOcean 等云服务商的 Anchor IP
- 设置 eth0 接口的默认路由

## 🛠️ 配置路径说明

配置路径使用点号分隔的格式，支持嵌套对象和数组索引：

- `Log.Level` - 日志级别
- `Services.0.Listen` - 第一个服务的监听端口
- `Services.0.Name` - 第一个服务的名称
- `Outbounds.0.TargetAddress` - 第一个出站的目标地址
- `Router.DefaultOutbound` - 默认出站

## 📄 响应格式

所有 API 响应都遵循统一格式：

### 成功响应
```json
{
    "success": true,
    "message": "操作成功",
    "data": {}
}
```

### 错误响应
```json
{
    "detail": "错误信息"
}
```

## 💡 使用示例

### Python 客户端示例

```python
import requests
import json

# API 基础地址
BASE_URL = "http://localhost:8000"

# 获取当前配置
response = requests.get(f"{BASE_URL}/config")
config = response.json()
print("当前配置:", json.dumps(config, indent=2, ensure_ascii=False))

# 修改日志级别
update_data = {
    "path": "Log.Level",
    "value": "info"
}
response = requests.put(f"{BASE_URL}/config", json=update_data)
print("更新结果:", response.json())

# 修复权限（如果需要）
response = requests.post(f"{BASE_URL}/fix-permissions")
print("权限修复:", response.json())

# 启动 ZBProxy
response = requests.post(f"{BASE_URL}/start")
print("启动结果:", response.json())

# 获取状态
response = requests.get(f"{BASE_URL}/status")
print("运行状态:", response.json())

# 停止 ZBProxy
response = requests.post(f"{BASE_URL}/stop")
print("停止结果:", response.json())

# 获取日志和状态监控
response = requests.get(f"{BASE_URL}/logs")
log_data = response.json()
print("ZBProxy状态:", log_data["zbproxy_status"])
print("日志文件信息:", {k: f"{v['total_lines']}行, {v['file_size']}字节" for k, v in log_data["logs"].items()})

# 获取out.log的最后10行
response = requests.get(f"{BASE_URL}/logs/tail/out.log?lines=10")
print("最新日志:", response.json())

# 清理日志文件
response = requests.post(f"{BASE_URL}/logs/clear")
print("清理结果:", response.json())

# 执行 Linux IP 路由设置（仅在 Linux 系统上）
response = requests.post(f"{BASE_URL}/dolinuxip")
print("Linux IP 设置结果:", response.json())
```

### cURL 示例

```bash
# 获取配置
curl -X GET "http://localhost:8000/config"

# 更新配置
curl -X PUT "http://localhost:8000/config" \
     -H "Content-Type: application/json" \
     -d '{"path": "Log.Level", "value": "debug"}'

# 修复权限
curl -X POST "http://localhost:8000/fix-permissions"

# 启动 ZBProxy
curl -X POST "http://localhost:8000/start"

# 获取状态
curl -X GET "http://localhost:8000/status"

# 停止 ZBProxy
curl -X POST "http://localhost:8000/stop"

# 获取日志和状态监控
curl -X GET "http://localhost:8000/logs"

# 获取out.log最后20行
curl -X GET "http://localhost:8000/logs/tail/out.log?lines=20"

# 清理日志文件
curl -X POST "http://localhost:8000/logs/clear"

# 执行 Linux IP 路由设置
curl -X POST "http://localhost:8000/dolinuxip"
```

## ⚠️ 注意事项

1. **权限**: 确保 API 服务有权限读写 ZBProxy 配置文件和执行程序
2. **端口冲突**: 默认 API 服务运行在 8000 端口，确保端口未被占用
3. **文件路径**: 确保 `ZBProxy.json` 和 `ZBProxy-linux-amd64-v1` 在同一目录下
4. **并发安全**: API 使用线程锁确保进程操作的安全性
5. **错误处理**: 所有操作都有完善的错误处理和异常捕获
6. **Linux系统**: `/dolinuxip` 接口仅在 Linux 系统上可用
7. **Root权限**: 网络路由设置和某些操作需要管理员权限

## 🔧 故障排除

### 常见问题

1. **配置文件未找到**
   - 确保 `ZBProxy.json` 文件存在于当前目录
   - 检查文件权限

2. **可执行文件未找到**
   - 确保 `ZBProxy-linux-amd64-v1` 文件存在
   - 使用 `/fix-permissions` 接口修复权限

3. **进程启动失败**
   - 检查端口是否被占用
   - 查看 ZBProxy 配置是否正确
   - 检查系统资源

4. **权限不足**
   - 以管理员身份运行 API 服务
   - 确保对文件和进程有足够权限
   - 使用 `sudo` 运行（Linux系统）

5. **网络路由设置失败**
   - 确保在支持的云平台上运行
   - 检查元数据服务是否可访问
   - 确保有root权限

## 📁 项目结构

```
.
├── main.py                     # 主 API 服务文件
├── requirements.txt            # Python 依赖
├── README.md                   # 说明文档
├── ZBProxy.json               # ZBProxy 配置文件
├── ZBProxy-linux-amd64-v1     # ZBProxy 可执行文件
└── out.log                    # ZBProxy 输出日志（自动生成）
```

## 🔄 工作流程

1. **启动API服务** → `python main.py`
2. **修复权限**（如需要） → `POST /fix-permissions`
3. **配置ZBProxy** → 使用配置管理接口
4. **启动ZBProxy** → `POST /start` （自动创建out.log）
5. **监控状态** → `GET /logs` 或 `GET /status`
6. **管理日志** → 使用日志管理接口
7. **停止服务** → `POST /stop`

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 📜 许可证

本项目采用 MIT 许可证。

---

**注意**: 此API专为管理ZBProxy代理服务而设计，请确保在安全的环境中使用，并遵循相关的安全最佳实践。
