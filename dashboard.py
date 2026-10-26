# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "streamlit>=1.32",
#   "pandas>=2.1",
#   "plotly>=5.18",
# ]
# ///
"""Dashboard local dos votos após as 17h (2º turno 2026)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DIR = Path(__file__).resolve().parent
SECOES = DIR / "secoes.csv"
MUNICIPIOS = DIR / "municipios.csv"

INK = "#1F2937"
NAV = "#0B1F33"
PRIMARY = "#1565C0"
ACCENT = "#E65100"
CHART_PALETTE = ["#1565C0", "#E65100", "#00897B", "#6A1B9A", "#F9A825", "#546E7A", "#C62828"]

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,300;0,400;0,500;0,700;1,400&display=swap');

/* —— Mobile first —— */
html, body, [class*="css"], .stApp, .stMarkdown, p, label, input, button {
  font-family: 'Roboto', Helvetica, Arial, sans-serif !important;
}
h1, h2, h3, .hero-title, .kpi .value {
  font-family: 'Roboto', Helvetica, Arial, sans-serif !important;
  font-weight: 700 !important;
}

.stApp, [data-testid="stAppViewContainer"] > .main {
  background: #F4F6F8;
}
.main .block-container {
  padding: 0.75rem 0.85rem 2rem;
  max-width: 100%;
}

/* Colunas empilham no mobile; KPIs 2 por linha */
div[data-testid="stHorizontalBlock"] {
  flex-wrap: wrap !important;
  gap: 0.65rem !important;
}
div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
  min-width: min(100%, 160px) !important;
  flex: 1 1 calc(50% - 0.4rem) !important;
}
div[data-testid="stHorizontalBlock"].chart-stack > div[data-testid="column"],
div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] .chart-full {
  flex: 1 1 100% !important;
}

[data-testid="stSidebar"] {
  background: #0B1F33 !important;
  border-right: 4px solid #1565C0 !important;
}
[data-testid="stSidebar"] > div:first-child {
  background: #0B1F33;
  padding-top: 1rem;
}
[data-testid="stSidebar"] .stMarkdown h3 {
  color: #FFFFFF !important;
  font-size: 0.85rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  margin-bottom: 0.65rem !important;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
[data-testid="stSidebar"] .stCheckbox label span {
  color: #B8C5D1 !important;
  font-weight: 500 !important;
  font-size: 0.88rem !important;
}
[data-testid="stSidebar"] [data-testid="stCaption"] { color: #8A9AAB !important; }
[data-testid="stSidebar"] hr {
  border-color: rgba(255,255,255,0.12) !important;
  margin: 1rem 0 !important;
}
[data-testid="stSidebar"] .stButton > button {
  background: #1565C0 !important;
  color: #fff !important;
  border: none !important;
  font-weight: 500 !important;
  width: 100%;
  min-height: 2.6rem;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: #0D47A1 !important;
  color: #fff !important;
}
.sidebar-brand {
  color: #fff;
  font-size: 0.68rem;
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  opacity: 0.7;
  margin-bottom: 0.3rem;
}
.sidebar-title {
  color: #fff;
  font-size: 1.05rem;
  font-weight: 700;
  margin: 0 0 1rem 0;
  line-height: 1.3;
}

.hero {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-left: 5px solid #1565C0;
  border-radius: 8px;
  padding: 0.95rem 1rem 1.05rem;
  margin-bottom: 0.9rem;
}
.hero-title {
  font-size: 1.45rem;
  font-weight: 700;
  color: #0B1F33;
  margin: 0;
  letter-spacing: -0.01em;
}
.hero-sub {
  color: #5B6B7C;
  font-size: 0.9rem;
  font-weight: 400;
  margin: 0.35rem 0 0;
  line-height: 1.45;
}

.kpi {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-left: 5px solid #1565C0;
  padding: 0.85rem 0.9rem;
  border-radius: 8px;
  min-height: 5.6rem;
  height: 100%;
}
.kpi.accent { border-left-color: #E65100; }
.kpi .label {
  font-size: 0.68rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748B;
}
.kpi .value {
  font-size: 1.35rem;
  font-weight: 700;
  color: #0B1F33;
  line-height: 1.25;
  margin-top: 0.15rem;
}
.kpi .hint {
  font-size: 0.78rem;
  color: #64748B;
  margin-top: 0.15rem;
}

.section-title {
  font-size: 1rem !important;
  font-weight: 700 !important;
  color: #0B1F33 !important;
  margin: 1.1rem 0 0.55rem !important;
  padding-bottom: 0.35rem;
  border-bottom: 2px solid #1565C0;
}

.chart-wrap {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  padding: 0.35rem 0.25rem 0.15rem;
  margin-bottom: 0.85rem;
}

.credit {
  margin-top: 1.5rem;
  padding: 0.9rem 1rem;
  background: #0B1F33;
  border-radius: 8px;
  color: #E8EEF4;
  font-size: 0.85rem;
  line-height: 1.5;
}
.credit strong { color: #FFFFFF; font-weight: 700; }
.credit .role { color: #90CAF9; font-weight: 500; }

.js-plotly-plot .ytick text,
.js-plotly-plot .xtick text,
.js-plotly-plot .legendtext,
.js-plotly-plot .gtitle,
.js-plotly-plot .g-xtitle text,
.js-plotly-plot .g-ytitle text {
  fill: #0B1F33 !important;
  opacity: 1 !important;
  font-weight: 700 !important;
}
.js-plotly-plot .ytick text { font-size: 12px !important; }
.js-plotly-plot { width: 100% !important; }

/* Mobile: modebar não cobre o título */
.js-plotly-plot .modebar-container {
  top: auto !important;
  bottom: 4px !important;
  right: 4px !important;
}
.js-plotly-plot .gtitle {
  transform: translateY(4px) !important;
}

/* —— Tablet+ —— */
@media (min-width: 768px) {
  .main .block-container {
    padding: 1.25rem 1.5rem 2.25rem;
  }
  .hero {
    padding: 1.2rem 1.4rem 1.3rem;
    margin-bottom: 1.15rem;
  }
  .hero-title { font-size: 1.85rem; }
  .hero-sub { font-size: 0.98rem; max-width: 46rem; }
  .kpi { min-height: 6.2rem; padding: 1rem 1.1rem; }
  .kpi .value { font-size: 1.65rem; }
  .kpi .label { font-size: 0.72rem; }
  .section-title { font-size: 1.15rem !important; margin: 1.4rem 0 0.7rem !important; }
  .sidebar-title { font-size: 1.15rem; }
  .chart-wrap { padding: 0.5rem 0.4rem 0.25rem; margin-bottom: 1.1rem; }
  .js-plotly-plot .ytick text { font-size: 13px !important; }
  /* Desktop: modebar volta ao canto superior direito */
  .js-plotly-plot .modebar-container {
    top: 0 !important;
    bottom: auto !important;
    right: 0 !important;
  }
  .js-plotly-plot .gtitle {
    transform: none !important;
  }
}

/* —— Desktop: gráficos largos e KPIs em 4 colunas —— */
@media (min-width: 1100px) {
  .main .block-container {
    max-width: 1480px;
    padding: 1.5rem 2rem 2.75rem;
  }
  div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    flex: 1 1 0 !important;
    min-width: 0 !important;
  }
  .kpi .value { font-size: 1.75rem; }
  .credit { font-size: 0.9rem; padding: 1rem 1.2rem; }
}
</style>
"""


