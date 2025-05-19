from tracing import tracer

@tracer.tool()
def execute_generated_code(generated_code: str, trace_id: str):
    """
    Executes the provided Python code string without halting the program.
    Returns a status message.
    """
    filename = f"output_graph_{trace_id}.png"
    try:
        safe_code = generated_code.replace("plt.show()", f"plt.savefig('{filename}'); plt.close()")
        exec(safe_code, {})
        return f"Visualization code executed successfully. Plot saved as {filename}"
    except Exception as e:
        return f"Error executing visualization code: {e}"
    