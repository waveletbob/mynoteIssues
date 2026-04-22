# MCP (Model Context Protocol) 技术

## MCP概述

MCP (Model Context Protocol) 是一个开放协议，用于连接AI助手与外部数据源和工具。它提供了一种标准化的方式，让AI模型能够安全、高效地访问和操作外部资源。

## 核心概念

### 协议架构

```
AI助手 ←→ MCP客户端 ←→ MCP服务器 ←→ 外部资源
                    ↓
                工具/数据源
```

### 主要组件

#### 1. MCP客户端

负责与AI助手和MCP服务器通信。

```python
from mcp import Client

# 创建MCP客户端
client = Client(
    server_url="http://localhost:3000",
    api_key="your-api-key"
)

# 连接到服务器
await client.connect()

# 获取可用工具
tools = await client.list_tools()
print(f"可用工具: {tools}")
```

#### 2. MCP服务器

提供工具和数据源访问。

```python
from mcp import Server

# 创建MCP服务器
server = Server(
    name="my-mcp-server",
    version="1.0.0"
)

# 定义工具
@server.tool()
async def get_weather(location: str) -> dict:
    """获取指定位置的天气信息"""
    # 实现天气查询逻辑
    return {
        "location": location,
        "temperature": 25,
        "condition": "晴朗"
    }

# 启动服务器
await server.start()
```

#### 3. 资源管理

管理可访问的数据资源。

```python
# 定义资源
@server.resource("weather://current")
async def current_weather() -> dict:
    """当前天气资源"""
    return {
        "data": "实时天气数据",
        "updated_at": "2024-01-01T00:00:00Z"
    }

# 访问资源
resource = await client.get_resource("weather://current")
print(resource)
```

## 工具开发

### 创建自定义工具

```python
from mcp import Tool
from typing import Optional

class DatabaseTool(Tool):
    """数据库操作工具"""
    
    name = "database_query"
    description = "执行数据库查询"
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection = None
    
    async def connect(self):
        """连接数据库"""
        import asyncpg
        self.connection = await asyncpg.connect(self.connection_string)
    
    async def execute(self, query: str, params: Optional[dict] = None) -> list:
        """执行查询"""
        if not self.connection:
            await self.connect()
        
        result = await self.connection.fetch(query, **(params or {}))
        return [dict(row) for row in result]
    
    async def close(self):
        """关闭连接"""
        if self.connection:
            await self.connection.close()

# 注册工具
server.register_tool(DatabaseTool("postgresql://user:pass@localhost/db"))
```

### 工具配置

```python
# 工具配置示例
tool_config = {
    "name": "file_system",
    "description": "文件系统操作工具",
    "parameters": {
        "operation": {
            "type": "string",
            "enum": ["read", "write", "delete", "list"],
            "required": True
        },
        "path": {
            "type": "string",
            "required": True
        },
        "content": {
            "type": "string",
            "required": False
        }
    },
    "permissions": {
        "allowed_paths": ["/safe/directory"],
        "max_file_size": 10485760  # 10MB
    }
}

# 应用配置
@server.tool(**tool_config)
async def file_system_tool(operation: str, path: str, content: Optional[str] = None):
    """文件系统操作"""
    # 实现文件操作逻辑
    pass
```

## 资源管理

### 资源定义

```python
from mcp import Resource

# 定义数据资源
@server.resource("data://users")
async def users_resource() -> Resource:
    """用户数据资源"""
    return Resource(
        uri="data://users",
        name="用户数据",
        description="所有用户信息",
        mime_type="application/json",
        data={
            "users": [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"}
            ]
        }
    )

# 定义流式资源
@server.resource("stream://logs")
async def logs_stream() -> Resource:
    """日志流资源"""
    async def log_generator():
        while True:
            log = await get_next_log()
            yield log
    
    return Resource(
        uri="stream://logs",
        name="日志流",
        description="实时日志流",
        mime_type="text/plain",
        stream=log_generator()
    )
```

### 资源访问控制

```python
# 访问控制配置
access_control = {
    "data://sensitive": {
        "allowed_roles": ["admin"],
        "authentication": "required"
    },
    "data://public": {
        "allowed_roles": ["*"],
        "authentication": "optional"
    }
}

# 应用访问控制
@server.resource("data://sensitive", access_control=access_control["data://sensitive"])
async def sensitive_data():
    """敏感数据"""
    return {"data": "敏感信息"}
```

## 安全机制

### 认证和授权

```python
from mcp.auth import AuthProvider

class JWTAuthProvider(AuthProvider):
    """JWT认证提供者"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    async def authenticate(self, token: str) -> dict:
        """验证JWT令牌"""
        import jwt
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return {
                "user_id": payload["user_id"],
                "roles": payload["roles"]
            }
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")

# 配置认证
server.auth_provider = JWTAuthProvider("your-secret-key")
```

### 权限管理

```python
# 权限定义
permissions = {
    "tools": {
        "database_query": ["read", "write"],
        "file_system": ["read", "write", "delete"]
    },
    "resources": {
        "data://users": ["read"],
        "data://admin": ["read", "write"]
    }
}

# 权限检查
async def check_permission(user: dict, resource: str, action: str) -> bool:
    """检查用户权限"""
    user_roles = user.get("roles", [])
    required_roles = permissions["resources"].get(resource, [])
    
    return any(role in user_roles for role in required_roles)
```

### 数据验证

```python
from pydantic import BaseModel, validator

class ToolInput(BaseModel):
    """工具输入验证"""
    operation: str
    path: str
    content: Optional[str] = None
    
    @validator('operation')
    def validate_operation(cls, v):
        allowed_operations = ["read", "write", "delete"]
        if v not in allowed_operations:
            raise ValueError(f"Invalid operation: {v}")
        return v
    
    @validator('path')
    def validate_path(cls, v):
        # 防止路径遍历攻击
        if ".." in v or v.startswith("/"):
            raise ValueError("Invalid path")
        return v

# 使用验证
input_data = ToolInput(
    operation="read",
    path="safe/file.txt"
)
```

