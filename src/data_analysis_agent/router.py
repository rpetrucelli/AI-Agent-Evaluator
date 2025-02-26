from tools.data_lookup import lookup_sales_data
from tools.data_analysis import analyze_sales_data
from tools.data_visualization import generate_visualization
import json
from  config import client, MODEL
import sys

# Define tools/functions that can be called by the model in the accepted syntax
tools = [
    {
        "type": "function",
        "function": {
            "name": "lookup_sales_data",
            "description": "Look up data from Store Sales Price Elasticity Promotions dataset",
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
            "description": "Analyze sales data to extract insights",
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
            "name": "generate_visualization",
            "description": "Generate Python code to create data visualizations",
            "parameters": {
                "type": "object", 
                "properties": {
                    "data": {"type": "string", "description": "The lookup_sales_data tool's output."},
                    "visualization_goal": {"type": "string", "description": "The goal of the visualization."}
                },
                "required": ["data", "visualization_goal"]
            }
        }
    }
]

# Dictionary mapping function names to their implementations
tool_implementations = {
    "lookup_sales_data": lookup_sales_data,
    "analyze_sales_data": analyze_sales_data, 
    "generate_visualization": generate_visualization
}

# define the LLM routers' behavior
SYSTEM_PROMPT = """
You are a helpful assistant that can answer questions about the Store Sales Price Elasticity Promotions dataset.
"""

# code for executing the tools returned in the model's response
def handle_tool_calls(tool_calls, messages):
    
    for tool_call in tool_calls:   
        function = tool_implementations[tool_call.function.name]
        function_args = json.loads(tool_call.function.arguments)
        result = function(**function_args)
        messages.append({"role": "tool", "content": result, "tool_call_id": tool_call.id})
        
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
        print("Making router call to OpenAI")
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
        )
        messages.append(response.choices[0].message)
        tool_calls = response.choices[0].message.tool_calls
        print("Received response with tool calls:", bool(tool_calls))

        # if the model decides to call function(s), print which one and call handle_tool_calls
        if tool_calls:
            print(f"Processing tool calls: {tool_calls[0].function.name}")
            messages = handle_tool_calls(tool_calls, messages)

        # otherwise, break the loop
        else:
            print("No tool calls, returning final response")
            return response.choices[0].message.content

# allow the agent to be run via cli
if __name__ == "__main__":
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        result = run_agent(prompt)
        print("Results: \n" + result)

    else:
        print("usage: python router.py <'your prompt here'>")

### Example usage
# result = run_agent('Show me the code for graph of sales by store in Nov 2021, and tell me what trends you see.')
# print(result) will then produce something similar to below:

### ------------------------------
# Here is the Python code to create a graph of sales by store for November 2021:

# ```
#    python code that can be run to generate a graph of the data
# ```

# ### Trends Observed:
# 1. **Store Performance**: Certain stores, particularly Store 1100, Store 3300, and Store 1650, show higher sales values, indicating they are performing well compared to others.
# 2. **Outlier Performance**: Store 2970 significantly outperforms others in terms of total sales value, suggesting it may have unique offerings or a strong customer base.
# 3. **Low Sales Stores**: Some stores like Store 4400, with a very low sales value, could be facing challenges such as low demand.
# 4. **Potential for Improvement**: Stores with lower performance could benefit from a review of inventory, marketing strategies, and customer engagement tactics.

# This analysis provides insights into store performance and can guide strategic decisions for inventory management, marketing initiatives, and potential promotions.
### ------------------------------
