import phoenix as px
from phoenix.trace.dsl import SpanQuery
from phoenix.evals import (
    llm_classify,
    OpenAIModel
)
from openinference.instrumentation import suppress_tracing
from phoenix.trace import SpanEvaluations

def evaluate_analyze_sales_data(trace_id, PROJECT_NAME, API_KEY):
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

    # export data analysis spans for the trace and grab the output and input values
    query = SpanQuery().where(
        f"name == 'analyze_sales_data' and trace_id == '{trace_id}'"
    ).select(
        response="output.value",
        query="input.value"
    )
    clarity_df = px.Client().query_spans(query,project_name=PROJECT_NAME, timeout=None)

    # if the tool was not called, exit
    if clarity_df.empty:
        print(f"No analyze_sales_data tool calls found for trace_id {trace_id}. Skipping eval.")
        return

    # run LLM-as-a-judge on the dataframe with the clarity prompt
    with suppress_tracing():
        clarity_eval = llm_classify(
            dataframe = clarity_df,
            template = CLARITY_LLM_JUDGE_PROMPT,
            rails = ['clear', 'unclear'],
            model=OpenAIModel(model="gpt-4o", api_key=API_KEY),
            provide_explanation=True
        )

    # add a score column to the eval dataframe with eval results
    clarity_eval['score'] = clarity_eval.apply(lambda x: 1 if x['label']=='clear' else 0, axis=1)
    print(f"\nAnalysis Clarity eval dataframe:\n {clarity_eval.head()}\n")

    # upload the evaluation back to phoenix
    print("\nUploading `clarity` evaluation to Phoenix...\n")
    px.Client().log_evaluations(
        SpanEvaluations(eval_name="Response Clarity", dataframe=clarity_eval),
    )
