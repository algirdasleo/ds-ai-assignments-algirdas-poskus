from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase
import asyncio


class PrecisionAtK(BaseMetric):
    def __init__(self, k: int = 5, threshold: float = 0.5):
        self.k = k
        self.scores = []
        self.threshold = threshold

    async def a_measure(self, test_case: LLMTestCase, *args, **kwargs):
        if test_case.additional_metadata is None:
            raise ValueError("Test case must have additional metadata.")

        expected_ids = set(test_case.additional_metadata.get("expected_arxiv_ids", []))
        retrieved_ids = set(test_case.additional_metadata.get("retrieved_arxiv_ids", []))

        if not retrieved_ids:
            precision = 0.0
        else:
            count = len(expected_ids.intersection(retrieved_ids))
            precision = count / len(retrieved_ids)

        self.scores.append(precision)
        self.score = precision
        self.success = precision >= self.threshold
        self.reason = f"Precision@{self.k} = {precision:.3f}"

        await asyncio.sleep(2)

        return precision

    def measure(self, test_case: LLMTestCase):
        return asyncio.run(self.a_measure(test_case))

    def is_successful(self) -> bool:
        return hasattr(self, "success") and bool(self.success)

    def get_result(self):
        if not self.scores:
            return 0.0
        return sum(self.scores) / len(self.scores)

    @property
    def name(self) -> str:
        return f"Precision@{self.k}"
