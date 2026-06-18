import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Retail Sales Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
}
[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {
    background-color: #3b82f6 !important;
}

/* Main background */
.main { background-color: #f8fafc; }

/* Header */
.dashboard-header {
    background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 60%, #0ea5e9 100%);
    padding: 2rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 24px rgba(15,23,42,0.18);
}
.dashboard-header h1 {
    color: white;
    font-size: 2rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.5px;
}
.dashboard-header p {
    color: #93c5fd;
    margin: 0.3rem 0 0 0;
    font-size: 0.95rem;
}

/* KPI Cards */
.kpi-card {
    background: white;
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    box-shadow: 0 2px 12px rgba(15,23,42,0.07);
    border-left: 4px solid;
    transition: transform 0.2s;
}
.kpi-card:hover { transform: translateY(-2px); }
.kpi-label {
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748b;
    margin-bottom: 0.4rem;
}
.kpi-value {
    font-size: 2rem;
    font-weight: 700;
    color: #0f172a;
    line-height: 1;
}
.kpi-delta {
    font-size: 0.82rem;
    margin-top: 0.4rem;
    font-weight: 500;
}

/* Chart cards */
.chart-card {
    background: white;
    border-radius: 14px;
    padding: 1.4rem;
    box-shadow: 0 2px 12px rgba(15,23,42,0.07);
    margin-bottom: 1rem;
}
.chart-title {
    font-size: 1rem;
    font-weight: 600;
    color: #0f172a;
    margin-bottom: 0.8rem;
}

/* Insight badges */
.insight-box {
    background: linear-gradient(135deg, #eff6ff, #dbeafe);
    border: 1px solid #bfdbfe;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
    font-size: 0.88rem;
    color: #1e40af;
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
}

/* Section headers */
.section-header {
    font-size: 1.1rem;
    font-weight: 700;
    color: #0f172a;
    margin: 1.5rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #e2e8f0;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── Load Data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("superstore_clean.csv", parse_dates=["Order Date", "Ship Date"])
    df["Year"] = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.to_period("M").astype(str)
    df["Month_dt"] = df["Order Date"].dt.to_period("M").dt.to_timestamp()
    df["Profit Margin %"] = (df["Profit"] / df["Sales"] * 100).round(2)
    return df

df = load_data()

# ── Sidebar Filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛️ Filters")
    st.markdown("---")

    years = sorted(df["Year"].unique())
    selected_years = st.multiselect("📅 Year", years, default=years)

    regions = sorted(df["Region"].unique())
    selected_regions = st.multiselect("🌍 Region", regions, default=regions)

    categories = sorted(df["Category"].unique())
    selected_categories = st.multiselect("📦 Category", categories, default=categories)

    segments = sorted(df["Segment"].unique())
    selected_segments = st.multiselect("👥 Segment", segments, default=segments)

    st.markdown("---")
    st.markdown("**👨‍💻 Author:** Adil Sujaoddin Maniyar")
    st.markdown("**📊 Dataset:** US Superstore 2014–2017")

# ── Filter Data ───────────────────────────────────────────────────────────────
fdf = df[
    df["Year"].isin(selected_years) &
    df["Region"].isin(selected_regions) &
    df["Category"].isin(selected_categories) &
    df["Segment"].isin(selected_segments)
]

# ── Color Palette ─────────────────────────────────────────────────────────────
PALETTE = ["#1d4ed8", "#0ea5e9", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444", "#ec4899"]
REGION_COLORS = {"West": "#1d4ed8", "East": "#0ea5e9", "Central": "#8b5cf6", "South": "#10b981"}
CAT_COLORS = {"Technology": "#1d4ed8", "Office Supplies": "#0ea5e9", "Furniture": "#8b5cf6"}

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="dashboard-header">
    <h1>🛒 AI-Powered Retail Sales Dashboard</h1>
    <p>Real-time analytics · US Superstore · 2014 – 2017</p>
</div>
""", unsafe_allow_html=True)

# ── KPI Cards ─────────────────────────────────────────────────────────────────
total_sales   = fdf["Sales"].sum()
total_profit  = fdf["Profit"].sum()
total_orders  = fdf["Order ID"].nunique()
total_qty     = fdf["Quantity"].sum()
avg_margin    = (total_profit / total_sales * 100) if total_sales > 0 else 0
avg_discount  = fdf["Discount"].mean() * 100

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(f"""
    <div class="kpi-card" style="border-color:#1d4ed8;">
        <div class="kpi-label">💰 Total Sales</div>
        <div class="kpi-value">${total_sales:,.0f}</div>
        <div class="kpi-delta" style="color:#1d4ed8;">{len(fdf):,} transactions</div>
    </div>""", unsafe_allow_html=True)

with kpi2:
    profit_color = "#10b981" if total_profit >= 0 else "#ef4444"
    st.markdown(f"""
    <div class="kpi-card" style="border-color:{profit_color};">
        <div class="kpi-label">📈 Total Profit</div>
        <div class="kpi-value">${total_profit:,.0f}</div>
        <div class="kpi-delta" style="color:{profit_color};">Margin: {avg_margin:.1f}%</div>
    </div>""", unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="kpi-card" style="border-color:#8b5cf6;">
        <div class="kpi-label">📦 Total Orders</div>
        <div class="kpi-value">{total_orders:,}</div>
        <div class="kpi-delta" style="color:#8b5cf6;">{fdf['Customer ID'].nunique():,} unique customers</div>
    </div>""", unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="kpi-card" style="border-color:#f59e0b;">
        <div class="kpi-label">🛍️ Units Sold</div>
        <div class="kpi-value">{total_qty:,}</div>
        <div class="kpi-delta" style="color:#f59e0b;">Avg discount: {avg_discount:.1f}%</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 1: Monthly Trend + Sales by Region ────────────────────────────────────
st.markdown('<div class="section-header">📊 Sales Performance</div>', unsafe_allow_html=True)

col_trend, col_region = st.columns([2, 1])

with col_trend:
    monthly = (fdf.groupby(["Month_dt", "Category"])["Sales"]
               .sum().reset_index().sort_values("Month_dt"))
    fig_trend = px.area(
        monthly, x="Month_dt", y="Sales", color="Category",
        color_discrete_map=CAT_COLORS,
        labels={"Month_dt": "Month", "Sales": "Sales ($)"},
        title="Monthly Sales Trend by Category",
    )
    fig_trend.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font_family="Inter", title_font_size=14,
        legend=dict(orientation="h", y=1.1, x=0),
        margin=dict(t=50, b=20, l=0, r=0),
        hovermode="x unified",
    )
    fig_trend.update_xaxes(showgrid=False)
    fig_trend.update_yaxes(showgrid=True, gridcolor="#f1f5f9")
    st.plotly_chart(fig_trend, use_container_width=True)

with col_region:
    region_data = fdf.groupby("Region")["Sales"].sum().reset_index()
    fig_region = px.pie(
        region_data, names="Region", values="Sales",
        color="Region", color_discrete_map=REGION_COLORS,
        title="Sales by Region",
        hole=0.45,
    )
    fig_region.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font_family="Inter", title_font_size=14,
        margin=dict(t=50, b=10, l=0, r=0),
        legend=dict(orientation="h", y=-0.1),
    )
    fig_region.update_traces(textposition="outside", textinfo="percent+label")
    st.plotly_chart(fig_region, use_container_width=True)

# ── Row 2: Category + Sub-Category Profit ─────────────────────────────────────
col_cat, col_sub = st.columns(2)

with col_cat:
    cat_data = fdf.groupby("Category").agg(Sales=("Sales","sum"), Profit=("Profit","sum")).reset_index()
    fig_cat = go.Figure()
    fig_cat.add_trace(go.Bar(name="Sales", x=cat_data["Category"], y=cat_data["Sales"],
                             marker_color="#1d4ed8", opacity=0.85))
    fig_cat.add_trace(go.Bar(name="Profit", x=cat_data["Category"], y=cat_data["Profit"],
                             marker_color="#10b981", opacity=0.85))
    fig_cat.update_layout(
        barmode="group", title="Sales & Profit by Category",
        plot_bgcolor="white", paper_bgcolor="white",
        font_family="Inter", title_font_size=14,
        legend=dict(orientation="h", y=1.1),
        margin=dict(t=50, b=20, l=0, r=0),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
        xaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig_cat, use_container_width=True)

with col_sub:
    sub_profit = (fdf.groupby("Sub-Category")["Profit"].sum()
                  .reset_index().sort_values("Profit"))
    sub_profit["Color"] = sub_profit["Profit"].apply(lambda x: "#ef4444" if x < 0 else "#10b981")
    fig_sub = go.Figure(go.Bar(
        x=sub_profit["Profit"], y=sub_profit["Sub-Category"],
        orientation="h",
        marker_color=sub_profit["Color"],
        text=sub_profit["Profit"].apply(lambda x: f"${x:,.0f}"),
        textposition="outside",
    ))
    fig_sub.update_layout(
        title="Profit by Sub-Category",
        plot_bgcolor="white", paper_bgcolor="white",
        font_family="Inter", title_font_size=14,
        margin=dict(t=50, b=20, l=0, r=10),
        xaxis=dict(showgrid=True, gridcolor="#f1f5f9", zeroline=True, zerolinecolor="#94a3b8"),
        yaxis=dict(showgrid=False),
        height=480,
    )
    st.plotly_chart(fig_sub, use_container_width=True)

# ── Row 3: Top 10 Products + Segment Analysis ─────────────────────────────────
st.markdown('<div class="section-header">🏆 Products & Segments</div>', unsafe_allow_html=True)

col_top, col_seg = st.columns([3, 2])

with col_top:
    top10 = (fdf.groupby("Product Name")
             .agg(Sales=("Sales","sum"), Profit=("Profit","sum"))
             .nlargest(10, "Sales").reset_index())
    top10["Short Name"] = top10["Product Name"].str[:40] + "..."
    fig_top = go.Figure()
    fig_top.add_trace(go.Bar(
        y=top10["Short Name"], x=top10["Sales"],
        orientation="h", name="Sales",
        marker=dict(color=top10["Sales"], colorscale="Blues"),
        text=top10["Sales"].apply(lambda x: f"${x:,.0f}"),
        textposition="outside",
    ))
    fig_top.update_layout(
        title="Top 10 Products by Sales",
        plot_bgcolor="white", paper_bgcolor="white",
        font_family="Inter", title_font_size=14,
        margin=dict(t=50, b=20, l=10, r=60),
        xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
        yaxis=dict(showgrid=False, autorange="reversed"),
        height=420,
    )
    st.plotly_chart(fig_top, use_container_width=True)

with col_seg:
    seg_data = fdf.groupby("Segment").agg(
        Sales=("Sales","sum"),
        Profit=("Profit","sum"),
        Orders=("Order ID","nunique")
    ).reset_index()
    fig_seg = px.scatter(
        seg_data, x="Sales", y="Profit",
        size="Orders", color="Segment",
        color_discrete_sequence=PALETTE,
        text="Segment",
        title="Segment: Sales vs Profit (bubble = orders)",
        size_max=60,
    )
    fig_seg.update_traces(textposition="top center")
    fig_seg.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font_family="Inter", title_font_size=14,
        margin=dict(t=50, b=20, l=0, r=0),
        xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
        height=420,
        showlegend=False,
    )
    st.plotly_chart(fig_seg, use_container_width=True)

# ── Row 4: Discount vs Profit Scatter + Regional KPIs ─────────────────────────
st.markdown('<div class="section-header">🔍 Deep Dive Analysis</div>', unsafe_allow_html=True)

col_disc, col_map = st.columns(2)

with col_disc:
    sample = fdf.sample(min(1000, len(fdf)), random_state=42)
    fig_disc = px.scatter(
        sample, x="Discount", y="Profit",
        color="Category", color_discrete_map=CAT_COLORS,
        opacity=0.55,
        title="Discount vs Profit (sampled)",
        trendline="ols",
        labels={"Discount": "Discount Rate", "Profit": "Profit ($)"},
    )
    fig_disc.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font_family="Inter", title_font_size=14,
        margin=dict(t=50, b=20, l=0, r=0),
        xaxis=dict(showgrid=True, gridcolor="#f1f5f9", tickformat=".0%"),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
    )
    st.plotly_chart(fig_disc, use_container_width=True)

with col_map:
    region_detail = fdf.groupby("Region").agg(
        Sales=("Sales","sum"),
        Profit=("Profit","sum"),
        Orders=("Order ID","nunique"),
        Margin=("Profit Margin %","mean")
    ).reset_index().sort_values("Sales", ascending=False)

    fig_reg = go.Figure()
    fig_reg.add_trace(go.Bar(
        x=region_detail["Region"], y=region_detail["Sales"],
        name="Sales", marker_color="#1d4ed8", opacity=0.8,
        yaxis="y"
    ))
    fig_reg.add_trace(go.Scatter(
        x=region_detail["Region"], y=region_detail["Margin"],
        name="Profit Margin %", marker=dict(color="#f59e0b", size=10),
        line=dict(color="#f59e0b", width=2),
        yaxis="y2", mode="lines+markers"
    ))
    fig_reg.update_layout(
        title="Regional Sales & Profit Margin",
        plot_bgcolor="white", paper_bgcolor="white",
        font_family="Inter", title_font_size=14,
        margin=dict(t=50, b=20, l=0, r=60),
        legend=dict(orientation="h", y=1.1),
        yaxis=dict(title="Sales ($)", showgrid=True, gridcolor="#f1f5f9"),
        yaxis2=dict(title="Margin %", overlaying="y", side="right", showgrid=False),
        xaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig_reg, use_container_width=True)

# ── Yearly Growth ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📅 Year-over-Year Growth</div>', unsafe_allow_html=True)

yearly = fdf.groupby("Year").agg(
    Sales=("Sales","sum"), Profit=("Profit","sum"), Orders=("Order ID","nunique")
).reset_index()

fig_yoy = make_subplots(rows=1, cols=3,
    subplot_titles=["Annual Sales ($)", "Annual Profit ($)", "Annual Orders"])

fig_yoy.add_trace(go.Bar(x=yearly["Year"], y=yearly["Sales"],
    marker_color="#1d4ed8", showlegend=False), row=1, col=1)
fig_yoy.add_trace(go.Bar(x=yearly["Year"], y=yearly["Profit"],
    marker_color="#10b981", showlegend=False), row=1, col=2)
fig_yoy.add_trace(go.Bar(x=yearly["Year"], y=yearly["Orders"],
    marker_color="#8b5cf6", showlegend=False), row=1, col=3)

fig_yoy.update_layout(
    plot_bgcolor="white", paper_bgcolor="white",
    font_family="Inter", height=300,
    margin=dict(t=50, b=20, l=0, r=0),
)
for i in range(1, 4):
    fig_yoy.update_xaxes(showgrid=False, row=1, col=i)
    fig_yoy.update_yaxes(showgrid=True, gridcolor="#f1f5f9", row=1, col=i)

st.plotly_chart(fig_yoy, use_container_width=True)

# ── Key Insights ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">💡 Key Insights</div>', unsafe_allow_html=True)

# Calculate dynamic insights
top_cat   = fdf.groupby("Category")["Sales"].sum().idxmax()
top_reg   = fdf.groupby("Region")["Sales"].sum().idxmax()
worst_sub = fdf.groupby("Sub-Category")["Profit"].sum().idxmin()
best_sub  = fdf.groupby("Sub-Category")["Profit"].sum().idxmax()
high_disc = fdf[fdf["Discount"] > 0.3]["Profit"].mean()
low_disc  = fdf[fdf["Discount"] <= 0.3]["Profit"].mean()

insights = [
    f"🏆 <b>{top_cat}</b> is the top-performing category by total sales revenue.",
    f"🌍 The <b>{top_reg}</b> region contributes the highest share of total revenue.",
    f"⚠️ <b>{worst_sub}</b> has the lowest profitability — consider pricing or cost review.",
    f"🥇 <b>{best_sub}</b> is the most profitable sub-category across all regions.",
    f"📉 Orders with >30% discount have an avg profit of <b>${high_disc:,.0f}</b> vs <b>${low_disc:,.0f}</b> for lower discounts — heavy discounting hurts margins.",
]

icol1, icol2 = st.columns(2)
for i, insight in enumerate(insights):
    col = icol1 if i % 2 == 0 else icol2
    with col:
        st.markdown(f'<div class="insight-box">💬 {insight}</div>', unsafe_allow_html=True)

# ── Raw Data Explorer ─────────────────────────────────────────────────────────
with st.expander("📋 View Raw Data"):
    st.dataframe(
        fdf[["Order Date","Region","Category","Sub-Category","Product Name",
             "Segment","Sales","Profit","Quantity","Discount"]]
        .sort_values("Order Date", ascending=False)
        .reset_index(drop=True),
        use_container_width=True,
        height=350,
    )
    st.caption(f"Showing {len(fdf):,} rows based on current filters.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<center style='color:#94a3b8;font-size:0.82rem;'>"
    "AI-Powered Retail Sales Dashboard · Built with Streamlit & Plotly · "
    "👨‍💻 Adil Sujaoddin Maniyar</center>",
    unsafe_allow_html=True
)
