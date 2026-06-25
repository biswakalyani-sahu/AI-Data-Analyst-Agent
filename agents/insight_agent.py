import os
from google.adk.agents import Agent
from skills.generate_insights import generate_insights

def get_insight_agent() -> Agent:
    """
    Creates and returns the Insight Agent.
    This agent specializes in calculating key metrics, identifying trends,
    and outputting qualitative business observations and opportunities.
    """
    model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    
    return Agent(
        name="insight_agent",
        model=model_name,
        instruction=(
            "You are a Business Intelligence and Insight Agent. "
            "Your role is to analyze sales data, identify performance drivers, and suggest improvements. "
            "You MUST call the generate_insights tool by passing it the file_path argument. "
            "Based on the tool outputs (such as metrics, top products, categories, monthly trends): "
            "1. Summarize key financial metrics (total sales, average sales value). "
            "2. Identify top 3 performing products/categories and any low-performing ones. "
            "3. Highlight trend observations (e.g. sales growth, seasonal variations). "
            "4. Generate strategic sections: "
            "   - Growth Opportunities: Where can the business expand or focus marketing? "
            "   - Risk Observations: Are there risks like product concentration, falling margins, or seasonal drops? "
            "Ensure your final response is formatted in clean markdown, suitable to be compiled into a report."
        ),
        tools=[generate_insights]
    )
