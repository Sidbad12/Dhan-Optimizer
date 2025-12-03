from __future__ import annotations

import json
from datetime import date, timedelta
from functools import lru_cache

import altair as alt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import numpy as np

from src.database import get_supabase_client
from src.settings import RESULTS_TABLE as SUPABASE_TABLE_NAME
from dotenv import load_dotenv
load_dotenv()


st.set_page_config(
    page_title="Dhan Optimizer Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Prophet-based Portfolio Optimization Dashboard"
    }
)


st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Chonburi&family=Domine:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet">
""", unsafe_allow_html=True)


st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    button[kind="header"] {
        display: none !important;
    }
    
    .main .block-container {
        max-width: 100% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    * {
        font-family: 'Domine', Georgia, serif !important;
    }
    
    html, body, [class*="css"], p, span, div, label {
        font-family: 'Domine', Georgia, serif !important;
    }
    
    .main-header {
        font-family: 'Chonburi', cursive !important;
        font-size: 3.5rem !important;
        font-weight: 400 !important;
        background: linear-gradient(120deg, #2E7D32, #66BB6A) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        margin-bottom: 0.5rem !important;
        letter-spacing: 0.02em !important;
    }
    
    .sub-header {
        font-family: 'Domine', serif !important;
        color: #666 !important;
        font-size: 1.15rem !important;
        font-weight: 400 !important;
        margin-bottom: 2rem !important;
        letter-spacing: 0.01em !important;
    }

    .metric-card {
        font-family: 'Domine', serif !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        padding: 1.5rem !important;
        border-radius: 10px !important;
        color: white !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }

    .positive {
        font-family: 'Domine', serif !important;
        color: #2E7D32 !important;
        font-weight: 700 !important;
    }
    .negative {
        font-family: 'Domine', serif !important;
        color: #C62828 !important;
        font-weight: 700 !important;
    }
    
    .stTab, [data-baseweb="tab"], button[role="tab"] {
        font-family: 'Domine', serif !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }

    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {
        font-family: 'Domine', serif !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.02em !important;
    }
    
    [data-testid="stMetricValue"], [data-testid="stMetricValue"] * {
        font-family: 'Domine', serif !important;
        font-weight: 700 !important;
    }
    
    h1, h2, h3, h4, h5, h6,
    .css-10trblm, .css-16huue1, 
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] h4 {
        font-family: 'Chonburi', cursive !important;
        font-weight: 400 !important;
    }
    
    .stDataFrame th, 
    [data-testid="stDataFrame"] th,
    table thead th {
        font-family: 'Chonburi', cursive !important;
        font-weight: 400 !important;
        letter-spacing: 0.03em !important;
    }
    
    .stDataFrame td, 
    [data-testid="stDataFrame"] td,
    table tbody td {
        font-family: 'Domine', serif !important;
    }
    
    .stButton > button, 
    button, 
    [data-testid="baseButton-secondary"],
    [data-testid="baseButton-primary"] {
        font-family: 'Domine', serif !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em !important;
    }
    
    .stSelectbox, .stSelectbox *, 
    [data-baseweb="select"] *,
    input, select, textarea {
        font-family: 'Domine', serif !important;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)
def load_supabase_predictions() -> pd.DataFrame:
    """Return latest Supabase rows (one per ticker per date)."""
    client = get_supabase_client()
    if client is None:
        st.error("Cannot connect to Supabase. Check credentials.")
        return pd.DataFrame()

    try:
        response = (
            client.table(SUPABASE_TABLE_NAME)
            .select("*")
            .order("as_of_date", desc=True)
            .order("created_at", desc=True)
            .execute()
        )
        data = getattr(response, "data", None)
        
        if not data:
            st.warning("No data returned from Supabase")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        
        if "as_of_date" in df.columns:
            df["as_of_date"] = pd.to_datetime(df["as_of_date"]).dt.date
        if "created_at" in df.columns:
            df["created_at"] = pd.to_datetime(df["created_at"])

        df = df.sort_values(["as_of_date", "created_at"], ascending=[True, False])
        df = df.drop_duplicates(subset=["as_of_date", "ticker"], keep="first")

        if "actual_prices_last_month" in df.columns:
            df["actual_prices_last_month"] = df["actual_prices_last_month"].apply(_parse_price_history)

        return df
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()


def _parse_price_history(raw: object) -> list[float]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [float(value) for value in raw]
    if isinstance(raw, str):
        try:
            decoded = json.loads(raw)
        except json.JSONDecodeError:
            return []
        if isinstance(decoded, list):
            return [float(value) for value in decoded]
    return []


def _latest_actual_price(row: pd.Series) -> float | None:
    prices = row.get("actual_prices_last_month", [])
    if prices:
        return float(prices[-1])
    return None


def _latest_price_from_row(row: pd.Series) -> float | None:
    prices = row.get("actual_prices_last_month")
    if isinstance(prices, list) and prices:
        return float(prices[-1])
    return None


@lru_cache(maxsize=1)
def compute_prediction_performance(data_json: str) -> pd.DataFrame:
    """Compare past predictions against actual outcomes using successive days."""
    from io import StringIO
    df = pd.read_json(StringIO(data_json), orient="records", convert_dates=False)
    if df.empty:
        return df

    df["as_of_date"] = pd.to_datetime(df["as_of_date"]).dt.date
    if "actual_prices_last_month" in df.columns:
        df["actual_prices_last_month"] = df["actual_prices_last_month"].apply(_parse_price_history)
    df = df.sort_values(["ticker", "as_of_date"])

    records: list[dict[str, object]] = []

    for ticker, group in df.groupby("ticker"):
        group = group.reset_index(drop=True)
        for idx in range(len(group) - 1):
            current = group.loc[idx]

            prices = current.get("actual_prices_last_month")
            if not prices:
                continue

            next_row = group.loc[idx + 1]
            actual_next_price = _latest_price_from_row(next_row)
            if actual_next_price is None:
                continue

            records.append(
                {
                    "ticker": ticker,
                    "prediction_date": current["as_of_date"],
                    "evaluation_date": next_row["as_of_date"],
                    "predicted_price": float(current["predicted_price"]),
                    "actual_price": actual_next_price,
                    "error": actual_next_price - float(current["predicted_price"]),
                }
            )

    perf_df = pd.DataFrame(records)
    if perf_df.empty:
        return perf_df

    perf_df["absolute_error"] = perf_df["error"].abs()
    perf_df["error_pct"] = perf_df["error"] / perf_df["predicted_price"]
    return perf_df


def calculate_portfolio_metrics(date_df: pd.DataFrame, perf_df: pd.DataFrame) -> dict:
    """Calculate key portfolio metrics."""
    metrics = {}
    
    # Portfolio expected return
    if "predicted_return" in date_df.columns and "portfolio_weight" in date_df.columns:
        date_df["predicted_return"] = pd.to_numeric(date_df["predicted_return"], errors="coerce")
        date_df["portfolio_weight"] = pd.to_numeric(date_df["portfolio_weight"], errors="coerce")
        metrics["expected_return"] = (date_df["predicted_return"] * date_df["portfolio_weight"]).sum()
    
    # Prediction accuracy
    if not perf_df.empty:
        metrics["mae"] = perf_df["absolute_error"].mean()
        metrics["mape"] = (perf_df["error_pct"].abs() * 100).mean()
        metrics["prediction_accuracy"] = 100 - metrics["mape"]
    
    # Portfolio concentration (Herfindahl index)
    if "portfolio_weight" in date_df.columns:
        weights = date_df["portfolio_weight"].fillna(0)
        metrics["concentration"] = (weights ** 2).sum()
    
    # Number of holdings
    if "portfolio_weight" in date_df.columns:
        metrics["num_holdings"] = (date_df["portfolio_weight"] > 0.01).sum()
    
    return metrics


def create_portfolio_sunburst(date_df: pd.DataFrame):
    """Create a sunburst chart for portfolio allocation."""
    chart_df = date_df[["ticker", "portfolio_weight"]].copy()
    chart_df["portfolio_weight"] = pd.to_numeric(chart_df["portfolio_weight"], errors="coerce")
    chart_df = chart_df.dropna(subset=["portfolio_weight"])
    chart_df = chart_df[chart_df["portfolio_weight"] > 0]
    
    if chart_df.empty:
        return None
    
    chart_df["parent"] = "Portfolio"
    
    fig = go.Figure(go.Sunburst(
        labels=list(chart_df["ticker"]) + ["Portfolio"],
        parents=list(chart_df["parent"]) + [""],
        values=list(chart_df["portfolio_weight"]) + [chart_df["portfolio_weight"].sum()],
        branchvalues="total",
        marker=dict(
            colorscale='Viridis',
            cmid=chart_df["portfolio_weight"].mean()
        ),
        hovertemplate='<b>%{label}</b><br>Weight: %{value:.2%}<extra></extra>',
    ))
    
    fig.update_layout(
        height=500,
        margin=dict(t=0, l=0, r=0, b=0)
    )
    
    return fig


def create_gauge_chart(value: float, title: str, max_value: float = 100):
    """Create a gauge chart for metrics."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 20}},
        gauge={
            'axis': {'range': [None, max_value], 'tickwidth': 1},
            'bar': {'color': "#2E7D32"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, max_value * 0.33], 'color': '#ffebee'},
                {'range': [max_value * 0.33, max_value * 0.66], 'color': '#fff9c4'},
                {'range': [max_value * 0.66, max_value], 'color': '#c8e6c9'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_value * 0.9
            }
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(t=50, b=0, l=20, r=20)
    )
    
    return fig


