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
.mobile-tip {
  display: block;
  margin: 0.65rem 0 0.85rem;
  padding: 0.65rem 0.85rem;
  background: #E3F2FD;
  border: 1px solid #90CAF9;
  border-radius: 8px;
  color: #0D47A1;
  font-size: 0.84rem;
  line-height: 1.4;
}
@media (min-width: 768px) {
  .mobile-tip { display: none !important; }
}
.explain {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-left: 5px solid #00897B;
  border-radius: 8px;
  padding: 1rem 1.1rem 1.05rem;
  margin: 0.85rem 0 1rem;
  color: #334155;
  font-size: 0.92rem;
  line-height: 1.5;
}
.explain h3 {
  margin: 0 0 0.55rem !important;
  font-size: 1.05rem !important;
  color: #0B1F33 !important;
  font-weight: 700 !important;
}
.explain p { margin: 0 0 0.55rem !important; }
.explain p:last-child { margin-bottom: 0 !important; }
.explain strong { color: #0B1F33; }
.explain .num { color: #E65100; font-weight: 700; }
@media (min-width: 768px) {
  .explain { font-size: 0.95rem; padding: 1.15rem 1.35rem; }
  .explain h3 { font-size: 1.12rem !important; }
}
.chart-head {
  margin: 1rem 0 0.35rem;
}
.chart-head h3 {
  margin: 0 !important;
  font-size: 1.05rem !important;
  font-weight: 700 !important;
  color: #0B1F33 !important;
  line-height: 1.3 !important;
  border: none !important;
  padding: 0 !important;
}
.chart-head p {
  margin: 0.2rem 0 0 !important;
  font-size: 0.82rem !important;
  color: #64748B !important;
  line-height: 1.35 !important;
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
.kpi.teal { border-left-color: #00897B; }
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
.js-plotly-plot .ytick text { font-size: 11px !important; }
.js-plotly-plot { width: 100% !important; }
/* Mobile: esconde toolbar do Plotly (zoom/pan confunde o toque) */
.js-plotly-plot .modebar-container { display: none !important; }
/* Evita arrastar o gráfico no scroll do celular */
.js-plotly-plot .plotly { touch-action: pan-y !important; }

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
  .chart-head h3 { font-size: 1.15rem !important; }
  .js-plotly-plot .ytick text { font-size: 13px !important; }
  .js-plotly-plot .modebar-container {
    display: flex !important;
    top: 0 !important;
    bottom: auto !important;
    right: 0 !important;
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


def kpi(label: str, value: str, hint: str = "", tone: str = "") -> str:
    cls = "kpi"
    if tone == "accent":
        cls += " accent"
    elif tone == "teal":
        cls += " teal"
    hint_html = f'<div class="hint">{hint}</div>' if hint else ""
    return f'<div class="{cls}"><div class="label">{label}</div><div class="value">{value}</div>{hint_html}</div>'


def chart_height(n_cats: int, row_px: int = 26, base: int = 160, lo: int = 380, hi: int = 820) -> int:
    """Altura responsiva: cresce com categorias, com piso/teto confortáveis no desktop."""
    return max(lo, min(hi, base + n_cats * row_px))


def chart_head(title: str, hint: str = "") -> None:
    hint_html = f"<p>{hint}</p>" if hint else ""
    st.markdown(
        f'<div class="chart-head"><h3>{title}</h3>{hint_html}</div>',
        unsafe_allow_html=True,
    )


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
        # título fica fora do Plotly (HTML) — margem superior menor
        margin=dict(l=left, r=24, t=12, b=40),
        height=height,
        autosize=True,
        dragmode=False,
        hovermode="closest",
        showlegend=False,
        title=None,
    )
    fig.update_xaxes(
        gridcolor="#E8EDF2",
        zeroline=False,
        linecolor="#94A3B8",
        tickfont=tick,
        title_font=dict(size=12, color="#334155"),
        color="#0B1F33",
        fixedrange=True,
    )
    fig.update_yaxes(
        gridcolor="#E8EDF2",
        zeroline=False,
        linecolor="#94A3B8",
        tickfont={**tick, "size": 14},
        title_font=dict(size=12, color="#334155"),
        color="#0B1F33",
        fixedrange=True,
    )
    return fig


def top_n_com_demais(df: pd.DataFrame, value_col: str, n: int = 10) -> pd.DataFrame:
    """Mantém as N maiores barras e agrega o resto em 'Demais' (mais legível no celular)."""
    if len(df) <= n:
        return df
    ordenado = df.sort_values(value_col, ascending=False)
    top = ordenado.head(n).copy()
    resto = ordenado.iloc[n:]
    demais = {
        "uf": "Demais",
        "urnas": int(resto["urnas"].sum()) if "urnas" in resto else 0,
        "estendidas": int(resto["estendidas"].sum()) if "estendidas" in resto else 0,
        "votos_apos_17h": float(resto["votos_apos_17h"].sum()) if "votos_apos_17h" in resto else 0,
        "pct": 0.0,
    }
    if demais["urnas"]:
        demais["pct"] = 100 * demais["estendidas"] / demais["urnas"]
    out = pd.concat([top, pd.DataFrame([demais])], ignore_index=True)
    return out.sort_values(value_col, ascending=True)


PLOT_CFG = {
    "responsive": True,
    "displayModeBar": False,
    "displaylogo": False,
    "scrollZoom": False,
    "doubleClick": False,
}


def main() -> None:
    st.set_page_config(
        page_title="Urnas tardias · 2026",
        layout="wide",
        initial_sidebar_state="collapsed",
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
<p class="mobile-tip">Para filtrar por estado ou município, toque no ícone <strong>☰</strong> no canto superior esquerdo.</p>
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

        mostrar_todas_ufs = st.checkbox(
            "Gráfico com todas as UFs",
            value=False,
            help="No celular, o padrão mostra só o Top 10 + Demais.",
        )

        with st.expander("Avançado"):
            if st.button("Recarregar CSVs"):
                load_secoes.clear()
                load_municipios.clear()
                st.rerun()
            st.caption(f"{SECOES.name}: {fmt_int(len(secoes))} seções · {len(ufs)} UFs")

    if base.empty:
        st.warning("Nenhuma seção com esses filtros.")
        return

    est = base[base["classe"] == "estendida"]
    votos_17_est = int(est["votos_apos_17h"].sum())
    votos_17_todas = int(base["votos_apos_17h"].sum())
    urnas_c_voto = int((est["votos_apos_17h"] > 0).sum())
    pct_est = 100 * len(est) / len(base) if len(base) else 0
    votos_tot = int(base["votos_total"].sum())
    peso_est = 100 * votos_17_est / votos_tot if votos_tot else 0
    peso_todas = 100 * votos_17_todas / votos_tot if votos_tot else 0

    # KPIs em pares (mobile-friendly)
    k1, k2 = st.columns(2)
    k1.markdown(
        kpi("Urnas no filtro", fmt_int(len(base)), f"{fmt_int(votos_tot)} votos registrados"),
        unsafe_allow_html=True,
    )
    k2.markdown(
        kpi("Urnas estendidas", fmt_int(len(est)), f"{pct_est:.1f}% das urnas · fecharam após 17h45"),
        unsafe_allow_html=True,
    )
    k3, k4 = st.columns(2)
    k3.markdown(
        kpi(
            "Votos após 17h (todas as urnas)",
            fmt_int(votos_17_todas),
            f"{peso_todas:.4f}% do total · inclui fila às 17h",
            tone="teal",
        ),
        unsafe_allow_html=True,
    )
    k4.markdown(
        kpi(
            "Votos após 17h (só estendidas)",
            fmt_int(votos_17_est),
            f"{peso_est:.4f}% do total · {fmt_int(urnas_c_voto)} seções com voto",
            tone="accent",
        ),
        unsafe_allow_html=True,
    )

    with st.expander("Entenda os números (leitura para leigo)", expanded=True):
        st.markdown(
            """
<div class="explain">
  <h3>Em uma frase</h3>
  <p>Os dois cards coloridos respondem perguntas diferentes.
  O <strong>verde</strong> é “voto depois das 17h em qualquer urna”.
  O <strong>laranja</strong> é “voto depois das 17h só nas urnas que fecharam tarde”
  (ligadas à extensão do horário).</p>

  <h3>1) O que foi a extensão</h3>
  <p>Normalmente a votação fecha às <strong>17h</strong>. Naquele domingo
  o horário foi estendido até às <strong>19h</strong>. Algumas seções
  realmente ficaram abertas (ou encerraram) bem depois das 17h.</p>

  <h3>2) Como achamos essas seções no computador</h3>
  <p>O arquivo da urna não diz “esta seção reabriu por causa do ministro”.
  Então usamos o horário de <strong>encerramento</strong> do log:</p>
  <p>Se fechou <strong>depois das 17h45</strong> → chamamos de
  <strong>urna estendida</strong> (são umas 7 mil no país).</p>
  <p>Usamos 17h45 (e não 17h) para não contar seção que só demorou uns minutos
  a mais para fechar a porta.</p>

  <h3>3) Card verde × card laranja</h3>
  <p><strong>Verde — Votos após 17h (todas as urnas):</strong>
  no Brasil ≈ <span class="num">35 mil</span>.
  Inclui quem <strong>já estava na fila às 17h</strong> e votou um pouco depois
  (isso já existia em eleições sem extensão até 19h).</p>
  <p><strong>Laranja — Votos após 17h (só estendidas):</strong>
  no Brasil ≈ <span class="num">5 mil</span>.
  Só nas seções que fecharam depois das 17h45 — o recorte da extensão.</p>
  <p>Por isso os números não batem: não são a mesma pergunta.</p>

  <h3>4) Os cards azuis</h3>
  <p><strong>Urnas no filtro</strong> = todas as seções do que você escolheu
  (ex.: Brasil ≈ 498 mil).</p>
  <p><strong>Urnas estendidas</strong> = quantas dessas fecharam depois das 17h45.</p>
</div>
""",
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
    por_uf["pct"] = 100 * por_uf["estendidas"] / por_uf["urnas"].clip(lower=1)
    if not mostrar_todas_ufs:
        por_uf = top_n_com_demais(por_uf, "estendidas", n=10)
    else:
        por_uf = por_uf.sort_values("estendidas", ascending=True)

    chart_head(
        "Urnas estendidas por UF",
        "Toque numa barra para ver o detalhe. No menu ☰ dá para filtrar estados.",
    )
    fig_uf = go.Figure()
    fig_uf.add_trace(
        go.Bar(
            y=por_uf["uf"],
            x=por_uf["estendidas"],
            orientation="h",
            name="Urnas estendidas",
            marker_color=PRIMARY,
            text=por_uf["estendidas"].map(fmt_int),
            textposition="auto",
            cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>%{x:,} estendidas<br>%{customdata[0]:.1f}% das urnas<br>%{customdata[1]:,.0f} votos >17h<extra></extra>",
            customdata=por_uf[["pct", "votos_apos_17h"]],
        )
    )
    fig_uf.update_layout(xaxis_title="", yaxis_title="")
    fig_uf.update_yaxes(
        tickfont=dict(family="Roboto, Helvetica, Arial, sans-serif", size=14, color="#000000"),
        automargin=True,
    )
    h_uf = chart_height(len(por_uf), row_px=36, base=120, lo=360, hi=900)
    st.plotly_chart(
        plot_layout(fig_uf, height=h_uf, left=56),
        use_container_width=True,
        config=PLOT_CFG,
    )

    if not est.empty and "encerramento_brt_h" in est.columns:
        chart_head(
            "Horário de encerramento",
            "Só urnas estendidas. A linha marca 17h45 (Brasília).",
        )
        fig_h = px.histogram(
            est,
            x="encerramento_brt_h",
            nbins=24,
            color_discrete_sequence=[ACCENT],
        )
        fig_h.update_traces(hovertemplate="Encerramento %{x:.2f}h<br>%{y} urnas<extra></extra>")
        fig_h.update_layout(
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
            annotation_position="top",
        )
        st.plotly_chart(
            plot_layout(fig_h, height=320, left=48),
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

    top = mun_view.sort_values("votos_apos_17h_nas_estendidas", ascending=False).head(10)
    if not top.empty:
        chart_head(
            "Top 10 municípios — votos após 17h",
            "Nas urnas estendidas. Deslize a tabela abaixo para ver mais.",
        )
        plot_df = top.sort_values("votos_apos_17h_nas_estendidas").copy()
        # rótulos curtos no eixo (melhor no celular)
        plot_df["rotulo"] = plot_df.apply(
            lambda r: f"{r['municipio'][:18]}…" if len(str(r["municipio"])) > 18 else r["municipio"],
            axis=1,
        )
        plot_df["rotulo"] = plot_df["uf"] + " · " + plot_df["rotulo"]
        fig_m = px.bar(
            plot_df,
            x="votos_apos_17h_nas_estendidas",
            y="rotulo",
            orientation="h",
            color_discrete_sequence=[PRIMARY],
            labels={"votos_apos_17h_nas_estendidas": "Votos após 17h", "rotulo": ""},
        )
        fig_m.update_traces(
            text=plot_df["votos_apos_17h_nas_estendidas"].map(fmt_int),
            textposition="auto",
            hovertemplate="<b>%{y}</b><br>%{x:,} votos após 17h<extra></extra>",
        )
        fig_m.update_yaxes(
            tickfont=dict(family="Roboto, Helvetica, Arial, sans-serif", size=12, color="#000000"),
            automargin=True,
        )
        h_m = chart_height(len(top), row_px=38, base=100, lo=380, hi=560)
        st.plotly_chart(
            plot_layout(fig_m, height=h_m, left=8),
            use_container_width=True,
            config=PLOT_CFG,
        )

        with st.expander("Tabela de municípios", expanded=False):
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
                height=280,
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
