from typing import List
from pydantic import BaseModel
from crewai import Agent, Crew
from crewai.tasks.conditional_task import ConditionalTask
from crewai.tasks.task_output import TaskOutput
from crewai.task import Task
from crewai_tools import SerperDevTool
from utils.helpers import *


# Define a condition function for the conditional task
# If false, the task will be skipped, if true, then execute the task.
def is_data_missing(output: TaskOutput) -> bool:
    return len(output.pydantic.events) < 10  # this will skip this task


# Define the agents
data_fetcher_agent = Agent(
    role="Data Fetcher",
    goal="Fetch data online using Serper tool",
    backstory="Backstory 1",
    verbose=True,
    tools=[SerperDevTool()],
)

data_processor_agent = Agent(
    role="Data Processor",
    goal="Process fetched data",
    backstory="Backstory 2",
    verbose=True,
    llm=llm_openai_4m,
)

summary_generator_agent = Agent(
    role="Summary Generator",
    goal="Generate summary from fetched data",
    backstory="Backstory 3",
    verbose=True,
    llm=llm_openai_4m,
)


class EventOutput(BaseModel):
    events: List[str]


task1 = Task(
    description="Fetch data about events in San Francisco using Serper tool",
    expected_output="List of 10 things to do in SF this week",
    agent=data_fetcher_agent,
    output_pydantic=EventOutput,
)

conditional_task = ConditionalTask(
    description="""
        Check if data is missing. If we have less than 10 events,
        fetch more events using Serper tool so that
        we have a total of 10 events in SF this week..
        """,
    expected_output="List of 10 Things to do in SF this week",
    condition=is_data_missing,
    agent=data_processor_agent,
)

task3 = Task(
    description="Generate summary of events in San Francisco from fetched data",
    expected_output="A complete report on the customer and their customers and competitors, including their demographics, preferences, market positioning and audience engagement.",
    agent=summary_generator_agent,
)

# Create a crew with the tasks
crew = Crew(
    agents=[data_fetcher_agent, data_processor_agent, summary_generator_agent],
    tasks=[task1, conditional_task, task3],
    verbose=True,
    planning=True,
)

# Run the crew
result = crew.kickoff()
print("results", result)

# from crewai import Agent, Crew, Process, Task
# from crewai.tasks.conditional_task import ConditionalTask
# from crewai.tasks.task_output import TaskOutput
# from utils.helpers import *


# # Your functions
# def some_llm_function():
#     pass


# def some_tool_function():
#     pass


# # Group your functions by type
# agent_functions = {
#     "llms": {"my_llm": some_llm_function},
#     "tools": {"my_tool": some_tool_function},
#     "cache_handlers": {},
#     "callbacks": {},
#     "agents": {},
# }

# task_functions = {
#     "agents": {},
#     "tasks": {},
#     "output_json": {},
#     "tools": {"my_tool": some_tool_function},
#     "callbacks": {},
#     "output_pydantic": {},
# }

# # Load and process configurations
# base_dir = Path(__file__).parent
# agents_config, tasks_config = load_and_process_configurations(
#     base_directory=base_dir,
#     agents_config_path="config/agents.yaml",
#     tasks_config_path="config/tasks.yaml",
#     agent_functions=agent_functions,
#     task_functions=task_functions,
# )


# def is_not_valid(output: TaskOutput) -> bool:
#     print(output.raw)
#     return int(output.raw) < 5


# researcher = Agent(
#     config=agents_config["researcher"],
#     verbose=True,
#     llm=llm_openai_4m,
# )


# reporting_analyst = Agent(
#     config=agents_config["reporting_analyst"],
#     verbose=True,
#     llm=llm_openai_4m,
# )


# research_task = Task(
#     config=tasks_config["research_task"],
#     agent=researcher,
# )


# validation_task = Task(
#     config=tasks_config["validation_task"],
#     agent=reporting_analyst,
# )


# reporting_task = ConditionalTask(
#     condition=is_not_valid,
#     config=tasks_config["reporting_task"],
#     context=[research_task],
#     agent=reporting_analyst,
#     output_file="report.md",
# )

# myCrew = Crew(
#     agents=[researcher, reporting_analyst],
#     tasks=[research_task, validation_task, reporting_task],
#     process=Process.sequential,
#     verbose=True,
# )

# result = myCrew.kickoff()
# print(result)
