import time
import warnings
warnings.filterwarnings('ignore')

from eval.router_eval import run_router_eval
from eval.data_lookup_eval import evaluate_lookup_sales_data
from eval.data_analysis_eval import evaluate_analyze_sales_data
from eval.data_visualization_eval import evaluate_generate_visualization_code

from tqdm import tqdm
from helper import get_openai_api_key

# run evaluations asynchronously
import nest_asyncio
nest_asyncio.apply()

# import the agent
from router import start_main_span

trace_name = "Evaluation Agent"
PROJECT_NAME = "Data Analysis Agent"
API_KEY = get_openai_api_key()

### Router Evaluation
agent_questions = [
    "What was the most popular product SKU?",
    # "What was the total revenue across all stores?",
    # "Which store had the highest sales volume?",
    #"Generate code representing a bar chart showing total sales by store. Do not execute the code.",
    # "What percentage of items were sold on promotion?",
    #"What was the average transaction value?",
    # "What are some trends in sales?",
]

# loop through the questions (use tdqm to show progress)
for question in tqdm(agent_questions, desc="Processing questions"):
    try:
        # run the agent with the question
        ret, trace_id = start_main_span([{"role": "user", "content": question}], trace_name=trace_name)
        # wait for the dashboard to be updated
        time.sleep(5)

        # Evaluate the router calls
        print(f"\n\nEvaluating router calls for trace_id {trace_id} ...\n")
        run_router_eval(trace_id, PROJECT_NAME, API_KEY)

        # Call each tool eval, which will only run if the tool was called in this trace
        print(f"\n\nEvaluating lookup sales data for trace_id {trace_id} ...\n")
        evaluate_lookup_sales_data(trace_id, PROJECT_NAME, API_KEY)

        print(f"\n\nEvaluating analyze sales data for trace_id {trace_id} ...\n")
        evaluate_analyze_sales_data(trace_id, PROJECT_NAME, API_KEY)

        print(f"\n\nEvaluating generate visualization code for trace_id {trace_id} ...\n")
        evaluate_generate_visualization_code(trace_id, PROJECT_NAME)


    except Exception as e:
        print(f"Error processing question: {question}")
        print(e)
        continue
