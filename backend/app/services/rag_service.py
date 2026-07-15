import json
import re
import uuid
from io import BytesIO
from pathlib import Path
from typing import Any


class RAGService:
    """A lightweight local RAG service for indexing uploaded PDFs and answering questions."""

    def __init__(self, storage_dir: str | Path | None = None) -> None:
        self.storage_dir = Path(storage_dir or Path(__file__).resolve().parents[1] / "storage" / "rag")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.storage_dir / "index.json"
        self.documents: list[dict[str, Any]] = self._load_documents()

    def _load_documents(self) -> list[dict[str, Any]]:
        if not self.index_path.exists():
            return []
        try:
            with self.index_path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except json.JSONDecodeError:
            return []

    def _save_documents(self) -> None:
        with self.index_path.open("w", encoding="utf-8") as handle:
            json.dump(self.documents, handle, indent=2)

    def _extract_text(self, file_bytes: bytes, filename: str) -> str:
        if filename.lower().endswith(".pdf"):
            try:
                from pypdf import PdfReader
            except ImportError:
                PdfReader = None

            if PdfReader is not None:
                try:
                    reader = PdfReader(BytesIO(file_bytes))
                    pages = [page.extract_text() or "" for page in reader.pages]
                    text = "\n".join(pages).strip()
                    if text:
                        return text
                except Exception:
                    pass

            try:
                decoded = file_bytes.decode("utf-8", errors="ignore")
            except Exception:
                decoded = ""

            matches = re.findall(r"[A-Za-z0-9][A-Za-z0-9 .,_:/()\\-]{2,}", decoded)
            return "\n".join(matches).strip()

        return file_bytes.decode("utf-8", errors="ignore").strip()

    def _chunk_text(self, text: str, chunk_size: int = 480, overlap: int = 80) -> list[str]:
        normalized = re.sub(r"\s+", " ", text).strip()
        if not normalized:
            return []

        chunks: list[str] = []
        start = 0
        while start < len(normalized):
            end = min(len(normalized), start + chunk_size)
            chunk = normalized[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end >= len(normalized):
                break
            start = max(0, end - overlap)
        return chunks

    def _similarity(self, question: str, chunk_text: str) -> float:
        question_tokens = {token for token in re.findall(r"\w+", question.lower()) if token}
        chunk_tokens = {token for token in re.findall(r"\w+", chunk_text.lower()) if token}
        if not question_tokens:
            return 0.0
        overlap = len(question_tokens & chunk_tokens)
        return overlap + (0.15 if any(token in chunk_text.lower() for token in question_tokens) else 0.0)

    def upload_document(self, file_bytes: bytes, filename: str) -> dict[str, Any]:
        text = self._extract_text(file_bytes, filename)
        chunks = self._chunk_text(text)

        document_id = str(uuid.uuid4())
        stored_path = self.storage_dir / f"{document_id}-{Path(filename).name}"
        stored_path.write_bytes(file_bytes)

        document = {
            "id": document_id,
            "source": filename,
            "stored_path": str(stored_path),
            "chunks": [
                {
                    "id": f"{document_id}-chunk-{index}",
                    "text": chunk,
                    "chunk_index": index,
                }
                for index, chunk in enumerate(chunks)
            ],
        }
        self.documents.append(document)
        self._save_documents()

        return {
            "document_id": document_id,
            "source": filename,
            "chunk_count": len(document["chunks"]),
        }

    def query(self, question: str, top_k: int = 3) -> dict[str, Any]:
        if not question.strip():
            return {"answer": "Please provide a question.", "citations": []}

        if not self.documents:
            return {"answer": "No documents have been uploaded yet.", "citations": []}

        scored_chunks: list[dict[str, Any]] = []
        for document in self.documents:
            for chunk in document["chunks"]:
                score = self._similarity(question, chunk["text"])
                if score > 0:
                    scored_chunks.append(
                        {
                            "score": score,
                            "source": document["source"],
                            "text": chunk["text"],
                            "chunk_index": chunk["chunk_index"],
                        }
                    )

        scored_chunks = sorted(scored_chunks, key=lambda item: item["score"], reverse=True)
        if not scored_chunks:
            fallback_chunks = [
                {
                    "score": 0.0,
                    "source": document["source"],
                    "text": document["chunks"][0]["text"],
                    "chunk_index": document["chunks"][0]["chunk_index"],
                }
                for document in self.documents
            ]
            scored_chunks = fallback_chunks[:top_k]
        else:
            scored_chunks = scored_chunks[:top_k]

        best_chunk = scored_chunks[0]
        answer = (
            f"Based on the uploaded content, the strongest match suggests: {best_chunk['text'][:260]}"
        )

        citations = [
            {
                "source": item["source"],
                "chunk_index": item["chunk_index"],
                "text": item["text"],
                "score": round(item["score"], 2),
            }
            for item in scored_chunks
        ]
        return {"answer": answer, "citations": citations}
