import json
from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff
import re

from devops_support.data.datadog_api import DatadogApi

###################
# Mock / Helpers
###################
def mock_datadog_api1(app_id: str, app_name: str) -> dict:
    return {
        "application_id": app_id,
        "application_name": app_name,
        "cpu_usage": "74%",
        "memory_usage": "512MB",
        "node_count": 3,
        "pod_health": {"running": 3, "pending": 1, "failed": 0},
        "timestamp": "2025-04-14 10:42:00"
    }

def mock_datadog_api(app_id: str, app_name: str) -> list[dict]:
    datadog_api = DatadogApi()
    logs_data = datadog_api.get_logs(app_name, 20)
    return logs_data


def parse_app_info(query: str) -> (str, str):
    app_id_match = re.search(r"(?i)app\s?id\s?(\d+)", query)
    app_name_match = re.search(r"(?i)app\s?name\s?(\w+)", query)

    app_id = app_id_match.group(1) if app_id_match else "N/A"
    app_name = app_name_match.group(1) if app_name_match else "UnknownApp"
    return app_id, app_name
    #return "app-002", "backend_service"

###################
# Main Crew Class
###################
@CrewBase
class DatadogCrew:

    @before_kickoff
    def prepare_inputs(self, inputs):
        # Modify inputs before the crew starts
        inputs['additional_data'] = "Some extra information"
        return inputs

    @after_kickoff
    def process_output(self, output):
        # Modify output after the crew finishes
        output.raw += "\nProcessed after kickoff."
        return output
    
    @agent
    def datadog_agent(self) -> Agent:
        """
        DatadogAgent:

        This agent processes raw Datadog infrastructure data based on an input query.
        The expected query should contain both the application id and name.
        The agent extracts the application id and name from the query, simulates retrieving the corresponding metrics (via a mock API),
        and produces a formatted report without speculation.
        """
        def handle_datadog_query(inputs: dict) -> str:
            query = inputs.get("query", "")
            app_id, app_name = parse_app_info(query)
            data = mock_datadog_api(app_id, app_name)   
            return data

        datadog_context_json = handle_datadog_query({"query": "can you check the status for appID app-002 with app name backend_service?"})
        datadog_context = json.dumps(datadog_context_json)
        backstory = "Specialized agent for retrieving and summarizing Datadog infrastructure metrics. It strictly uses provided data without adding any speculation. Input queries must include an app id and an app name.\nContext:: {}".format(datadog_context.replace('{', '{{').replace('}', '}}'))
        return Agent(
            role="DatadogAgent",
            backstory=backstory,
            goal="Answer questions related to Datadog metrics and analytics based on the input query that can be consumed by customers these might not have infrastructure knowlage.",
            verbose=True,
        )

    @agent
    def reporting_agent(self) -> Agent:
        """
        Agent that summarizes the raw DatadogAgent output provided as context. We provide a specialized prompt
        to ensure it doesn't invent or speculate on data that isn't there.
        """

        return Agent(
            role="ReportingAgent",
            backstory="Agent that summarizes or reports on Datadog data without adding speculation.",
            goal="Provide short, factual summaries of the given infrastructure data.",
            verbose=True,
        )

    @task
    def query_task(self) -> Task:
        """
        Query Task for Datadog Data:

        This task sends a query to the DatadogAgent and saves the report output in 'datadog_summary.md'.        
        The expected output is a detailed, raw Datadog infrastructure report based on the provided input query.
        """
        return Task(
            description="Answer the following query about Datadog: {query}",
            expected_output="Raw Datadog infrastructure report based on the input provided as context. provide insight about how the application is doing and any recommandation if applicable. No structure data.",
            agent=self.datadog_agent()
            #output_file='datadog_summary.md'
        )


    @task
    def summary_task(self) -> Task:
        return Task(
            description="Use the following Datadog response to create a summary: {query}",
            expected_output="A concise summary of the Datadog data how the given app is doing so that the app team or managers have good insight about the application and any recommandation if applicable. No structure data.",
            agent=self.reporting_agent(),
            context=[self.query_task()],
            output_file='datadog_summary.md'
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.datadog_agent(), self.reporting_agent()],
            tasks=[self.query_task(), self.summary_task()],
            process=Process.sequential,
            verbose=True
        )
