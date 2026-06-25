import json
from skills.mcp_client_helper import call_mcp_tool

def analyze_dataset(file_path: str) -> dict:
    """
    Skill: analyze_dataset
    Connects to the MCP server to retrieve data quality summary and column schemas.
    
    Args:
        file_path (str): The local path to the uploaded CSV file.
        
    Returns:
        dict: A dictionary containing the file summary, column list, and data types.
    """
    # 1. Call MCP tool 'get_dataset_summary'
    summary_raw = call_mcp_tool("get_dataset_summary", {"file_path": file_path})
    summary_data = json.loads(summary_raw)
    
    if "error" in summary_data:
        return {"error": summary_data["error"]}
        
    # 2. Call MCP tool 'get_column_names'
    columns_raw = call_mcp_tool("get_column_names", {"file_path": file_path})
    columns_data = json.loads(columns_raw)
    
    if "error" in columns_data:
        return {"error": columns_data["error"]}
        
    # Combine results
    result = {
        "file_name": summary_data.get("file_name"),
        "total_rows": summary_data.get("total_rows"),
        "total_columns": summary_data.get("total_columns"),
        "total_missing_values": summary_data.get("total_missing_values"),
        "missing_values_by_column": summary_data.get("missing_values_by_column"),
        "duplicate_records": summary_data.get("duplicate_records"),
        "columns": columns_data.get("columns"),
        "data_types": columns_data.get("data_types")
    }
    
    return result