def create_correlation_heatmap(date_df: pd.DataFrame, all_data: pd.DataFrame):
    """Create correlation heatmap for portfolio stocks."""
    # Get tickers from current portfolio
    tickers = date_df["ticker"].unique()
    
    # Filter historical data for these tickers
    ticker_data = all_data[all_data["ticker"].isin(tickers)]
    
    if "predicted_return" not in ticker_data.columns or ticker_data.empty:
        return None
    
    # Create pivot table of returns
    returns_pivot = ticker_data.pivot_table(
        index="as_of_date",
        columns="ticker",
        values="predicted_return"
    )
    
    if returns_pivot.shape[1] < 2:
        return None
    
    # Calculate correlation
    corr = returns_pivot.corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.columns,
        colorscale='RdYlGn',
        zmid=0,
        text=np.round(corr.values, 2),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Correlation")
    ))
    
    fig.update_layout(
        title="Portfolio Correlation Matrix",
        height=500,
        xaxis={'side': 'bottom'},
    )
    
    return fig


def create_treemap(date_df: pd.DataFrame):
    """Create treemap for portfolio allocation."""
    chart_df = date_df[["ticker", "portfolio_weight", "predicted_return"]].copy()
    chart_df["portfolio_weight"] = pd.to_numeric(chart_df["portfolio_weight"], errors="coerce")
    chart_df["predicted_return"] = pd.to_numeric(chart_df["predicted_return"], errors="coerce")
    chart_df = chart_df.dropna()
    chart_df = chart_df[chart_df["portfolio_weight"] > 0]
    
    if chart_df.empty:
        return None
    
    # Color by predicted return
    fig = px.treemap(
        chart_df,
        path=[px.Constant("Portfolio"), "ticker"],
        values="portfolio_weight",
        color="predicted_return",
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=0,
        hover_data={
            "portfolio_weight": ":.2%",
            "predicted_return": ":.2%"
        }
    )
    
    fig.update_traces(
        textinfo="label+value",
        texttemplate="<b>%{label}</b><br>%{value:.1%}",
        hovertemplate="<b>%{label}</b><br>Weight: %{value:.2%}<br>Expected Return: %{color:.2%}<extra></extra>"
    )
    
    fig.update_layout(
        height=500,
        margin=dict(t=50, l=25, r=25, b=25)
    )
    
    return fig


