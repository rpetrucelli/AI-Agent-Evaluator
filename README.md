# LLM Data Analysis Agent with Tracing and Evaluation

## Project Description
AI data analysis agent capable of querying a sales database, analyzing trends, and creating data visualizations.
Leverages OpenAI GPT-4o mini.

Tracing and observability is provided by Arize Phoenix, an open-source observability tool.

Inspired by the DeepLearning.AI course "Evaluating AI Agents".

### LLM Agent
The agent defined in `src/data_analysis_agent/` will call GPT-4o mini to execute one or more of the following actions:
- Query a database (currently a duckdb table loaded from the dataset in `src/data_analysis_agent/data/`)
- Run analysis on the data
- Generate python code to represent visualizations of the data
- Execute the code to create the visualizations

...all defined by user-input natural language

Each of these operations is defined in their own file contained in`src/data_analysis_agent/tools/`  
Tool execution is decided by the LLM router `run_agent()` in `src/data_analysis_agent/router.py`

### Agent Tracing
Arize Phoenix provides observability in a localhost server.  
This gives robust tracing of the agents behvavior and performance by logging:
- API & LLM calls
- Execution order
- Token usage
- Performance
- and more!

Once starting the server, the dashboard will be accessible via the link console logged at the end of each execution  
(It should be "http://localhost:6006/v1/traces")

### LLM Evaluator
Leveraging Phoenix and OpenInference Instrumentation, I have built out an agent evaluation suite using both LLM-as-a-Judge, and code-based eval approaches.  
The evaluation script `src/data_analysis_agent/run_eval.py/` will run a suite of test questions (contained in `eval/cases.py`) against the agent to evalute its behavior.  
Using LLM-as-a-Judge, GPT-4o mini will qualitatively evaluate the agents choice of tool calls, response clarity, and accuracy of generated SQL queries.  
Using code-based eval, we evaluate the correctness of any generated code, as well as the success of its execution

To improve efficiency and cost, I have configured tool evals to only execute if the agent called a given tool in the thread under test  

## How to run 
### Setup
1) Instantiate a virtual environment (optional): `python -m venv venv` 
2) Install requirements: `pip install -r requirements.txt`
3) Configure your OpenAI API key in `src/data_analysis_agent/helper.py` (you will need OpenAI tokens to run this)
4) `cd src/data_analysis_agent`

### Start Tracing
In a terminal window, run `phoenix serve`

### Run Agent
In a separate terminal window, run `python router.py`

You will be prompted, then just ask whatever you'd like!  
eg. `Generate a line graph of sales in December 2022 by store` or `What are the best performing products` or `Based on product performance, how can I increase overall sales?`, etc.

### Evaluate Agent
Run `python run_eval.py`  
This script will run a list of test prompts through the agent.  
All progress will be console logged, and all eval results will be visible on the phoenix dashboard!

## Note
To protect my API key, I stopped VCS tracing by running `git update-index --assume-unchanged .\src\data_analysis_agent\helper.py`