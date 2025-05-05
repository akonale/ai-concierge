import asyncio

import chromadb
from sentence_transformers import SentenceTransformer # Import sentence transformer

async def main():
    chroma_client = await chromadb.AsyncHttpClient(host='localhost', port=8000)

    collection = await chroma_client.get_collection(name='experiences')
    # Add documents to the collection
    # await collection.add(
    #     documents=[
    #         "This is a document about pineapple",
    #         "This is a document about oranges"
    #     ],
    #     ids=["id1", "id2"]
    # )
    # Query the collection
#    results = await collection.count()
    EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    message = "Amsterdam things to do";
    query_embedding = embedding_model.encode(message).tolist()
    
    results = await collection.query(
        query_embeddings=query_embedding,
    n_results=10,
    include=['metadatas', 'documents', 'distances'])

    print(results)

asyncio.run(main())