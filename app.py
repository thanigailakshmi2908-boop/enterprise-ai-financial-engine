import gradio as gr
import duckdb
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai

# 1. High-Performance Dataset Generation (10,000 Enterprise Records)
np.random.seed(42)
n = 10000
df = pd.DataFrame({
    'Transaction_ID': range(1, n + 1),
    'Region': np.random.choice(['North', 'South', 'East', 'West'], n),
    'Category': np.random.choice(['Electronics', 'Clothing', 'Grocery', 'Home & Kitchen'], n),
    'Sales': np.random.exponential(scale=150, size=n).round(2),
    'Profit': np.random.normal(loc=25, scale=60, size=n).round(2),
    'Customer_Rating': np.random.uniform(1.0, 5.0, size=n).round(1)
})

con = duckdb.connect(database=':memory:')
con.register('sales_data', df)

# 2. Base Metric Aggregations
kpis = con.execute("""
    SELECT 
        SUM(Sales) as total_sales, 
        AVG(Profit) as avg_profit, 
        COUNT(*) as total_txns, 
        AVG(Customer_Rating) as avg_rating,
        SUM(CASE WHEN Profit < 0 THEN 1 ELSE 0 END) as loss_txns
    FROM sales_data
""").df().iloc[0]

# 3. Enterprise Responsive CSS
custom_css = """
.gradio-container {
    font-family: 'Inter', sans-serif;
}
table {
    width: 100% !important;
    border-collapse: collapse !important;
}
th, td {
    padding: 10px 12px !important;
    text-align: left !important;
    word-break: normal !important;
}
@media (max-width: 768px) {
    table {
        display: block;
        overflow-x: auto;
        white-space: nowrap;
    }
}
"""

