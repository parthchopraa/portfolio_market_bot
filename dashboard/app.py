import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

px.defaults.template = "plotly_dark"

DB_PATH = "data/database/market_intelligence.db"
LIVE_DB_PATH = "data/database/market_data.db"

st.set_page_config(
    page_title="Market Intelligence Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Premium UI Styling
# -----------------------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&family=Syne:wght@600;700;800&display=swap');

[data-testid="collapsedControl"] {
    display: none !important;
}

:root {
    --gold: #F0B90B;
    --gold-soft: rgba(240,185,11,0.15);
    --green: #22C55E;
    --red: #EF4444;
    --amber: #F59E0B;
    --bg: #070A0E;
    --panel: rgba(17, 24, 39, 0.88);
    --panel2: rgba(13, 17, 23, 0.96);
    --border: rgba(255,255,255,0.08);
    --text: #F8FAFC;
    --muted: #94A3B8;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 20% 0%, rgba(240,185,11,0.10), transparent 28%),
        radial-gradient(circle at 85% 12%, rgba(34,197,94,0.08), transparent 28%),
        radial-gradient(circle at 45% 105%, rgba(99,102,241,0.06), transparent 26%),
        var(--bg);
    color: var(--text);
}

.block-container {
    padding-top: 1.1rem;
    padding-bottom: 3rem;
    max-width: 1520px;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080B10 0%, #0F172A 100%);
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * { color: #EAECEF; }

[data-testid="stSidebar"] [role="radiogroup"] label {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.04);
    border-radius: 12px;
    padding: 8px 10px;
    margin-bottom: 6px;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(240,185,11,0.08);
    border-color: rgba(240,185,11,0.16);
}

.brand-card {
    padding: 18px 16px;
    border-radius: 20px;
    background: linear-gradient(145deg, rgba(240,185,11,0.20), rgba(17,24,39,0.85));
    border: 1px solid rgba(240,185,11,0.28);
    margin-bottom: 16px;
    box-shadow: 0 18px 45px rgba(0,0,0,0.28);
}
.brand-title {
    font-family: 'Syne', sans-serif;
    font-size: 24px;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -0.7px;
}
.brand-title span { color: var(--gold); }
.brand-subtitle {
    font-size: 12px;
    color: var(--muted);
    line-height: 1.55;
    margin-top: 6px;
}

.topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 18px;
    margin-bottom: 18px;
    border-radius: 18px;
    background: rgba(7, 10, 14, 0.72);
    border: 1px solid var(--border);
    backdrop-filter: blur(14px);
    box-shadow: 0 14px 40px rgba(0,0,0,0.25);
}
.topbar-logo {
    font-family: 'Syne', sans-serif;
    font-size: 18px;
    font-weight: 800;
    letter-spacing: -0.4px;
}
.topbar-logo span { color: var(--gold); }
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 999px;
    background: rgba(34,197,94,0.12);
    color: var(--green);
    border: 1px solid rgba(34,197,94,0.32);
    font-size: 12px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.hero {
    padding: 32px;
    border-radius: 28px;
    background: linear-gradient(135deg, rgba(17,24,39,0.96), rgba(3,7,18,0.96));
    border: 1px solid var(--border);
    box-shadow: 0 22px 70px rgba(0,0,0,0.38);
    margin-bottom: 22px;
    position: relative;
    overflow: hidden;
}
.hero:before {
    content: "";
    position: absolute;
    top: -100px;
    right: -90px;
    width: 330px;
    height: 330px;
    background: radial-gradient(circle, rgba(240,185,11,0.24), transparent 64%);
}
.eyebrow {
    display: inline-block;
    padding: 6px 10px;
    border-radius: 999px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    color: #070A0E;
    background: var(--gold);
    margin-bottom: 14px;
    letter-spacing: 0.8px;
}
.main-title {
    font-family: 'Syne', sans-serif;
    font-size: 48px;
    line-height: 1.0;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -1.4px;
    margin-bottom: 12px;
    position: relative;
    z-index: 1;
}
.accent { color: var(--gold); }
.subtitle {
    font-size: 16px;
    color: var(--muted);
    max-width: 900px;
    line-height: 1.75;
    position: relative;
    z-index: 1;
}

.ticker-strip {
    display: flex;
    gap: 12px;
    overflow-x: auto;
    padding: 6px 2px 18px 2px;
    margin-top: -4px;
    margin-bottom: 12px;
}
.ticker-card {
    min-width: 150px;
    padding: 14px 15px;
    border-radius: 18px;
    background: linear-gradient(145deg, rgba(17,24,39,0.94), rgba(15,23,42,0.82));
    border: 1px solid var(--border);
    box-shadow: 0 12px 35px rgba(0,0,0,0.24);
}
.ticker-symbol {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: var(--muted);
    font-weight: 800;
    margin-bottom: 5px;
}
.ticker-price {
    font-size: 20px;
    color: var(--text);
    font-weight: 900;
}
.ticker-source {
    font-size: 11px;
    color: #64748B;
    margin-top: 5px;
}

.executive-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 16px;
    margin-bottom: 16px;
}
.executive-card {
    background: linear-gradient(145deg, rgba(17,24,39,0.96), rgba(3,7,18,0.92));
    border: 1px solid var(--border);
    border-radius: 22px;
    padding: 20px;
    box-shadow: 0 18px 45px rgba(0,0,0,0.32);
    position: relative;
    overflow: hidden;
}
.executive-card:after {
    content: "";
    position: absolute;
    right: -45px;
    top: -45px;
    width: 120px;
    height: 120px;
    background: radial-gradient(circle, rgba(240,185,11,0.16), transparent 65%);
}
.executive-label {
    color: var(--muted);
    font-size: 12px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 8px;
}
.executive-value {
    color: var(--text);
    font-family: 'Syne', sans-serif;
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -0.8px;
    margin-bottom: 8px;
}
.executive-note {
    color: var(--muted);
    font-size: 12px;
    line-height: 1.5;
}

