## Test LLM Agent Evaluator 

## Description
This is a data analysis agent that is inspired by the DeepLearning.AI course "Evaluating AI Agents".

It will prompt GPT 4.0 mini to query data from a database (in this test case just a file contained in `/data`), run an LLM analysis on the data, and then generate python code to build a visual representation of the data.

Each of these operations and defined in their own files in the `tools/` dir, and the order in which the tools are run in is decided by a LLM router as defined in the `run_agent()` method in `router.py`.

## How to run data analysis agent
 1) optional: instantiate venv with `python -m venv venv`
 2) `pip install -r requirements.txt`
 3) configure your openAI API key in helper.py
 3) nav to `./src/data_analysis_agent/`
 4) `python router.py <'your request'>` will run the agent with the hardcoded prompt input

 eg. python router.py 'Show me the code for graph of sales by store in Nov 2021, and tell me what trends you see.'


## Note
to protect my API key, I have asked git to stop tracking `helper.py` by running `git update-index --assume-unchanged .\src\data_analysis_agent\helper.py` from the CLI