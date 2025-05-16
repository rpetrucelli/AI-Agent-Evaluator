# LLM Agent & Evaluator 

## Project Description
An AI data analysis agent capable of querying a sales datasbase, analyzing for trends, and creating visualizations of data, all from a user prompt.

Tracing and observability is provided by Arize Phoenix, an open-source observability tool.

Inspired by the DeepLearning.AI course "Evaluating AI Agents"

### LLM Agent Description
The agent defined in `src/data_analysis_agent/` will prompt GPT 4.0 mini to execute one or more of the following actions:
- Query a database (currently just a duckdb table created from the dataset from `src/data_analysis_agent/data`), 
- Run analysis on the data
- Generate python code to represent visualizations of the data
- Execute the code to create the visualizations, if asked

...all defined by user-input natural language

Each of these operations is defined in their own files in the `src/data_analysis_agent/tools/` dir.  
The tool execution order is decided by the LLM router defined in the `run_agent()` method of `src/data_analysis_agent/router.py`

### LLM Evaluator Description
Arize Phoenix provides all observability tracing in a localhost server.
This provides robust tracing of the agents behvavior and performance by logging:
- Tool & LLM calls
- Execution order
- Token usage
- Performance
- and more!

Once starting the server, the dashboard will be accessible via the link console logged at the end of each execution (it should be "http://localhost:6006/v1/traces")

## How to run 
### Setup
1) Instantiate a virtual environment (optional): `python -m venv venv` 
2) Install Requirements: `pip install -r requirements.txt`
3) Configure your openAI API key in `src/data_analysis_agent/helper.py` (you will need tokens to run this)

### LLM Evaluator
In a terminal window, run `phoenix serve`  
This starts a server that runs the tracing dashboard on your localhost

### Data Analysis Agent
In a separate terminal window, run `python ./src/data_analysis_agent/router.py` from the CLI
You will be prompted, then just ask whatever you'd like!

eg. `Generate a line graph of sales in December 2022 by store` or `What are the best performing products` or `Based on product performance, how can I increase overall sales?`, etc.

## Note
To protect my API key, I stop vcs tracing of `helper.py` by running `git update-index --assume-unchanged .\src\data_analysis_agent\helper.py` from the CLI