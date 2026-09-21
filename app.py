"""
TEA / LCA Modelling Tool – Post-Consumer HDPE Mechanical Recycling
================================================================================
Interactive Streamlit dashboard for techno-economic assessment and life-cycle
carbon analysis of an industrial-scale HDPE bottle-to-pellet recycling facility.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import NamedTuple

# ------------------------------------------------------------------------------
# Page configuration
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="HDPE Recycling TEA / LCA",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------------------
# Baseline defaults
# ------------------------------------------------------------------------------
DEFAULTS: dict[str, float] = {
    "throughput": 18.0,
    "op_hours": 24.0,
    "yield_pct": 80.0,
    "pre_ext_kw": 276.0,
    "ext_kwh_t": 250.0,
    "tariff": 1.30,
    "distance": 30.0,
    "grid_factor": 0.39,
    "raw_price": 3500.0,
    "sell_price": 7200.0,
    "virgin_gwp": 2100.0,
    "freight_ef": 0.10,
    "food_grade_price": 9500.0,
}

SUBSYSTEMS: dict[str, float] = {
    "Sorting (Optical / Flake)": 15.0,
    "Conveyors & Vertical Elevators": 37.5,
    "Shredder / Crusher": 72.5,
    "Washing, Friction Washers & Dewatering": 151.0,
}

# ------------------------------------------------------------------------------
# Design tokens - muted, professional, light palette
# ------------------------------------------------------------------------------
CLR = {
    "bg":       "#ffffff",
    "surface":  "#ffffff",
    "border":   "#e7e5e4",
    "text":     "#1c1917",
    "text2":    "#57534e",
    "text3":    "#a8a29e",
    "accent":   "#2563eb",
    "green":    "#16a34a",
    "amber":    "#d97706",
    "red":      "#dc2626",
    "teal":     "#0d9488",
    "indigo":   "#4f46e5",
    "slate":    "#64748b",
}

# ------------------------------------------------------------------------------
# CSS - minimal, readable, warm neutral palette
# ------------------------------------------------------------------------------
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    *, html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    /* -- Pure White Background across entire app -- */
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stToolbar"], section.main, .main {{
        background-color: #ffffff !important;
        background: #ffffff !important;
    }}

    .main .block-container {{
        max-width: 1200px;
        padding-top: 2rem;
        background-color: #ffffff !important;
    }}

    /* -- Sidebar -- */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div,
    [data-testid="stSidebarContent"],
    [data-testid="stSidebarUserContent"],
    [data-testid="stSidebarNav"],
    aside[data-testid="stSidebar"],
    section[data-testid="stSidebar"],
    .stSidebar {{
        background-color: #ffffff !important;
        background: #ffffff !important;
    }}
    [data-testid="stSidebar"] {{
        border-right: 1px solid {CLR["border"]} !important;
    }}
    [data-testid="stSidebar"] .stSlider label,
    [data-testid="stSidebar"] .stCheckbox label {{
        color: {CLR["text2"]} !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
    }}
    .sidebar-section {{
        font-size: 0.7rem;
        font-weight: 600;
        color: {CLR["text3"]};
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin: 1.4rem 0 0.5rem 0;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid {CLR["border"]};
    }}

    /* -- KPI cards -- */
    .kpi {{
        background: {CLR["surface"]};
        border: 1px solid {CLR["border"]};
        border-radius: 8px;
        padding: 1rem 1.1rem;
    }}
    .kpi-label {{
        font-size: 0.72rem;
        font-weight: 600;
        color: {CLR["text3"]};
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 0.35rem;
    }}
    .kpi-value {{
        font-size: 1.5rem;
        font-weight: 700;
        color: {CLR["text"]};
        line-height: 1.25;
    }}
    .kpi-sub {{
        font-size: 0.78rem;
        font-weight: 500;
        color: {CLR["text3"]};
        margin-top: 0.25rem;
    }}

    /* -- Section labels -- */
    .section-label {{
        font-size: 0.88rem;
        font-weight: 600;
        color: {CLR["text"]};
        margin-bottom: 0.35rem;
    }}

    /* -- Process flow cards -- */
    .flow-card {{
        background: {CLR["surface"]};
        border: 1px solid {CLR["border"]};
        border-radius: 8px;
        padding: 0.85rem 0.7rem;
        text-align: center;
    }}
    .flow-icon {{
        font-size: 0.75rem;
        font-weight: 700;
        color: {CLR["text3"]};
        width: 1.5rem;
        height: 1.5rem;
        line-height: 1.5rem;
        border-radius: 50%;
        border: 1px solid {CLR["border"]};
        display: inline-block;
        margin-bottom: 0.25rem;
    }}
    .flow-name {{
        font-size: 0.8rem;
        font-weight: 600;
        color: {CLR["text"]};
        margin-bottom: 0.1rem;
    }}
    .flow-spec {{
        font-size: 0.72rem;
        color: {CLR["text3"]};
    }}
    .flow-arrow {{
        display: flex;
        align-items: center;
        justify-content: center;
        color: {CLR["text3"]};
        font-size: 1.1rem;
    }}

    /* -- Callout box -- */
    .callout {{
        background: #ffffff;
        border: 1px solid {CLR["border"]};
        border-left: 3px solid {CLR["accent"]};
        border-radius: 6px;
        padding: 0.75rem 1rem;
        font-size: 0.84rem;
        color: {CLR["text2"]};
    }}
    .callout strong {{
        color: {CLR["text"]};
    }}

    /* -- Hide Streamlit chrome -- */
    #MainMenu, footer {{visibility: hidden;}}

    /* -- Tab styling -- */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0;
        border-bottom: 1px solid {CLR["border"]};
    }}
    .stTabs [data-baseweb="tab"] {{
        font-size: 0.84rem;
        font-weight: 500;
        padding: 0.55rem 1.15rem;
        color: {CLR["text2"]};
    }}
    .stTabs [aria-selected="true"] {{
        color: {CLR["text"]} !important;
        border-bottom-color: {CLR["text"]} !important;
    }}

    .stDataFrame {{ border-radius: 6px; overflow: hidden; }}
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# Data model
# ------------------------------------------------------------------------------
class Results(NamedTuple):
    pre_ext_kwh_t: float
    ext_kwh_t: float
    total_kwh_t: float
    transit_co2: float
    pre_ext_co2: float
    ext_co2: float
    process_co2: float
    total_gwp: float
    abatement: float
    pct_reduction: float
    energy_opex_t: float
    raw_input_cost_t: float
    gross_margin_t: float
    net_margin_t: float
    daily_profit: float
    subsystem_df: pd.DataFrame


def compute(
    throughput: float, op_hours: float, yield_pct: float,
    pre_ext_kw: float, ext_kwh_t: float, tariff: float,
    distance: float, grid_factor: float,
    raw_price: float, sell_price: float,
    virgin_gwp: float = DEFAULTS["virgin_gwp"],
    freight_ef: float = DEFAULTS["freight_ef"],
) -> Results:
    """Run TEA / LCA calculations and return all derived metrics."""
    inv_yield = 1.0 / (yield_pct / 100.0)

    # Energy intensity
    pre_ext_kwh_t = (pre_ext_kw * op_hours) / throughput
    total_kwh_t = pre_ext_kwh_t + ext_kwh_t

    # Carbon footprint
    transit_co2 = distance * inv_yield * freight_ef
    pre_ext_co2 = pre_ext_kwh_t * grid_factor
    ext_co2 = ext_kwh_t * grid_factor
    process_co2 = total_kwh_t * grid_factor
    total_gwp = transit_co2 + process_co2
    abatement = virgin_gwp - total_gwp
    pct_reduction = (abatement / virgin_gwp) * 100.0 if virgin_gwp else 0.0

    # Economics
    energy_opex_t = total_kwh_t * tariff
    raw_input_cost_t = raw_price * inv_yield
    gross_margin_t = sell_price - raw_input_cost_t
    net_margin_t = gross_margin_t - energy_opex_t
    daily_profit = net_margin_t * throughput

    # Subsystem breakdown
    rows = []
    for name, kw in SUBSYSTEMS.items():
        kwh_t = (kw * op_hours) / throughput
        rows.append({
            "Stage": name,
            "Power (kW)": kw,
            "Energy (kWh/t)": round(kwh_t, 1),
            "Carbon (kg CO₂e/t)": round(kwh_t * grid_factor, 2),
            "Cost ($/t)": round(kwh_t * tariff, 2),
        })
    rows.append({
        "Stage": "Extrusion & Pelletizing",
        "Power (kW)": None,
        "Energy (kWh/t)": round(ext_kwh_t, 1),
        "Carbon (kg CO₂e/t)": round(ext_kwh_t * grid_factor, 2),
        "Cost ($/t)": round(ext_kwh_t * tariff, 2),
    })

    return Results(
        pre_ext_kwh_t=pre_ext_kwh_t, ext_kwh_t=ext_kwh_t, total_kwh_t=total_kwh_t,
        transit_co2=transit_co2, pre_ext_co2=pre_ext_co2, ext_co2=ext_co2,
        process_co2=process_co2, total_gwp=total_gwp, abatement=abatement,
        pct_reduction=pct_reduction, energy_opex_t=energy_opex_t,
        raw_input_cost_t=raw_input_cost_t, gross_margin_t=gross_margin_t,
        net_margin_t=net_margin_t, daily_profit=daily_profit,
        subsystem_df=pd.DataFrame(rows),
    )


# ------------------------------------------------------------------------------
# Chart helpers - clean, minimal Plotly styling
# ------------------------------------------------------------------------------
_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, -apple-system, sans-serif", color=CLR["text2"], size=12),
    margin=dict(l=48, r=24, t=32, b=48),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11, color=CLR["text2"])),
)


def _style(fig: go.Figure, **kw) -> go.Figure:
    """Apply consistent layout to a Plotly figure."""
    fig.update_layout(**{**_LAYOUT, **kw})
    fig.update_xaxes(
        gridcolor="rgba(0,0,0,0.05)", zeroline=False,
        tickfont=dict(color=CLR["text2"], size=11),
        title_font=dict(color=CLR["text2"], size=12),
    )
    fig.update_yaxes(
        gridcolor="rgba(0,0,0,0.05)", zeroline=False,
        tickfont=dict(color=CLR["text2"], size=11),
        title_font=dict(color=CLR["text2"], size=12),
    )
    return fig


# ------------------------------------------------------------------------------
# Sidebar controls
# ------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Parameters")

    if st.button("Reset to defaults", width="stretch", type="secondary"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

    st.markdown('<div class="sidebar-section">Throughput & Operations</div>',
                unsafe_allow_html=True)
    throughput = st.slider("Daily throughput (t/day)", 5.0, 40.0,
                           DEFAULTS["throughput"], 0.5)
    op_hours = st.slider("Operating hours / day", 8.0, 24.0,
                         DEFAULTS["op_hours"], 1.0)
    yield_pct = st.slider("Process yield (%)", 60.0, 95.0,
                          DEFAULTS["yield_pct"], 0.5)

    st.markdown('<div class="sidebar-section">Energy</div>',
                unsafe_allow_html=True)
    pre_ext_kw = st.slider("Pre-extrusion power (kW)", 150.0, 400.0,
                           DEFAULTS["pre_ext_kw"], 1.0)
    ext_kwh_t = st.slider("Extrusion energy (kWh/t)", 150.0, 400.0,
                          DEFAULTS["ext_kwh_t"], 5.0)
    tariff = st.slider("Electricity tariff ($/kWh)", 0.80, 2.50,
                       DEFAULTS["tariff"], 0.05)

    st.markdown('<div class="sidebar-section">Logistics & Grid</div>',
                unsafe_allow_html=True)
    distance = st.slider("Transport distance (km)", 5.0, 100.0,
                         DEFAULTS["distance"], 1.0)
    grid_factor = st.slider("Grid emission factor (kg CO₂e/kWh)", 0.20, 0.70,
                            DEFAULTS["grid_factor"], 0.01)

    st.markdown('<div class="sidebar-section">Market Prices</div>',
                unsafe_allow_html=True)
    raw_price = st.slider("Raw HDPE cost ($/t)", 2000.0, 8000.0,
                          DEFAULTS["raw_price"], 100.0)
    sell_price = st.slider("Recycled pellet price ($/t)", 5000.0, 14000.0,
                           DEFAULTS["sell_price"], 100.0)
    food_grade = st.toggle("Food-grade benchmark ($9,500/t)", value=False)


# ------------------------------------------------------------------------------
# Compute results
# ------------------------------------------------------------------------------
r = compute(throughput, op_hours, yield_pct, pre_ext_kw, ext_kwh_t,
            tariff, distance, grid_factor, raw_price, sell_price)

if food_grade:
    r_fg = compute(throughput, op_hours, yield_pct, pre_ext_kw, ext_kwh_t,
                   tariff, distance, grid_factor, raw_price,
                   DEFAULTS["food_grade_price"])


# ------------------------------------------------------------------------------
# Header
# ------------------------------------------------------------------------------
st.markdown(f"""
<div style="margin-bottom: 0.15rem">
    <span style="font-size: 1.3rem; font-weight: 700; color: {CLR['text']}">
        HDPE Recycling - TEA / LCA
    </span>
