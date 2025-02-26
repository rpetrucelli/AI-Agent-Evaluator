from config import client, MODEL

# Construct prompt based on analysis type and data subset
DATA_ANALYSIS_PROMPT = """
Analyze the following data: {data}
Your job is to answer the following question: {prompt}
"""

# define a method to analyze a provided dataset based on a natural language prompt
def analyze_sales_data(prompt: str, data: str) -> str:
    """Implementation of AI-powered sales data analysis"""
    formatted_prompt = DATA_ANALYSIS_PROMPT.format(data=data, prompt=prompt)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": formatted_prompt}],
    )
    
    analysis = response.choices[0].message.content
    return analysis if analysis else "No analysis could be generated"


#### example usage of the data analysis tool
# example_data = lookup_sales_data("Show me all the sales for store 1320 on November 1st, 2021")
# analyze_sales_data(prompt="what trends do you see in this data?", data=example_data)
