# LLM Agent Evaluator 

## Project Description
An AI data analysis agent and evaluation platform that is inspired by the DeepLearning.AI course "Evaluating AI Agents"

### Agent Description
The agent defined in `src/data_analysis_agent/` will prompt GPT 4.0 mini to query data from a database (in this test case, just a file contained in `/data`), run an LLM analysis on the data, and then generate python code to build a visual representation of the data, all defined by user-input natural language

Each of these operations is defined in their own files in the `tools/` dir, and the order in which the tools are run in is decided by a LLM router as defined in the `run_agent()` method in `router.py`

### LLM Evaluator Description
In development

## How to run 
### Data Analysis Agent
 1) Optional: Instantiate a virtual environment with `python -m venv venv`
 2) Install Requirements: `pip install -r requirements.txt`
 3) Configure your openAI API key in helper.py (you will need tokens to run this)
 3) Nav to `./src/data_analysis_agent/`
 4) Run `python router.py <'your request'>` from the CLI

 eg. `python router.py 'Show me the code for graph of sales by store in Nov 2021, and tell me what trends you see.'`

### LLM Evaluator
In development

## Note
To protect my API key, I told git to stop tracking `helper.py` by running `git update-index --assume-unchanged .\src\data_analysis_agent\helper.py` from the CLI