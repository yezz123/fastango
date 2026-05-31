"""AI and RAG code-template integrations."""

from __future__ import annotations

from fastango.integrations.catalog import docs_integration
from fastango.scaffold.plan import EnvVar

CHAT_ROUTE = '''"""LLM chat route placeholder."""

from fastapi import APIRouter

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/chat")
async def chat() -> dict[str, str]:
    return {"message": "Configure your selected LLM provider before enabling chat."}
'''

AI_SERVICE = '''"""Provider-agnostic AI service boundary."""


async def complete_prompt(prompt: str) -> dict[str, str]:
    return {"prompt": prompt, "response": "configure-ai-provider"}
'''

RAG_ROUTE = '''"""RAG search route placeholder."""

from fastapi import APIRouter

router = APIRouter(prefix="/rag", tags=["ai"])


@router.get("/search")
async def search(query: str) -> dict[str, str]:
    return {"query": query, "answer": "configure-vector-store"}
'''

PROMPT_STORE = '''"""Prompt store service boundary."""


async def get_prompt_template(name: str) -> str:
    return f"Prompt template: {name}"
'''

MEMORY_SERVICE = '''"""Conversation memory service boundary."""


async def remember_message(conversation_id: str, message: str) -> dict[str, str]:
    return {"conversation_id": conversation_id, "message": message}
'''

AI_CODE_INTEGRATIONS = (
    docs_integration(
        name="pydantic-ai-code",
        label="Pydantic AI Code",
        category="ai-code",
        description="Adds a Pydantic AI service boundary.",
        dependencies=("pydantic-ai>=0.0.13",),
        files=(("app/services/ai.py", AI_SERVICE),),
        tags=("ai", "agents"),
    ),
    docs_integration(
        name="litellm-code",
        label="LiteLLM Code",
        category="ai-code",
        description="Adds LiteLLM gateway settings and service boundary.",
        dependencies=("litellm>=1.50.0",),
        env_vars=(EnvVar("LITELLM_MODEL", "gpt-4o-mini", "Default LiteLLM model."),),
        settings_fields=('litellm_model: str = "gpt-4o-mini"',),
        files=(("app/services/ai.py", AI_SERVICE),),
        tags=("ai", "gateway"),
    ),
    docs_integration(
        name="openai-chat-code",
        label="OpenAI Chat Code",
        category="ai-code",
        description="Adds OpenAI chat route and settings.",
        dependencies=("openai>=1.55.0",),
        env_vars=(EnvVar("OPENAI_API_KEY", "", "OpenAI API key."),),
        files=(("app/api/routes/ai.py", CHAT_ROUTE), ("app/services/ai.py", AI_SERVICE)),
        settings_fields=('openai_api_key: str = ""',),
        router_imports=("from app.api.routes.ai import router as ai_router",),
        router_includes=("app.include_router(ai_router)",),
        tags=("ai", "openai"),
    ),
    docs_integration(
        name="anthropic-chat-code",
        label="Anthropic Chat Code",
        category="ai-code",
        description="Adds Anthropic chat route and settings.",
        dependencies=("anthropic>=0.39.0",),
        env_vars=(EnvVar("ANTHROPIC_API_KEY", "", "Anthropic API key."),),
        files=(("app/api/routes/ai.py", CHAT_ROUTE), ("app/services/ai.py", AI_SERVICE)),
        settings_fields=('anthropic_api_key: str = ""',),
        router_imports=("from app.api.routes.ai import router as ai_router",),
        router_includes=("app.include_router(ai_router)",),
        tags=("ai", "anthropic"),
    ),
    docs_integration(
        name="rag-pgvector",
        label="RAG pgvector",
        category="ai-code",
        description="Adds pgvector RAG route placeholder.",
        dependencies=("pgvector>=0.3.0",),
        files=(("app/api/routes/rag.py", RAG_ROUTE),),
        router_imports=("from app.api.routes.rag import router as rag_router",),
        router_includes=("app.include_router(rag_router)",),
        requires=("postgres",),
        tags=("rag", "pgvector"),
    ),
    docs_integration(
        name="qdrant-rag-code",
        label="Qdrant RAG Code",
        category="ai-code",
        description="Adds Qdrant RAG route placeholder.",
        dependencies=("qdrant-client>=1.12.0",),
        env_vars=(EnvVar("QDRANT_URL", "http://localhost:6333", "Qdrant URL."),),
        files=(("app/api/routes/rag.py", RAG_ROUTE),),
        router_imports=("from app.api.routes.rag import router as rag_router",),
        router_includes=("app.include_router(rag_router)",),
        tags=("rag", "qdrant"),
    ),
    docs_integration(
        name="prompt-store",
        label="Prompt Store",
        category="ai-code",
        description="Adds prompt template storage service boundary.",
        files=(("app/services/prompts.py", PROMPT_STORE),),
        tags=("ai", "prompts"),
    ),
    docs_integration(
        name="conversation-memory",
        label="Conversation Memory",
        category="ai-code",
        description="Adds Redis-backed conversation memory service boundary.",
        requires=("redis",),
        files=(("app/services/memory.py", MEMORY_SERVICE),),
        tags=("ai", "memory"),
    ),
)
