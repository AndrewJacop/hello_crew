# Import necessary modules
from dotenv import load_dotenv
import os
from crewai import LLM
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List

# Load environment variables from .env file
load_dotenv()

llm_openai_4m = LLM(
    model=os.getenv("OPENAI_MODEL"),
    temperature=0.0,
    api_key=os.getenv("OPENAI_API_KEY"),
)

llm_deepseek_v3 = LLM(
    model=os.getenv("DEEPSEEK_MODEL"),
    temperature=0.0,
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)

llm_nemo = LLM(
    model=os.getenv("OPTOGPT_MODEL_NEMO"),
    base_url=os.getenv("OPTOGPT_BASE_URL"),
    api_key=os.getenv("OPTOGPT_API_KEY"),
)

llm_deepseek_r1 = LLM(
    model=os.getenv("OPTOGPT_MODEL_R1"),
    base_url=os.getenv("OPTOGPT_BASE_URL"),
    api_key=os.getenv("OPTOGPT_API_KEY"),
)


def load_yaml(config_path: Path) -> Dict[str, Any]:
    """Load and parse a YAML configuration file."""
    try:
        with open(config_path, "r", encoding="utf-8") as file:
            content = yaml.safe_load(file)
            return content if isinstance(content, dict) else {}
    except FileNotFoundError:
        print(f"File not found: {config_path}")
        raise


def map_agent_variables(
    agent_name: str, agent_info: Dict[str, Any], agent_functions: Dict[str, Dict[str, Callable]], agents_config: Dict[str, Any]
) -> None:
    """Map agent variables to their corresponding functions."""
    llms = agent_functions.get("llms", {})
    tool_functions = agent_functions.get("tools", {})
    cache_handler_functions = agent_functions.get("cache_handlers", {})
    callbacks = agent_functions.get("callbacks", {})
    agents = agent_functions.get("agents", {})

    if llm := agent_info.get("llm"):
        try:
            agents_config[agent_name]["llm"] = llms[llm]()
        except KeyError:
            agents_config[agent_name]["llm"] = llm

    if tools := agent_info.get("tools"):
        agents_config[agent_name]["tools"] = [tool_functions[tool]() for tool in tools]

    if function_calling_llm := agent_info.get("function_calling_llm"):
        agents_config[agent_name]["function_calling_llm"] = agents[function_calling_llm]()

    if step_callback := agent_info.get("step_callback"):
        agents_config[agent_name]["step_callback"] = callbacks[step_callback]()

    if cache_handler := agent_info.get("cache_handler"):
        agents_config[agent_name]["cache_handler"] = cache_handler_functions[cache_handler]()


def map_task_variables(
    task_name: str, task_info: Dict[str, Any], task_functions: Dict[str, Dict[str, Callable]], tasks_config: Dict[str, Any]
) -> None:
    """Map task variables to their corresponding functions."""
    agents = task_functions.get("agents", {})
    tasks = task_functions.get("tasks", {})
    output_json_functions = task_functions.get("output_json", {})
    tool_functions = task_functions.get("tools", {})
    callback_functions = task_functions.get("callbacks", {})
    output_pydantic_functions = task_functions.get("output_pydantic", {})

    if context_list := task_info.get("context"):
        tasks_config[task_name]["context"] = [tasks[context_task_name]() for context_task_name in context_list]

    if tools := task_info.get("tools"):
        tasks_config[task_name]["tools"] = [tool_functions[tool]() for tool in tools]

    if agent_name := task_info.get("agent"):
        tasks_config[task_name]["agent"] = agents[agent_name]

    if output_json := task_info.get("output_json"):
        tasks_config[task_name]["output_json"] = output_json_functions[output_json]

    if output_pydantic := task_info.get("output_pydantic"):
        tasks_config[task_name]["output_pydantic"] = output_pydantic_functions[output_pydantic]

    if callbacks := task_info.get("callbacks"):
        tasks_config[task_name]["callbacks"] = [callback_functions[callback]() for callback in callbacks]


def load_and_process_configurations(
    base_directory: Path,
    agents_config_path: str,
    tasks_config_path: str,
    agent_functions: Dict[str, Dict[str, Callable]],
    task_functions: Dict[str, Dict[str, Callable]],
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Load and process both agent and task configurations with explicitly provided functions.

    Args:
        base_directory: Base directory containing config files
        agents_config_path: Path to agents config file
        tasks_config_path: Path to tasks config file
        agent_functions: Dictionary containing all agent-related functions grouped by type
            {
                'llms': {name: function, ...},
                'tools': {name: function, ...},
                'cache_handlers': {name: function, ...},
                'callbacks': {name: function, ...},
                'agents': {name: function, ...}
            }
        task_functions: Dictionary containing all task-related functions grouped by type
            {
                'agents': {name: function, ...},
                'tasks': {name: function, ...},
                'output_json': {name: function, ...},
                'tools': {name: function, ...},
                'callbacks': {name: function, ...},
                'output_pydantic': {name: function, ...}
            }

    Returns:
        tuple[Dict[str, Any], Dict[str, Any]]: Processed agents and tasks configurations
    """
    # Load raw configurations
    agents_config = {}
    tasks_config = {}

    # Load agents configuration
    if agents_config_path:
        full_agents_path = base_directory / agents_config_path
        try:
            agents_config = load_yaml(full_agents_path)
        except FileNotFoundError:
            logging.warning(f"Agent config file not found at {full_agents_path}. " "Proceeding with empty agent configurations.")

    # Load tasks configuration
    if tasks_config_path:
        full_tasks_path = base_directory / tasks_config_path
        try:
            tasks_config = load_yaml(full_tasks_path)
        except FileNotFoundError:
            logging.warning(f"Task config file not found at {full_tasks_path}. " "Proceeding with empty task configurations.")

    # Process agents configuration
    for agent_name, agent_info in agents_config.items():
        map_agent_variables(agent_name, agent_info, agent_functions, agents_config)

    # Process tasks configuration
    for task_name, task_info in tasks_config.items():
        map_task_variables(task_name, task_info, task_functions, tasks_config)

    return agents_config, tasks_config
