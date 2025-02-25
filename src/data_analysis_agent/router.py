from tools.data_lookup import lookup_sales_data
from tools.data_analysis import analyze_sales_data
from tools.data_visualization import generate_visualization
import json
from  config import client, MODEL

# Define tools/functions that can be called by the model
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

    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]
        
    # Check and add system prompt if needed
    if not any(
            isinstance(message, dict) and message.get("role") == "system" for message in messages
        ):
            system_prompt = {"role": "system", "content": SYSTEM_PROMPT}
            messages.append(system_prompt)

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
        else:
            print("No tool calls, returning final response")
            return response.choices[0].message.content
        
if __name__ == "__main__":
     result = run_agent('Show me the code for graph of sales by store in Nov 2021, and tell me what trends you see.')
     print(result)



## Example usage
# result = run_agent('Show me the code for graph of sales by store in Nov 2021, and tell me what trends you see.')
# print(result) will then produce the below >>>

# Here is the Python code to create a graph of sales by store for November 2021:

# ```python
# import pandas as pd
# import matplotlib.pyplot as plt
# from io import StringIO

# data = """Store_Number  Total_Qty_Sold  Total_Sales_Value
# 0           1100          1712.0       19298.679917
# 1           3300          1859.0       23730.719905
# 2           3190          1003.0       11934.999961
# 3            880          1525.0       17753.769956
# 4           4180           913.0       10213.819920
# 5            550           764.0        9554.049975
# 6           1650          1770.0       23186.909958
# 7           1210          1821.0       21021.669984
# 8           2750          1462.0       16310.409961
# 9           1760          1207.0       14598.209948
# 10          1980           893.0        9084.959929
# 11           330          1105.0       12569.599911
# 12          990          1280.0       15101.459945
# 13          3410          1345.0       15982.159946
# 14          2640          1005.0       10891.639931
# 15          2090          1080.0       11617.179888
# 16          4840          1612.0       19127.169971
# 17          3080          1454.0       18044.450005
# 18          1320          1701.0       19553.789981
# 19          1540          1801.0       21207.689942
# 20          4070           932.0        9161.409921
# 21          4730           819.0       10571.779962
# 22          2420          1370.0       15234.709888
# 23           660          1208.0       13041.239901
# 24           770           973.0        9181.769959
# 25          2970          2312.0       31000.569969
# 26          2530           890.0       11139.740003
# 27          3740           949.0       10719.049952
# 28          4400           225.0        4390.689987
# 29          2200          1513.0       16854.439921
# 30          2310          1594.0       16611.539945
# 31          1870          1648.0       17091.849894
# 32          3630          1311.0       14202.299958"""

# # Load data into a pandas DataFrame
# df = pd.read_csv(StringIO(data), sep=r'\s+')

# # Create a line chart
# plt.figure(figsize=(10, 6))
# plt.plot(df['Store_Number'], df['Total_Sales_Value'], marker='o')
# plt.title('Sales by Store in November 2021')
# plt.xlabel('Store Number')
# plt.ylabel('Total Sales Value')
# plt.grid(True)
# plt.xticks(df['Store_Number'], rotation=45)
# plt.tight_layout()
# plt.show()
# ```

# ### Trends Observed:
# 1. **Store Performance**: Certain stores, particularly Store 1100, Store 3300, and Store 1650, show higher sales values, indicating they are performing well compared to others.
# 2. **Outlier Performance**: Store 2970 significantly outperforms others in terms of total sales value, suggesting it may have unique offerings or a strong customer base.
# 3. **Low Sales Stores**: Some stores like Store 4400, with a very low sales value, could be facing challenges such as low demand.
# 4. **Potential for Improvement**: Stores with lower performance could benefit from a review of inventory, marketing strategies, and customer engagement tactics.

# This analysis provides insights into store performance and can guide strategic decisions for inventory management, marketing initiatives, and potential promotions.
