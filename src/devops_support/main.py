#!/usr/bin/env python
import json
import sys
import warnings

from datetime import datetime
import weave
from devops_support.agents.datadog_agent import DatadogCrew
from devops_support.agents.splunk_agent import SplunkCrew
from devops_support.crews.crew import DevopsResearch
from devops_support.orchestrator.orchestrator import Orchestator

#warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information


def run():
    """
    Run the crew.
    """
    query = "can you check the status for application AuthService?"
    
    try:
        crew_instance = SplunkCrew().crew()
        crew_instance.kickoff(inputs={"query": query})
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

def run_datadog():
    """
    Run the crew.
    """
    query = "can you check the status for appID app-002 with app name backend_service?"
    
    try:
        # Initialize Weave with your project name
        #weave.init(project_name="crewai")
        crew_instance = DatadogCrew().crew()
        crew_instance.kickoff(inputs={"query": query})
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")
    
def run2():
    try:
        #"What are the best practices for setting up ArgoCD?"
        Orchestator().run(query="I want to list steps to set up ArgoCD in EKS cluster.")
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")
    
def run1():
    """
    Run the crew.
    """
    inputs = {
        'topic': 'AI LLMs',
        'current_year': str(datetime.now().year)
    }
    
    try:
        DevopsResearch().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        DevopsResearch().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        DevopsResearch().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    try:
        DevopsResearch().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
