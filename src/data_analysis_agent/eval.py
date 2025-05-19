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

# import nest_asyncio
# nest_asyncio.apply()

# import the agent
from router import start_main_span, run_agent, tools

trace_name = "Evaluation Agent"

# define some agent questions (test cases)
agent_questions = [
    "What was the most popular product SKU?"#,
    # "What was the total revenue across all stores?",
    # "Which store had the highest sales volume?",
    # "Generate code representing a bar chart showing total sales by store. Do not execute the code.",
    # "What percentage of items were sold on promotion?",
    # "What was the average transaction value?"
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

# The Phoenix Client can take this query and return the dataframe of LLM calls.
tool_calls_df = px.Client().query_spans(query, project_name="Data Analysis Agent",timeout=None)
tool_calls_df = tool_calls_df.dropna(subset=["tool_call"])
print(f"\nTool calls dataframe:\n {tool_calls_df.head()}\n")

# format the eval template
EVAL_TEMPLATE = TOOL_CALLING_PROMPT_TEMPLATE.template[0].template.replace(
        "{tool_definitions}", json.dumps(tools).replace("{", '"').replace("}", '"')
    )

print(f"\nEval template:\n {EVAL_TEMPLATE}\n")
# This will take each tool call and run it against the formatted tool call prompt template
# the tool definitions to classify the tool call as correct or incorrect.
with suppress_tracing():
    tool_call_eval = llm_classify(
        dataframe = tool_calls_df,
        template = EVAL_TEMPLATE,
        rails = ['correct', 'incorrect'],
        model=OpenAIModel(model="gpt-4o", api_key=get_openai_api_key()),
        provide_explanation=True
    )

# add a score column to the eval dataframe
tool_call_eval['score'] = tool_call_eval.apply(lambda x: 1 if x['label']=='correct' else 0, axis=1)
print(f"\nEval dataframe:\n {tool_call_eval.head()})\n")

# upload the evaluation back to phoenix
px.Client().log_evaluations(
    SpanEvaluations(eval_name="Tool Calling Eval", dataframe=tool_call_eval),
)