def create_performance_comparison(perf_df: pd.DataFrame, selected_ticker: str):
    """Create performance comparison chart."""
    ticker_perf = perf_df[perf_df["ticker"] == selected_ticker].copy()
    
    if ticker_perf.empty:
        return None
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Price Prediction vs Actual", "Prediction Error Over Time"),
        vertical_spacing=0.15,
        row_heights=[0.6, 0.4]
    )
    
    # Price comparison
    fig.add_trace(
        go.Scatter(
            x=ticker_perf["evaluation_date"],
            y=ticker_perf["actual_price"],
            name="Actual",
            mode="lines+markers",
            line=dict(color="#2E7D32", width=2),
            marker=dict(size=8)
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=ticker_perf["evaluation_date"],
            y=ticker_perf["predicted_price"],
            name="Predicted",
            mode="lines+markers",
            line=dict(color="#FF6F00", width=2, dash="dash"),
            marker=dict(size=8, symbol="diamond")
        ),
        row=1, col=1
    )
    
    # Error bars
    colors = ['green' if e < 0 else 'red' for e in ticker_perf["error"]]
    fig.add_trace(
        go.Bar(
            x=ticker_perf["evaluation_date"],
            y=ticker_perf["error"],
            name="Error",
            marker_color=colors,
            showlegend=False
        ),
        row=2, col=1
    )
    
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Price (₹)", row=1, col=1)
    fig.update_yaxes(title_text="Error (₹)", row=2, col=1)
    
    fig.update_layout(
        height=700,
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig


def run_dashboard() -> None:
    st.markdown('<h1 class="main-header">Dhan Optimizer Dashboard</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">AI-Powered Portfolio Optimization using Prophet Forecasting & Markowitz Theory</p>',
        unsafe_allow_html=True
    )

    df = load_supabase_predictions()
    if df.empty:
        st.info("No prediction data available. Run the optimization pipeline to populate Supabase.")
        return

    st.markdown("---")
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        available_dates = sorted(df["as_of_date"].unique(), reverse=True)
        selected_date = st.selectbox(
            "Select Date",
            options=available_dates,
            format_func=lambda d: d.strftime("%d %B %Y")
        )
    
    with col2:
        total_predictions = len(df)
        st.metric("Total Predictions", f"{total_predictions:,}")
    
    with col3:
        unique_tickers = df["ticker"].nunique()
        st.metric("Unique Stocks", unique_tickers)
    
    with col4:
        date_range = (df["as_of_date"].max() - df["as_of_date"].min()).days
        st.metric("Days of Data", date_range)
    
    st.markdown("---")

    date_df = df[df["as_of_date"] == selected_date].copy().sort_values("ticker")
    perf_df = compute_prediction_performance(df.to_json(orient="records", date_format="iso"))

    metrics = calculate_portfolio_metrics(date_df, perf_df)
    st.markdown("### Portfolio Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        expected_return = metrics.get("expected_return", 0) * 100
        delta_color = "normal" if expected_return >= 0 else "inverse"
        st.metric(
            "Expected Return",
            f"{expected_return:.2f}%",
            delta=f"{expected_return:.2f}%",
            delta_color=delta_color
        )
    
    with col2:
        accuracy = metrics.get("prediction_accuracy", 0)
        st.metric("Prediction Accuracy", f"{accuracy:.1f}%")
    
    with col3:
        num_holdings = metrics.get("num_holdings", 0)
        st.metric("Active Holdings", int(num_holdings))
    
    with col4:
        concentration = metrics.get("concentration", 0)
        diversification = (1 - concentration) * 100
        st.metric("Diversification", f"{diversification:.1f}%")

    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["Portfolio Overview", " Stock Analysis", "Performance", "Advanced"])

    with tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### Portfolio Allocation")
            treemap = create_treemap(date_df)
            if treemap:
                st.plotly_chart(treemap, width='stretch')
            else:
                st.info("No allocation data available")
        
        with col2:
            st.markdown("####  Expected Returns Distribution")
            sunburst = create_portfolio_sunburst(date_df)
            if sunburst:
                st.plotly_chart(sunburst, width='stretch')
            else:
                st.info("No weight data available")
        
        st.markdown("#### Portfolio Holdings")
        summary_table = date_df[["ticker", "predicted_price", "predicted_return", "portfolio_weight"]].copy()
        summary_table["predicted_return"] = summary_table["predicted_return"] * 100
        summary_table["portfolio_weight"] = summary_table["portfolio_weight"] * 100
        summary_table = summary_table.rename(columns={
            "ticker": "Ticker",
            "predicted_price": "Predicted Price (₹)",
            "predicted_return": "Expected Return (%)",
            "portfolio_weight": "Weight (%)"
        })
        
        st.dataframe(
            summary_table,
            hide_index=True,
            width='stretch',
            column_config={
                "Predicted Price (₹)": st.column_config.NumberColumn(format="₹%.2f"),
                "Expected Return (%)": st.column_config.NumberColumn(
                    format="%.2f%%",
                    help="Expected return for next trading day"
                ),
                "Weight (%)": st.column_config.ProgressColumn(
                    format="%.2f%%",
                    min_value=0,
                    max_value=100,
                )
            }
        )

    with tab2:
        tickers = date_df["ticker"].tolist()
        selected_ticker = st.selectbox(" Select Stock", options=tickers, index=0)
        
        ticker_row = date_df.set_index("ticker").loc[selected_ticker]
        latest_actual = _latest_actual_price(ticker_row)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Current Price", f"₹{latest_actual:.2f}" if latest_actual else "—")
        with col2:
            pred_price = ticker_row['predicted_price']
            change = ((pred_price - latest_actual) / latest_actual * 100) if latest_actual else 0
            st.metric("Predicted Price", f"₹{pred_price:.2f}", f"{change:+.2f}%")
        with col3:
            st.metric("Expected Return", f"{ticker_row['predicted_return']*100:.2f}%")
        with col4:
            st.metric("Portfolio Weight", f"{ticker_row['portfolio_weight']*100:.2f}%")
        
        st.markdown("---")
    
        perf_chart = create_performance_comparison(perf_df, selected_ticker)
        if perf_chart:
            st.plotly_chart(perf_chart, width='stretch')
        else:
            st.info("No historical performance data available for this ticker yet.")

    with tab3:
        if not perf_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Prediction Accuracy")
                avg_accuracy = metrics.get("prediction_accuracy", 0)
                gauge = create_gauge_chart(avg_accuracy, "Overall Accuracy (%)")
                st.plotly_chart(gauge, width='stretch')
            
            with col2:
                st.markdown("#### Error Distribution")
                error_dist = px.histogram(
                    perf_df,
                    x="error_pct",
                    nbins=30,
                    title="Prediction Error Distribution",
                    labels={"error_pct": "Error (%)"},
                    color_discrete_sequence=["#2E7D32"]
                )
                error_dist.update_xaxes(tickformat=".1%")
                error_dist.update_layout(height=300)
                st.plotly_chart(error_dist, width='stretch')
            
            # Ticker-wise performance
            st.markdown("#### Stock-wise Performance")
            ticker_stats = perf_df.groupby("ticker").agg({
                "error": "mean",
                "absolute_error": "mean",
                "error_pct": lambda x: (x.abs() * 100).mean()
            }).reset_index()
            
            ticker_stats.columns = ["Ticker", "Avg Error (₹)", "MAE (₹)", "MAPE (%)"]
            ticker_stats = ticker_stats.sort_values("MAPE (%)")
            
            st.dataframe(
                ticker_stats,
                hide_index=True,
                width='stretch',
                column_config={
                    "Avg Error (₹)": st.column_config.NumberColumn(format="₹%.2f"),
                    "MAE (₹)": st.column_config.NumberColumn(format="₹%.2f"),
                    "MAPE (%)": st.column_config.NumberColumn(format="%.2f%%")
                }
            )
        else:
            st.info("No performance data available yet. Check back after multiple optimization runs.")

    with tab4:
        st.markdown("#### Correlation Analysis")
        corr_heatmap = create_correlation_heatmap(date_df, df)
        if corr_heatmap:
            st.plotly_chart(corr_heatmap, width='stretch')
        else:
            st.info("Insufficient data for correlation analysis")
        
        st.markdown("#### Historical Trends")
        historical_returns = df.groupby("as_of_date").agg({
            "predicted_return": lambda x: (x * df.loc[x.index, "portfolio_weight"]).sum()
        }).reset_index()
        
        if not historical_returns.empty:
            historical_returns.columns = ["Date", "Portfolio Return"]
            historical_returns["Cumulative Return"] = (1 + historical_returns["Portfolio Return"]).cumprod() - 1
            
            fig = px.line(
                historical_returns,
                x="Date",
                y="Cumulative Return",
                title="Cumulative Portfolio Return",
                labels={"Cumulative Return": "Return"}
            )
            fig.update_yaxes(tickformat=".1%")
            fig.update_traces(line_color="#2E7D32", line_width=3)
            st.plotly_chart(fig, width='stretch')

def main() -> None:
    run_dashboard()


if __name__ == "__main__":
    main()