.insight-panel {
    padding: 22px;
    border-radius: 22px;
    background: linear-gradient(135deg, rgba(240,185,11,0.10), rgba(17,24,39,0.92));
    border: 1px solid rgba(240,185,11,0.18);
    box-shadow: 0 18px 45px rgba(0,0,0,0.30);
    margin-bottom: 18px;
}
.insight-title {
    color: var(--gold);
    font-weight: 900;
    font-size: 18px;
    margin-bottom: 8px;
}
.insight-text {
    color: #D1D5DB;
    font-size: 14px;
    line-height: 1.65;
}
.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 26px;
    font-weight: 800;
    color: var(--text);
    margin-top: 26px;
    margin-bottom: 14px;
    letter-spacing: -0.6px;
}

.badge {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
}
.badge-buy { background: rgba(34,197,94,0.15); color: var(--green); border: 1px solid rgba(34,197,94,0.35); }
.badge-hold { background: rgba(245,158,11,0.15); color: var(--amber); border: 1px solid rgba(245,158,11,0.35); }
.badge-sell { background: rgba(239,68,68,0.15); color: var(--red); border: 1px solid rgba(239,68,68,0.35); }

div[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(17,24,39,0.95), rgba(31,41,55,0.92));
    border: 1px solid var(--border);
    padding: 18px;
    border-radius: 18px;
    box-shadow: 0 10px 35px rgba(0,0,0,0.22);
}
div[data-testid="stMetric"] label { color: var(--muted) !important; font-weight: 700; }
div[data-testid="stMetricValue"] { color: var(--text) !important; font-weight: 900; }

div[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid var(--border);
}
.stPlotlyChart {
    background: rgba(17,24,39,0.28);
    border-radius: 18px;
    padding: 8px;
    border: 1px solid rgba(255,255,255,0.05);
}

footer {visibility: hidden;}
#MainMenu {visibility: hidden;}
header {visibility: hidden;}

@media (max-width: 1100px) {
    .executive-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .main-title { font-size: 40px; }
}
@media (max-width: 700px) {
    .executive-grid { grid-template-columns: 1fr; }
    .main-title { font-size: 34px; }
}
</style>
""",
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def load_table(table_name: str) -> pd.DataFrame:
    if not Path(DB_PATH).exists():
        return pd.DataFrame()
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()
        return df
    except Exception as exc:
        st.error(f"Could not load table '{table_name}': {exc}")
        return pd.DataFrame()


def load_live_data() -> pd.DataFrame:
    if not Path(LIVE_DB_PATH).exists():
        return pd.DataFrame()
    try:
        conn = sqlite3.connect(LIVE_DB_PATH)
        df = pd.read_sql_query(
            """
            SELECT *
            FROM live_market_data
            ORDER BY id DESC
            LIMIT 1500
            """,
            conn,
        )
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


def safe_columns(df: pd.DataFrame, columns: list[str]) -> list[str]:
    return [col for col in columns if col in df.columns]


def get_asset_row(df: pd.DataFrame, asset: str):
    if df is None or df.empty or "asset" not in df.columns:
        return None
    rows = df[df["asset"] == asset]
    if rows.empty:
        return None
    return rows.iloc[0]


def fmt_money(value) -> str:
    try:
        return f"${float(value):,.2f}"
    except Exception:
        return "N/A"


def fmt_pct(value) -> str:
    try:
        return f"{float(value) * 100:.2f}%"
    except Exception:
        return "N/A"

def make_display_df(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    rename_map: dict[str, str] | None = None,
    money_cols: list[str] | None = None,
    pct_cols: list[str] | None = None,
    weight_cols: list[str] | None = None,
    score_cols: list[str] | None = None,
) -> pd.DataFrame:
    """Return a user-facing dataframe with readable column names and formatted values."""
    if df is None or df.empty:
        return pd.DataFrame()

    out = df.copy()
    if columns is not None:
        out = out[safe_columns(out, columns)].copy()

    money_cols = money_cols or []
    pct_cols = pct_cols or []
    weight_cols = weight_cols or []
    score_cols = score_cols or []

    for col in money_cols:
        if col in out.columns:
            out[col] = out[col].apply(fmt_money)

    for col in pct_cols:
        if col in out.columns:
            out[col] = out[col].apply(fmt_pct)

    for col in weight_cols:
        if col in out.columns:
            out[col] = out[col].apply(lambda x: f"{float(x) * 100:.2f}%" if pd.notna(x) else "N/A")

    for col in score_cols:
        if col in out.columns:
            out[col] = out[col].apply(lambda x: f"{float(x):.2f}" if pd.notna(x) else "N/A")

    if rename_map:
        out = out.rename(columns=rename_map)

    return out


READABLE_COLUMNS = {
    "rank": "Rank",
    "asset": "Asset",
    "asset_type": "Market Type",
    "close": "Current Price",
    "latest_close": "Current Price",
    "next_forecast_close": "Predicted Price",
    "predicted_return": "Expected Gain/Loss",
    "forecast_direction": "AI Outlook",
    "rmse": "Forecast Error Range",
    "final_recommendation": "Recommendation",
    "confidence_level": "Confidence",
    "confidence": "Confidence Score",
    "risk_category": "Risk Level",
    "risk_score": "Risk Score",
    "market_regime": "Market Environment",
    "correlation_risk": "Diversification Impact",
    "final_score": "Investment Score",
    "opportunity_score": "Opportunity Score",
    "reason": "Why This Recommendation",
    "annual_return": "Historical Annual Growth",
    "annual_volatility": "Price Swing Risk",
    "sharpe_ratio": "Risk-Reward Score",
    "strategy_sharpe": "Strategy Efficiency Score",
    "max_drawdown": "Worst Historical Drop",
    "win_rate": "Win Rate",
    "allocation_percent": "Portfolio Share",
    "allocation_amount": "Dollar Allocation",
    "max_sharpe_weight": "Growth Portfolio Share",
    "min_volatility_weight": "Defensive Portfolio Share",
    "equal_weight": "Balanced Portfolio Share",
    "portfolio_type": "Portfolio Strategy",
    "expected_annual_return": "Projected Annual Growth",
    "annual_volatility": "Portfolio Risk",
    "strategy_total_return": "Strategy Total Growth",
    "buy_hold_total_return": "Buy & Hold Growth",
    "strategy_volatility": "Strategy Risk",
    "asset_1": "Asset 1",
    "asset_2": "Asset 2",
    "average_rolling_correlation": "Average Co-Movement",
    "relationship": "Relationship",
    "diversification_score": "Diversification Benefit",
    "insight": "Plain-English Insight",
}


def style_plotly(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#EAECEF",
        title_font_color="#F8FAFC",
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.06)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.06)")
    return fig


def render_topbar():
    st.markdown(
        """
        <div class="topbar">
            <div class="topbar-logo"><span>Quant</span>Edge Intelligence Terminal</div>
            <div class="status-pill">● System Online</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_header(title: str, subtitle: str = "", label: str = "MARKET TERMINAL"):
    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">{label}</div>
            <div class="main-title">{title}</div>
            <div class="subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section(title: str):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