</div>
<span style="font-size: 0.82rem; color: {CLR['text3']}">
    Post-consumer mechanical recycling
    {throughput:.0f} t/day at {yield_pct:.0f}% yield
</span>
""", unsafe_allow_html=True)

st.markdown(f'<div style="border-bottom: 1px solid {CLR["border"]}; '
            f'margin: 0.5rem 0 1rem 0"></div>', unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# KPI cards
# ------------------------------------------------------------------------------
def _kpi(label: str, value: str, sub: str, sub_color: str = CLR["text3"]) -> str:
    return f"""<div class="kpi">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub" style="color:{sub_color}">{sub}</div>
    </div>"""


k1, k2, k3, k4 = st.columns(4, gap="medium")

with k1:
    st.markdown(_kpi(
        "Total Energy",
        f'{r.total_kwh_t:,.0f} <span style="font-size:0.85rem; font-weight:500; '
        f'color:{CLR["text3"]}">kWh/t</span>',
        f"Pre-ext {r.pre_ext_kwh_t:,.0f} + Extrusion {r.ext_kwh_t:,.0f}",
    ), unsafe_allow_html=True)

with k2:
    st.markdown(_kpi(
        "Carbon Footprint",
        f'{r.total_gwp:,.1f} <span style="font-size:0.85rem; font-weight:500; '
        f'color:{CLR["text3"]}">kg CO₂e/t</span>',
        f"↓ {r.pct_reduction:.1f}% vs virgin HDPE",
        CLR["green"],
    ), unsafe_allow_html=True)

with k3:
    st.markdown(_kpi(
        "Energy OpEx",
        f'${r.energy_opex_t:,.0f} <span style="font-size:0.85rem; font-weight:500; '
        f'color:{CLR["text3"]}">/t</span>',
        f"@ ${tariff:.2f}/kWh",
    ), unsafe_allow_html=True)

with k4:
    margin_clr = CLR["green"] if r.net_margin_t >= 0 else CLR["red"]
    sign = "+" if r.net_margin_t >= 0 else ""
    st.markdown(_kpi(
        "Net Margin",
        f'<span style="color:{margin_clr}">{sign}${r.net_margin_t:,.0f}</span>'
        f' <span style="font-size:0.85rem; font-weight:500; '
        f'color:{CLR["text3"]}">/t</span>',
        f"Daily profit: ${r.daily_profit:,.0f}",
        margin_clr,
    ), unsafe_allow_html=True)

st.markdown('<div style="height:0.6rem"></div>', unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# Tabs
# ------------------------------------------------------------------------------
tab_lca, tab_tea, tab_proc = st.tabs([
    "Environmental Impact",
    "Economic Assessment",
    "Process Inventory",
])

# --- TAB 1 : Environmental Impact (LCA) -------------------------------------
with tab_lca:
    st.markdown('<div style="height:0.35rem"></div>', unsafe_allow_html=True)
    col_l, col_r = st.columns(2, gap="large")

    # -- Emission breakdown donut --
    with col_l:
        st.markdown('<div class="section-label">Emission Breakdown</div>',
                    unsafe_allow_html=True)

        labels = ["Transport", "Pre-Extrusion", "Extrusion"]
        values = [r.transit_co2, r.pre_ext_co2, r.ext_co2]
        colors = ["#d97706", "#0d9488", "#6366f1"]

        fig_donut = go.Figure(go.Pie(
            labels=labels, values=values,
            hole=0.55,
            marker=dict(colors=colors, line=dict(color="#ffffff", width=2)),
            textinfo="label+percent",
            textposition="outside",
            textfont=dict(size=12, color=CLR["text"]),
            hovertemplate="%{label}<br>%{value:.2f} kg CO₂e/t<br>%{percent}"
                          "<extra></extra>",
            sort=False,
        ))
        fig_donut.add_annotation(
            text=f"<b>{r.total_gwp:.0f}</b><br>"
                 f"<span style='font-size:11px'>kg CO₂e/t</span>",
            showarrow=False,
            font=dict(size=17, color=CLR["text"]),
        )
        _style(fig_donut, height=380, showlegend=False)
        st.plotly_chart(fig_donut, width="stretch")

    # -- Recycled vs. virgin comparison --
    with col_r:
        st.markdown('<div class="section-label">Recycled vs. Virgin HDPE</div>',
                    unsafe_allow_html=True)

        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(
            x=["Recycled HDPE"], y=[r.total_gwp],
            marker_color="#16a34a", marker_line=dict(width=0),
            text=[f"{r.total_gwp:.0f}"], textposition="outside",
            textfont=dict(size=13, color=CLR["text"]),
            width=0.45, showlegend=False,
        ))
        fig_comp.add_trace(go.Bar(
            x=["Virgin HDPE"], y=[DEFAULTS["virgin_gwp"]],
            marker_color="#dc2626", marker_opacity=0.65,
            marker_line=dict(width=0),
            text=[f'{DEFAULTS["virgin_gwp"]:,.0f}'], textposition="outside",
            textfont=dict(size=13, color=CLR["text"]),
            width=0.45, showlegend=False,
        ))
        fig_comp.add_annotation(
            x=0.5, y=DEFAULTS["virgin_gwp"] * 0.48,
            text=f"<b>{r.pct_reduction:.1f}%</b> lower",
            showarrow=False,
            font=dict(size=14, color=CLR["green"]),
            xref="paper",
        )
        _style(fig_comp, height=360, yaxis_title="kg CO₂e / tonne", bargap=0.35)
        st.plotly_chart(fig_comp, width="stretch")

    # -- LCI summary table --
    st.markdown('<div class="section-label" style="margin-top:0.4rem">'
                'Life Cycle Inventory</div>', unsafe_allow_html=True)

    lci = pd.DataFrame({
        "Parameter": [
            "Functional unit", "Raw material input", "Process yield",
            "Transport distance", "Transport emissions",
            "Pre-extrusion energy", "Extrusion energy",
            "Total electrical demand", "Grid emission factor",
            "Processing emissions", "Total GWP", "Abatement vs. virgin",
        ],
        "Value": [
            "1 tonne recycled HDPE pellet",
            f"{1.0 / (yield_pct / 100):.3f} t raw",
            f"{yield_pct:.1f} %",
            f"{distance:.0f} km",
            f"{r.transit_co2:.2f} kg CO₂e",
            f"{r.pre_ext_kwh_t:.1f} kWh",
            f"{r.ext_kwh_t:.1f} kWh",
            f"{r.total_kwh_t:.1f} kWh",
            f"{grid_factor:.2f} kg CO₂e/kWh",
            f"{r.process_co2:.2f} kg CO₂e",
            f"{r.total_gwp:.2f} kg CO₂e",
            f"{r.abatement:.0f} kg CO₂e  ({r.pct_reduction:.1f} %)",
        ],
    })
    st.dataframe(lci, width="stretch", hide_index=True, height=460)


# --- TAB 2 : Techno-Economic Assessment -------------------------------------
with tab_tea:
    st.markdown('<div style="height:0.35rem"></div>', unsafe_allow_html=True)
    tea_l, tea_r = st.columns(2, gap="large")

    # -- Cost structure --
    with tea_l:
        st.markdown('<div class="section-label">Cost Structure per Tonne</div>',
                    unsafe_allow_html=True)

        cats = ["Raw Material\nInput", "Energy\nOpEx", "Net\nMargin"]
        vals = [r.raw_input_cost_t, r.energy_opex_t, r.net_margin_t]
        bar_colors = [
            "#d97706",
            "#6366f1",
            "#16a34a" if r.net_margin_t >= 0 else "#dc2626",
        ]

        fig_cost = go.Figure()
        for cat, val, clr in zip(cats, vals, bar_colors):
            fig_cost.add_trace(go.Bar(
                x=[cat], y=[val],
                marker_color=clr, marker_opacity=0.85,
                marker_line=dict(width=0),
                text=[f"${val:,.0f}"], textposition="outside",
                textfont=dict(size=12, color=CLR["text"]),
                showlegend=False, width=0.50,
            ))

        fig_cost.add_hline(
            y=sell_price, line_dash="dot", line_color=CLR["text3"], line_width=1,
            annotation_text=f"Selling price ${sell_price:,.0f}",
            annotation_font=dict(color=CLR["text2"], size=11),
            annotation_position="top right",
        )
        _style(fig_cost, height=370, yaxis_title="$ / tonne", bargap=0.30)
        st.plotly_chart(fig_cost, width="stretch")

        breakeven = r.raw_input_cost_t + r.energy_opex_t
        st.markdown(f"""<div class="callout">
            <strong>Break-even price:</strong>&ensp;${breakeven:,.0f} / tonne
            &nbsp;(Material ${r.raw_input_cost_t:,.0f} + Energy ${r.energy_opex_t:,.0f})
        </div>""", unsafe_allow_html=True)

    # -- Sensitivity analysis --
    with tea_r:
        st.markdown('<div class="section-label">Sensitivity - Net Margin</div>',
                    unsafe_allow_html=True)

        sweep_var = st.radio(
            "Sweep variable",
            ["Electricity tariff", "Raw material price"],
            horizontal=True, label_visibility="collapsed",
        )

        if sweep_var == "Electricity tariff":
            xs = np.linspace(0.80, 2.50, 60)
            ys = np.array([
                compute(throughput, op_hours, yield_pct, pre_ext_kw, ext_kwh_t,
                        t, distance, grid_factor, raw_price,
                        sell_price).net_margin_t
                for t in xs
            ])
            x_title = "Electricity tariff ($/kWh)"
            cur_x = tariff
        else:
            xs = np.linspace(2000, 8000, 60)
            ys = np.array([
                compute(throughput, op_hours, yield_pct, pre_ext_kw, ext_kwh_t,
                        tariff, distance, grid_factor, rp,
                        sell_price).net_margin_t
                for rp in xs
            ])
            x_title = "Raw material price ($/t)"
            cur_x = raw_price

        fig_sens = go.Figure()

        # Positive / negative fill regions
        fig_sens.add_trace(go.Scatter(
            x=xs, y=np.clip(ys, 0, None),
            fill="tozeroy", fillcolor="rgba(22,163,74,0.06)",
            line=dict(width=0), showlegend=False, hoverinfo="skip",
        ))
        fig_sens.add_trace(go.Scatter(
            x=xs, y=np.clip(ys, None, 0),
            fill="tozeroy", fillcolor="rgba(220,38,38,0.06)",
            line=dict(width=0), showlegend=False, hoverinfo="skip",
        ))

        # Main line
        fig_sens.add_trace(go.Scatter(
            x=xs, y=ys,
            mode="lines",
            line=dict(width=2, color=CLR["green"]),
            name="Net margin",
            hovertemplate="Margin: $%{y:,.0f}<extra></extra>",
        ))

        # Zero reference
        fig_sens.add_hline(y=0, line_dash="dash", line_color=CLR["red"],
                           line_width=1, opacity=0.45)

        # Current operating point
        fig_sens.add_trace(go.Scatter(
            x=[cur_x], y=[r.net_margin_t],
            mode="markers",
            marker=dict(size=9, color=CLR["accent"],
                        line=dict(width=2, color="#ffffff")),
            name=f"Current (${r.net_margin_t:,.0f})",
            hovertemplate=f"Current: ${r.net_margin_t:,.0f}<extra></extra>",
        ))

        # Food-grade overlay
        if food_grade:
            if sweep_var == "Electricity tariff":
                fg_ys = np.array([
                    compute(throughput, op_hours, yield_pct, pre_ext_kw,
                            ext_kwh_t, t, distance, grid_factor, raw_price,
                            DEFAULTS["food_grade_price"]).net_margin_t
                    for t in xs
                ])
            else:
                fg_ys = np.array([
                    compute(throughput, op_hours, yield_pct, pre_ext_kw,
                            ext_kwh_t, tariff, distance, grid_factor, rp,
                            DEFAULTS["food_grade_price"]).net_margin_t
                    for rp in xs
                ])
            fig_sens.add_trace(go.Scatter(
                x=xs, y=fg_ys,
                mode="lines",
                line=dict(width=2, color=CLR["amber"], dash="dot"),
                name="Food-grade ($9,500/t)",
            ))

        _style(fig_sens, height=370, xaxis_title=x_title,
               yaxis_title="$ / tonne", showlegend=True,
               legend=dict(
                   bgcolor="rgba(0,0,0,0)",
                   font=dict(size=11, color=CLR["text2"]),
                   yanchor="top", y=0.99, xanchor="right", x=0.99,
               ))
        st.plotly_chart(fig_sens, width="stretch")

    # Food-grade comparison callout
    if food_grade:
        delta = r_fg.net_margin_t - r.net_margin_t
        st.markdown(f"""<div class="callout" style="border-left-color:{CLR['amber']}">
            <strong>Food-grade scenario</strong> ($9,500/t) →
            Net margin <strong style="color:{CLR['green']}">${r_fg.net_margin_t:,.0f}</strong>/t
            &nbsp;·&nbsp; Daily profit <strong>${r_fg.daily_profit:,.0f}</strong>
            &nbsp;·&nbsp; Premium uplift <strong style="color:{CLR['amber']}">+${delta:,.0f}</strong>/t
        </div>""", unsafe_allow_html=True)


# --- TAB 3 : Process Flow & Inventory ---------------------------------------
with tab_proc:
    st.markdown('<div style="height:0.35rem"></div>', unsafe_allow_html=True)

    # Process flow cards
    st.markdown('<div class="section-label">Process Flow</div>',
                unsafe_allow_html=True)

    stages = [
        ("1", "Sorting",
         f"{SUBSYSTEMS['Sorting (Optical / Flake)']:.0f} kW"),
        ("2", "Conveying",
         f"{SUBSYSTEMS['Conveyors & Vertical Elevators']:.1f} kW"),
        ("3", "Shredding",
         f"{SUBSYSTEMS['Shredder / Crusher']:.1f} kW"),
        ("4", "Washing",
         f"{SUBSYSTEMS['Washing, Friction Washers & Dewatering']:.0f} kW"),
        ("5", "Extrusion",
         f"{ext_kwh_t:.0f} kWh/t"),
    ]

    cols = st.columns([4, 1, 4, 1, 4, 1, 4, 1, 4])
    for i, (icon, name, spec) in enumerate(stages):
        with cols[i * 2]:
            st.markdown(f"""<div class="flow-card">
                <div class="flow-icon">{icon}</div>
                <div class="flow-name">{name}</div>
                <div class="flow-spec">{spec}</div>
            </div>""", unsafe_allow_html=True)
        if i < len(stages) - 1:
            with cols[i * 2 + 1]:
                st.markdown('<div class="flow-arrow">→</div>',
                            unsafe_allow_html=True)

    st.markdown('<div style="height:0.8rem"></div>', unsafe_allow_html=True)

    p_left, p_right = st.columns([3, 2], gap="large")

    with p_left:
        st.markdown('<div class="section-label">Subsystem Energy Inventory</div>',
                    unsafe_allow_html=True)
        st.markdown(
            f'<span style="font-size:0.78rem; color:{CLR["text3"]}">'
            f'{throughput:.1f} t/day · {op_hours:.0f} h · '
            f'{yield_pct:.0f}% yield</span>',
            unsafe_allow_html=True,
        )

        display_df = r.subsystem_df.copy()
        totals = {
            "Stage": "Total",
            "Power (kW)": sum(SUBSYSTEMS.values()),
            "Energy (kWh/t)": round(r.total_kwh_t, 1),
            "Carbon (kg CO₂e/t)": round(r.process_co2, 2),
            "Cost ($/t)": round(r.energy_opex_t, 2),
        }
        display_df = pd.concat(
            [display_df, pd.DataFrame([totals])], ignore_index=True
        )
        st.dataframe(display_df, width="stretch",
                     hide_index=True, height=300)

    with p_right:
        st.markdown('<div class="section-label">Energy by Stage</div>',
                    unsafe_allow_html=True)

        chart_df = r.subsystem_df.copy()
        fig_bar = go.Figure(go.Bar(
            y=chart_df["Stage"],
            x=chart_df["Energy (kWh/t)"],
            orientation="h",
            marker=dict(
                color=chart_df["Energy (kWh/t)"],
                colorscale=[[0, "#0d9488"], [0.5, "#2563eb"], [1, "#6366f1"]],
                line=dict(width=0),
            ),
            text=chart_df["Energy (kWh/t)"].apply(lambda v: f"{v:.0f}"),
            textposition="outside",
            textfont=dict(size=11, color=CLR["text2"]),
        ))
        _style(fig_bar, height=300, showlegend=False,
               xaxis_title="kWh / tonne",
               yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_bar, width="stretch")


# ------------------------------------------------------------------------------
# Footer
# ------------------------------------------------------------------------------
st.markdown(f"""<div style="
    border-top: 1px solid {CLR['border']};
    margin-top: 2rem;
    padding-top: 0.7rem;
    text-align: center;
    font-size: 0.72rem;
    color: {CLR['text3']};
">
    HDPE Recycling TEA / LCA Model
</div>""", unsafe_allow_html=True)
