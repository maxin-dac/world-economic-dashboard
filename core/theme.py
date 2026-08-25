"""Theme helpers shared by dashboard visualizations."""
import plotly.graph_objects as go
import streamlit as st


def style_plotly(fig: go.Figure, mode: str) -> go.Figure:
    dark = mode == "dark"
    text = "#f8fafc" if dark else "#172033"
    muted = "#94a3b8" if dark else "#69778d"
    grid = "rgba(148, 163, 184, 0.18)" if dark else "rgba(100, 116, 139, 0.18)"
    hover_bg = "#1e293b" if dark else "#ffffff"
    layout_style = dict(
        font=dict(color=text),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(bgcolor=hover_bg, font_color=text, bordercolor=grid),
        legend=dict(font=dict(color=text)),
        xaxis=dict(gridcolor=grid, linecolor=grid, zerolinecolor=grid, tickfont=dict(color=muted)),
        yaxis=dict(gridcolor=grid, linecolor=grid, zerolinecolor=grid, tickfont=dict(color=muted)),
    )
    if fig.layout.title.text:
        layout_style["title_font"] = dict(color=text)
    fig.update_layout(**layout_style)
    fig.update_geos(
        bgcolor="rgba(0,0,0,0)",
        showland=True,
        landcolor="rgba(0,0,0,0)",
        showocean=True,
        oceancolor="rgba(0,0,0,0)",
        showcountries=True,
        countrycolor=muted,
    )
    return fig


def render_table(data, mode: str, **kwargs) -> None:
    """Render the validated native dark dataframe with consistent row density."""
    kwargs.setdefault("row_height", 36)
    st.dataframe(data, **kwargs)