def render_ticker_strip(live_df: pd.DataFrame):
    """Render latest prices using native Streamlit cards so raw HTML can never leak."""
    if live_df is None or live_df.empty:
        return

    df = live_df.copy()
    df["timestamp"] = pd.to_datetime(df.get("timestamp"), errors="coerce")
    latest = df.sort_values("timestamp").groupby("asset").tail(1).sort_values("asset").head(10)

    if latest.empty:
        return

    cols = st.columns(min(len(latest), 5))
    for i, (_, row) in enumerate(latest.iterrows()):
        with cols[i % len(cols)]:
            st.metric(
                label=f"{row.get('asset', 'N/A')} · {row.get('source', 'live')}",
                value=fmt_money(row.get("price")),
                delta=f"Qty/Vol {row.get('quantity', 'N/A')}",
            )


def render_executive_cards(cards):
    """Render executive summary cards with native Streamlit metrics to prevent HTML leakage."""
    if not cards:
        return
    cols = st.columns(min(len(cards), 4))
    for i, (label, value, note) in enumerate(cards):
        with cols[i % len(cols)]:
            st.metric(label=label, value=value, delta=note)


def render_insight(title: str, text: str):
    st.markdown(
        f"""
        <div class="insight-panel">
            <div class="insight-title">{title}</div>
            <div class="insight-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def opportunity_rank(intelligence_df: pd.DataFrame) -> pd.DataFrame:
    if intelligence_df.empty:
        return pd.DataFrame()
    ranked_df = intelligence_df.copy()
    recommendation_bonus = {
        "CONSERVATIVE STRONG BUY": 4,
        "MODERATE STRONG BUY": 3,
        "SPECULATIVE BUY": 2,
        "CAUTIOUS BUY": 1,
        "NEUTRAL HOLD": 0,
        "HIGH-RISK HOLD": -1,
        "SELL / AVOID": -3,
    }
    confidence_bonus = {"High": 2, "Medium": 1, "Low": 0}
    ranked_df["opportunity_score"] = (
        ranked_df.get("final_score", 0)
        + ranked_df.get("final_recommendation", pd.Series(index=ranked_df.index)).map(recommendation_bonus).fillna(0)
        + ranked_df.get("confidence_level", pd.Series(index=ranked_df.index)).map(confidence_bonus).fillna(0)
    )
    ranked_df = ranked_df.sort_values("opportunity_score", ascending=False).reset_index(drop=True)
    ranked_df["rank"] = range(1, len(ranked_df) + 1)
    return ranked_df


def add_signal_badges(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "final_recommendation" not in df.columns:
        return df
    out = df.copy()
    def badge(value):
        txt = str(value)
        if "SELL" in txt or "AVOID" in txt:
            return f'<span class="badge badge-sell">{txt}</span>'
        if "HOLD" in txt:
            return f'<span class="badge badge-hold">{txt}</span>'
        return f'<span class="badge badge-buy">{txt}</span>'
    out["recommendation_badge"] = out["final_recommendation"].apply(badge)
    return out


# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------
st.sidebar.markdown(
    """
    <div class="brand-card">
        <div class="brand-title"><span>Quant</span>Edge</div>
        <div class="brand-subtitle">Real-time market intelligence, portfolio analytics, and decision-support terminal.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Live Market Feed",
        "Asset Intelligence",
        "Portfolio Manager",
        "Top Opportunities",
        "Market Intelligence",
        "Portfolio Optimization",
        "Correlation Analysis",
        "Backtesting",
    ],
)

st.sidebar.markdown("---")
st.sidebar.caption("Capstone FinTech Analytics System")

render_topbar()

