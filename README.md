# LLM Agent & Evaluator 

## Project Description
An AI data analysis agent capable of querying a dataset, analyzing for trends, and creating visualizations of data from user-defined parameters

Inspired by the DeepLearning.AI course "Evaluating AI Agents"

### LLM Agent Description
The agent defined in `src/data_analysis_agent/` will prompt GPT 4.0 mini to execute one or more of the following actions:
- Query data from a database (in this test case, just a file contained in `/data`), 
- Run an analysis on the data
- Generate python code to build a visual representation of the data
- Execute code to create visualizations

...all defined by user-input natural language

Each of these operations is defined in their own files in the `tools/` dir..
The order in which the tools are run is decided by the  LLM router defined in the `run_agent()` method of `router.py`

### LLM Evaluator Description
In dev

## How to run 
### Data Analysis Agent
 1) Instantiate a virtual environment with `python -m venv venv` (optional)
 2) Install Requirements with `pip install -r requirements.txt`
 3) Configure your openAI API key in helper.py (you will need OpenAI tokens to run this)
 4) Run `python ./src/data_analysis_agent/router.py <'your request'>` from the CLI with any request of your choosing

 eg. `python router.py 'Generate a line graph of sales in December 2022 by store'` or `'What are the best performing products'` or `Based on product performance, how can I increase my overall sales?`, etc.
  
### LLM Evaluator
In dev

## Note
To protect my API key, I told git to stop tracking `helper.py` by running `git update-index --assume-unchanged .\src\data_analysis_agent\helper.py` from the CLI