@st.cache_data(show_spinner="Carregando seções…")
def load_secoes(_mtime: float) -> pd.DataFrame:
    if not SECOES.exists():
        return pd.DataFrame()
    df = pd.read_csv(SECOES)
    df["uf"] = df["uf"].astype(str).str.upper()
    df = df[df["uf"] != "ZZ"].copy()
    for col in ("abertura_brt", "encerramento_brt", "ultimo_voto_brt"):
        if col in df.columns:
            t = pd.to_timedelta(df[col].replace("", pd.NA), errors="coerce")
            df[f"{col}_h"] = t.dt.total_seconds() / 3600
    return df


@st.cache_data(show_spinner="Carregando municípios…")
def load_municipios(_mtime: float) -> pd.DataFrame:
    if not MUNICIPIOS.exists():
        return pd.DataFrame()
    df = pd.read_csv(MUNICIPIOS)
    df["uf"] = df["uf"].astype(str).str.upper()
    return df


def secoes_mtime() -> float:
    return SECOES.stat().st_mtime if SECOES.exists() else 0.0


def municipios_mtime() -> float:
    return MUNICIPIOS.stat().st_mtime if MUNICIPIOS.exists() else 0.0


def fmt_int(n: float | int) -> str:
    return f"{int(n):,}".replace(",", ".")


