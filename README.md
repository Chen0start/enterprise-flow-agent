# EnterpriseFlow Agent

EnterpriseFlow Agent 是一个面向企业知识查询和业务流程操作的智能助手项目。

项目将以后端服务和关系型数据库为基础，逐步实现：

- 用户、项目和任务管理；
- 企业文档管理；
- 企业知识库检索；
- Agent 工具调用；
- 权限控制和操作审计；
- RAG 与 Agent 效果评测。

## 当前状态

项目正在开发中。

当前阶段：用户管理后端开发。

已实现：

- FastAPI 应用骨架；
- PostgreSQL 数据库连接；
- SQLAlchemy 用户模型；
- Alembic 数据库迁移；
- 用户创建与查询接口；
- Argon2 密码哈希；
- 独立测试数据库与接口测试。

## 技术栈规划

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- Pytest
- pgvector
- Docker

## 项目文档

- [项目定义](docs/project_definition.md)