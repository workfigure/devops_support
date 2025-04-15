import json
from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff
import re
import datetime

from devops_support.data.splunk_api import SplunkApi

###################
# Mock / Helpers
###################
def mock_splunk_api(app_id: str, app_name: str) -> list[dict]:
    splunk_api = SplunkApi()
    logs_data = splunk_api.get_logs(app_name, 20)
    return logs_data


def parse_app_info(query: str) -> (str, str):
    app_id_match = re.search(r"(?i)app\s?id\s?(\d+)", query)
    app_name_match = re.search(r"(?i)app\s?name\s?(\w+)", query)

    app_id = app_id_match.group(1) if app_id_match else "N/A"
    app_name = app_name_match.group(1) if app_name_match else "UnknownApp"
    #return app_id, app_name
    return "7", "AuthService"

###################
# Main Crew Class
###################
@CrewBase
class SplunkCrew:
    """Crew for analyzing Splunk log data using the latest CrewAI version."""

    @before_kickoff
    def prepare_inputs(self, inputs: dict) -> dict:
        # Add additional context/data before the crew execution starts
        inputs['additional_data'] = "Extra data for Splunk analysis"
        return inputs

    @after_kickoff
    def process_output(self, output) -> any:
        # Append post-processing information to the raw output
        output.raw += "\nProcessed Splunk report after kickoff."
        return output

    @agent
    def splunk_agent(self) -> Agent:
        def handle_splunk_query(inputs: dict) -> str:
            query = inputs.get("query", "")
            app_id, app_name = parse_app_info(query)
            data = mock_splunk_api(app_id, app_name)   
            return data

        splunk_context_json = handle_splunk_query({"query": "can you check the status for application AuthService?"})
        splunk_context = json.dumps(splunk_context_json)
        backstory = "Agent specialized in analyzing Splunk logs for applications. It strictly uses provided data without adding any speculation.\nContext:: {}".format(splunk_context.replace('{', '{{').replace('}', '}}'))
        print(f"Splunk context: {backstory}")
        return Agent(
            role="SplunkAgent",
            backstory=backstory,
            goal="Provide detailed Splunk log analytics and insights.",
            handle=handle_splunk_query,
            verbose=True,
        )

    @agent
    def reporting_agent(self) -> Agent:
        return Agent(
            role="ReportingAgent",
            backstory="Summarizes detailed Splunk logs into concise reports.",
            goal="Generate concise, factual summaries from Splunk log analysis.",
            verbose=True,
        )

    @task
    def query_task(self) -> Task:
        return Task(
            description="Answer the following query about Splunk logs: {query}",
            expected_output="Detailed Splunk log analysis.",
            agent=self.splunk_agent()
            #output_name="splunk_response"
        )

    @task
    def summary_task(self) -> Task:
        return Task(
            description="Create a concise summary using this Splunk analysis: {query}",
            expected_output="Concise summary report.",
            agent=self.reporting_agent(),
            context=[self.query_task()],
            output_file='splunk_summary.md'
        )

    @crew
    def crew(self) -> Crew:
        # Create the crew with a sequential process using the defined agents and tasks
        return Crew(
            agents=[self.splunk_agent(), self.reporting_agent()],
            tasks=[self.query_task(), self.summary_task()],
            process=Process.sequential,
            verbose=True,
        )
    