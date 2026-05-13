# MCP (Model Context Protocol) 技术

## 是什么

MCP 是 AI 连接外部世界的**标准协议**。类比 USB：各种外设通过统一接口连接电脑，MCP 让各种工具/数据源通过统一协议连接 AI。

## 架构

```
AI 助手 ←→ MCP Client ←→ MCP Server ←→ 外部资源
                │               │
           (协议通信)      (工具/数据/API)
```

三种能力：

| 能力 | 说明 | 示例 |
|------|------|------|
| **Tools** | 可调用的函数 | 查数据库、操作文件、调 Kafka |
| **Resources** | 可读取的数据 | 配置文件、实时日志、数据库表 |
| **Prompts** | 预定义提示模板 | 标准化的交互模式 |

## 开发 MCP Server

```python
from mcp.server import Server

server = Server("my-mcp-server")

@server.tool()
async def query_db(sql: str) -> list:
    """执行安全的数据查询"""
    return await db.fetch(sql)

@server.resource("config://app")
async def get_config() -> dict:
    """获取应用配置"""
    return {"version": "1.0", "debug": False}

server.start()
```

## 安全机制

| 层面 | 措施 |
|------|------|
| **认证** | API Key、JWT Token |
| **授权** | 按用户/角色限制可访问的 tool 和 resource |
| **输入验证** | Pydantic 校验参数，防止注入 |
| **路径限制** | 文件/目录白名单，防止路径遍历 |
| **审批** | 高风险操作需要用户手动确认 |

## 已知 MCP Server 生态

- **文件系统**：安全读写限定目录
- **数据库**：PostgreSQL、MySQL、SQLite
- **Kafka**：topic 管理、消息查询、告警
- **GitHub/GitLab**：仓库操作、Issue 管理
- **搜索**：Brave Search、Tavily

## 实践要点

- MCP Server 要**单一职责**：一个 Server 做一类事（如只做 Kafka）
- **参数约束要严格**：用 Pydantic model 定义，让 AI 知道怎么调
- **描述要精确**：工具描述直接决定 AI 调用成功率
- **先本地开发再容器化**：开发时用 stdio transport，生产用 HTTP

---

*最后更新: 2026年5月*
