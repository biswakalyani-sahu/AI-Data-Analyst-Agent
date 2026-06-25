import os
from google.adk.agents import Agent
from skills.analyze_dataset import analyze_dataset

def get_cleaning_agent() -> Agent:
    """
    Creates and returns the Data Cleaning Agent.
    This agent specializes in checking data quality, formats, and shapes
    by utilizing the analyze_dataset skill.
    """
    model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    
    return Agent(
        name="data_cleaning_agent",
        model=model_name,
        instruction=(
            "You are a Data Cleaning Specialist agent. "
            "Your role is to inspect the uploaded dataset and write a descriptive summary of its quality. "
            "You MUST call the analyze_dataset tool by passing it the file_path argument. "
            "Once you receive the results from the tool, summarize: "
            "1. Total row and column count, and the file name. "
            "2. Columns present and their detected data types. "
            "3. Missing values count per column (if any), and total duplicate records. "
            "4. A clean evaluation of whether the dataset is ready for analysis, warning of any anomalies."
            "Keep your formatting clean, professional, and clear."
        ),
        tools=[analyze_dataset]
    )
