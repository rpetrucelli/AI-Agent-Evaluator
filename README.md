## Test LLM Agent Evaluator 

## Description
This is a data analysis agent that is inspired by the DeepLearning.AI course "Evaluating AI Agents"
It will query GPT 4.0 mini to query data from a database (in this test case just a file contained in `/data`), run an LLM analysis on the data, and generate a visual representation of the data

## How to run data analysis agent
 1) optional: instantiate venv
 2) `pip install -r requirements.txt`
 3) configure your openAI API key in helper.py
 3) nav to `src/data_analysis_agent`
 4) `python router.py` will run the agent with the hardcoded prompt input


## Note
to protect my API key, I have asked git to stop tracking `helper.py` by running `git update-index --assume-unchanged .\src\data_analysis_agent\helper.py` from the CLI