def kpi(label: str, value: str, hint: str = "", accent: bool = False) -> str:
    cls = "kpi accent" if accent else "kpi"
    hint_html = f'<div class="hint">{hint}</div>' if hint else ""
    return f'<div class="{cls}"><div class="label">{label}</div><div class="value">{value}</div>{hint_html}</div>'


def chart_height(n_cats: int, row_px: int = 26, base: int = 160, lo: int = 380, hi: int = 820) -> int:
    """Altura responsiva: cresce com categorias, com piso/teto confortáveis no desktop."""
    return max(lo, min(hi, base + n_cats * row_px))


def plot_layout(fig: go.Figure, height: int = 480, left: int = 56) -> go.Figure:
    tick = dict(
        family="Roboto, Helvetica, Arial, sans-serif",
        size=13,
        color="#0B1F33",
    )
    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FAFBFC",
        font=dict(family="Roboto, Helvetica, Arial, sans-serif", color="#0B1F33", size=13),
        margin=dict(l=left, r=36, t=72, b=56),
        height=height,
        autosize=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            x=0,
            font=dict(size=12, color="#0B1F33"),
        ),
        title=dict(
            font=dict(size=16, color=NAV, family="Roboto, Helvetica, Arial, sans-serif"),
            x=0.01,
            xanchor="left",
            y=0.98,
            yanchor="top",
            pad=dict(t=4, b=12),
        ),
    )
    fig.update_xaxes(
        gridcolor="#E8EDF2",
        zeroline=False,
        linecolor="#94A3B8",
        tickfont=tick,
        title_font=dict(size=12, color="#334155"),
        color="#0B1F33",
    )
    fig.update_yaxes(
        gridcolor="#E8EDF2",
        zeroline=False,
        linecolor="#94A3B8",
        tickfont={**tick, "size": 14},
        title_font=dict(size=12, color="#334155"),
        color="#0B1F33",
    )
    return fig


PLOT_CFG = {
    "responsive": True,
    "displayModeBar": True,
    "displaylogo": False,
    "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
    "toImageButtonOptions": {"format": "png", "filename": "urnas_tardias"},
}


