
from devops_support.agents.argocd_agent import ArgoCDCrew
from devops_support.knowledge.ingest import ArgoWebReader, WebReader
from devops_support.knowledge.query import QueryEngine
from devops_support.knowledge.vector_store import VectorStore
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding


class Orchestator:
    def __init__(self):
        Settings.llm = Ollama(model="phi:latest")
        Settings.embed_model = OllamaEmbedding(model_name="phi:latest")

    def run(self, query: str):
        """
        Run the orchestrator.
        """
        return self.run_argocd(query)
    
    def run_argocd(self, query: str):
        """
        Run the argocd crew.
        """      
        try:
            
            # Instantiate your WebReader and vector store object.
            reader_obj = ArgoWebReader()
            print(f"Reader object created. {reader_obj}")
            docs_reader = reader_obj.get_documents()
            vector_store = VectorStore("argocd_vector_store")
            # Create and initialize the QueryEngine.
            query_engine_instance = QueryEngine(vector_store, docs_reader)
            ArgoCDCrew.query_engine = query_engine_instance.get_query_engine()

            # Instantiate your crew
            argocd_crew_instance = ArgoCDCrew()
            crew = argocd_crew_instance.crew()

            # Pass the query input when starting the crew
            return crew.kickoff(inputs={"query": query})
        except Exception as e:
            raise Exception(f"An error occurred while running the crew: {e}")


