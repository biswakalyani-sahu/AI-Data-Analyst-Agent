import os
import pandas as pd
import json

def validate_csv(file_path: str) -> str:
    """
    Validates that the file exists, is a CSV, and is under the 10 MB limit.
    Returns None if valid, or an error message string if invalid.
    """
    if not os.path.exists(file_path):
        return f"Error: File not found at path: {file_path}"
    
    if not file_path.lower().endswith('.csv'):
        return "Error: Invalid file type. Only CSV files are supported."
    
    # 10 MB limit check
    file_size_bytes = os.path.getsize(file_path)
    max_size_bytes = 10 * 1024 * 1024  # 10 MB
    if file_size_bytes > max_size_bytes:
        return f"Error: File size ({file_size_bytes / (1024*1024):.2f} MB) exceeds the 10 MB limit."
    
    return None

def get_dataset_summary(file_path: str) -> str:
    """
    Analyzes the structure and quality of the uploaded dataset.
    Detects row/column count, missing values, and duplicate records.
    """
    validation_error = validate_csv(file_path)
    if validation_error:
        return json.dumps({"error": validation_error})
    
    try:
        df = pd.read_csv(file_path)
        
        # Calculate summary metrics
        total_rows = len(df)
        total_columns = len(df.columns)
        
        # Missing values per column
        missing_values = df.isnull().sum().to_dict()
        total_missing = sum(missing_values.values())
        
        # Duplicate records
        duplicate_count = df.duplicated().sum()
        
        summary = {
            "file_name": os.path.basename(file_path),
            "total_rows": int(total_rows),
            "total_columns": int(total_columns),
            "total_missing_values": int(total_missing),
            "missing_values_by_column": {col: int(val) for col, val in missing_values.items()},
            "duplicate_records": int(duplicate_count),
            "status": "Success"
        }
        return json.dumps(summary, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to parse CSV: {str(e)}"})

def get_column_names(file_path: str) -> str:
    """
    Identifies column names and data types of the uploaded dataset.
    """
    validation_error = validate_csv(file_path)
    if validation_error:
        return json.dumps({"error": validation_error})
    
    try:
        df = pd.read_csv(file_path)
        
        columns_info = {}
        for col in df.columns:
            # Map type to a human readable format
            dtype = str(df[col].dtype)
            columns_info[col] = dtype
            
        return json.dumps({
            "columns": list(df.columns),
            "data_types": columns_info,
            "status": "Success"
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to get columns: {str(e)}"})

def get_sales_metrics(file_path: str) -> str:
    """
    Calculates sales metrics: total revenue, average order value, top selling products,
    and monthly trends from the dataset.
    Expects columns like 'Product', 'Quantity', 'Price', 'Revenue', and 'Date' or similar.
    """
    validation_error = validate_csv(file_path)
    if validation_error:
        return json.dumps({"error": validation_error})
    
    try:
        df = pd.read_csv(file_path)
        
        # Standardize columns to case-insensitive matching
        col_mapping = {col.lower(): col for col in df.columns}
        
        # Required columns mapping
        revenue_col = col_mapping.get('revenue') or col_mapping.get('sales') or col_mapping.get('total')
        product_col = col_mapping.get('product') or col_mapping.get('item')
        quantity_col = col_mapping.get('quantity') or col_mapping.get('qty') or col_mapping.get('units')
        price_col = col_mapping.get('price') or col_mapping.get('rate')
        date_col = col_mapping.get('date') or col_mapping.get('timestamp') or col_mapping.get('time')
        category_col = col_mapping.get('category') or col_mapping.get('dept') or col_mapping.get('department')
        
        # Data preparation and calculation fallback
        if not revenue_col:
            if quantity_col and price_col:
                # Calculate revenue dynamically
                df['Calculated_Revenue'] = pd.to_numeric(df[quantity_col], errors='coerce') * pd.to_numeric(df[price_col], errors='coerce')
                revenue_col = 'Calculated_Revenue'
            else:
                return json.dumps({"error": "Unable to calculate revenue. Ensure the file has a 'Revenue' column, or both 'Quantity' and 'Price' columns."})
        
        # Clean numeric values
        df[revenue_col] = pd.to_numeric(df[revenue_col], errors='coerce').fillna(0)
        
        total_revenue = df[revenue_col].sum()
        total_transactions = len(df)
        avg_revenue = df[revenue_col].mean() if total_transactions > 0 else 0
        
        # Product breakdown
        product_summary = {}
        if product_col:
            prod_group = df.groupby(product_col).agg(
                total_revenue=(revenue_col, 'sum'),
                total_quantity=(quantity_col, 'sum') if quantity_col else ('Date', 'count')
            ).reset_index()
            
            # Sort by revenue
            prod_group_sorted = prod_group.sort_values(by='total_revenue', ascending=False)
            product_summary = prod_group_sorted.to_dict(orient='records')
            
            # Convert values to native types for JSON serialization
            for p in product_summary:
                p['total_revenue'] = float(p['total_revenue'])
                p['total_quantity'] = int(p['total_quantity'])
        
        # Category breakdown
        category_summary = {}
        if category_col:
            cat_group = df.groupby(category_col).agg(
                total_revenue=(revenue_col, 'sum'),
                total_quantity=(quantity_col, 'sum') if quantity_col else ('Date', 'count')
            ).reset_index()
            category_summary = cat_group.sort_values(by='total_revenue', ascending=False).to_dict(orient='records')
            for c in category_summary:
                c['total_revenue'] = float(c['total_revenue'])
                c['total_quantity'] = int(c['total_quantity'])
                
        # Monthly sales trends
        trends_summary = []
        if date_col:
            # Parse dates
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            # Extract month identifier (YYYY-MM)
            df['Month'] = df[date_col].dt.to_period('M').astype(str)
            # Group by Month
            trend_group = df.groupby('Month').agg(
                revenue=(revenue_col, 'sum'),
                orders=('Date', 'count')
            ).reset_index().sort_values(by='Month')
            
            trends_summary = trend_group.to_dict(orient='records')
            for t in trends_summary:
                t['revenue'] = float(t['revenue'])
                t['orders'] = int(t['orders'])
                
        return json.dumps({
            "metrics": {
                "total_revenue": float(total_revenue),
                "total_transactions": int(total_transactions),
                "average_transaction_value": float(avg_revenue)
            },
            "top_products": product_summary[:5] if product_summary else [],
            "category_performance": category_summary,
            "monthly_trends": trends_summary,
            "status": "Success"
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to compute sales metrics: {str(e)}"})
