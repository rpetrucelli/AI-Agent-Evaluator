from helper import get_phoenix_endpoint
from tools.data_lookup import lookup_sales_data
from tools.data_analysis import analyze_sales_data
from tools.data_visualization import generate_visualization_code
from tools.create_graph import execute_generated_code
import json
from  config import client, MODEL
from tracing import tracer
from opentelemetry.trace import StatusCode


# Define tools/functions that can be called by the model in the accepted syntax
tools = [
    {
        "type": "function",
        "function": {
            "name": "lookup_sales_data",
            "description": "Look up data from Store Sales Price Elasticity Promotions dataset. Do not call this tool multiple times",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "The unchanged prompt that the user provided."}
                },
                "required": ["prompt"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_sales_data", 
            "description": "Analyze sales data to extract insights.",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {"type": "string", "description": "The lookup_sales_data tool's output."},
                    "prompt": {"type": "string", "description": "The unchanged prompt that the user provided."}
                },
                "required": ["data", "prompt"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_visualization_code",
            "description": "Generate Python code to represent data visualizations.",
            "parameters": {
                "type": "object", 
                "properties": {
                    "data": {"type": "string", "description": "The lookup_sales_data tool's output."},
                    "visualization_goal": {"type": "string", "description": "The goal of the visualization."}
                },
                "required": ["data", "visualization_goal"]
            }
        }
    },
    {
    "type": "function",
    "function": {
        "name": "execute_generated_code",
        "description": "Only if prompted by the user, execute the data visualization code from the generate_visualization_code tool",
        "parameters": {
            "type": "object",
            "properties": {
                "generated_code": {"type": "string", "description": "The Python code to execute."}
            },
            "required": ["generated_code"]
        }
    }
}
]

# Dictionary mapping function names to their implementations
tool_implementations = {
    "lookup_sales_data": lookup_sales_data,
    "analyze_sales_data": analyze_sales_data,
    "generate_visualization_code": generate_visualization_code,
    "execute_generated_code": execute_generated_code 
}

# define the LLM routers' behavior
SYSTEM_PROMPT = """
You are a helpful data scientist that excels in analyzing and answer questions about the Store Sales Price Elasticity Promotions dataset.
You excel at generating clean and readable visaulizations of the data.
"""

# code for executing the tools returned in the model's response
@tracer.chain()
def handle_tool_calls(tool_calls, messages):
    for tool_call in tool_calls:   
        function = tool_implementations[tool_call.function.name]
        function_args = json.loads(tool_call.function.arguments)
        result = function(**function_args)
        messages.append({"role": "tool", "content": result, "tool_call_id": tool_call.id})

        print(f"Completed tool call to {function}")
        
    return messages

def run_agent(messages):
    print("Running agent with messages:", messages)

    # check for incorrect syntax
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]
        
    # add system prompt if needed
    if not any( isinstance(message, dict) and message.get("role") == "system" for message in messages ):
            system_prompt = {"role": "system", "content": SYSTEM_PROMPT}
            messages.append(system_prompt)

    # define a loop to recursively make tool calls while the LLM router decides they are necessary
    while True:
        # Router Span
        print("Starting router call span")

        with tracer.start_as_current_span("router_call", openinference_span_kind="chain") as span:
            # set the span input and call the model with any tools
            span.set_input(value=messages) 
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=tools,
            )

            messages.append(response.choices[0].message.model_dump())
            tool_calls = response.choices[0].message.tool_calls
            print("Received response with tool calls:", bool(tool_calls))
            span.set_status(StatusCode.OK)
    
            if tool_calls:
                print("Starting tool calls span")
                messages = handle_tool_calls(tool_calls, messages)
                span.set_output(value=tool_calls)
            else:
                print("No tool calls, returning final response")
                span.set_output(value=response.choices[0].message.content)
                return response.choices[0].message.content

# this main span will wrap the entire agent run`
def start_main_span(messages):
    print("Starting main span with messages:", messages)
    
    with tracer.start_as_current_span("Run Data Analysis Agent", openinference_span_kind="agent") as span:
        span.set_input(value=messages)
        ret = run_agent(messages)
        print("Main span completed with return value:", ret)
        span.set_output(value=ret)
        span.set_status(StatusCode.OK)

        return ret

# allow the agent to be run via cli
# TODO fix chart file saving
if __name__ == "__main__":
    prompt = input("Enter your prompt: ")
    if prompt.strip():
        messages = [{"role": "user", "content": prompt}]
        result = start_main_span(messages)
        print("Results: \n" + result)
        print("\nView the phoenix trace at: " + get_phoenix_endpoint())
    else:
        print("No prompt provided")

### ------Example usage-----------
###
### python router.py
### Enter your prompt: "What is the average sales price for each product in the dataset?"
###
### ------------------------------
