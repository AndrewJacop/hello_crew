from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from hello_world_crew.utils.helpers import *


@CrewBase
class HelloWorldCrew:
    """HelloWorldCrew crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["researcher"],
            verbose=True,
            # you can switch between different LLMs object such as the ones provided in the utils/helpers file
            llm=llm_openai_4m,
        )

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["reporting_analyst"],
            verbose=True,
            llm=llm_openai_4m,
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_task"],
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config["reporting_task"],
            output_file="report.md",
        )

    @crew
    def crew(self) -> Crew:
        """Creates the HelloWorld crew"""

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
