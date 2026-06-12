import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

DB_PATH = "data/database/market_intelligence.db"
LIVE_DB_PATH = "data/database/market_data.db"

st.set_page_config(
    page_title="Market Intelligence Platform",
    layout="wide"
)

# -----------------------------
# Helpers
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
        LIMIT 1000
        """,
        conn
    )
    conn.close()
    return df

def safe_columns(df, columns):
    return [col for col in columns if col in df.columns]

def get_asset_row(df, asset):
    rows = df[df["asset"] == asset]
    if rows.empty:
        return None
    return rows.iloc[0]

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("Market Intelligence Platform")

page = st.sidebar.radio(
    "Navigation",
    [
    "Overview",
    "Live Market Feed",
    "Asset Intelligence",
    "Portfolio Manager",
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
    forecasting, risk scoring, portfolio optimization, correlation analysis, market regime
    detection, and strategy backtesting.
    """)

    intelligence_df = load_table("unified_market_intelligence")
    risk_df = load_table("asset_risk_summary")
    optimization_df = load_table("portfolio_optimization_summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Assets Tracked", intelligence_df["asset"].nunique())
    col2.metric("Buy Signals", int(intelligence_df["final_recommendation"].astype(str).str.contains("BUY").sum()))
    col3.metric("High Risk Assets", int((risk_df["risk_category"] == "High Risk").sum()))

    best_portfolio = optimization_df.sort_values("sharpe_ratio", ascending=False).iloc[0]
    col4.metric("Best Sharpe", round(best_portfolio["sharpe_ratio"], 2))

    st.subheader("Latest Market Intelligence")

    overview_columns = [
        "asset",
        "asset_type",
        "close",
        "final_recommendation",
        "confidence_level",
        "risk_category",
        "market_regime",
        "correlation_risk",
        "final_score"
    ]

    st.dataframe(
        intelligence_df[safe_columns(intelligence_df, overview_columns)],
        use_container_width=True
    )

    st.subheader("Recommendation Distribution")

    fig = px.histogram(
        intelligence_df,
        x="final_recommendation",
        color="asset_type",
        title="Final Recommendation Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Live Market Feed
# -----------------------------
elif page == "Live Market Feed":

    st.title("Live Market Feed")

    live_df = load_live_data()

    if live_df.empty:
        st.warning("No live data found. Start live crypto/stock collectors first.")
    else:
        live_df["timestamp"] = pd.to_datetime(live_df["timestamp"])

        latest_prices = (
            live_df.sort_values("timestamp")
            .groupby("asset")
            .tail(1)
            .sort_values("asset")
        )

        st.subheader("Latest Live Prices")

        metric_cols = st.columns(min(len(latest_prices), 5))

        for i, (_, row) in enumerate(latest_prices.iterrows()):
            col = metric_cols[i % len(metric_cols)]
            col.metric(
                label=f"{row['asset']} ({row['source']})",
                value=f"${row['price']:,.2f}",
                delta=f"Qty/Vol {row['quantity']}"
            )

        st.markdown("---")

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

        st.subheader("Latest Trades / Snapshots")

        st.dataframe(
            live_df.sort_values("timestamp", ascending=False).head(200),
            use_container_width=True
        )

# -----------------------------
# Asset Intelligence
# -----------------------------
elif page == "Asset Intelligence":

    st.title("Asset Intelligence Profile")

    intelligence_df = load_table("unified_market_intelligence")
    risk_df = load_table("asset_risk_summary")
    forecasts_df = load_table("forecasts")
    regime_df = load_table("market_regime_summary")
    backtest_df = load_table("backtest_summary")
    weights_df = load_table("optimized_portfolio_weights")
    technical_df = load_table("technical_indicators")

    all_assets = sorted(intelligence_df["asset"].unique())

    selected_asset = st.selectbox("Select Asset", all_assets)

    intel = get_asset_row(intelligence_df, selected_asset)
    risk = get_asset_row(risk_df, selected_asset)
    forecast = get_asset_row(forecasts_df, selected_asset)
    regime = get_asset_row(regime_df, selected_asset)
    backtest = get_asset_row(backtest_df, selected_asset)
    weights = get_asset_row(weights_df, selected_asset)

    latest_tech = technical_df[technical_df["asset"] == selected_asset].copy()
    latest_tech["timestamp"] = pd.to_datetime(latest_tech["timestamp"])
    latest_tech = latest_tech.sort_values("timestamp")

    if latest_tech.empty:
        st.warning("No technical indicator data found for this asset.")
    else:
        latest_row = latest_tech.iloc[-1]

        st.subheader(f"{selected_asset} Full Intelligence View")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Latest Close", f"${float(intel['close']):,.2f}" if intel is not None else "N/A")
        col2.metric("Recommendation", intel["final_recommendation"] if intel is not None else "N/A")
        col3.metric("Confidence", intel["confidence_level"] if intel is not None else "N/A")
        col4.metric("Risk Category", intel["risk_category"] if intel is not None else "N/A")

        col5, col6, col7, col8 = st.columns(4)

        col5.metric("Market Regime", regime["market_regime"] if regime is not None else "N/A")
        col6.metric("Correlation Risk", intel["correlation_risk"] if intel is not None else "N/A")
        col7.metric("Win Rate", f"{float(backtest['win_rate']) * 100:.2f}%" if backtest is not None else "N/A")
        col8.metric("Strategy Sharpe", round(float(backtest["strategy_sharpe"]), 2) if backtest is not None else "N/A")

        st.markdown("---")

        st.subheader("Decision Explanation")

        if intel is not None:
            st.info(intel["reason"])

        st.subheader("Forecast & Risk Metrics")

        left, right = st.columns(2)

        with left:
            if forecast is not None:
                st.dataframe(
                    pd.DataFrame([forecast])[safe_columns(pd.DataFrame([forecast]), [
                        "asset",
                        "latest_close",
                        "next_forecast_close",
                        "predicted_return",
                        "forecast_direction",
                        "rmse"
                    ])],
                    use_container_width=True
                )

        with right:
            if risk is not None:
                st.dataframe(
                    pd.DataFrame([risk])[safe_columns(pd.DataFrame([risk]), [
                        "asset",
                        "annual_return",
                        "annual_volatility",
                        "sharpe_ratio",
                        "max_drawdown",
                        "risk_score",
                        "risk_category"
                    ])],
                    use_container_width=True
                )

        st.subheader("Portfolio Allocation Role")

        if weights is not None:
            st.dataframe(
                pd.DataFrame([weights])[safe_columns(pd.DataFrame([weights]), [
                    "asset",
                    "asset_type",
                    "max_sharpe_weight",
                    "min_volatility_weight",
                    "equal_weight"
                ])],
                use_container_width=True
            )

        st.subheader("Price History")

        fig_price = px.line(
            latest_tech.tail(250),
            x="timestamp",
            y="close",
            title=f"{selected_asset} Closing Price"
        )

        st.plotly_chart(fig_price, use_container_width=True)

        st.subheader("Technical Indicators")

        indicator_cols = [
            "rsi_14",
            "macd",
            "macd_signal",
            "macd_diff",
            "bb_high",
            "bb_low",
            "ema_20",
            "ema_50",
            "atr_14",
            "stoch_k",
            "stoch_d",
            "vwap"
        ]

        indicator_snapshot = pd.DataFrame([latest_row])[safe_columns(pd.DataFrame([latest_row]), indicator_cols)]

        st.dataframe(indicator_snapshot, use_container_width=True)

        fig_rsi = px.line(
            latest_tech.tail(250),
            x="timestamp",
            y="rsi_14",
            title=f"{selected_asset} RSI 14"
        )

        st.plotly_chart(fig_rsi, use_container_width=True)


# -----------------------------
# Portfolio Manager
# -----------------------------
elif page == "Portfolio Manager":

    st.title("Portfolio Manager & Investment Simulator")

    st.markdown("""
    This tool converts the optimization engine into a practical allocation simulator.
    Users can enter a portfolio size and select a risk profile to view recommended
    asset allocations, dollar amounts, and expected portfolio performance.
    """)

    weights_df = load_table("optimized_portfolio_weights")
    summary_df = load_table("portfolio_optimization_summary")
    intelligence_df = load_table("unified_market_intelligence")

    portfolio_amount = st.number_input(
        "Enter Portfolio Amount ($)",
        min_value=100.0,
        value=10000.0,
        step=500.0
    )

    risk_profile = st.selectbox(
        "Select Risk Profile",
        [
            "Conservative",
            "Moderate",
            "Aggressive"
        ]
    )

    if risk_profile == "Conservative":
        weight_column = "min_volatility_weight"
        portfolio_label = "Minimum Volatility Portfolio"
    elif risk_profile == "Moderate":
        weight_column = "equal_weight"
        portfolio_label = "Equal Weight Portfolio"
    else:
        weight_column = "max_sharpe_weight"
        portfolio_label = "Maximum Sharpe Portfolio"

    selected_summary = summary_df[
        summary_df["portfolio_type"] == portfolio_label
    ].iloc[0]

    allocation_df = weights_df.copy()

    allocation_df["allocation_percent"] = allocation_df[weight_column]
    allocation_df["allocation_amount"] = allocation_df["allocation_percent"] * portfolio_amount

    allocation_df = allocation_df[allocation_df["allocation_percent"] > 0.001]

    allocation_df = allocation_df.merge(
        intelligence_df[[
            "asset",
            "final_recommendation",
            "confidence_level",
            "risk_category",
            "market_regime"
        ]],
        on="asset",
        how="left"
    )
           # -----------------------------
    # Portfolio Health Score v3 - Risk Profile Aware
    # -----------------------------

    avg_confidence = allocation_df["confidence_level"].map({
        "High": 1.0,
        "Medium": 0.75,
        "Low": 0.45
    }).fillna(0.45).mean()

    high_risk_exposure = allocation_df.loc[
        allocation_df["risk_category"] == "High Risk",
        "allocation_percent"
    ].sum()

    moderate_risk_exposure = allocation_df.loc[
        allocation_df["risk_category"] == "Moderate Risk",
        "allocation_percent"
    ].sum()

    low_risk_exposure = allocation_df.loc[
        allocation_df["risk_category"] == "Low Risk",
        "allocation_percent"
    ].sum()

    number_of_assets = allocation_df["asset"].nunique()
    diversification_score = min(number_of_assets / 8, 1)

    sharpe_ratio = selected_summary["sharpe_ratio"]
    annual_return = selected_summary["expected_annual_return"]
    annual_volatility = selected_summary["annual_volatility"]

    sharpe_component = min(sharpe_ratio / 1.2, 1) * 30
    confidence_component = avg_confidence * 20
    diversification_component = diversification_score * 15

    # Risk-profile-specific scoring
    if risk_profile == "Conservative":
        return_component = min(annual_return / 0.20, 1) * 15
        volatility_penalty = min(annual_volatility / 0.30, 1) * 20
        high_risk_penalty = high_risk_exposure * 25
        moderate_risk_penalty = moderate_risk_exposure * 10
        risk_fit_bonus = low_risk_exposure * 15

    elif risk_profile == "Moderate":
        return_component = min(annual_return / 0.30, 1) * 20
        volatility_penalty = min(annual_volatility / 0.45, 1) * 12
        high_risk_penalty = high_risk_exposure * 12
        moderate_risk_penalty = moderate_risk_exposure * 5
        risk_fit_bonus = (moderate_risk_exposure * 10) + (low_risk_exposure * 5)

    else:  # Aggressive
        return_component = min(annual_return / 0.40, 1) * 25
        volatility_penalty = min(annual_volatility / 0.70, 1) * 6
        high_risk_penalty = high_risk_exposure * 4
        moderate_risk_penalty = moderate_risk_exposure * 2
        risk_fit_bonus = high_risk_exposure * 12

    health_score = (
        sharpe_component
        + return_component
        + confidence_component
        + diversification_component
        + risk_fit_bonus
        - volatility_penalty
        - high_risk_penalty
        - moderate_risk_penalty
    )

    health_score = max(0, min(100, health_score))

    if health_score >= 85:
        health_rating = "Excellent"
    elif health_score >= 70:
        health_rating = "Strong"
    elif health_score >= 55:
        health_rating = "Moderate"
    elif health_score >= 40:
        health_rating = "Risky"
    else:
        health_rating = "Weak"

    if health_score >= 85:
        health_comment = "This portfolio is well aligned with the selected risk profile and shows strong risk-adjusted characteristics."
    elif health_score >= 70:
        health_comment = "This portfolio is strong for the selected risk profile, with a reasonable balance between return potential and risk."
    elif health_score >= 55:
        health_comment = "This portfolio is usable, but it has some limitations in risk, volatility, concentration, or confidence."
    elif health_score >= 40:
        health_comment = "This portfolio is risky for the selected profile and should be monitored carefully."
    else:
        health_comment = "This portfolio has weak health characteristics for the selected risk profile."

    st.subheader("Portfolio Summary")


    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Portfolio Size", f"${portfolio_amount:,.2f}")
    col2.metric("Expected Annual Return", f"{selected_summary['expected_annual_return'] * 100:.2f}%")
    col3.metric("Annual Volatility", f"{selected_summary['annual_volatility'] * 100:.2f}%")
    col4.metric("Sharpe Ratio", round(selected_summary["sharpe_ratio"], 2))
    col5.metric("Health Score", f"{health_score:.0f}/100", health_rating)

    st.info(health_comment)

    st.subheader("Recommended Allocation")

    display_cols = [
        "asset",
        "asset_type",
        "allocation_percent",
        "allocation_amount",
        "final_recommendation",
        "confidence_level",
        "risk_category",
        "market_regime"
    ]

    st.dataframe(
        allocation_df[display_cols].sort_values("allocation_amount", ascending=False),
        use_container_width=True
    )
    st.subheader("Why These Assets Were Selected")

    explanation_rows = []

    for _, row in allocation_df.sort_values("allocation_amount", ascending=False).iterrows():

        reasons = []

        if "BUY" in str(row.get("final_recommendation", "")):
            reasons.append("positive intelligence recommendation")

        if row.get("confidence_level") == "High":
            reasons.append("high confidence signal")
        elif row.get("confidence_level") == "Medium":
            reasons.append("moderate confidence signal")

        if row.get("risk_category") == "Low Risk":
            reasons.append("lower risk profile")
        elif row.get("risk_category") == "Moderate Risk":
            reasons.append("balanced risk profile")
        elif row.get("risk_category") == "High Risk":
            reasons.append("higher growth but higher risk exposure")

        if row.get("market_regime") == "Bullish Regime":
            reasons.append("bullish market regime")
        elif row.get("market_regime") == "Mixed Regime":
            reasons.append("mixed market conditions")
        elif row.get("market_regime") == "Stable / Sideways Regime":
            reasons.append("stable sideways behavior")

        allocation_pct = row["allocation_percent"] * 100

        explanation_rows.append({
            "asset": row["asset"],
            "allocation": f"{allocation_pct:.2f}%",
            "amount": f"${row['allocation_amount']:,.2f}",
            "recommendation": row.get("final_recommendation", "N/A"),
            "explanation": "Selected because of " + ", ".join(reasons) + "."
        })

    explanation_df = pd.DataFrame(explanation_rows)

    st.dataframe(
        explanation_df,
        use_container_width=True
    )
    st.subheader("Allocation Chart")

    fig = px.pie(
        allocation_df,
        names="asset",
        values="allocation_amount",
        title=f"{risk_profile} Portfolio Allocation"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Allocation by Asset Type")

    asset_type_summary = allocation_df.groupby("asset_type").agg({
        "allocation_amount": "sum",
        "allocation_percent": "sum"
    }).reset_index()

    fig2 = px.bar(
        asset_type_summary,
        x="asset_type",
        y="allocation_amount",
        text="allocation_amount",
        title="Allocation by Asset Type"
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Decision Interpretation")

    if risk_profile == "Conservative":
        st.info(
            "The conservative portfolio prioritizes lower volatility and capital stability. "
            "It is suitable for users who prefer reduced downside risk."
        )
    elif risk_profile == "Moderate":
        st.info(
            "The moderate portfolio distributes capital equally across assets to balance "
            "growth exposure and diversification."
        )
    else:
        st.info(
            "The aggressive portfolio prioritizes risk-adjusted return using the Maximum Sharpe strategy. "
            "It may allocate more capital to higher-growth assets while accepting higher volatility."
        )

# -----------------------------
# Market Intelligence
# -----------------------------
elif page == "Market Intelligence":

    st.title("Market Intelligence")

    intelligence_df = load_table("unified_market_intelligence")

    asset_type_filter = st.selectbox(
        "Asset Type",
        ["All"] + sorted(intelligence_df["asset_type"].unique().tolist())
    )

    filtered_df = intelligence_df.copy()

    if asset_type_filter != "All":
        filtered_df = filtered_df[filtered_df["asset_type"] == asset_type_filter]

    st.subheader("Final Recommendations")

    intelligence_columns = [
        "asset",
        "asset_type",
        "final_recommendation",
        "confidence_level",
        "risk_category",
        "market_regime",
        "correlation_risk",
        "final_score",
        "reason"
    ]

    st.dataframe(
        filtered_df[safe_columns(filtered_df, intelligence_columns)],
        use_container_width=True
    )

    st.subheader("Final Intelligence Score")

    fig = px.bar(
        filtered_df,
        x="asset",
        y="final_score",
        color="risk_category",
        title="Final Intelligence Score by Asset"
    )

    st.plotly_chart(fig, use_container_width=True)

    if "risk_score" in filtered_df.columns:
        st.subheader("Risk vs Final Score")

        fig2 = px.scatter(
            filtered_df,
            x="risk_score",
            y="final_score",
            color="asset_type",
            hover_name="asset",
            size="confidence",
            title="Risk Score vs Final Intelligence Score"
        )

        st.plotly_chart(fig2, use_container_width=True)

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

    plot_df = weights_df[weights_df[selected_portfolio] > 0.001].copy()

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