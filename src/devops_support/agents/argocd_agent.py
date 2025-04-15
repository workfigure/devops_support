from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, task, crew
from crewai_tools import LlamaIndexTool
from pydantic import PrivateAttr
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class ArgoCDAgentWithLogging(Agent):
    _query_history: list = PrivateAttr(default_factory=list)
    _log_file: str = PrivateAttr(default=None)

    def __init__(self, *args, log_file=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._log_file = log_file

    def _log(self, query: str, answer: str) -> str:
        self._query_history.append({"query": query, "answer": answer})
        if self._log_file:
            try:
                with open(self._log_file, 'a', encoding='utf-8') as f:
                    f.write(f"Q: {query}\nA: {answer}\n---\n")
            except Exception as e:
                print(f"Logging error: {e}")
        return answer

    def run(self, query: str) -> str:
        answer = super().run(query)
        return self._log(query, answer)

    def reset_conversation(self):
        if hasattr(self, 'memory') and self.memory:
            self.memory.clear()
        self._query_history = []

@CrewBase
class ArgoCDCrew:
    """
    Crew for handling ArgoCD Q&A tasks.
    
    The crew uses an externally provided QueryEngine instance to initialize its LlamaIndexTool.
    The QueryEngine must be assigned to the class attribute `query_engine_obj` before the crew is kicked off.
    """
    # This attribute must be set externally to an instance of QueryEngine
    query_engine = None

    @agent
    def argocd_agent(self) -> Agent:
        """
        Creates an ArgoCD agent that uses the external QueryEngine.
        """
        if not self.query_engine:
            raise ValueError("QueryEngine instance not provided. Please assign one to ArgoCDCrew.query_engine_obj")
        
        # Retrieve the query engine from the external QueryEngine object.
        query_engine = self.query_engine
        
        # Wrap the query engine using LlamaIndexTool.
        query_tool = LlamaIndexTool.from_query_engine(
            query_engine,
            name="ArgoCD_DocSearch",
            description="Tool to query ArgoCD documentation."
        )
        
        return ArgoCDAgentWithLogging(
            role="ArgoCD Documentation Expert",
            goal=("Answer queries about ArgoCD using its official documentation. "
                  "Provide detailed, formatted Markdown responses."),
            backstory=("You are an expert in ArgoCD documentation. You support follow-up questions with context "
                       "and log all interactions for traceability."),
            tools=[query_tool],
            memory=True,
            log_file="argocd_agent.log"  # Update the path as needed
        )

    @task
    def query_task(self) -> Task:
        """
        Define a task for processing a user query about ArgoCD.
        """
        return Task(
            description="Answer the following query about ArgoCD: {query}",
            expected_output="Provide a Markdown answer with examples and code blocks.",
            agent=self.argocd_agent()  # ✅ bind the task to the agent
        )

    @crew
    def crew(self) -> Crew:
        """
        Assemble the crew from the defined agents and tasks.
        """
        return Crew(
            agents=self.agents,  # Collected automatically via the @agent decorator
            tasks=self.tasks,    # Collected automatically via the @task decorator
            process=Process.sequential,
            verbose=True,
            output_log_file = True
        )