# -----------------------------------------------------------------------------
# Overview
# -----------------------------------------------------------------------------
if page == "Overview":
    render_header(
        'Every signal. Every asset. <span class="accent">One terminal.</span>',
        "A premium market intelligence system combining live feeds, technical indicators, ML forecasts, risk scoring, portfolio optimization, backtesting, and regime intelligence.",
        "EXECUTIVE COMMAND CENTER",
    )

    intelligence_df = load_table("unified_market_intelligence")
    risk_df = load_table("asset_risk_summary")
    optimization_df = load_table("portfolio_optimization_summary")
    regime_df = load_table("market_regime_summary")
    live_df = load_live_data()

    render_ticker_strip(live_df)

    if intelligence_df.empty:
        st.warning("No intelligence data found. Run the analytics pipeline and database sync first.")
    else:
        ranked_df = opportunity_rank(intelligence_df)
        top_asset = ranked_df.iloc[0] if not ranked_df.empty else None
        highest_risk = risk_df.sort_values("risk_score", ascending=False).iloc[0] if not risk_df.empty and "risk_score" in risk_df.columns else None
        best_portfolio = optimization_df.sort_values("sharpe_ratio", ascending=False).iloc[0] if not optimization_df.empty and "sharpe_ratio" in optimization_df.columns else None
        dominant_regime = regime_df["market_regime"].mode().iloc[0] if not regime_df.empty and "market_regime" in regime_df.columns else "N/A"

        render_executive_cards([
            (
                "Top Opportunity",
                top_asset["asset"] if top_asset is not None else "N/A",
                f'{top_asset.get("final_recommendation", "")} · Score {top_asset.get("opportunity_score", 0):.2f}' if top_asset is not None else "No ranking available",
            ),
            (
                "Highest Risk",
                highest_risk["asset"] if highest_risk is not None else "N/A",
                f'Risk score {highest_risk.get("risk_score", "N/A")} · {highest_risk.get("risk_category", "")}' if highest_risk is not None else "No risk data",
            ),
            (
                "Best Portfolio",
                best_portfolio["portfolio_type"].replace(" Portfolio", "") if best_portfolio is not None else "N/A",
                f'Sharpe {best_portfolio.get("sharpe_ratio", 0):.2f}' if best_portfolio is not None else "No optimization data",
            ),
            (
                "Dominant Regime",
                dominant_regime,
                f'{regime_df["asset"].nunique()} assets monitored' if not regime_df.empty and "asset" in regime_df.columns else "Regime data unavailable",
            ),
        ])

        if top_asset is not None:
            render_insight(
                "Executive Readout",
                f"The platform currently ranks {top_asset['asset']} as the strongest opportunity based on technical, forecast, risk, regime, correlation, and backtest intelligence. Use Portfolio Manager to convert this intelligence into dollar allocations.",
            )

        render_section("Market Pulse")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Assets Tracked", intelligence_df["asset"].nunique() if "asset" in intelligence_df.columns else len(intelligence_df))
        c2.metric("Buy Signals", int(intelligence_df["final_recommendation"].astype(str).str.contains("BUY").sum()) if "final_recommendation" in intelligence_df.columns else 0)
        c3.metric("High Risk Assets", int((risk_df["risk_category"] == "High Risk").sum()) if not risk_df.empty and "risk_category" in risk_df.columns else 0)
        c4.metric("Best Sharpe", round(float(best_portfolio["sharpe_ratio"]), 2) if best_portfolio is not None else "N/A")

        render_section("Top Opportunities")
        top_display_cols = ["rank", "asset", "asset_type", "opportunity_score", "final_recommendation", "confidence_level", "risk_category", "market_regime"]
        st.dataframe(
            make_display_df(
                ranked_df.head(10),
                top_display_cols,
                READABLE_COLUMNS,
                money_cols=["close"],
                score_cols=["opportunity_score"],
            ),
            use_container_width=True,
        )

        col_left, col_right = st.columns([1.15, 0.85])
        with col_left:
            fig = px.bar(ranked_df.head(10), x="asset", y="opportunity_score", color="asset_type", text="opportunity_score", title="Top Opportunity Scores")
            st.plotly_chart(style_plotly(fig), use_container_width=True)
        with col_right:
            fig2 = px.histogram(intelligence_df, x="final_recommendation", color="asset_type", title="Recommendation Distribution")
            st.plotly_chart(style_plotly(fig2), use_container_width=True)

        render_section("Latest Intelligence Table")
        overview_columns = ["asset", "asset_type", "close", "final_recommendation", "confidence_level", "risk_category", "market_regime", "correlation_risk", "final_score"]
        st.dataframe(
            make_display_df(
                intelligence_df,
                overview_columns,
                READABLE_COLUMNS,
                money_cols=["close"],
                score_cols=["final_score"],
            ),
            use_container_width=True,
        )

# -----------------------------------------------------------------------------
# Live Market Feed
# -----------------------------------------------------------------------------
elif page == "Live Market Feed":
    render_header("Live Market Feed", "Unified live market tape powered by crypto WebSocket streams and stock snapshot collectors.", "LIVE DATA")
    live_df = load_live_data()

    if live_df.empty:
        st.warning("No live data found. Start live crypto/stock collectors first.")
    else:
        live_df["timestamp"] = pd.to_datetime(live_df["timestamp"], errors="coerce")
        render_ticker_strip(live_df)
        latest_prices = live_df.sort_values("timestamp").groupby("asset").tail(1).sort_values("asset")

        render_section("Latest Live Prices")
        metric_cols = st.columns(min(len(latest_prices), 5))
        for i, (_, row) in enumerate(latest_prices.iterrows()):
            metric_cols[i % len(metric_cols)].metric(
                label=f"{row['asset']} ({row.get('source', 'live')})",
                value=fmt_money(row.get("price")),
                delta=f"Qty/Vol {row.get('quantity', 'N/A')}",
            )

        selected_asset = st.selectbox("Select Asset", sorted(live_df["asset"].dropna().unique()))
        asset_live = live_df[live_df["asset"] == selected_asset].sort_values("timestamp")

        fig = px.line(asset_live, x="timestamp", y="price", title=f"Live Price Stream: {selected_asset}")
        st.plotly_chart(style_plotly(fig), use_container_width=True)

        render_section("Latest Trades / Snapshots")
        st.dataframe(live_df.sort_values("timestamp", ascending=False).head(250), use_container_width=True)

