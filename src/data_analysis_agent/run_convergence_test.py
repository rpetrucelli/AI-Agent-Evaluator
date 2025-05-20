import warnings
warnings.filterwarnings('ignore')

import phoenix as px
from phoenix.experiments import run_experiment, evaluate_experiment
from phoenix.experiments.types import Example
from phoenix.experiments.evaluators import create_evaluator
import pandas as pd
from datetime import datetime

from router import run_agent
from eval.cases import convergence_questions

import nest_asyncio
nest_asyncio.apply()

# Firstly create a dataset of test cases
px_client = px.Client()


convergence_df = pd.DataFrame({
    'question': convergence_questions
})

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
dataset = px_client.upload_dataset(dataframe=convergence_df, dataset_name=f"convergence_questions-{now}", input_keys=["question"])

## Write the eval task
# Format the output of the agent to be a readable string
def format_message_steps(messages):
    """
    Convert a list of message objects into a readable format that shows the steps taken.

    Args:
        messages (list): A list of message objects containing role, content, tool calls, etc.

    Returns:
        str: A readable string showing the steps taken.
    """
    steps = []
    for message in messages:
        role = message.get("role")
        if role == "user":
            steps.append(f"User: {message.get('content')}")
        elif role == "system":
            steps.append("System: Provided context")
        elif role == "assistant":
            if message.get("tool_calls"):
                for tool_call in message["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    steps.append(f"Assistant: Called tool '{tool_name}'")
            else:
                steps.append(f"Assistant: {message.get('content')}")
        elif role == "tool":
            steps.append(f"Tool response: {message.get('content')}")
    
    return "\n".join(steps)

# Define the function to run the agent and track the path
def run_agent_and_track_path(example: Example) -> str:
    messages = [{"role": "user", "content": example.input.get("question")}]
    ret = run_agent(messages)
    # If ret is a string, wrap it as a message dict
    if isinstance(ret, str):
        ret = [{"role": "assistant", "content": ret}]
    return {"path_length": len(ret), "messages": format_message_steps(ret)}


## Run the experiment to create a dataframe of the results
experiment = run_experiment(
    dataset,
    run_agent_and_track_path,
    experiment_name="Convergence Eval",
    experiment_description="Evaluating the convergence of the agent"
)
print("\nExperiment Dataframe\n" + experiment.as_dataframe().to_string() + "\n")


## Evaluate the path
outputs = experiment.as_dataframe()["output"].to_dict().values()

# Calculate the optimal path (Will include the user and system messages)
optimal_path_length = min(output.get('path_length') for output in outputs if output and output.get('path_length') is not None)
print(f"\nThe optimal path length is {optimal_path_length}\n")

# Create an evaluator to evaluate the path length
# The evaluator will return the ratio of the optimal path length to the actual path length
@create_evaluator(name="Convergence Eval", kind="CODE")
def evaluate_path_length(output: str) -> float:
    if output and output.get("path_length"):
        return optimal_path_length/float(output.get("path_length"))
    else:
        return 0

# Pass the experiment through the evaluator
experiment = evaluate_experiment(experiment, evaluators=[evaluate_path_length])