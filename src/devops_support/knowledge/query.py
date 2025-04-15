from llama_index.core import VectorStoreIndex

class QueryEngine:
    def __init__(self, vector_store, documents):
        self.documents = documents
        self.vector_store = vector_store
        self.query_engine = None

    def initialize_query_engine(self):
        # Create a storage context from the vector store
        storage_context = self.vector_store.get_storage_context()

        # Create an index from the documents using the new import path
        index = VectorStoreIndex.from_documents(
            self.documents, 
            storage_context=storage_context)

        # Create a query engine from the index
        self.query_engine = index.as_query_engine()

    def get_query_engine(self):
        if self.query_engine is None:
            self.initialize_query_engine()
        return self.query_engine
