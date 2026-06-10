import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

DB_PATH = "data/database/market_intelligence.db"
LIVE_DB_PATH = "data/database/market_data.db"

st.set_page_config(
    page_title="Market Intelligence Platform",
    layout="wide"
)

# -----------------------------
# Database helpers
# -----------------------------
def load_table(table_name):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df

def load_live_data():
    conn = sqlite3.connect(LIVE_DB_PATH)
    df = pd.read_sql_query(
        """
        SELECT *
        FROM live_market_data
        ORDER BY id DESC
        LIMIT 500
        """,
        conn
    )
    conn.close()
    return df

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("Market Intelligence Platform")

page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Live Market Feed",
        "Market Intelligence",
        "Portfolio Optimization",
        "Correlation Analysis",
        "Backtesting"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("Capstone FinTech Analytics System")

# -----------------------------
# Overview
# -----------------------------
if page == "Overview":

    st.title("Real-Time Market Intelligence Platform")

    st.markdown("""
    This platform integrates historical data, live market streaming, technical indicators,
    forecasting, risk scoring, portfolio optimization, correlation analysis, and strategy backtesting.
    """)

    intelligence_df = load_table("unified_market_intelligence")
    risk_df = load_table("asset_risk_summary")
    optimization_df = load_table("portfolio_optimization_summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Assets Tracked", intelligence_df["asset"].nunique())
    col2.metric("Buy Signals", (intelligence_df["final_recommendation"].str.contains("BUY")).sum())
    col3.metric("High Risk Assets", (risk_df["risk_category"] == "High Risk").sum())

    best_portfolio = optimization_df.sort_values("sharpe_ratio", ascending=False).iloc[0]
    col4.metric("Best Sharpe", round(best_portfolio["sharpe_ratio"], 2))

    st.subheader("Latest Market Intelligence")

    st.dataframe(
        intelligence_df[[
            "asset",
            "asset_type",
            "close",
            "final_recommendation",
            "confidence_level",
            "risk_category",
            "market_stance"
        ]],
        use_container_width=True
    )

# -----------------------------
# Live Market Feed
# -----------------------------
elif page == "Live Market Feed":

    st.title("Live Market Feed")

    live_df = load_live_data()

    if live_df.empty:
        st.warning("No live data found. Start the live crypto stream first.")
    else:
        live_df["timestamp"] = pd.to_datetime(live_df["timestamp"])

        latest_prices = (
            live_df.sort_values("timestamp")
            .groupby("asset")
            .tail(1)
        )

        cols = st.columns(len(latest_prices))

        for i, (_, row) in enumerate(latest_prices.iterrows()):
            cols[i].metric(
                row["asset"],
                f"${row['price']:,.2f}",
                f"Qty {row['quantity']}"
            )

        selected_asset = st.selectbox(
            "Select Asset",
            sorted(live_df["asset"].unique())
        )

        asset_live = live_df[live_df["asset"] == selected_asset].sort_values("timestamp")

        fig = px.line(
            asset_live,
            x="timestamp",
            y="price",
            title=f"Live Price Stream: {selected_asset}"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Latest Trades")
        st.dataframe(live_df.head(100), use_container_width=True)

# -----------------------------
# Market Intelligence
# -----------------------------
elif page == "Market Intelligence":

    st.title("Market Intelligence")

    intelligence_df = load_table("unified_market_intelligence")
    regime_df = load_table("market_regime_summary")

    merged_df = intelligence_df.merge(
        regime_df[["asset", "market_regime"]],
        on="asset",
        how="left"
    )

    asset_type_filter = st.selectbox(
        "Asset Type",
        ["All"] + sorted(merged_df["asset_type"].unique().tolist())
    )

    if asset_type_filter != "All":
        merged_df = merged_df[merged_df["asset_type"] == asset_type_filter]

    st.subheader("Final Recommendations")

    st.dataframe(
        merged_df[[
            "asset",
            "asset_type",
            "final_recommendation",
            "confidence_level",
            "risk_category",
            "market_regime",
            "final_score",
            "reason"
        ]],
        use_container_width=True
    )

    fig = px.bar(
        merged_df,
        x="asset",
        y="final_score",
        color="risk_category",
        title="Final Intelligence Score by Asset"
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Portfolio Optimization
# -----------------------------
elif page == "Portfolio Optimization":

    st.title("Portfolio Optimization")

    weights_df = load_table("optimized_portfolio_weights")
    summary_df = load_table("portfolio_optimization_summary")

    st.subheader("Optimization Summary")
    st.dataframe(summary_df, use_container_width=True)

    selected_portfolio = st.selectbox(
        "Select Portfolio Type",
        ["max_sharpe_weight", "min_volatility_weight", "equal_weight"]
    )

    plot_df = weights_df[weights_df[selected_portfolio] > 0.001]

    fig = px.pie(
        plot_df,
        names="asset",
        values=selected_portfolio,
        title=f"Portfolio Allocation: {selected_portfolio}"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Portfolio Weights")
    st.dataframe(weights_df, use_container_width=True)

# -----------------------------
# Correlation Analysis
# -----------------------------
elif page == "Correlation Analysis":

    st.title("Correlation Analysis")

    corr_df = load_table("correlation_matrix")
    rolling_df = load_table("rolling_correlation_summary")
    insights_df = load_table("diversification_insights")

    # Correlation matrix table may contain first unnamed index column
    corr_df = corr_df.set_index(corr_df.columns[0])

    fig = px.imshow(
        corr_df,
        text_auto=True,
        aspect="auto",
        title="Asset Correlation Heatmap"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Rolling Correlation Summary")
    st.dataframe(rolling_df, use_container_width=True)

    st.subheader("Diversification Insights")
    st.dataframe(insights_df, use_container_width=True)

# -----------------------------
# Backtesting
# -----------------------------
elif page == "Backtesting":

    st.title("Backtesting Results")

    summary_df = load_table("backtest_summary")

    st.subheader("Strategy Performance Summary")

    st.dataframe(summary_df, use_container_width=True)

    fig = px.bar(
        summary_df,
        x="asset",
        y=["strategy_total_return", "buy_hold_total_return"],
        barmode="group",
        title="Strategy Return vs Buy & Hold"
    )

    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.scatter(
        summary_df,
        x="strategy_volatility",
        y="strategy_total_return",
        size="win_rate",
        color="asset_type",
        hover_name="asset",
        title="Risk vs Return by Strategy"
    )

    st.plotly_chart(fig2, use_container_width=True)