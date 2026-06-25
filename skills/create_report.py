import os

def create_report(clean_summary: dict, insights_data: dict, gemini_insights: str) -> str:
    """
    Skill: create_report
    Assembles the data quality summary, quantitative metrics, and qualitative AI insights
    into a professional, structured Markdown report, and saves it to the reports folder.
    
    Args:
        clean_summary (dict): Results from analyze_dataset.
        insights_data (dict): Quantitative metrics and chart path info from generate_insights.
        gemini_insights (str): Markdown text from Gemini containing recommendations and insights.
        
    Returns:
        str: The full Markdown report as a string.
    """
    # 1. Extract details
    total_rows = clean_summary.get("total_rows", 0)
    missing_vals = clean_summary.get("total_missing_values", 0)
    duplicates = clean_summary.get("duplicate_records", 0)
    
    metrics = insights_data.get("metrics", {})
    total_rev = metrics.get("total_revenue", 0.0)
    total_tx = metrics.get("total_transactions", 0)
    avg_tx = metrics.get("average_transaction_value", 0.0)
    
    top_products = insights_data.get("top_products", [])
    category_perf = insights_data.get("category_performance", [])
    
    # 2. Build Markdown
    report_md = []
    report_md.append("# Small Business Sales Performance & Insights Report\n")
    report_md.append("## 1. Executive Summary\n")
    report_md.append(f"This automated business analysis report summarizes sales transaction data from **{clean_summary.get('file_name', 'your uploaded file')}**.")
    report_md.append(f"Across **{total_tx:,} transactions**, the business generated a total revenue of **${total_rev:,.2f}**, with an average transaction value of **${avg_tx:,.2f}**.\n")
    
    report_md.append("## 2. Data Quality & Profiling Summary\n")
    report_md.append("| Metric | Value | Status |")
    report_md.append("| :--- | :--- | :--- |")
    report_md.append(f"| Total Transactions (Rows) | {total_rows:,} | Verified |")
    report_md.append(f"| Missing Cells | {missing_vals:,} | {'Action Required' if missing_vals > 0 else 'Healthy'} |")
    report_md.append(f"| Duplicate Records | {duplicates:,} | {'Action Required' if duplicates > 0 else 'Healthy'} |")
    report_md.append("")
    
    if clean_summary.get("missing_values_by_column"):
        report_md.append("### Missing Values Breakdown:")
        for col, count in clean_summary["missing_values_by_column"].items():
            if count > 0:
                report_md.append(f"- **{col}**: {count} missing values")
        report_md.append("")
        
    report_md.append("## 3. Financial Metrics & Performance\n")
    report_md.append("### Top Selling Products")
    if top_products:
        report_md.append("| Product | Total Revenue | Units Sold |")
        report_md.append("| :--- | :--- | :--- |")
        for prod in top_products[:5]:
            name = prod.get("Product") or prod.get("Product Name") or "Unknown"
            rev = prod.get("total_revenue", 0.0)
            qty = prod.get("total_quantity", 0)
            report_md.append(f"| {name} | ${rev:,.2f} | {qty:,} |")
    else:
        report_md.append("*No product data available.*")
    report_md.append("")
    
    report_md.append("### Category Performance")
    if category_perf:
        report_md.append("| Category | Total Revenue | Units Sold |")
        report_md.append("| :--- | :--- | :--- |")
        for cat in category_perf:
            name = cat.get("Category") or "Unknown"
            rev = cat.get("total_revenue", 0.0)
            qty = cat.get("total_quantity", 0)
            report_md.append(f"| {name} | ${rev:,.2f} | {qty:,} |")
    else:
        report_md.append("*No category data available.*")
    report_md.append("\n")
    
    report_md.append("## 4. AI Strategic Insights & Recommendations\n")
    report_md.append(gemini_insights)
    report_md.append("\n")
    
    report_md.append("---\n*Report generated automatically by the AI Data Analyst Team.*")
    
    full_report_text = "\n".join(report_md)
    
    # 3. Save report to the reports folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    reports_dir = os.path.join(project_root, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    report_path = os.path.join(reports_dir, "business_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(full_report_text)
        
    return full_report_text
