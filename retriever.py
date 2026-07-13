import os
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

embedder = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)


def retrieve(query: str, top_k: int = 6) -> str:
    """Retrieve the most relevant code snippets for a natural-language query.

    Encodes ``query`` into an embedding with the SentenceTransformer model,
    performs a vector similarity search against the ``devwhisper`` Qdrant
    collection, and formats the top matches into a human-readable context
    string. For each match it reports the source file, the detected function
    name (parsed from the first ``def`` line in the snippet), the starting
    line number, and the code itself.

    Args:
        query: The natural-language search query to find relevant code for.
        top_k: The maximum number of matching snippets to return. Defaults to 6.

    Returns:
        A newline-separated string containing the formatted results. Each
        result includes its rank, file path, function name, start line, and
        code block. Returns an empty string if no matches are found.
    """
    vector = embedder.encode(query).tolist()

    results = client.query_points(
        collection_name="devwhisper",
        query=vector,
        limit=top_k
    ).points

    structured_context = []

    for i, r in enumerate(results):
        payload = r.payload or {}

        file = payload.get("file", "unknown")
        start_line = payload.get("start_line", "?")
        code = payload.get("text", "")

        # Extract function name
        function_name = "unknown"
        for line in code.split("\n"):
            if line.strip().startswith("def "):
                function_name = line.strip().split("(")[0].replace("def ", "")
                break

        structured_context.append(
            f"""
Result {i+1}:
File: {file}
Function: {function_name}
Start Line: {start_line}

Code:
{code}
"""
        )

    return "\n\n".join(structured_context)