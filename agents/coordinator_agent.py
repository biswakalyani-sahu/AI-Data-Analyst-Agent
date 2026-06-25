import os
import json
import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Import specialized agents
from agents.cleaning_agent import get_cleaning_agent
from agents.insight_agent import get_insight_agent
from agents.report_agent import get_report_agent

# Import raw skill functions for direct data access if needed
from skills.analyze_dataset import analyze_dataset
from skills.generate_insights import generate_insights

async def execute_adk_agent_async(agent, prompt: str) -> str:
    """
    Executes a google-adk Agent using the standard Runner and InMemorySessionService.
    Captures and returns the final response text.
    """
    session_service = InMemorySessionService()
    runner = Runner(
    app_name="AI_Data_Analyst",
    agent=agent,
    session_service=session_service
)
    
    session = await session_service.create_session(app_name="AI_Data_Analyst", user_id="business_owner")
    
    # Prepare the message content
    content = types.Content(role='user', parts=[types.Part(text=prompt)])
    
    response_text = ""
    # Run the agent asynchronously and collect response events
    async for event in runner.run_async(
        session_id=session.id,
        user_id=session.user_id,
        new_message=content
    ):
        # Extract content from final response or stream chunk
        if hasattr(event, 'content') and event.content:
            if hasattr(event.content, 'parts') and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        response_text += part.text
        elif hasattr(event, 'is_final_response') and event.is_final_response():
            if hasattr(event, 'content') and event.content:
                part = event.content.parts[0]
                if hasattr(part, 'text') and part.text:
                    response_text = part.text
                    
    return response_text

def run_adk_agent(agent, prompt: str) -> str:
    """Synchronous wrapper to run an ADK agent using asyncio."""
    try:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(execute_adk_agent_async(agent, prompt))
        else:
            return loop.run_until_complete(execute_adk_agent_async(agent, prompt))
    except Exception as e:
        return f"Agent Execution Error: {str(e)}"

def run_analyst_team(file_path: str) -> dict:
    """
    Orchestration Pipeline (Coordinator Agent Logic):
    1. Instantiates and calls the Data Cleaning Agent.
    2. Instantiates and calls the Insight Agent.
    3. Extracts data details directly from the skills to ensure clean values are passed.
    4. Calls the Report Agent to generate and save the final report.
    5. Returns all summaries, chart paths, and the final report.
    """
    results = {}
    
    # Ensure file exists
    if not os.path.exists(file_path):
        return {"error": f"Dataset file not found at: {file_path}"}
        
    # --- STEP 1: Data Cleaning Agent ---
    clean_agent = get_cleaning_agent()
    cleaning_prompt = f"Please analyze and profiles the data quality of the CSV file at: {file_path}"
    cleaning_summary_ai = run_adk_agent(clean_agent, cleaning_prompt)
    results["cleaning_summary_ai"] = cleaning_summary_ai
    
    # Run the raw skill to get structure dictionary for the report tool
    try:
        clean_summary_dict = analyze_dataset(file_path)
        results["clean_summary_dict"] = clean_summary_dict
    except Exception as e:
        results["clean_summary_dict"] = {"error": f"Failed to run cleaning skill: {str(e)}"}
        
    # --- STEP 2: Insight Agent ---
    ins_agent = get_insight_agent()
    insight_prompt = f"Please generate sales metrics, charts, and business insights for the CSV file at: {file_path}"
    insight_summary_ai = run_adk_agent(ins_agent, insight_prompt)
    results["insight_summary_ai"] = insight_summary_ai
    
    # Run raw skill to get computed metrics and chart paths
    try:
        insights_data_dict = generate_insights(file_path)
        results["insights_data_dict"] = insights_data_dict
    except Exception as e:
        results["insights_data_dict"] = {"error": f"Failed to run insights skill: {str(e)}"}
        
    # --- STEP 3: Report Agent ---
    rep_agent = get_report_agent()
    
    # Pack parameters inside prompt so the Report Agent can call create_report tool
    report_prompt = (
        "Please compile the final business report.\n\n"
        "Here is the clean summary data:\n"
        f"{json.dumps(results.get('clean_summary_dict', {}))}\n\n"
        "Here is the insights quantitative metrics and chart path data:\n"
        f"{json.dumps(results.get('insights_data_dict', {}))}\n\n"
        "Here is the qualitative business observations text:\n"
        f"{results.get('insight_summary_ai', 'No qualitative insights available.')}\n\n"
        "Use the create_report tool to write these details into the final report file and return the confirmation."
    )
    
    report_summary_ai = run_adk_agent(rep_agent, report_prompt)
    results["report_summary_ai"] = report_summary_ai
    
    # Verify if report file was written
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    report_file_path = os.path.join(project_root, "reports", "business_report.md")
    
    if os.path.exists(report_file_path):
        with open(report_file_path, "r", encoding="utf-8") as f:
            results["final_report_markdown"] = f.read()
    else:
        results["final_report_markdown"] = f"# Error\n\nReport file was not created. Agent summary:\n\n{report_summary_ai}"
        
    return results
