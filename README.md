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

当前阶段：企业项目与成员管理。

已实现：

- FastAPI 分层后端架构；
- PostgreSQL 与 SQLAlchemy 数据访问；
- Alembic 数据库迁移；
- Argon2 密码哈希；
- OAuth2 Password 登录；
- JWT Access Token；
- 用户管理与管理员权限控制；
- 项目创建与项目查询；
- 项目成员关系管理；
- 项目级 Owner、Manager、Member 权限；
- 独立测试数据库；
- API 集成测试。。

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