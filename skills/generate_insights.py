import json
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Set non-interactive backend for web application safety
import matplotlib.pyplot as plt
from skills.mcp_client_helper import call_mcp_tool

def generate_insights(file_path: str) -> dict:
    """
    Skill: generate_insights
    Calls the MCP server for sales metrics, parses the output,
    and generates visualization charts saved in the reports directory.
    
    Args:
        file_path (str): Path to the CSV dataset.
        
    Returns:
        dict: A dictionary containing metrics, top products, trend data,
              and file paths to the generated charts.
    """
    # 1. Call MCP tool 'get_sales_metrics'
    metrics_raw = call_mcp_tool("get_sales_metrics", {"file_path": file_path})
    metrics_data = json.loads(metrics_raw)
    
    if "error" in metrics_data:
        return {"error": metrics_data["error"]}
        
    # Ensure the reports output directory exists
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    reports_dir = os.path.join(project_root, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    chart_paths = {}
    
    # 2. Generate Revenue Trend Chart (Line Chart)
    monthly_trends = metrics_data.get("monthly_trends", [])
    if monthly_trends:
        try:
            df_trend = pd.DataFrame(monthly_trends)
            df_trend = df_trend.sort_values("Month")
            
            plt.figure(figsize=(10, 5))
            plt.plot(df_trend["Month"], df_trend["revenue"], marker='o', color='#1E88E5', linewidth=2.5)
            plt.title("Monthly Revenue Trend", fontsize=14, fontweight='bold', pad=15)
            plt.xlabel("Month", fontsize=12)
            plt.ylabel("Revenue ($)", fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            trend_chart_path = os.path.join(reports_dir, "revenue_trend.png")
            plt.savefig(trend_chart_path, dpi=300)
            plt.close()
            chart_paths["revenue_trend"] = trend_chart_path
        except Exception as e:
            chart_paths["revenue_trend_error"] = f"Failed to plot trend chart: {str(e)}"
            
    # 3. Generate Top Products Chart (Bar Chart)
    top_products = metrics_data.get("top_products", [])
    if top_products:
        try:
            df_products = pd.DataFrame(top_products)
            # Sort ascending for horizontal bar chart or descending for vertical
            df_products = df_products.sort_values("total_revenue", ascending=True)
            
            plt.figure(figsize=(10, 5))
            plt.barh(df_products["Product"], df_products["total_revenue"], color='#26A69A')
            plt.title("Top 5 Products by Revenue", fontsize=14, fontweight='bold', pad=15)
            plt.xlabel("Total Revenue ($)", fontsize=12)
            plt.ylabel("Product", fontsize=12)
            plt.grid(True, axis='x', linestyle='--', alpha=0.5)
            plt.tight_layout()
            
            products_chart_path = os.path.join(reports_dir, "top_products.png")
            plt.savefig(products_chart_path, dpi=300)
            plt.close()
            chart_paths["top_products"] = products_chart_path
        except Exception as e:
            chart_paths["top_products_error"] = f"Failed to plot products chart: {str(e)}"
            
    # Combine data and chart path info
    result = {
        "metrics": metrics_data.get("metrics"),
        "top_products": metrics_data.get("top_products"),
        "category_performance": metrics_data.get("category_performance"),
        "monthly_trends": metrics_data.get("monthly_trends"),
        "charts": chart_paths
    }
    
    return result
