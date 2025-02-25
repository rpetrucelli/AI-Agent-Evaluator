from pydantic import BaseModel, Field
from config import client, MODEL
from .data_lookup import lookup_sales_data

# prompt template for step 1 of tool 3
CHART_CONFIGURATION_PROMPT = """
Generate a chart configuration based on this data: {data}
The goal is to show: {visualization_goal}
"""

# prompt template for step 2 of tool 3
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

    # code for step 1 of tool 3
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
        
# code for step 2 of tool 3
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

# code for tool 3
def generate_visualization(data: str, visualization_goal: str) -> str:
    """Generate a visualization based on the data and goal"""
    config = VisualizationConfig.extract_chart_config(data, visualization_goal)
    code = create_chart(config)
    return code

# example usage of the data visualization tool
visualization_prompt = "A bar chart of sales by product SKU. Put the product SKU on the x-axis and the sales on the y-axis."
code = generate_visualization(lookup_sales_data("Show me all the sales for store 1320 on November 1st, 2021"), visualization_prompt)