def main() -> None:
    st.set_page_config(
        page_title="Urnas tardias · 2026",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(CSS, unsafe_allow_html=True)

    secoes = load_secoes(secoes_mtime())
    mun = load_municipios(municipios_mtime())

    st.markdown(
        """
<div class="hero">
  <p class="hero-title">Urnas tardias</p>
  <p class="hero-sub">Votos computados depois das 17h no 2º turno de 2026, nas urnas que encerraram após as 17h45 (horário de Brasília).</p>
</div>
""",
        unsafe_allow_html=True,
    )

    if secoes.empty:
        st.error(
            "Não achei `secoes.csv`. Rode `uv run crawl.py` e depois `python3 analisa.py`."
        )
        return

    with st.sidebar:
        st.markdown(
            '<p class="sidebar-brand">Análise eleitoral · 2026</p>'
            '<p class="sidebar-title">Navegação e filtros</p>',
            unsafe_allow_html=True,
        )
        st.markdown("### Escopo")
        ufs = sorted(secoes["uf"].unique().tolist())
        uf_modo = st.radio(
            "UF",
            ["Todos", "Selecionar"],
            index=0,
            horizontal=True,
            key="uf_modo",
            help="Todos = Brasil inteiro (exceto exterior).",
        )
        if uf_modo == "Todos":
            uf_sel = []
            base = secoes
        else:
            uf_sel = st.multiselect("Escolher UFs", ufs, default=[], key="filtro_uf")
            base = secoes[secoes["uf"].isin(uf_sel)] if uf_sel else secoes.iloc[0:0]

        munis = sorted(base["municipio"].unique().tolist())
        mun_sel = st.multiselect("Município (vazio = todos)", munis, default=[], key="filtro_mun")
        if mun_sel:
            base = base[base["municipio"].isin(mun_sel)]

        st.markdown("### Opções")
        so_est = st.checkbox("Só urnas estendidas", value=False)
        if so_est:
            base = base[base["classe"] == "estendida"]

        if st.button("Recarregar CSVs"):
            load_secoes.clear()
            load_municipios.clear()
            st.rerun()

        st.markdown("---")
        st.caption(f"{SECOES.name}: {fmt_int(len(secoes))} seções · {len(ufs)} UFs")

    if base.empty:
        st.warning("Nenhuma seção com esses filtros.")
        return

    est = base[base["classe"] == "estendida"]
    votos_tarde = int(est["votos_apos_17h"].sum())
    urnas_c_voto = int((est["votos_apos_17h"] > 0).sum())
    pct_est = 100 * len(est) / len(base) if len(base) else 0
    votos_tot = int(base["votos_total"].sum())
    peso = 100 * votos_tarde / votos_tot if votos_tot else 0

    # KPIs: 2x2 no mobile; em desktop largo as 4 colunas se expandem via CSS
    k1, k2 = st.columns(2)
    k1.markdown(
        kpi("Urnas no filtro", fmt_int(len(base)), f"{fmt_int(votos_tot)} votos registrados"),
        unsafe_allow_html=True,
    )
    k2.markdown(
        kpi("Urnas estendidas", fmt_int(len(est)), f"{pct_est:.1f}% das urnas"),
        unsafe_allow_html=True,
    )
    k3, k4 = st.columns(2)
    k3.markdown(
        kpi("Com voto após 17h", fmt_int(urnas_c_voto), "entre as estendidas", accent=True),
        unsafe_allow_html=True,
    )
    k4.markdown(
        kpi("Votos após 17h", fmt_int(votos_tarde), f"{peso:.4f}% do total no filtro", accent=True),
        unsafe_allow_html=True,
    )

    # Gráficos empilhados em largura total (melhor no mobile e maiores no desktop)
    por_uf = (
        base.assign(estendida=base["classe"].eq("estendida"))
        .groupby("uf", as_index=False)
        .agg(urnas=("secao", "count"), estendidas=("estendida", "sum"))
    )
    v17 = est.groupby("uf", as_index=False)["votos_apos_17h"].sum()
    por_uf = por_uf.merge(v17, on="uf", how="left").fillna({"votos_apos_17h": 0})
    por_uf["pct"] = 100 * por_uf["estendidas"] / por_uf["urnas"]
    por_uf = por_uf.sort_values("estendidas", ascending=True)

    fig_uf = go.Figure()
    fig_uf.add_trace(
        go.Bar(
            y=por_uf["uf"],
            x=por_uf["estendidas"],
            orientation="h",
            name="Urnas estendidas",
            marker_color=PRIMARY,
            text=por_uf["estendidas"].map(fmt_int),
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}: %{x:,} estendidas<br>%{customdata[0]:.1f}% das urnas<br>%{customdata[1]:,.0f} votos >17h<extra></extra>",
            customdata=por_uf[["pct", "votos_apos_17h"]],
        )
    )
    fig_uf.update_layout(title="Urnas estendidas por UF", xaxis_title="", yaxis_title="")
    fig_uf.update_yaxes(
        tickfont=dict(family="Roboto, Helvetica, Arial, sans-serif", size=15, color="#000000"),
        automargin=True,
    )
    h_uf = chart_height(len(por_uf), row_px=28, base=180, lo=420, hi=900)
    st.plotly_chart(
        plot_layout(fig_uf, height=h_uf, left=72),
        use_container_width=True,
        config=PLOT_CFG,
    )

    if not est.empty and "encerramento_brt_h" in est.columns:
        fig_h = px.histogram(
            est,
            x="encerramento_brt_h",
            nbins=36,
            color_discrete_sequence=[ACCENT],
        )
        fig_h.update_traces(hovertemplate="Encerramento %{x:.2f}h<br>%{y} urnas<extra></extra>")
        fig_h.update_layout(
            title="Horário de encerramento (urnas estendidas)",
            xaxis_title="Hora (Brasília)",
            yaxis_title="Urnas",
            showlegend=False,
        )
        fig_h.add_vline(
            x=17.75,
            line_dash="dot",
            line_color=PRIMARY,
            annotation_text="17h45",
            annotation_font_color=PRIMARY,
        )
        st.plotly_chart(
            plot_layout(fig_h, height=480, left=56),
            use_container_width=True,
            config=PLOT_CFG,
        )
    else:
        st.info("Sem urnas estendidas no filtro.")

    st.markdown('<p class="section-title">Municípios com urnas estendidas</p>', unsafe_allow_html=True)
    mun_view = mun.copy()
    if uf_sel:
        mun_view = mun_view[mun_view["uf"].isin(uf_sel)]
    if mun_sel:
        mun_view = mun_view[mun_view["municipio"].isin(mun_sel)]
    if mun_view.empty:
        # fallback from secoes if municipios.csv desatualizado
        mun_view = (
            est.groupby(["uf", "municipio"], as_index=False)
            .agg(
                urnas=("secao", "count"),
                estendidas=("secao", "count"),
                estendidas_com_voto_apos_17h=("votos_apos_17h", lambda s: (s > 0).sum()),
                votos_apos_17h_nas_estendidas=("votos_apos_17h", "sum"),
            )
        )
        tot = base.groupby(["uf", "municipio"]).size().rename("urnas_tot")
        mun_view = mun_view.merge(tot, on=["uf", "municipio"], how="left")
        mun_view["urnas"] = mun_view["urnas_tot"]
        mun_view["pct_estendidas"] = (100 * mun_view["estendidas"] / mun_view["urnas"]).round(1)
        mun_view = mun_view.drop(columns=["urnas_tot"])
    else:
        # se filtro só estendidas na sidebar, municipios.csv já é só com est>0
        pass

    top = mun_view.sort_values("votos_apos_17h_nas_estendidas", ascending=False).head(15)
    if not top.empty:
        fig_m = px.bar(
            top.sort_values("votos_apos_17h_nas_estendidas"),
            x="votos_apos_17h_nas_estendidas",
            y="municipio",
            color="uf",
            orientation="h",
            color_discrete_sequence=CHART_PALETTE,
            labels={"votos_apos_17h_nas_estendidas": "Votos após 17h", "municipio": ""},
        )
        fig_m.update_layout(title="Top 15 municípios por votos após 17h (urnas estendidas)")
        fig_m.update_yaxes(
            tickfont=dict(family="Roboto, Helvetica, Arial, sans-serif", size=13, color="#000000"),
            automargin=True,
        )
        h_m = chart_height(len(top), row_px=32, base=160, lo=460, hi=640)
        st.plotly_chart(
            plot_layout(fig_m, height=h_m, left=140),
            use_container_width=True,
            config=PLOT_CFG,
        )

        st.dataframe(
            mun_view.sort_values("votos_apos_17h_nas_estendidas", ascending=False).rename(
                columns={
                    "uf": "UF",
                    "municipio": "Município",
                    "urnas": "Urnas",
                    "estendidas": "Estendidas",
                    "pct_estendidas": "% est.",
                    "estendidas_com_voto_apos_17h": "Est. c/ voto >17h",
                    "votos_apos_17h_nas_estendidas": "Votos >17h",
                }
            ),
            use_container_width=True,
            hide_index=True,
            height=320,
        )

    with st.expander("Seções (detalhe)"):
        cols = [
            "uf",
            "municipio",
            "zona",
            "secao",
            "abertura_brt",
            "encerramento_brt",
            "ultimo_voto_brt",
            "votos_apos_17h",
            "votos_total",
            "classe",
        ]
        show = base[cols].sort_values(
            ["votos_apos_17h", "encerramento_brt"], ascending=[False, False]
        )
        st.dataframe(show, use_container_width=True, hide_index=True, height=400)
        st.download_button(
            "Baixar CSV filtrado",
            show.to_csv(index=False).encode("utf-8"),
            file_name="secoes_filtrado.csv",
            mime="text/csv",
        )

    st.markdown(
        """
<div class="credit">
  Desenvolvido por <strong>Jonnes Santos</strong>
  · <span class="role">Arquiteto de Software</span>
</div>
""",
        unsafe_allow_html=True,
    )


def _under_streamlit() -> bool:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        return get_script_run_ctx() is not None
    except Exception:
        return False


if __name__ == "__main__":
    if _under_streamlit():
        main()
    else:
        import subprocess
        import sys

        raise SystemExit(
            subprocess.call(
                [sys.executable, "-m", "streamlit", "run", str(Path(__file__).resolve()), *sys.argv[1:]]
            )
        )
elif _under_streamlit():
    main()
