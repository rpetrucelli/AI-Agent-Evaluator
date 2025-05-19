import phoenix as px
from phoenix.trace.dsl import SpanQuery
from phoenix.evals import (
    TOOL_CALLING_PROMPT_TEMPLATE, 
    llm_classify,
    OpenAIModel
)
import json
from router import tools
from openinference.instrumentation import suppress_tracing
from phoenix.trace import SpanEvaluations

def run_router_eval(trace_id, PROJECT_NAME, API_KEY):
    # pull tool calls from the trace
    query = SpanQuery().where(
        # Filter for the `LLM` span kind.
        # The filter condition is a string of valid Python boolean expression.
        f"span_kind == 'LLM' and trace_id == '{trace_id}'",
    ).select(
        question="input.value",
        tool_call="llm.tools"
    )

    # Query phoenix and return the dataframe of LLM calls.
    tool_calls_df = px.Client().query_spans(query, project_name=PROJECT_NAME,timeout=None)
    tool_calls_df = tool_calls_df.dropna(subset=["tool_call"])

    # format the eval template
    TOOL_CALL_EVAL_TEMPLATE = TOOL_CALLING_PROMPT_TEMPLATE.template[0].template.replace(
            "{tool_definitions}", json.dumps(tools).replace("{", '"').replace("}", '"')
        )

    # Use LLM-as-a-judge to evaluate the tool calls chosen by the router
    with suppress_tracing():
        tool_call_eval = llm_classify(
            dataframe = tool_calls_df,
            template = TOOL_CALL_EVAL_TEMPLATE,
            rails = ['correct', 'incorrect'],
            model=OpenAIModel(model="gpt-4o", api_key=API_KEY),
            provide_explanation=True
        )

    # add a score column to the eval dataframe
    tool_call_eval['score'] = tool_call_eval.apply(lambda x: 1 if x['label']=='correct' else 0, axis=1)
    print(f"\nTool Calls eval dataframe:\n {tool_call_eval.head()})\n")

    # upload the evaluation back to phoenix
    print("\nUploading Tool Call Evaluation to Phoenix...\n")
    px.Client().log_evaluations(
        SpanEvaluations(eval_name="Tool Calling Eval", dataframe=tool_call_eval),
    )
