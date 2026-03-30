from django.conf import settings

# LangChain Core
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate

# LangChain OpenAI (1.0.3 兼容版)
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# LangChain Postgres
from langchain_postgres import PGVector

# 文档处理
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

class RAGService:
    def __init__(self):
        # 初始化 Embedding
        self.embeddings = OpenAIEmbeddings(
            model="embedding-3",
            base_url="https://open.bigmodel.cn/api/paas/v4/",
            api_key=settings.OPENAI_API_KEY
        )
        
        # 构建数据库连接字符串
        db_settings = settings.DATABASES['default']
        self.connection_string = (
            f"postgresql+psycopg://{db_settings['USER']}:{db_settings['PASSWORD']}"
            f"@{db_settings['HOST']}:{db_settings['PORT']}/{db_settings['NAME']}"
        )

        # 构建 Prompt
        self.rag_prompt = ChatPromptTemplate.from_messages([
            ("system", """
            你是一个严谨的文档助手。请根据以下【上下文】回答【问题】。
            
            【规则】
            1. 答案必须完全来自上下文，禁止编造。
            2. 如果上下文没有答案，请明确告知："文档中未提及相关内容"。
            3. 回答要简洁、条理清晰。
            
            【上下文】
            {context}
            """),
            ("human", "{question}"),
        ])

    def _get_vector_store(self, collection_name: str):
        return PGVector(
            connection=self.connection_string,
            embeddings=self.embeddings,
            collection_name=collection_name,
            use_jsonb=True,
        )

    def _format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def ingest_document(self, file_path: str, collection_name: str):
        """向量化文档"""
        loader = PyPDFLoader(file_path)
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        split_docs = text_splitter.split_documents(docs)

        PGVector.from_documents(
            documents=split_docs,
            embedding=self.embeddings,
            connection=self.connection_string,
            collection_name=collection_name,
            use_jsonb=True,
        )
        return True

    def query(self, document_id: int, question: str) -> dict:
        """RAG 查询 (LCEL 链式调用)"""
        collection_name = f"doc_{document_id}"
        vector_store = self._get_vector_store(collection_name)
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})

        llm = ChatOpenAI(
            model="glm-4-flash",
            base_url="https://open.bigmodel.cn/api/paas/v4/",
            temperature=0.1,
            api_key=settings.OPENAI_API_KEY
        )

        # LangChain 1.2.0 标准 LCEL 写法
        rag_chain = (
            {"context": retriever | self._format_docs, "question": RunnablePassthrough()}
            | self.rag_prompt
            | llm
            | StrOutputParser()
        )

        answer = rag_chain.invoke(question)
        source_docs = retriever.invoke(question)

        return {
            "answer": answer,
            "sources": [doc.page_content for doc in source_docs]
        }