# -----------------------------------------------------------------------------
# Asset Intelligence
# -----------------------------------------------------------------------------
elif page == "Asset Intelligence":
    render_header("Asset Intelligence Profile", "Drill into one asset across recommendations, risk, forecasts, regimes, backtests, and technical indicators.", "ASSET RESEARCH")

    intelligence_df = load_table("unified_market_intelligence")
    risk_df = load_table("asset_risk_summary")
    forecasts_df = load_table("forecasts")
    regime_df = load_table("market_regime_summary")
    backtest_df = load_table("backtest_summary")
    weights_df = load_table("optimized_portfolio_weights")
    technical_df = load_table("technical_indicators")

    if intelligence_df.empty:
        st.warning("No asset intelligence data found.")
    else:
        selected_asset = st.selectbox("Select Asset", sorted(intelligence_df["asset"].dropna().unique()))
        intel = get_asset_row(intelligence_df, selected_asset)
        risk = get_asset_row(risk_df, selected_asset)
        forecast = get_asset_row(forecasts_df, selected_asset)
        regime = get_asset_row(regime_df, selected_asset)
        backtest = get_asset_row(backtest_df, selected_asset)
        weights = get_asset_row(weights_df, selected_asset)

        latest_tech = technical_df[technical_df["asset"] == selected_asset].copy() if not technical_df.empty and "asset" in technical_df.columns else pd.DataFrame()
        if not latest_tech.empty:
            latest_tech["timestamp"] = pd.to_datetime(latest_tech["timestamp"], errors="coerce")
            latest_tech = latest_tech.sort_values("timestamp")
            latest_row = latest_tech.iloc[-1]
        else:
            latest_row = None

        render_section(f"{selected_asset} Full Intelligence View")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Latest Close", fmt_money(intel.get("close")) if intel is not None else "N/A")
        c2.metric("Recommendation", intel.get("final_recommendation", "N/A") if intel is not None else "N/A")
        c3.metric("Confidence", intel.get("confidence_level", "N/A") if intel is not None else "N/A")
        c4.metric("Risk", intel.get("risk_category", "N/A") if intel is not None else "N/A")

        c5, c6, c7, c8 = st.columns(4)
        c5.metric("Market Regime", regime.get("market_regime", "N/A") if regime is not None else "N/A")
        c6.metric("Correlation Risk", intel.get("correlation_risk", "N/A") if intel is not None else "N/A")
        c7.metric("Win Rate", fmt_pct(backtest.get("win_rate")) if backtest is not None else "N/A")
        c8.metric("Strategy Sharpe", round(float(backtest.get("strategy_sharpe")), 2) if backtest is not None and pd.notna(backtest.get("strategy_sharpe")) else "N/A")

        if intel is not None:
            render_insight("Decision Explanation", intel.get("reason", "No reasoning available."))

        left, right = st.columns(2)
        with left:
            render_section("Investment Outlook")
            if forecast is not None:
                forecast_one = pd.DataFrame([forecast])
                st.dataframe(
                    make_display_df(
                        forecast_one,
                        ["asset", "latest_close", "next_forecast_close", "predicted_return", "forecast_direction", "rmse"],
                        READABLE_COLUMNS,
                        money_cols=["latest_close", "next_forecast_close"],
                        pct_cols=["predicted_return"],
                        score_cols=["rmse"],
                    ),
                    use_container_width=True,
                )
            else:
                st.info("No forecast row for this asset.")
        with right:
            render_section("Risk Assessment")
            if risk is not None:
                risk_one = pd.DataFrame([risk])
                st.dataframe(
                    make_display_df(
                        risk_one,
                        ["asset", "annual_return", "annual_volatility", "sharpe_ratio", "max_drawdown", "risk_score", "risk_category"],
                        READABLE_COLUMNS,
                        pct_cols=["annual_return", "annual_volatility", "max_drawdown"],
                        score_cols=["sharpe_ratio", "risk_score"],
                    ),
                    use_container_width=True,
                )
            else:
                st.info("No risk row for this asset.")

        render_section("Portfolio Allocation Role")
        if weights is not None:
            weights_one = pd.DataFrame([weights])
            st.dataframe(
                make_display_df(
                    weights_one,
                    ["asset", "asset_type", "max_sharpe_weight", "min_volatility_weight", "equal_weight"],
                    READABLE_COLUMNS,
                    weight_cols=["max_sharpe_weight", "min_volatility_weight", "equal_weight"],
                ),
                use_container_width=True,
            )

        if not latest_tech.empty:
            render_section("Price History")
            fig_price = px.line(latest_tech.tail(250), x="timestamp", y="close", title=f"{selected_asset} Closing Price")
            st.plotly_chart(style_plotly(fig_price), use_container_width=True)

            render_section("Technical Indicators")
            indicator_cols = ["rsi_14", "macd", "macd_signal", "macd_diff", "bb_high", "bb_low", "ema_20", "ema_50", "atr_14", "stoch_k", "stoch_d", "vwap"]
            indicator_snapshot = pd.DataFrame([latest_row])
            st.dataframe(indicator_snapshot[safe_columns(indicator_snapshot, indicator_cols)], use_container_width=True)

            if "rsi_14" in latest_tech.columns:
                fig_rsi = px.line(latest_tech.tail(250), x="timestamp", y="rsi_14", title=f"{selected_asset} RSI 14")
                st.plotly_chart(style_plotly(fig_rsi), use_container_width=True)

