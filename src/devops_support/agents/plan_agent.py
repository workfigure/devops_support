from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, task, crew
import logging


@CrewBase
class PlanningCrew:
     
    def _handle_planning_query(self, query: str, context: dict[str, any]) -> str:
        """Handle a planning query using the PlanningAgent (creating a multi-step action plan)."""
        session_id = context.get("session_id", "")
        # Create a PlanningAgent focused on strategic multi-step solutions
        planning_agent = Agent(
            role="PlanningAgent",
            goal="Develop a step-by-step plan to address complex issues or achieve the user's goal"
        )
        # Incorporate known context (issue or app info) into the plan prompt
        issue_description = ""
        if "previous_diagnosis" in context:
            issue_description = f"The known issue is: {context['previous_diagnosis']}. "
        elif "app_metadata" in context:
            app_meta = context["app_metadata"]
            issue_description = (f"Plan for application {app_meta['app_name']} (version {app_meta['version']} "
                                 f"in {app_meta['env']} environment). ")
        task_description = issue_description + "Provide a detailed plan with multiple steps to address the user's request or problem."
        planning_task = Task(
            description=task_description,
            expected_output="A numbered list of actionable steps to resolve the issue or achieve the goal, with reasoning.",
            agent=planning_agent
        )
        planning_crew = Crew(
            agents=[planning_agent],
            tasks=[planning_task],
            process=Process.sequential,
            verbose=False
        )
        result = planning_crew.kickoff()
        plan = str(result)
        # Save the plan in memory for future reference
        if session_id:
            mem = self.session_memory.get(session_id, {})
            mem["plan"] = plan
            self.session_memory[session_id] = mem
        return plan