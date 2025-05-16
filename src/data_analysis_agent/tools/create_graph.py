from tracing import tracer

@tracer.tool()
def execute_generated_code(generated_code: str):
    """
    Executes the provided Python code string without halting the program.
    Returns a status message.
    """
    try:
        safe_code = generated_code.replace("plt.show()", "plt.savefig('output_graph.png'); plt.close()")
        exec(safe_code, {})
        return "Visualization code executed successfully. Plot saved as output.png."
    except Exception as e:
        return f"Error executing visualization code: {e}"
    