# -----------------------------------------------------------------------------
# Portfolio Manager
# -----------------------------------------------------------------------------
elif page == "Portfolio Manager":
    render_header("Portfolio Manager", "Convert the optimization engine into dollar allocations, health scores, and investment projections.", "PORTFOLIO SIMULATOR")

    weights_df = load_table("optimized_portfolio_weights")
    summary_df = load_table("portfolio_optimization_summary")
    intelligence_df = load_table("unified_market_intelligence")

    if weights_df.empty or summary_df.empty:
        st.warning("Portfolio optimization data is missing. Run the optimizer and database sync first.")
    else:
        portfolio_amount = st.number_input("Enter Portfolio Amount ($)", min_value=100.0, value=10000.0, step=500.0)
        risk_profile = st.selectbox("Select Risk Profile", ["Conservative", "Moderate", "Aggressive"])

        if risk_profile == "Conservative":
            weight_column = "min_volatility_weight"
            portfolio_label = "Minimum Volatility Portfolio"
        elif risk_profile == "Moderate":
            weight_column = "equal_weight"
            portfolio_label = "Equal Weight Portfolio"
        else:
            weight_column = "max_sharpe_weight"
            portfolio_label = "Maximum Sharpe Portfolio"

        selected_summary = summary_df[summary_df["portfolio_type"] == portfolio_label].iloc[0]
        allocation_df = weights_df.copy()
        allocation_df["allocation_percent"] = allocation_df[weight_column]
        allocation_df["allocation_amount"] = allocation_df["allocation_percent"] * portfolio_amount
        allocation_df = allocation_df[allocation_df["allocation_percent"] > 0.001]

        if not intelligence_df.empty:
            allocation_df = allocation_df.merge(
                intelligence_df[safe_columns(intelligence_df, ["asset", "final_recommendation", "confidence_level", "risk_category", "market_regime"])],
                on="asset",
                how="left",
            )

        avg_confidence = allocation_df.get("confidence_level", pd.Series(index=allocation_df.index)).map({"High": 1.0, "Medium": 0.75, "Low": 0.45}).fillna(0.45).mean()
        high_risk_exposure = allocation_df.loc[allocation_df.get("risk_category", "") == "High Risk", "allocation_percent"].sum() if "risk_category" in allocation_df.columns else 0
        moderate_risk_exposure = allocation_df.loc[allocation_df.get("risk_category", "") == "Moderate Risk", "allocation_percent"].sum() if "risk_category" in allocation_df.columns else 0
        low_risk_exposure = allocation_df.loc[allocation_df.get("risk_category", "") == "Low Risk", "allocation_percent"].sum() if "risk_category" in allocation_df.columns else 0
        diversification_score = min(allocation_df["asset"].nunique() / 8, 1)

        sharpe_ratio = float(selected_summary["sharpe_ratio"])
        annual_return = float(selected_summary["expected_annual_return"])
        annual_volatility = float(selected_summary["annual_volatility"])

        sharpe_component = min(sharpe_ratio / 1.2, 1) * 30
        confidence_component = avg_confidence * 20
        diversification_component = diversification_score * 15

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
        else:
            return_component = min(annual_return / 0.40, 1) * 25
            volatility_penalty = min(annual_volatility / 0.70, 1) * 6
            high_risk_penalty = high_risk_exposure * 4
            moderate_risk_penalty = moderate_risk_exposure * 2
            risk_fit_bonus = high_risk_exposure * 12

        health_score = max(0, min(100, sharpe_component + return_component + confidence_component + diversification_component + risk_fit_bonus - volatility_penalty - high_risk_penalty - moderate_risk_penalty))
        if health_score >= 85:
            health_rating = "Excellent"
            health_comment = "This portfolio is well aligned with the selected risk profile and shows strong risk-adjusted characteristics."
        elif health_score >= 70:
            health_rating = "Strong"
            health_comment = "This portfolio is strong for the selected risk profile, with a reasonable balance between return potential and risk."
        elif health_score >= 55:
            health_rating = "Moderate"
            health_comment = "This portfolio is usable, but it has some limitations in risk, volatility, concentration, or confidence."
        elif health_score >= 40:
            health_rating = "Risky"
            health_comment = "This portfolio is risky for the selected profile and should be monitored carefully."
        else:
            health_rating = "Weak"
            health_comment = "This portfolio has weak health characteristics for the selected risk profile."

        render_section("Portfolio Summary")
        p1, p2, p3, p4, p5 = st.columns(5)
        p1.metric("Portfolio Size", fmt_money(portfolio_amount))
        p2.metric("Expected Annual Return", fmt_pct(selected_summary["expected_annual_return"]))
        p3.metric("Annual Volatility", fmt_pct(selected_summary["annual_volatility"]))
        p4.metric("Sharpe Ratio", round(sharpe_ratio, 2))
        p5.metric("Health Score", f"{health_score:.0f}/100", health_rating)
        st.info(health_comment)

        render_section("Recommended Allocation")
        display_cols = ["asset", "asset_type", "allocation_percent", "allocation_amount", "final_recommendation", "confidence_level", "risk_category", "market_regime"]
        allocation_display = make_display_df(
            allocation_df.sort_values("allocation_amount", ascending=False),
            display_cols,
            READABLE_COLUMNS,
            money_cols=["allocation_amount"],
            weight_cols=["allocation_percent"],
        )
        st.dataframe(allocation_display, use_container_width=True)

        render_section("Why These Assets Were Selected")
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
            if not reasons:
                reasons.append("optimization and diversification fit")
            explanation_rows.append({
                "asset": row["asset"],
                "allocation": f"{row['allocation_percent'] * 100:.2f}%",
                "amount": fmt_money(row["allocation_amount"]),
                "recommendation": row.get("final_recommendation", "N/A"),
                "explanation": "Selected because of " + ", ".join(reasons) + ".",
            })
        explanation_display = pd.DataFrame(explanation_rows).rename(columns={
            "asset": "Asset",
            "allocation": "Portfolio Share",
            "amount": "Dollar Allocation",
            "recommendation": "Recommendation",
            "explanation": "Why It Was Selected",
        })
        st.dataframe(explanation_display, use_container_width=True)

        chart_left, chart_right = st.columns(2)
        with chart_left:
            fig = px.pie(allocation_df, names="asset", values="allocation_amount", title=f"{risk_profile} Portfolio Allocation")
            st.plotly_chart(style_plotly(fig), use_container_width=True)
        with chart_right:
            asset_type_summary = allocation_df.groupby("asset_type").agg({"allocation_amount": "sum", "allocation_percent": "sum"}).reset_index()
            fig2 = px.bar(asset_type_summary, x="asset_type", y="allocation_amount", text="allocation_amount", title="Allocation by Asset Type")
            st.plotly_chart(style_plotly(fig2), use_container_width=True)

        render_section("Scenario Simulator")
        sim_col1, sim_col2 = st.columns(2)
        with sim_col1:
            monthly_contribution = st.number_input("Monthly Contribution ($)", min_value=0.0, value=500.0, step=100.0)
        with sim_col2:
            investment_years = st.number_input("Investment Horizon (Years)", min_value=1, max_value=40, value=10, step=1)

        base_annual_return = float(selected_summary["expected_annual_return"])
        bear_annual_return = base_annual_return * 0.45
        bull_annual_return = base_annual_return * 1.35
        months = int(investment_years * 12)

        def simulate_growth(initial_amount, monthly_amount, annual_return, months):
            monthly_return = (1 + annual_return) ** (1 / 12) - 1
            values = []
            portfolio_value = initial_amount
            for month in range(1, months + 1):
                portfolio_value = portfolio_value * (1 + monthly_return)
                portfolio_value += monthly_amount
                values.append({"month": month, "year": month / 12, "portfolio_value": portfolio_value})
            return pd.DataFrame(values)

        bear_df = simulate_growth(portfolio_amount, monthly_contribution, bear_annual_return, months)
        bear_df["scenario"] = "Bear Case"
        base_df = simulate_growth(portfolio_amount, monthly_contribution, base_annual_return, months)
        base_df["scenario"] = "Base Case"
        bull_df = simulate_growth(portfolio_amount, monthly_contribution, bull_annual_return, months)
        bull_df["scenario"] = "Bull Case"
        scenario_df = pd.concat([bear_df, base_df, bull_df], ignore_index=True)

        s1, s2, s3 = st.columns(3)
        s1.metric("Bear Case", fmt_money(bear_df["portfolio_value"].iloc[-1]))
        s2.metric("Base Case", fmt_money(base_df["portfolio_value"].iloc[-1]))
        s3.metric("Bull Case", fmt_money(bull_df["portfolio_value"].iloc[-1]))

        fig_sim = px.line(scenario_df, x="year", y="portfolio_value", color="scenario", title="Portfolio Growth Scenario Projection")
        st.plotly_chart(style_plotly(fig_sim), use_container_width=True)

        if risk_profile == "Conservative":
            st.info("The conservative portfolio prioritizes lower volatility and capital stability. It is suitable for users who prefer reduced downside risk.")
        elif risk_profile == "Moderate":
            st.info("The moderate portfolio distributes capital equally across assets to balance growth exposure and diversification.")
        else:
            st.info("The aggressive portfolio prioritizes risk-adjusted return using the Maximum Sharpe strategy. It may allocate more capital to higher-growth assets while accepting higher volatility.")

