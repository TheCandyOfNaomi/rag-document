```markdown
# RAG 文档智能问答系统
基于 Django + RAG + Celery + Redis + pgvector 的私有文档智能问答系统，支持 PDF 上传、异步向量化、智能问答。

## 部署步骤
1. 克隆仓库：git clone 你的仓库地址
2. 进入项目目录：cd rag-document-qa-system
3. 安装依赖：pip install -r requirements.txt
4. 启动 Redis、Celery、Docker pgvector 容器
5. 启动 Django：python manage.py runserver

## 核心技术栈
Django、DRF、Celery、Redis、Docker、PostgreSQL、pgvector、LangChain、GLM-4-Flash
```