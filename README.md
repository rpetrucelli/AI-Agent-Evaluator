# LLM Agent & Evaluator 

## Project Description
An AI data analysis agent capable of querying a dataset, analyzing for trends, and creating visualizations of data from user-defined parameters.

Tracing and observability is provides by Arize Phoenix, and open-source observability tool

Inspired by the DeepLearning.AI course "Evaluating AI Agents"

### LLM Agent Description
The agent defined in `src/data_analysis_agent/` will prompt GPT 4.0 mini to execute one or more of the following actions:
- Query a database (in this test case, just a file contained in `/data`), 
- Run analysis on the data
- Generate python code to build a visual representation of the data
- Execute code to create visualizations

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
 1) Instantiate a virtual environment with `python -m venv venv` (optional)
 2) Install Requirements with `pip install -r requirements.txt`
 3) Configure your openAI API key in `src/data_analysis_agent/helper.py` (you will need OpenAI tokens to run this)

### LLM Evaluator
In a terminal window, run `phoenix serve`  
This starts a server which runs the tracing dashboard on your localhost

### Data Analysis Agent
In a separate terminal window, run `python ./src/data_analysis_agent/router.py` from the CLI
You will be prompted, ask whatever you'd like!

eg. `Generate a line graph of sales in December 2022 by store` or `What are the best performing products` or `Based on product performance, how can I increase my overall sales?`, etc.

## Note
To protect my API key, I stop vcs tracing of `helper.py` by running `git update-index --assume-unchanged .\src\data_analysis_agent\helper.py` from the CLI