# -----------------------------------------------------------------------------
# Top Opportunities
# -----------------------------------------------------------------------------
elif page == "Top Opportunities":
    render_header("Top Opportunities", "Ranked opportunities powered by unified intelligence, confidence, risk, regime, and backtesting evidence.", "OPPORTUNITY ENGINE")
    intelligence_df = load_table("unified_market_intelligence")
    ranked_df = opportunity_rank(intelligence_df)

    if ranked_df.empty:
        st.warning("No opportunity data available.")
    else:
        render_section("Top Ranked Opportunities")
        display_cols = ["rank", "asset", "asset_type", "opportunity_score", "final_recommendation", "confidence_level", "market_regime", "risk_category"]
        st.dataframe(
            make_display_df(
                ranked_df,
                display_cols,
                READABLE_COLUMNS,
                score_cols=["opportunity_score"],
            ),
            use_container_width=True,
        )

        fig = px.bar(ranked_df.head(10), x="asset", y="opportunity_score", color="risk_category", text="opportunity_score", title="Top Opportunity Rankings")
        st.plotly_chart(style_plotly(fig), use_container_width=True)

        render_section("Best Opportunities Today")
        top_cols = st.columns(min(5, len(ranked_df.head(5))))
        for i, (_, row) in enumerate(ranked_df.head(5).iterrows()):
            with top_cols[i]:
                st.metric(f"#{row['rank']} {row['asset']}", f"{row['opportunity_score']:.2f}", row.get("final_recommendation", ""))