## 集成应用

### 与LangChain集成

```python
from langchain.tools import StructuredTool
from langchain.agents import initialize_agent

# 创建MCP工具包装器
class MCPToolWrapper:
    def __init__(self, mcp_client, tool_name):
        self.client = mcp_client
        self.tool_name = tool_name
    
    async def run(self, **kwargs):
        """执行MCP工具"""
        result = await self.client.call_tool(self.tool_name, kwargs)
        return result

# 集成到LangChain
mcp_tool = StructuredTool.from_function(
    func=lambda **kwargs: asyncio.run(
        MCPToolWrapper(client, "database_query").run(**kwargs)
    ),
    name="database_query",
    description="执行数据库查询"
)

# 创建Agent
agent = initialize_agent(
    tools=[mcp_tool],
    llm=OpenAI(),
    agent="zero-shot-react-description"
)
```

### 与LlamaIndex集成

```python
from llama_index.tools import FunctionTool
from llama_index.agent import ReActAgent

# 创建MCP工具
async def mcp_database_query(query: str) -> str:
    """MCP数据库查询"""
    result = await client.call_tool("database_query", {"query": query})
    return str(result)

# 转换为LlamaIndex工具
llama_tool = FunctionTool.from_defaults(
    fn=mcp_database_query,
    name="database_query",
    description="执行数据库查询"
)

# 创建Agent
agent = ReActAgent.from_tools(
    [llama_tool],
    llm=OpenAI(),
    verbose=True
)
```

### 与Claude Desktop集成

```python
# Claude Desktop配置文件
claude_config = {
    "mcpServers": {
        "filesystem": {
            "command": "python",
            "args": ["-m", "mcp_server.filesystem"],
            "env": {
                "ALLOWED_DIRECTORIES": "/safe/path"
            }
        },
        "database": {
            "command": "python",
            "args": ["-m", "mcp_server.database"],
            "env": {
                "DATABASE_URL": "postgresql://user:pass@localhost/db"
            }
        }
    }
}

# 保存配置
import json
with open("claude_desktop_config.json", "w") as f:
    json.dump(claude_config, f, indent=2)
```

## 最佳实践

### 1. 错误处理

```python
async def safe_tool_call(client, tool_name, params, max_retries=3):
    """安全的工具调用"""
    for attempt in range(max_retries):
        try:
            result = await client.call_tool(tool_name, params)
            return result
        except Exception as e:
            if attempt == max_retries - 1:
                raise ToolExecutionError(f"Tool call failed: {str(e)}")
            await asyncio.sleep(2 ** attempt)  # 指数退避
```

### 2. 性能优化

```python
from functools import lru_cache

class CachedMCPClient:
    """带缓存的MCP客户端"""
    
    def __init__(self, base_client):
        self.client = base_client
        self.cache = {}
    
    @lru_cache(maxsize=100)
    async def get_resource(self, uri: str):
        """获取资源（带缓存）"""
        if uri not in self.cache:
            self.cache[uri] = await self.client.get_resource(uri)
        return self.cache[uri]
    
    async def invalidate_cache(self, uri: str):
        """使缓存失效"""
        if uri in self.cache:
            del self.cache[uri]
```

### 3. 监控和日志

```python
import logging

class MonitoredMCPClient:
    """带监控的MCP客户端"""
    
    def __init__(self, base_client):
        self.client = base_client
        self.logger = logging.getLogger(__name__)
    
    async def call_tool(self, tool_name: str, params: dict):
        """调用工具（带监控）"""
        start_time = time.time()
        
        try:
            self.logger.info(f"Calling tool: {tool_name} with params: {params}")
            result = await self.client.call_tool(tool_name, params)
            
            duration = time.time() - start_time
            self.logger.info(f"Tool {tool_name} completed in {duration:.2f}s")
            
            return result
        except Exception as e:
            self.logger.error(f"Tool {tool_name} failed: {str(e)}")
            raise
```

## 应用场景

### 1. 数据库访问

```python
@server.tool()
async def query_database(sql: str) -> list:
    """查询数据库"""
    # 实现数据库查询
    pass

@server.tool()
async def update_database(table: str, data: dict) -> bool:
    """更新数据库"""
    # 实现数据库更新
    pass
```

### 2. 文件操作

```python
@server.tool()
async def read_file(path: str) -> str:
    """读取文件"""
    with open(path, 'r') as f:
        return f.read()

@server.tool()
async def write_file(path: str, content: str) -> bool:
    """写入文件"""
    with open(path, 'w') as f:
        f.write(content)
    return True
```

### 3. API调用

```python
@server.tool()
async def call_api(url: str, method: str = "GET", data: Optional[dict] = None) -> dict:
    """调用外部API"""
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.request(method, url, json=data)
        return response.json()
```

## 常见问题

### Q1: MCP与其他协议的区别？

**A**: MCP特点：
- 专为AI助手设计
- 标准化的工具接口
- 内置安全机制
- 易于集成

### Q2: 如何保证MCP的安全性？

**A**: 安全措施：
- 认证和授权
- 输入验证
- 访问控制
- 审计日志

### Q3: MCP的性能如何优化？

**A**: 优化方法：
- 连接池
- 缓存机制
- 异步处理
- 批量操作

## 参考资料

- [MCP Specification](https://modelcontextprotocol.io/)
- [MCP GitHub](https://github.com/modelcontextprotocol)
- [Claude Desktop Integration](https://docs.anthropic.com/claude/desktop/mcp)
