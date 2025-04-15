import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext

class VectorStore:
    def __init__(self, collection_name):
        self.collection_name = collection_name
        self.vector_store = None

    def initialize_vector_store(self):
        # Initialize Chroma client
        chroma_client = chromadb.Client()

        # Create a Chroma collection
        chroma_collection = chroma_client.create_collection(name=self.collection_name)

        # Set up the vector store
        self.vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    def get_vector_store(self):
        if self.vector_store is None:
            self.initialize_vector_store()
        return self.vector_store

    def get_storage_context(self):
        vector_store = self.get_vector_store()
        return StorageContext.from_defaults(vector_store=vector_store)
