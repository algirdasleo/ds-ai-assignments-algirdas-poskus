from smart_research_assistant.evaluation.evaluate import run_generate_evaluation, run_rag_evaluation
import asyncio


async def main():
    rag_eval = await run_rag_evaluation()
    if rag_eval.is_success():
        print("\n\nRAG Evaluation completed successfully!")
    else:
        print(f"Failed to evaluate RAG pipeline: {rag_eval.error_message}")

    generation_eval = await run_generate_evaluation()
    if generation_eval.is_success():
        print("\n\nGeneration Evaluation completed successfully!")
    else:
        print(f"Failed to evaluate Generate pipeline: {generation_eval.error_message}")


if __name__ == "__main__":
    asyncio.run(main())
