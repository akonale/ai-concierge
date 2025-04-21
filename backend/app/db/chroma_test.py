import asyncio

import chromadb

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
    results = await collection.count()
    print(results)

asyncio.run(main())