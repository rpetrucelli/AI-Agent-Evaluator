from pydantic import BaseModel, Field
from config import client, MODEL
from .data_lookup import lookup_sales_data

## in this file, we take a 2 step approach to visualize the data, which reduces variance in and improves the accuracy off the LLMs response
# Firstly, we use an LLM call to generate the correct chart configuration
# Secondly, we use another LLM to generate the code for the data visualization for the chat configuration defined in the first step


# Define a prompt to generate a chart configuration based on a natural language goal
CHART_CONFIGURATION_PROMPT = """
Generate a chart configuration based on this data: {data}
The goal is to show: {visualization_goal}
"""

# Prompt to generate the code for a data visualization 
CREATE_CHART_PROMPT = """
Write python code to create a chart based on the following configuration.
Only return the code, no other text.
config: {config}
"""


# class defining the response format of step 1 of tool 3
class VisualizationConfig(BaseModel):
    chart_type: str = Field(..., description="Type of chart to generate")
    x_axis: str = Field(..., description="Name of the x-axis column")
    y_axis: str = Field(..., description="Name of the y-axis column")
    title: str = Field(..., description="Title of the chart")

    # method to generate the chart configurations
    def extract_chart_config(data: str, visualization_goal: str) -> dict:
        """Generate chart visualization configuration
        
        Args:
            data: String containing the data to visualize
            visualization_goal: Description of what the visualization should show
            
        Returns:
            Dictionary containing line chart configuration
        """
        formatted_prompt = CHART_CONFIGURATION_PROMPT.format(data=data, visualization_goal=visualization_goal)
        
        response = client.beta.chat.completions.parse(
            model=MODEL,
            messages=[{"role": "user", "content": formatted_prompt}],
            response_format=VisualizationConfig,
        )
        
        try:
            # Extract axis and title info from response
            content = response.choices[0].message.content
            
            # Return structured chart config
            return {
                "chart_type": content.chart_type,
                "x_axis": content.x_axis,
                "y_axis": content.y_axis,
                "title": content.title,
                "data": data
            }
        except Exception:
            return {
                "chart_type": "line", 
                "x_axis": "date",
                "y_axis": "value",
                "title": visualization_goal,
                "data": data
            }
        
# 2nd step, create a chart based on the config defined in the above method
def create_chart(config: dict) -> str:
    """Create a chart based on the configuration"""
    formatted_prompt = CREATE_CHART_PROMPT.format(config=config)
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": formatted_prompt}],
    )
    
    code = response.choices[0].message.content
    code = code.replace("```python", "").replace("```", "")
    code = code.strip()
    
    return code

# TODO, add a 3rd method to error check the code generated

# Method to tie the 2 steps together and return the code for the visualizations
def generate_visualization(data: str, visualization_goal: str) -> str:
    """Generate a visualization based on the data and goal"""
    config = VisualizationConfig.extract_chart_config(data, visualization_goal)
    code = create_chart(config)
    return code

### example usage
# visualization_prompt = "A bar chart of sales by product SKU. Put the product SKU on the x-axis and the sales on the y-axis."
# code = generate_visualization(lookup_sales_data("Show me all the sales for store 1320 on November 1st, 2021"), visualization_prompt)
# exec(code) # if you wish to actually generate the visualization