# 4. Analytical Visualization Engine
def build_analytics_charts():
    reg_df = con.execute("""
        SELECT Region, ROUND(SUM(Sales),2) as Sales, ROUND(SUM(Profit),2) as Profit,
               ROUND((SUM(Profit)/SUM(Sales))*100, 2) as Margin_Pct
        FROM sales_data GROUP BY Region ORDER BY Margin_Pct DESC
    """).df()
    
    fig_margin = px.bar(
        reg_df, x='Region', y='Margin_Pct', color='Region', text='Margin_Pct',
        title="<b>Regional Profit Margin (%) Leaderboard</b>",
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig_margin.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig_margin.update_layout(showlegend=False, height=380, margin=dict(t=40, b=20, l=20, r=20))

    cat_df = con.execute("""
        SELECT Category, Region, ROUND(SUM(Profit),2) as Profit 
        FROM sales_data GROUP BY Category, Region
    """).df()
    
    fig_sunburst = px.sunburst(
        cat_df, path=['Category', 'Region'], values='Profit',
        title="<b>Granular Profit Hierarchy by Category & Region</b>"
    )
    fig_sunburst.update_layout(height=380, margin=dict(t=40, b=20, l=20, r=20))
    
    return fig_margin, fig_sunburst

# 5. Advanced What-If Simulation Engine
def run_scenario_simulation(price_increase, loss_reduction_pct):
    base_sales = kpis['total_sales']
    base_profit = con.execute("SELECT SUM(Profit) FROM sales_data").fetchone()[0]
    loss_amount = con.execute("SELECT ABS(SUM(Profit)) FROM sales_data WHERE Profit < 0").fetchone()[0]
    
    added_revenue = base_sales * (price_increase / 100.0)
    recovered_loss = loss_amount * (loss_reduction_pct / 100.0)
    new_profit = base_profit + added_revenue + recovered_loss
    new_margin = (new_profit / (base_sales + added_revenue)) * 100.0
    profit_growth = ((new_profit - base_profit) / base_profit) * 100.0
    
    fig_waterfall = go.Figure(go.Waterfall(
        name="Simulation", orientation="v",
        measure=["relative", "relative", "relative", "total"],
        x=["Baseline Profit", "Pricing Adjustment", "Loss Mitigation", "Simulated Target"],
        textposition="outside",
        text=[f"${base_profit:,.0f}", f"+${added_revenue:,.0f}", f"+${recovered_loss:,.0f}", f"${new_profit:,.0f}"],
        y=[base_profit, added_revenue, recovered_loss, 0],
        connector={"line":{"color":"rgb(63, 63, 63)"}},
    ))
    fig_waterfall.update_layout(title="<b>Simulated Profit Impact Waterfall</b>", height=380, margin=dict(t=40, b=20, l=20, r=20))
    
    summary_md = f"""
    ### 🎯 Simulation Impact Summary
    * **New Net Profit:** `${new_profit:,.2f}` (**+{profit_growth:.1f}%** increase)
    * **Optimized Margin:** **{new_margin:.2f}%** (Baseline: {((base_profit/base_sales)*100):.2f}%)
    * **Additional Capital Generated:** `${(added_revenue + recovered_loss):,.2f}`
    """
    return summary_md, fig_waterfall

# 6. Enterprise AI Orchestrator Core
def run_ai_analytics(user_query, api_key):
    api_key = api_key.strip() if api_key else ""
    if not api_key:
        return "⚠️ **Error:** Please input your active Gemini API key from Google AI Studio."
    
    gemini_models = ['gemini-3.6-flash', 'gemini-3.5-lite', 'gemini-3.1-pro-preview']
    
    sec_perf = con.execute("""
        SELECT Category, Region, COUNT(*) as Orders,
               ROUND(SUM(Sales), 2) as Revenue, ROUND(SUM(Profit), 2) as Profit,
               ROUND((SUM(Profit)/SUM(Sales))*100, 2) as Margin_Pct
        FROM sales_data GROUP BY Category, Region ORDER BY Profit DESC
    """).df()

genai.configure(api_key=api_key)

        prompt = f"""You are an elite Enterprise Chief Data Scientist & Commercial Operations Strategist. Analyze this complete transactional performance matrix:
    {sec_perf_to_string()}
    User Question / Custom Focus: {user_query if user_query.strip() else 'Provide a complete cross-regional profit leak diagnosis and high-ROI execution roadmap.'}
    Deliver a rigorous enterprise executive report structure using clean Markdown tables (`| Col | Col |`) for all financial models and metrics.
    """



    errors = []
    for model in gemini_models:
        try:
    model_instance = genai.GenerativeModel(model)
    response = model_instance.generate_content(prompt)
    return f"### Enterprise Strategic AI Briefing ({model} Engine)\n\n" + response.text

        except Exception as e:
            errors.append(f"`{model}` error: {str(e)}")

    return "❌ **Analytics Execution Error:**\n\n" + "\n\n".join(errors)

# 7. Gradio Block Layout
with gr.Blocks(theme=gr.themes.Soft(primary_hue="cyan"), css=custom_css) as app:
    gr.Markdown("# 🧠 Enterprise AI Analytics & Financial Growth Engine")
    gr.Markdown("**Developer:** Deepak | **Tech Stack:** DuckDB + Plotly + Gemini Multi-Model API + Gradio")
    
    with gr.Row():
        gr.Number(value=round(kpis['total_sales'], 2), label="Total Revenue ($)", interactive=False)
        gr.Number(value=round(kpis['avg_profit'], 2), label="Avg Profit / Order ($)", interactive=False)
        gr.Number(value=int(kpis['total_txns']), label="Total Orders Processed", interactive=False)
        gr.Number(value=int(kpis['loss_txns']), label="Unprofitable Leakage Orders", interactive=False)
        gr.Number(value=round(kpis['avg_rating'], 1), label="Avg Customer Rating", interactive=False)
        
    with gr.Tabs():
        with gr.TabItem("🤖 AI Strategic Report & Diagnostics"):
            with gr.Row():
                api_input = gr.Textbox(label="🔑 Gemini API Key", placeholder="Paste active AI Studio key...", type="password")
                query_input = gr.Textbox(label="💬 Custom Analytical Focus", placeholder="e.g., Identify exact margin gaps and provide a 90-day turnaround plan.")
            
            btn_ai = gr.Button("🔍 Execute Deep AI Strategic Growth Analysis", variant="primary")
            output_text = gr.Markdown(label="📊 Comprehensive Strategic Report")
            btn_ai.click(fn=run_ai_analytics, inputs=[query_input, api_input], outputs=output_text)

        with gr.TabItem("📈 Interactive Visual Dashboards"):
            btn_chart = gr.Button("🔄 Render Multi-Variable Analytics Charts", variant="secondary")
            with gr.Row():
                chart1 = gr.Plot(label="Margin Leaderboard")
                chart2 = gr.Plot(label="Profit Hierarchy Sunburst")
            btn_chart.click(fn=build_analytics_charts, outputs=[chart1, chart2])

        with gr.TabItem("🎛️ What-If Profit Simulator"):
            gr.Markdown("### Dynamic Executive Scenario Planning & Sensitivity Controls")
            with gr.Row():
                price_slider = gr.Slider(0.0, 10.0, value=2.0, step=0.5, label="Pricing Lift Across Underperforming Categories (%)")
                loss_slider = gr.Slider(0.0, 100.0, value=50.0, step=5.0, label="Unprofitable Order Mitigation Target (%)")
            
            btn_sim = gr.Button("⚡ Run Financial Simulation Engine", variant="primary")
            with gr.Row():
                sim_md = gr.Markdown()
                sim_plot = gr.Plot()
            btn_sim.click(fn=run_scenario_simulation, inputs=[price_slider, loss_slider], outputs=[sim_md, sim_plot])

# Generates a free public live link in Google Colab instantly

app.launch(server_name="0.0.0.0", server_port=5000, share=False, debug=False, inline=False)
