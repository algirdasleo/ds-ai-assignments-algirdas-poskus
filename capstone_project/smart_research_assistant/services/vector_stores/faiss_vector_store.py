import json
from pathlib import Path
from typing import Dict, List, Tuple

import faiss
import numpy as np
from sklearn.preprocessing import normalize
from smart_research_assistant.services.vector_stores.base import VectorStore
from smart_research_assistant.types.result.result import ErrorType, Result
from smart_research_assistant.types.vector_document import RelevantDocument

SAVE_PATH = Path(__file__).parents[2] / "rag_files"
SAVE_PATH.mkdir(parents=True, exist_ok=True)
SAVE_INDEX_PATH = Path(SAVE_PATH, "index.faiss")
SAVE_MAP_PATH = Path(SAVE_PATH, "id_to_doc.json")


class FaissVectorStore(VectorStore):
    def __init__(self, dimension: int):
        self.dimension: int = dimension
        self.index: faiss.IndexFlatIP = faiss.IndexFlatIP(dimension)
        self.id_to_doc: Dict[int, Tuple[str, int]] = {}
        self.next_id: int = 0

    def add(self, doc_id: str, embeddings: List[List[float]]) -> Result[None]:
        try:
            vectors = np.array(embeddings, dtype=np.float32)
            vectors = normalize(vectors, norm="l2", axis=1)
            if vectors.shape[1] != self.dimension:
                return Result.fail(
                    ErrorType.VECTOR_STORE_ERROR,
                    f"Embedding dimension mismatch: expected {self.dimension}, got {vectors.shape[1]}",
                )

            self.index.add(vectors)  # type: ignore

            new_ids = range(self.next_id, self.next_id + len(vectors))
            expanded_map = {i: (doc_id, i - self.next_id) for i in new_ids}
            self.id_to_doc.update(expanded_map)
            self.next_id += len(vectors)

            return Result.ok(None)
        except Exception as e:
            return Result.fail(ErrorType.VECTOR_STORE_ERROR, str(e))

    def search(self, prompt_embedding: List[float], top_k: int) -> Result[List[RelevantDocument]]:
        try:
            if len(prompt_embedding) != self.dimension:
                return Result.fail(
                    ErrorType.VECTOR_STORE_ERROR,
                    f"Expected dimension: {self.dimension}, received: {len(prompt_embedding)}",
                )

            vector = np.array(prompt_embedding, dtype=np.float32).reshape(1, -1)
            vector = normalize(vector, norm="l2", axis=1)
            distances, ids = self.index.search(vector, top_k)  # type: ignore

            results: List[RelevantDocument] = []
            for idx, dist in zip(ids[0], distances[0]):
                if idx == -1 or idx not in self.id_to_doc:
                    continue

                doc_id, chunk_idx = self.id_to_doc[idx]
                results.append(
                    RelevantDocument(
                        doc_id=doc_id,
                        chunk_id=chunk_idx,
                        similarity_score=float(dist),
                    )
                )

            return Result.ok(results)

        except Exception as e:
            return Result.fail(ErrorType.VECTOR_STORE_ERROR, str(e))

    def save(self) -> Result[None]:
        try:
            faiss.write_index(self.index, str(SAVE_INDEX_PATH))

            with open(SAVE_MAP_PATH, "w") as f:
                json.dump(self.id_to_doc, f)

            return Result.ok(None)
        except Exception as e:
            return Result.fail(ErrorType.VECTOR_STORE_ERROR, str(e))

    def load(self) -> Result[None]:
        try:
            self.index = faiss.read_index(str(SAVE_INDEX_PATH))

            with open(SAVE_MAP_PATH, "r") as file:
                self.id_to_doc = json.load(file)
                self.id_to_doc = {int(key): value for key, value in self.id_to_doc.items()}

            self.next_id = max(self.id_to_doc.keys()) + 1 if self.id_to_doc else 0

            return Result.ok(None)
        except Exception as e:
            return Result.fail(ErrorType.VECTOR_STORE_ERROR, str(e))

    def reset(self) -> Result[None]:
        self.index = faiss.IndexFlatIP(self.dimension)
        self.id_to_doc = {}
        self.next_id = 0
        self.save()
        return Result.ok(None)