# -----------------------------------------------------------------------------
# Market Intelligence
# -----------------------------------------------------------------------------
elif page == "Market Intelligence":
    render_header("Market Intelligence", "Multi-factor final recommendations combining signals, forecasts, regimes, risk, and correlation intelligence.", "INTELLIGENCE LAYER")
    intelligence_df = load_table("unified_market_intelligence")

    if intelligence_df.empty:
        st.warning("No market intelligence data available.")
    else:
        asset_type_filter = st.selectbox("Asset Type", ["All"] + sorted(intelligence_df["asset_type"].dropna().unique().tolist()))
        filtered_df = intelligence_df.copy()
        if asset_type_filter != "All":
            filtered_df = filtered_df[filtered_df["asset_type"] == asset_type_filter]

        render_section("Final Recommendations")
        intelligence_columns = ["asset", "asset_type", "final_recommendation", "confidence_level", "risk_category", "market_regime", "correlation_risk", "final_score", "reason"]
        st.dataframe(
            make_display_df(
                filtered_df,
                intelligence_columns,
                READABLE_COLUMNS,
                score_cols=["final_score"],
            ),
            use_container_width=True,
        )

        fig = px.bar(filtered_df, x="asset", y="final_score", color="risk_category", title="Final Intelligence Score by Asset")
        st.plotly_chart(style_plotly(fig), use_container_width=True)

        if "risk_score" in filtered_df.columns:
            fig2 = px.scatter(filtered_df, x="risk_score", y="final_score", color="asset_type", hover_name="asset", size="confidence", title="Risk Score vs Final Intelligence Score")
            st.plotly_chart(style_plotly(fig2), use_container_width=True)

# -----------------------------------------------------------------------------
# Portfolio Optimization
# -----------------------------------------------------------------------------
elif page == "Portfolio Optimization":
    render_header("Portfolio Optimization", "Compare maximum Sharpe, minimum volatility, and equal-weight portfolio constructions.", "OPTIMIZATION")
    weights_df = load_table("optimized_portfolio_weights")
    summary_df = load_table("portfolio_optimization_summary")

    if weights_df.empty or summary_df.empty:
        st.warning("Portfolio optimization data unavailable.")
    else:
        st.dataframe(
            make_display_df(
                summary_df,
                None,
                READABLE_COLUMNS,
                pct_cols=["expected_annual_return", "annual_volatility"],
                score_cols=["sharpe_ratio"],
            ),
            use_container_width=True,
        )
        selected_portfolio = st.selectbox("Select Portfolio Type", ["max_sharpe_weight", "min_volatility_weight", "equal_weight"])
        plot_df = weights_df[weights_df[selected_portfolio] > 0.001].copy()
        fig = px.pie(plot_df, names="asset", values=selected_portfolio, title=f"Portfolio Allocation: {selected_portfolio}")
        st.plotly_chart(style_plotly(fig), use_container_width=True)
        st.dataframe(
            make_display_df(
                weights_df,
                None,
                READABLE_COLUMNS,
                weight_cols=["max_sharpe_weight", "min_volatility_weight", "equal_weight"],
            ),
            use_container_width=True,
        )

# -----------------------------------------------------------------------------
# Correlation Analysis
# -----------------------------------------------------------------------------
elif page == "Correlation Analysis":
    render_header("Correlation Analysis", "Understand relationships, diversification value, and co-movement risk across assets.", "DIVERSIFICATION")
    corr_df = load_table("correlation_matrix")
    rolling_df = load_table("rolling_correlation_summary")
    insights_df = load_table("diversification_insights")

    if corr_df.empty:
        st.warning("Correlation matrix unavailable.")
    else:
        corr_df = corr_df.set_index(corr_df.columns[0])
        fig = px.imshow(corr_df, text_auto=True, aspect="auto", title="Asset Correlation Heatmap")
        st.plotly_chart(style_plotly(fig), use_container_width=True)
    render_section("Rolling Correlation Summary")
    st.dataframe(
        make_display_df(
            rolling_df,
            None,
            READABLE_COLUMNS,
            score_cols=["average_rolling_correlation", "diversification_score"],
        ),
        use_container_width=True,
    )
    render_section("Diversification Insights")
    st.dataframe(make_display_df(insights_df, None, READABLE_COLUMNS, score_cols=["diversification_score"]), use_container_width=True)

# -----------------------------------------------------------------------------
# Backtesting
# -----------------------------------------------------------------------------
elif page == "Backtesting":
    render_header("Backtesting Results", "Validate strategy behavior against buy-and-hold using returns, drawdowns, Sharpe, and win rate.", "STRATEGY VALIDATION")
    summary_df = load_table("backtest_summary")

    if summary_df.empty:
        st.warning("Backtesting data unavailable.")
    else:
        st.dataframe(
            make_display_df(
                summary_df,
                None,
                READABLE_COLUMNS,
                pct_cols=["expected_annual_return", "annual_volatility"],
                score_cols=["sharpe_ratio"],
            ),
            use_container_width=True,
        )
        fig = px.bar(summary_df, x="asset", y=["strategy_total_return", "buy_hold_total_return"], barmode="group", title="Strategy Return vs Buy & Hold")
        st.plotly_chart(style_plotly(fig), use_container_width=True)
        fig2 = px.scatter(summary_df, x="strategy_volatility", y="strategy_total_return", size="win_rate", color="asset_type", hover_name="asset", title="Risk vs Return by Strategy")
        st.plotly_chart(style_plotly(fig2), use_container_width=True)
