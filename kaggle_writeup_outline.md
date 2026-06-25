# Kaggle Writeup Outline: AI Data Analyst Team 📝

**Title Idea**: Building an Automated Business Analyst Team with Multi-Agent Systems (ADK) and Model Context Protocol (MCP)

---

## 1. Abstract & Introduction
*   **The Hook**: Small business owners often lack the resources to hire data science teams. Automated analysis tools must be secure, precise, and capable of generating actionable strategic advice.
*   **The Solution**: An open-source, multi-agent AI system that profiles datasets, aggregates metrics, renders custom visual plots, and compiles full business reports using Gemini models.
*   **Key Tech Stack**: Python, Google Agent Development Kit (ADK), Model Context Protocol (MCP) with FastMCP, Streamlit, Pandas, Matplotlib.

## 2. Technical Architecture & Design Decisions
*   **Multi-Agent Collaborative Pipeline**:
    *   *Coordinator*: Sequencing execution and passing state.
    *   *Data Cleaning Agent*: Verifying dataset shapes, profiling data types, and checking missing cells.
    *   *Insight Agent*: Aggregating transaction values, category performance, monthly trend graphs, and drafting qualitative observations.
    *   *Report Agent*: Compiling structured markdown summaries and exporting final deliverables.
*   **Decoupled Tool Access via MCP**:
    *   Why MCP? Emphasize the security and decoupling benefit—the LLM cannot run arbitrary python code on the host machine. It can only query specific dataset metrics through pre-approved tools (`get_dataset_summary()`, `get_sales_metrics()`) exposed by the MCP server.
    *   Implementation details: Launching the MCP server as a subprocess using an asynchronous Stdio Client.

## 3. Engineering Challenges & How We Solved Them
*   **Streamlit Event Loop Nesting**:
    *   *Problem*: Streamlit runs on its own event loop, which can conflict with nested asynchronous client calls (like the MCP client).
    *   *Solution*: Using `nest_asyncio` and custom event loop checking patterns in the MCP client helper.
*   **Web-Safe Visualizations**:
    *   *Problem*: Running Matplotlib GUI threads inside web servers leads to hangs and thread-safety warnings.
    *   *Solution*: Forcing the non-interactive `Agg` backend (`matplotlib.use('Agg')`) in the visualization skill.
*   **Prompt Injection & Safety**:
    *   *Mitigation*: Restricting upload formats strictly to `.csv`, limiting files to 10MB, and using explicit system instructions to restrict agent scopes to sales analysis.

## 4. Key Results & Performance
*   **Accuracy**: Direct calculation of total revenue and products is handled by Pandas (via MCP tools) rather than the LLM, eliminating hallucination risks for numerical calculations.
*   **Usability**: A business owner can upload a dataset and get an executive report, including trend graphs, in less than 45 seconds.
*   **Deployability**: Low footprint, runs smoothly on Streamlit Community Cloud without needing heavy Docker setups.

## 5. Future Directions
*   **Database MCP integration**: Connecting the MCP server to PostgreSQL or Shopify APIs instead of static CSVs.
*   **Advanced visualizations**: Transitioning from Matplotlib to interactive Plotly charts.
*   **Predictive Analysis**: Equipping the Insight Agent with statistical forecasting models (like ARIMA or Prophet) to project future revenue trends.
