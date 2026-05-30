"""AI, LLM, vector database, and search integrations."""

from __future__ import annotations

from fastango.integrations.catalog import docs_integration
from fastango.scaffold.plan import EnvVar

AI_INTEGRATIONS = (
    docs_integration(
        name="openai",
        label="OpenAI",
        category="ai",
        description="Adds OpenAI client dependencies and settings.",
        dependencies=("openai>=1.55.0",),
        env_vars=(EnvVar("OPENAI_API_KEY", "", "OpenAI API key."),),
        tags=("ai", "llm", "embeddings"),
    ),
    docs_integration(
        name="anthropic",
        label="Anthropic",
        category="ai",
        description="Adds Anthropic client dependencies and settings.",
        dependencies=("anthropic>=0.39.0",),
        env_vars=(EnvVar("ANTHROPIC_API_KEY", "", "Anthropic API key."),),
        tags=("ai", "llm", "claude"),
    ),
    docs_integration(
        name="ollama",
        label="Ollama",
        category="ai",
        description="Adds local Ollama client settings.",
        dependencies=("httpx>=0.27.0",),
        env_vars=(EnvVar("OLLAMA_BASE_URL", "http://localhost:11434", "Ollama API base URL."),),
        tags=("ai", "local", "llm"),
    ),
    docs_integration(
        name="langchain",
        label="LangChain",
        category="ai",
        description="Adds LangChain service skeleton guidance.",
        dependencies=("langchain>=0.3.0", "langchain-community>=0.3.0"),
        tags=("ai", "chains", "rag"),
        maturity="beta",
    ),
    docs_integration(
        name="llamaindex",
        label="LlamaIndex",
        category="ai",
        description="Adds LlamaIndex indexing guidance.",
        dependencies=("llama-index>=0.12.0",),
        tags=("ai", "rag", "indexing"),
        aliases=("llama-index",),
        maturity="beta",
    ),
    docs_integration(
        name="qdrant",
        label="Qdrant",
        category="ai",
        description="Adds Qdrant vector database settings.",
        dependencies=("qdrant-client>=1.12.0",),
        env_vars=(EnvVar("QDRANT_URL", "http://localhost:6333", "Qdrant URL."),),
        tags=("ai", "vector", "search"),
        conflicts=("pgvector", "pinecone", "weaviate"),
    ),
    docs_integration(
        name="pinecone",
        label="Pinecone",
        category="ai",
        description="Adds Pinecone vector database settings.",
        dependencies=("pinecone>=5.0.0",),
        env_vars=(EnvVar("PINECONE_API_KEY", "", "Pinecone API key."),),
        tags=("ai", "vector", "search"),
        conflicts=("pgvector", "qdrant", "weaviate"),
    ),
    docs_integration(
        name="weaviate",
        label="Weaviate",
        category="ai",
        description="Adds Weaviate vector database settings.",
        dependencies=("weaviate-client>=4.8.0",),
        env_vars=(EnvVar("WEAVIATE_URL", "", "Weaviate cluster URL."),),
        tags=("ai", "vector", "search"),
        conflicts=("pgvector", "qdrant", "pinecone"),
    ),
    docs_integration(
        name="elasticsearch",
        label="Elasticsearch",
        category="ai",
        description="Adds Elasticsearch search client settings.",
        dependencies=("elasticsearch[async]>=8.15.0",),
        env_vars=(EnvVar("ELASTICSEARCH_URL", "http://localhost:9200", "Elasticsearch URL."),),
        tags=("search", "indexing", "analytics"),
    ),
)
