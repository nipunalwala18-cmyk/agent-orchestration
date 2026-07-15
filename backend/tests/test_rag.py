import os
from pathlib import Path

import pytest

os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("POSTGRES_DB", "testdb")
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from app.services.rag_service import RAGService


@pytest.fixture
def rag_service(tmp_path: Path) -> RAGService:
    return RAGService(storage_dir=tmp_path / "rag")


def test_upload_and_query_pdf(rag_service: RAGService) -> None:
    pdf_bytes = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT /F1 18 Tf 72 72 Td (AI orchestration guide) Tj ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f 
0000000010 00000 n 
0000000062 00000 n 
0000000119 00000 n 
0000000207 00000 n 
0000000304 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
0
%%EOF
"""

    uploaded = rag_service.upload_document(pdf_bytes, "sample.pdf")

    assert uploaded["document_id"]
    assert uploaded["source"] == "sample.pdf"

    result = rag_service.query("What does the document describe?", top_k=3)

    assert result["answer"]
    assert any("AI" in citation["source"] or "AI" in citation["text"] for citation in result["citations"])
