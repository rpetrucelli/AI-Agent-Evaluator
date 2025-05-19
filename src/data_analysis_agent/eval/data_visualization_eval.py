import phoenix as px
from phoenix.trace.dsl import SpanQuery
from phoenix.trace import SpanEvaluations

# Code-based eval on tthe generated visualization code
def evaluate_generate_visualization_code(trace_id, PROJECT_NAME):
    query = SpanQuery().where(
        f"name =='generate_visualization_code' and trace_id == '{trace_id}'"
    ).select(generated_code="output.value")

    # The Phoenix Client can take this query and return the dataframe.
    code_gen_df = px.Client().query_spans(query, project_name=PROJECT_NAME, timeout=None)

    # exit if this tool was not called
    if code_gen_df.empty:
        print(f"No generate_visualization_code tool calls found for trace_id {trace_id}. Skipping eval.")
        return

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

    print(f"\nCode generation eval dataframe:\n {code_gen_df.head()}\n")

    # upload the evaluation back to phoenix
    print("\nUploading `generate_visualization_code` evaluation to Phoenix...\n")
    px.Client().log_evaluations(
        SpanEvaluations(eval_name="Runnable Code Eval", dataframe=code_gen_df),
    )
