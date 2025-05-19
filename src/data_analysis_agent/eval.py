import warnings
warnings.filterwarnings('ignore')

import phoenix as px
import os
import json
from tqdm import tqdm
from phoenix.evals import (
    TOOL_CALLING_PROMPT_TEMPLATE, 
    llm_classify,
    OpenAIModel
)
from phoenix.trace import SpanEvaluations
from phoenix.trace.dsl import SpanQuery
from openinference.instrumentation import suppress_tracing
from helper import get_openai_api_key

# run evaluations asynchronously
import nest_asyncio
nest_asyncio.apply()

# import the agent
from router import start_main_span, tools

trace_name = "Evaluation Agent"
PROJECT_NAME = "Data Analysis Agent"
API_KEY = get_openai_api_key()

### Router Evaluation
agent_questions = [
    #"What was the most popular product SKU?",
    # "What was the total revenue across all stores?",
    # "Which store had the highest sales volume?",
    #"Generate code representing a bar chart showing total sales by store. Do not execute the code.",
    # "What percentage of items were sold on promotion?",
    #"What was the average transaction value?",
    "What are some trends in sales?",
]

# loop through the questions (use tdqm to show progress)
for question in tqdm(agent_questions, desc="Processing questions"):
    try:
        ret = start_main_span([{"role": "user", "content": question}], trace_name=trace_name)
    except Exception as e:
        print(f"Error processing question: {question}")
        print(e)
        continue


# pull tool calls from the trace
query = SpanQuery().where(
    # Filter for the `LLM` span kind.
    # The filter condition is a string of valid Python boolean expression.
    "span_kind == 'LLM'",
).select(
    question="input.value",
    tool_call="llm.tools"
)

# Query phoenix and return the dataframe of LLM calls.
tool_calls_df = px.Client().query_spans(query, project_name=PROJECT_NAME,timeout=None)
tool_calls_df = tool_calls_df.dropna(subset=["tool_call"])
print(f"\nTool calls dataframe:\n {tool_calls_df.head()}\n")

# format the eval template
EVAL_TEMPLATE = TOOL_CALLING_PROMPT_TEMPLATE.template[0].template.replace(
        "{tool_definitions}", json.dumps(tools).replace("{", '"').replace("}", '"')
    )

# Use LLM-as-a-judge to evaluate the tool calls chosen by the router
with suppress_tracing():
    tool_call_eval = llm_classify(
        dataframe = tool_calls_df,
        template = EVAL_TEMPLATE,
        rails = ['correct', 'incorrect'],
        model=OpenAIModel(model="gpt-4o", api_key=API_KEY),
        provide_explanation=True
    )

# add a score column to the eval dataframe
tool_call_eval['score'] = tool_call_eval.apply(lambda x: 1 if x['label']=='correct' else 0, axis=1)
print(f"\nEval dataframe:\n {tool_call_eval.head()})\n")

# upload the evaluation back to phoenix
print("\nUploading Tool Call evaluation to Phoenix...\n")
px.Client().log_evaluations(
    SpanEvaluations(eval_name="Tool Calling Eval", dataframe=tool_call_eval),
)

### Tool Evaluations
## Firstly, the data lookup tool

## Data Analysis tool with LLM-as-a-judge
# Define a prompt to evaluate the clarity of the analysis
CLARITY_LLM_JUDGE_PROMPT ="""
In this task, you will be presented with a query and an answer. Your objective is to evaluate the clarity 
of the answer in addressing the query. A clear response is one that is precise, coherent, and directly 
addresses the query without introducing unnecessary complexity or ambiguity. An unclear response is one 
that is vague, disorganized, or difficult to understand, even if it may be factually correct.

Your response should be a single word: either "clear" or "unclear," and it should not include any other text or characters. 
"clear" indicates that the answer is well-structured, easy to understand, and appropriately addresses the query. 
"unclear" indicates that some part of the response could be better structured or worded.
Please carefully consider the query and answer before determining your response.

After analyzing the query and the answer, you must write a detailed explanation of your reasoning to 
justify why you chose either "clear" or "unclear." Avoid stating the final label at the beginning of your 
explanation. Your reasoning should include specific points about how the answer does or does not meet the 
criteria for clarity.

[BEGIN DATA]
Query: {query}
Answer: {response}
[END DATA]
Please analyze the data carefully and provide an explanation followed by your response.

EXPLANATION: Provide your reasoning step by step, evaluating the clarity of the answer based on the query.
LABEL: "clear" or "unclear"
"""

# export data analysis spans and grab the output and input values
query = SpanQuery().where(
    "name == 'analyze_sales_data'"
).select(
    response="output.value",
    query="input.value"
)

# query the project for those and write to a clarity dataframe
clarity_df = px.Client().query_spans(query,project_name=PROJECT_NAME, timeout=None)
print(f"\nClarity dataframe:\n {clarity_df.head()}\n")

# run LLM-as-a-judge on the dataframe with the clarity prompt
with suppress_tracing():
    clarity_eval = llm_classify(
        dataframe = clarity_df,
        template = CLARITY_LLM_JUDGE_PROMPT,
        rails = ['clear', 'unclear'],
        model=OpenAIModel(model="gpt-4o", api_key=API_KEY),
        provide_explanation=True
    )

clarity_eval['score'] = clarity_eval.apply(lambda x: 1 if x['label']=='clear' else 0, axis=1)
print(f"\nClarity eval dataframe:\n {clarity_eval.head()}\n")

# upload the evaluation back to phoenix
print("\nUploading `clarity` evaluation to Phoenix...\n")
px.Client().log_evaluations(
    SpanEvaluations(eval_name="Response Clarity", dataframe=clarity_eval),
)

## Code generation tool
# grab the code generated by generate_visualization_code spans
query = SpanQuery().where( "name =='generate_visualization_code'").select(generated_code="output.value")

# The Phoenix Client can take this query and return the dataframe.
code_gen_df = px.Client().query_spans(query, project_name=PROJECT_NAME, timeout=None)
code_gen_df.head()

def code_is_runnable(output: str) -> bool:
    """Check if the code is runnable"""
    output = output.strip()
    output = output.replace("```python", "").replace("```", "")
    try:
        compile(output, "<string>", "exec")
        return True
    except Exception as e:
        return False
    
# assign the result to a new column with `runnable` or `not_runnable` label
code_gen_df["label"] = code_gen_df["generated_code"].apply(code_is_runnable).map({True: "runnable", False: "not_runnable"})
code_gen_df["score"] = code_gen_df["label"].map({"runnable": 1, "not_runnable": 0})
print(f"\nCode generation dataframe:\n {code_gen_df.head()}\n")

# upload the evaluation back to phoenix
print("\nUploading `generate_visualization_code` evaluation to Phoenix...\n")
px.Client().log_evaluations(
    SpanEvaluations(eval_name="Runnable Code Eval", dataframe=code_gen_df),
)
