import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "apps", "api"))

import asyncio
from app.services.llm_client import llm_client
from app.models.paper import Paper

async def main():
    papers = [
        Paper(
            id="W2963403868",
            title="Attention Is All You Need",
            year=2017,
            abstract="We propose the Transformer, a model architecture eschewing recurrence and instead relying entirely on an attention mechanism to draw global dependencies between input and output.",
            citation_count=100000,
            source_num=1,
        ),
        Paper(
            id="W3015467442",
            title="Longformer: The Long-Document Transformer",
            year=2020,
            abstract="Transformers are unable to process long sequences due to their quadratic scaling with sequence length. We present Longformer with an attention mechanism that scales linearly with sequence length.",
            citation_count=5000,
            source_num=2,
        )
    ]
    print("Testing live Gemini streaming generation...\n---")
    token_count = 0
    async for token in llm_client.stream_review("Efficient attention mechanisms in Transformers", papers):
        print(token, end="", flush=True)
        token_count += 1
    print(f"\n---\nStream finished successfully! Chunks received: {token_count}")

if __name__ == "__main__":
    asyncio.run(main())
