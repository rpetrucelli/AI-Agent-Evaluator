import phoenix as px
from phoenix.trace.dsl import SpanQuery
from phoenix.evals import (
    llm_classify,
    OpenAIModel
)
from openinference.instrumentation import suppress_tracing
from phoenix.trace import SpanEvaluations

# Evaluate the data lookup tool
def evaluate_lookup_sales_data(trace_id, PROJECT_NAME, API_KEY):
    SQL_EVAL_GEN_PROMPT = """
        SQL Evaluation Prompt:
        -----------------------
        You are tasked with determining if the SQL generated appropiately answers a given instruction
        taking into account its generated query and response.

        Data:
        -----
        - [Instruction]: {question}
        This section contains the specific task or problem that the sql query is intended to solve.

        - [Reference Query]: {query_gen}
        This is the sql query submitted for evaluation. Analyze it in the context of the provided
        instruction.

        Evaluation:
        -----------
        Your response should be a single word: either "correct" or "incorrect".
        You must assume that the db exists and that columns are appropiately named.
        You must take into account the response as additional information to determine the correctness.

        - "correct" indicates that the sql query correctly solves the instruction.
        - "incorrect" indicates that the sql query correctly does not solve the instruction correctly.

        Note: Your response should contain only the word "correct" or "incorrect" with no additional text
        or characters.
    """

    # filter down to LLM spans in the trace that generated SQL queries
    query = SpanQuery().where(
        "span_kind=='LLM'"
    ).select(
        query_gen="llm.output_messages",
        question="input.value",
    )
    sql_df = px.Client().query_spans(query, project_name=PROJECT_NAME, timeout=None)
    sql_df = sql_df[sql_df["question"].str.contains("Generate an efficient SQL query based on a prompt.", case=False, na=False)]
    print(f"SQL generation dataframe:\n {sql_df.head()}\n")

    # exit if this tool was not called
    if sql_df.empty:
        print(f"No lookup_sales_data tool calls found for trace_id {trace_id}. Skipping eval.")
        return
    
    # run LLM-as-a-judge on the dataframe with the SQL prompt
    with suppress_tracing():
        sql_gen_eval = llm_classify(
            dataframe = sql_df,
            template = SQL_EVAL_GEN_PROMPT,
            rails = ['correct', 'incorrect'],
            model=OpenAIModel(model="gpt-4o", api_key=API_KEY),
            provide_explanation=True
        )
        
    # add a score column to the eval dataframe with eval results
    sql_gen_eval['score'] = sql_gen_eval.apply(lambda x: 1 if x['label']=='correct' else 0, axis=1)
    print(f"\nSQL generation eval dataframe:\n {sql_gen_eval.head()}\n")
    
    # upload the evaluation back to phoenix
    print("\nUploading SQL generation evaluation to Phoenix...\n")
    px.Client().log_evaluations(
        SpanEvaluations(eval_name="SQL Gen Eval", dataframe=sql_gen_eval),
    )
