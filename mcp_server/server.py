import os
import sys

# Ensure the script's directory is in the import path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastmcp import FastMCP
import tools

# Create FastMCP server
mcp = FastMCP("Sales Data Analyst MCP Server")

@mcp.tool()
def get_dataset_summary(file_path: str) -> str:
    """
    Analyzes the structure and quality of the uploaded dataset.
    Detects row/column count, missing values, and duplicate records.
    """
    return tools.get_dataset_summary(file_path)

@mcp.tool()
def get_column_names(file_path: str) -> str:
    """
    Identifies column names and data types of the uploaded dataset.
    """
    return tools.get_column_names(file_path)

@mcp.tool()
def get_sales_metrics(file_path: str) -> str:
    """
    Calculates sales metrics: total revenue, average order value, top selling products,
    and monthly trends from the dataset.
    """
    return tools.get_sales_metrics(file_path)

if __name__ == "__main__":
    mcp.run()
