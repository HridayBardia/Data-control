import pytest
import asyncio
from app.services.embeddings import ResilientEmbeddingService, OpenAIEmbeddingProvider
from app.services.parsers import EnterpriseDocumentParser, SmartSemanticChunker
from app.core.authorization import AuthContext, Role, PermissionEvaluator
from app.core.secrets import secret_vault
from app.core.rate_limiter import rate_limiter

def test_secret_vault_envelope_encryption():
    secret = "sk-proj-atlas-enterprise-super-secret-key"
    encrypted = secret_vault.encrypt_secret(secret)
    assert encrypted != secret
    decrypted = secret_vault.decrypt_secret(encrypted)
    assert decrypted == secret

def test_document_parser_and_chunking():
    parser = EnterpriseDocumentParser()
    raw_content = b"Project Atlas is an enterprise AI knowledge platform. It integrates RAG and zero trust security."
    parsed_doc = parser.parse("architecture.txt", raw_content)
    assert parsed_doc.title == "architecture.txt"
    assert parsed_doc.file_type == "TXT"
    assert parsed_doc.metadata["language"] == "en"

    chunker = SmartSemanticChunker(max_tokens=20)
    chunks = chunker.chunk_document(parsed_doc)
    assert len(chunks) >= 1
    assert chunks[0].text != ""

def test_authorization_evaluator():
    ctx = AuthContext(user_id="u1", organization_id="org1", role=Role.MEMBER)
    allowed, _ = PermissionEvaluator.evaluate(
        context=ctx,
        action="read",
        resource_type="document",
        resource_org_id="org1"
    )
    assert allowed is True

    # Test Tenant isolation mismatch
    allowed_cross, reason = PermissionEvaluator.evaluate(
        context=ctx,
        action="read",
        resource_type="document",
        resource_org_id="org2"
    )
    assert allowed_cross is False
    assert "Tenant mismatch" in reason

def test_rate_limiter_sliding_window():
    allowed, count, retry_after = rate_limiter.is_allowed("test_user_key")
    assert allowed is True
    assert count >= 1

@pytest.mark.anyio
async def test_resilient_embedding_service():
    provider = OpenAIEmbeddingProvider(api_key="")
    service = ResilientEmbeddingService(providers=[provider], target_dimension=1536)
    embeddings = await service.embed_texts(["Atlas AI enterprise platform"])
    assert len(embeddings) == 1
    assert len(embeddings[0]) == 1536
