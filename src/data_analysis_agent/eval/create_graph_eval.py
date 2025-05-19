import os
import phoenix as px
from phoenix.trace.dsl import SpanQuery
from phoenix.trace import SpanEvaluations

def evaluate_execute_generated_code(trace_id, PROJECT_NAME):
    query = SpanQuery().where(
        f"name =='execute_generated_code' and trace_id == '{trace_id}'"
    ).select(generated_code="output.value")

    code_gen_df = px.Client().query_spans(query, project_name=PROJECT_NAME, timeout=None)

    if code_gen_df.empty:
        print(f"No execute_generated_code tool calls found for trace_id {trace_id}. Skipping eval.")
        return

    def chart_created(_output: str) -> bool:
        """Check if the code was executed and a chart was created for this trace."""
        return os.path.exists(f"output_graph_{trace_id}.png")

    # assign the result to a new column with `executed` or `not_executed` label
    code_gen_df["label"] = code_gen_df["generated_code"].apply(chart_created).map({True: "executed", False: "not_executed"})
    code_gen_df["score"] = code_gen_df["label"].map({"executed": 1, "not_executed": 0})

    print(f"\nCode Execution eval dataframe:\n {code_gen_df.head()}\n")

    print("\nUploading `execute_generated_code` evaluation to Phoenix...\n")
    px.Client().log_evaluations(
        SpanEvaluations(eval_name="Code Executed Eval", dataframe=code_gen_df),
    )
