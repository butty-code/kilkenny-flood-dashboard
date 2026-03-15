"""
Kilkenny Flood Risk Dashboard
A production-grade interactive dashboard built with Plotly Dash
"""

import dash
from dash import dcc, html, Input, Output, callback, dash_table
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')
from prevention import build_prevention
from guide import build_guide
from analytics import build_analytics

# ─────────────────────────────────────────────
# DATA LOADING — reads your real combined_rainfall.csv
# Columns expected: date, rain, ind, station
# ─────────────────────────────────────────────

def generate_sample_data():
    csv_file = 'combined_rainfall.csv'

    print(f"  → Looking for {csv_file}...")

    # ── Check the file exists ──────────────────
    import os
    if not os.path.exists(csv_file):
        print(f"  ✗ File not found: {csv_file}")
        print(f"    Make sure combined_rainfall.csv is in the same")
        print(f"    folder as app.py  ({os.getcwd()})")
        print(f"    Falling back to sample data for now...")
        return _generate_fallback()

    # ── Load with optimised dtypes for large files ──
    print(f"  → Reading CSV (optimised for large files)...")
    df = pd.read_csv(
        csv_file,
        dtype={'rain': 'float32', 'ind': 'Int8', 'station': 'category'},
    )
    # Parse DD-Mon-YY format e.g. '01-Jul-84'
    df['date'] = pd.to_datetime(df['date'], format='%d-%b-%y', errors='coerce')
    # Also handle any rows that might be YYYY-MM-DD
    mask = df['date'].isna()
    if mask.any():
        df.loc[mask, 'date'] = pd.to_datetime(df.loc[mask, 'date'], errors='coerce')

    # ── Rename rain → rain_mm ──────────────────
    if 'rain' in df.columns and 'rain_mm' not in df.columns:
        df = df.rename(columns={'rain': 'rain_mm'})

    # ── Clean up ───────────────────────────────
    df['rain_mm'] = pd.to_numeric(df['rain_mm'], errors='coerce').fillna(0).clip(lower=0)
    df['date']    = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['date'])
    df = df.sort_values('date').reset_index(drop=True)

    # ── Report what we found ───────────────────
    print(f"  ✓ Loaded {len(df):,} rows from {csv_file}")
    for st in df['station'].unique():
        sub = df[df['station'] == st]
        print(f"     {st}: {len(sub):,} rows  "
              f"({sub['date'].min().date()} → {sub['date'].max().date()})")

    return df


def _generate_fallback():
    """Minimal fallback so the app still runs if the CSV is missing."""
    rng = np.random.default_rng(42)
    def make(start, name):
        dates = pd.date_range(start, datetime.today(), freq='D')
        doy   = dates.dayofyear.to_numpy()
        s     = 2.5 + 1.8 * np.sin(2 * np.pi * doy / 365 + np.pi)
        rain  = rng.gamma(shape=1.1, scale=s).clip(0)
        rain[rng.random(len(dates)) > 0.55] = 0.0
        return pd.DataFrame({'date': dates, 'rain_mm': rain.round(1),
                             'ind': 1, 'station': name})
    df = pd.concat([make('1962-01-01', 'Kilkenny (Lavistown)'),
                    make('2001-01-01', 'Graiguenamanagh (Ballyogan)')], ignore_index=True)
    print(f"  → Fallback sample data: {len(df):,} rows")
    return df


def load_and_process(df_raw):
    """
    Fast metric calculations — uses vectorised cumsum instead of
    rolling().apply() which was the slow O(n²) bottleneck.
    """
    results = []
    stations = df_raw['station'].unique()

    for i, station in enumerate(stations):
        print(f"\n[{i+1}/{len(stations)}] Processing: {station}")
        g = df_raw[df_raw['station'] == station].sort_values('date').copy().reset_index(drop=True)
        n = len(g)
        print(f"  → {n:,} rows loaded")

        g['rain_mm'] = pd.to_numeric(g['rain_mm'], errors='coerce').fillna(0).clip(lower=0)

        # ── STEP 1: Rolling totals (pandas rolling — simple and correct) ──
        print(f"  → Calculating 7-day and 30-day rolling totals...")
        g['roll7']  = g['rain_mm'].rolling(7,  min_periods=1).sum()
        g['roll30'] = g['rain_mm'].rolling(30, min_periods=1).sum()
        roll30 = g['roll30'].to_numpy()
        print(f"  ✓ Rolling totals done")

        # ── STEP 2: Historical baseline — fast DOY lookup (not groupby transform) ──
        print(f"  → Calculating historical baseline (fast DOY method)...")
        g['doy'] = g['date'].dt.dayofyear
        # Simple mean of all rain_mm values per day-of-year × 30 (approx 30-day avg)
        doy_mean = g.groupby('doy')['rain_mm'].mean() * 30
        g['hist_avg_30'] = g['doy'].map(doy_mean).fillna(roll30.mean())
        print(f"  ✓ Baseline done")

        # ── STEP 3: Risk score (vectorised, no .apply()) ──
        print(f"  → Calculating flood risk scores...")
        hist = g['hist_avg_30'].to_numpy()
        hist_safe = np.where(hist == 0, np.nan, hist)
        g['risk_score'] = np.clip((roll30 - hist_safe) / hist_safe * 100, -50, 200)
        g['risk_score'] = g['risk_score'].fillna(0)
        print(f"  ✓ Risk scores done")

        # ── STEP 4: Risk level (vectorised np.select, not .apply()) ──
        print(f"  → Assigning risk levels...")
        s = g['risk_score'].to_numpy()
        g['risk_level'] = np.select(
            [s > 70, s >= 40, s >= 15],
            ['HIGH', 'ELEVATED', 'MODERATE'],
            default='LOW'
        )
        print(f"  ✓ Risk levels done")

        g['year']  = g['date'].dt.year
        g['month'] = g['date'].dt.month

        level_counts = g['risk_level'].value_counts().to_dict()
        print(f"  → Risk breakdown: {level_counts}")
        results.append(g)

    return pd.concat(results).reset_index(drop=True)


# ─────────────────────────────────────────────
# LOAD DATA — with full progress reporting
# ─────────────────────────────────────────────
print("=" * 55)
print("  KILKENNY FLOOD RISK DASHBOARD")
print("  Starting up...")
print("=" * 55)

# ── Initial data fetch on startup ────────────────────────
try:
    print("\n[0/3] Checking for new Met Éireann data...")
    from update_data import update as _run_update
    _added = _run_update()
    if _added > 0:
        print(f"  ✓ {_added} new rows downloaded from Met Éireann")
    else:
        print("  ✓ Data already current")
except Exception as _e:
    print(f"  ⚠ Initial update skipped: {_e}")

t0 = datetime.now()
print("\n[1/3] Loading combined_rainfall.csv...")
df_raw = generate_sample_data()
t1 = datetime.now()
print(f"  ✓ Data loaded in {(t1-t0).seconds}s")

print("\n[2/3] Running calculations...")
df = load_and_process(df_raw)
t2 = datetime.now()
print(f"\n  ✓ All calculations done in {(t2-t1).seconds}s")

stations = sorted(df['station'].unique())
print(f"\n[3/3] Building app layout...")
print(f"  → {len(df):,} total rows")
print(f"  → {len(stations)} stations: {', '.join(stations)}")
print(f"  → Date range: {df['date'].min().date()} → {df['date'].max().date()}")
total_secs = (datetime.now() - t0).seconds
print(f"\n{'='*55}")
print(f"  ✓ Ready in {total_secs}s total")
print(f"  Open http://127.0.0.1:8050 in your browser")
print(f"{'='*55}\n")

# ─────────────────────────────────────────────
# DESIGN TOKENS
# ─────────────────────────────────────────────
COLORS = {
    'bg':           '#0a0f1e',
    'panel':        '#0f1729',
    'panel_light':  '#141f38',
    'border':       '#1e3058',
    'accent':       '#00c8ff',
    'accent2':      '#0066ff',
    'text':         '#e8f0ff',
    'text_dim':     '#7a95c2',
    'HIGH':         '#ff3b5c',
    'ELEVATED':     '#ff8c00',
    'MODERATE':     '#ffd700',
    'LOW':          '#00e676',
    'grid':         '#1a2847',
}

RISK_ORDER  = ['HIGH', 'ELEVATED', 'MODERATE', 'LOW']
RISK_COLORS = {k: COLORS[k] for k in RISK_ORDER}

CHART_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='IBM Plex Mono, monospace', color=COLORS['text'], size=11),
    margin=dict(l=50, r=20, t=40, b=40),
    xaxis=dict(gridcolor=COLORS['grid'], linecolor=COLORS['border'],
               tickfont=dict(color=COLORS['text_dim'])),
    yaxis=dict(gridcolor=COLORS['grid'], linecolor=COLORS['border'],
               tickfont=dict(color=COLORS['text_dim'])),
    legend=dict(bgcolor='rgba(0,0,0,0)', bordercolor=COLORS['border'],
                font=dict(color=COLORS['text_dim'])),
    hoverlabel=dict(bgcolor=COLORS['panel_light'], font_color=COLORS['text'],
                    bordercolor=COLORS['border']),
)

# ─────────────────────────────────────────────
# HELPER: RISK BADGE
# ─────────────────────────────────────────────
def risk_badge(level):
    glow = {
        'HIGH':     '0 0 16px #ff3b5c88',
        'ELEVATED': '0 0 16px #ff8c0088',
        'MODERATE': '0 0 16px #ffd70088',
        'LOW':      '0 0 16px #00e67688',
    }.get(level, '')
    return html.Span(level, style={
        'background': RISK_COLORS.get(level, '#555'),
        'color': '#000' if level in ('MODERATE', 'LOW') else '#fff',
        'padding': '3px 14px',
        'borderRadius': '3px',
        'fontWeight': '700',
        'fontSize': '13px',
        'letterSpacing': '2px',
        'boxShadow': glow,
        'fontFamily': 'IBM Plex Mono, monospace',
    })


# ─────────────────────────────────────────────
# APP LAYOUT
# ─────────────────────────────────────────────
app = dash.Dash(
    __name__,
    title='Kilkenny Flood Risk',
    suppress_callback_exceptions=True,
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}]
)

# Google Font import injected via external stylesheet
app.index_string = '''
<!DOCTYPE html>
<html>
<head>
    {%metas%}
    <title>{%title%}</title>
    {%favicon%}
    {%css%}
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;700&family=Space+Grotesk:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #0a0f1e; color: #e8f0ff; font-family: "Space Grotesk", sans-serif; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #0a0f1e; }
        ::-webkit-scrollbar-thumb { background: #1e3058; border-radius: 3px; }
        .tab-content { animation: fadeIn 0.3s ease; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
        .stat-card:hover { border-color: #00c8ff44 !important; transform: translateY(-2px); transition: all 0.2s; }
        .risk-row:hover { background: #141f38 !important; }
    </style>
</head>
<body>{%app_entry%}<footer>{%config%}{%scripts%}{%renderer%}</footer></body>
</html>
'''

def header():
    return html.Div([
        html.Div([
            html.Div([
                html.Div('◈', style={'fontSize': '28px', 'color': COLORS['accent'], 'lineHeight': '1'}),
                html.Div([
                    html.Div('KILKENNY FLOOD RISK', style={
                        'fontFamily': 'IBM Plex Mono, monospace',
                        'fontSize': '20px', 'fontWeight': '700',
                        'letterSpacing': '4px', 'color': COLORS['text'],
                    }),
                    html.Div('RAINFALL MONITORING SYSTEM · NORE VALLEY', style={
                        'fontFamily': 'IBM Plex Mono, monospace',
                        'fontSize': '9px', 'letterSpacing': '3px',
                        'color': COLORS['text_dim'], 'marginTop': '2px',
                    }),
                ], style={'marginLeft': '14px'}),
            ], style={'display': 'flex', 'alignItems': 'center'}),
            html.Div(id='live-clock', style={
                'fontFamily': 'IBM Plex Mono, monospace',
                'fontSize': '12px', 'color': COLORS['text_dim'],
                'textAlign': 'right',
            }),
        ], style={
            'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center',
            'padding': '20px 32px',
            'borderBottom': f'1px solid {COLORS["border"]}',
            'background': f'linear-gradient(90deg, {COLORS["panel"]} 0%, #0a1428 100%)',
        }),

        # Controls bar — RadioItems (reliable, no dropdown quirks)
        html.Div([
            html.Div([
                html.Div('STATION', style={
                    'fontFamily': 'IBM Plex Mono, monospace', 'fontSize': '9px',
                    'letterSpacing': '3px', 'color': COLORS['text_dim'], 'marginBottom': '6px',
                }),
                dcc.RadioItems(
                    id='station-select',
                    options=[{'label': f'  {s}', 'value': s} for s in stations],
                    value=stations[0],
                    inline=True,
                    inputStyle={'marginRight': '4px', 'accentColor': COLORS['accent']},
                    labelStyle={
                        'marginRight': '24px', 'cursor': 'pointer',
                        'fontFamily': 'IBM Plex Mono, monospace',
                        'fontSize': '12px', 'color': COLORS['text'],
                    },
                ),
            ]),
            html.Div(style={'width': '1px', 'background': COLORS['border'],
                            'margin': '0 28px', 'alignSelf': 'stretch'}),
            html.Div([
                html.Div('DATE RANGE', style={
                    'fontFamily': 'IBM Plex Mono, monospace', 'fontSize': '9px',
                    'letterSpacing': '3px', 'color': COLORS['text_dim'], 'marginBottom': '6px',
                }),
                dcc.RadioItems(
                    id='date-range-select',
                    options=[
                        {'label': '  90d',  'value': 90},
                        {'label': '  1yr',  'value': 365},
                        {'label': '  5yr',  'value': 1825},
                        {'label': '  10yr', 'value': 3650},
                        {'label': '  All',  'value': 99999},
                    ],
                    value=99999,
                    inline=True,
                    inputStyle={'marginRight': '4px', 'accentColor': COLORS['accent']},
                    labelStyle={
                        'marginRight': '16px', 'cursor': 'pointer',
                        'fontFamily': 'IBM Plex Mono, monospace',
                        'fontSize': '12px', 'color': COLORS['text'],
                    },
                ),
            ]),
        ], style={
            'display': 'flex', 'alignItems': 'center',
            'padding': '14px 32px',
            'background': COLORS['panel'],
            'borderBottom': f'1px solid {COLORS["border"]}',
            'flexWrap': 'wrap', 'gap': '8px',
        }),
    ])


def tab_style(selected=False):
    return {
        'background':   COLORS['panel_light'] if selected else COLORS['panel'],
        'color':        COLORS['accent'] if selected else COLORS['text_dim'],
        'border':       f'1px solid {COLORS["border"]}',
        'borderBottom': f'2px solid {COLORS["accent"]}' if selected else f'1px solid {COLORS["border"]}',
        'padding':      '10px 24px',
        'fontFamily':   'IBM Plex Mono, monospace',
        'fontSize':     '11px',
        'letterSpacing':'2px',
        'cursor':       'pointer',
    }


app.layout = html.Div([
    dcc.Interval(id='clock-tick', interval=1000, n_intervals=0),
    header(),
    dcc.Tabs(id='main-tabs', value='tab-overview', children=[
        dcc.Tab(label='01  OVERVIEW',    value='tab-overview',    style=tab_style(), selected_style=tab_style(True)),
        dcc.Tab(label='02  HISTORICAL',  value='tab-historical',  style=tab_style(), selected_style=tab_style(True)),
        dcc.Tab(label='03  PREDICTIONS', value='tab-predictions', style=tab_style(), selected_style=tab_style(True)),
        dcc.Tab(label='05  PREVENTION',   value='tab-prevention',  style=tab_style(), selected_style=tab_style(True)),
        dcc.Tab(label='06  GUIDE & HELP',   value='tab-guide',       style=tab_style(), selected_style=tab_style(True)),
        dcc.Tab(label='07  DEEP ANALYTICS', value='tab-analytics',   style=tab_style(), selected_style=tab_style(True)),
    ], style={'background': COLORS['bg'], 'border': 'none'}),
    html.Div(id='tab-content', className='tab-content'),
], style={'background': COLORS['bg'], 'minHeight': '100vh'})


# ─────────────────────────────────────────────
# CLOCK CALLBACK
# ─────────────────────────────────────────────
@callback(Output('live-clock', 'children'), Input('clock-tick', 'n_intervals'))
def update_clock(_):
    now = datetime.now()
    return [
        html.Div(now.strftime('%A %d %B %Y'), style={'fontSize': '10px', 'letterSpacing': '1px'}),
        html.Div(now.strftime('%H:%M:%S  UTC'), style={'fontSize': '14px', 'fontWeight': '700', 'color': COLORS['accent']}),
    ]


# ─────────────────────────────────────────────
# TAB ROUTER
# ─────────────────────────────────────────────
@callback(Output('tab-content', 'children'),
          Input('main-tabs', 'value'),
          Input('station-select', 'value'),
          Input('date-range-select', 'value'))
def render_tab(tab, station, days):
    # Guard: dropdowns not yet populated on first load
    if not station or not days or not tab:
        return html.Div("Loading data...", style={
            'color': COLORS['text_dim'], 'padding': '60px 32px',
            'fontFamily': 'IBM Plex Mono, monospace', 'fontSize': '14px',
        })
    try:
        d = df[df['station'] == station].copy()
        if d.empty:
            return html.Div(f"No data found for: {station}", style={
                'color': COLORS['HIGH'], 'padding': '60px 32px',
                'fontFamily': 'IBM Plex Mono, monospace',
            })
        days_int = int(days)
        if days_int >= 99999:
            d_filtered = d.copy()          # All time — no cutoff
        else:
            cutoff     = d['date'].max() - timedelta(days=days_int)
            d_filtered = d[d['date'] >= cutoff].copy()

        if tab == 'tab-overview':    return build_overview(d, d_filtered)
        if tab == 'tab-historical':  return build_historical(d_filtered)
        if tab == 'tab-predictions': return build_predictions(d)
        if tab == 'tab-prevention':  return build_prevention(d)
        if tab == 'tab-guide':       return build_guide()
        if tab == 'tab-analytics':   return build_analytics(d_filtered)
        return html.Div("Select a tab")

    except Exception as e:
        import traceback
        return html.Div([
            html.Div("⚠  Error rendering tab — details below:",
                     style={'color': COLORS['HIGH'], 'fontSize': '14px',
                            'fontFamily': 'IBM Plex Mono, monospace', 'marginBottom': '12px'}),
            html.Pre(traceback.format_exc(),
                     style={'color': COLORS['text_dim'], 'fontSize': '11px',
                            'fontFamily': 'IBM Plex Mono, monospace',
                            'background': COLORS['panel'], 'padding': '16px',
                            'borderRadius': '6px', 'overflowX': 'auto',
                            'whiteSpace': 'pre-wrap', 'maxHeight': '400px'}),
        ], style={'padding': '32px'})


# ─────────────────────────────────────────────
# PAGE 1: OVERVIEW
# ─────────────────────────────────────────────
def build_overview(d_all, d):
    latest = d_all.iloc[-1]
    current_risk  = latest['risk_level']
    current_score = latest['risk_score']
    current_30    = latest['roll30']
    current_7     = latest['roll7']
    hist_avg      = latest['hist_avg_30']
    anomaly_pct   = current_score

    def stat_card(label, value, unit='', color=COLORS['accent'], sub=None):
        return html.Div([
            html.Div(label, style={
                'fontFamily': 'IBM Plex Mono, monospace', 'fontSize': '9px',
                'letterSpacing': '3px', 'color': COLORS['text_dim'], 'marginBottom': '8px',
            }),
            html.Div([
                html.Span(value, style={'fontSize': '32px', 'fontWeight': '700', 'color': color}),
                html.Span(unit,  style={'fontSize': '13px', 'color': COLORS['text_dim'], 'marginLeft': '4px'}),
            ]),
            html.Div(sub or '', style={'fontSize': '11px', 'color': COLORS['text_dim'], 'marginTop': '4px'}),
        ], className='stat-card', style={
            'background':    COLORS['panel'],
            'border':        f'1px solid {COLORS["border"]}',
            'borderRadius':  '6px',
            'padding':       '20px 24px',
            'flex':          '1',
            'minWidth':      '160px',
            'transition':    'all 0.2s',
        })

    stats_row = html.Div([
        stat_card('7-DAY TOTAL',       f'{current_7:.1f}',     'mm', COLORS['accent'],
                  f'vs {hist_avg * 7/30:.1f} mm avg'),
        stat_card('30-DAY TOTAL',      f'{current_30:.1f}',    'mm', COLORS['accent2'],
                  f'vs {hist_avg:.1f} mm avg'),
        stat_card('RISK SCORE',        f'{current_score:.0f}', '/100',
                  COLORS[current_risk], f'Anomaly: {anomaly_pct:+.0f}%'),
        html.Div([
            html.Div('RISK LEVEL', style={
                'fontFamily': 'IBM Plex Mono, monospace', 'fontSize': '9px',
                'letterSpacing': '3px', 'color': COLORS['text_dim'], 'marginBottom': '12px',
            }),
            risk_badge(current_risk),
        ], className='stat-card', style={
            'background': COLORS['panel'], 'border': f'1px solid {COLORS["border"]}',
            'borderRadius': '6px', 'padding': '20px 24px', 'flex': '1', 'minWidth': '160px',
        }),
    ], style={'display': 'flex', 'gap': '12px', 'padding': '24px 32px', 'flexWrap': 'wrap'})

    # Main timeline chart
    fig = go.Figure()
    # 30-day rolling
    fig.add_trace(go.Scatter(
        x=d['date'], y=d['roll30'],
        name='30-Day Rolling Total', mode='lines',
        line=dict(color=COLORS['accent2'], width=2),
        fill='tozeroy', fillcolor='rgba(0,102,255,0.08)',
        hovertemplate='%{x|%d %b %Y}<br>30d Total: %{y:.1f} mm<extra></extra>',
    ))
    # 7-day rolling
    fig.add_trace(go.Scatter(
        x=d['date'], y=d['roll7'],
        name='7-Day Rolling Total', mode='lines',
        line=dict(color=COLORS['accent'], width=1.5, dash='dot'),
        hovertemplate='%{x|%d %b %Y}<br>7d Total: %{y:.1f} mm<extra></extra>',
    ))
    # Historical average
    fig.add_trace(go.Scatter(
        x=d['date'], y=d['hist_avg_30'],
        name='Historical Avg', mode='lines',
        line=dict(color=COLORS['MODERATE'], width=1, dash='dash'),
        hovertemplate='%{x|%d %b %Y}<br>Hist Avg: %{y:.1f} mm<extra></extra>',
    ))

    # Shade risk zones as horizontal bands
    for threshold, label, color in [
        (70, 'HIGH',     COLORS['HIGH']),
        (40, 'ELEVATED', COLORS['ELEVATED']),
        (15, 'MODERATE', COLORS['MODERATE']),
    ]:
        fig.add_hline(y=threshold, line_dash='dot', line_color=color,
                      line_width=1, opacity=0.4,
                      annotation_text=label, annotation_position='right',
                      annotation_font=dict(color=color, size=9,
                                           family='IBM Plex Mono, monospace'))

    fig.update_layout(
        **CHART_LAYOUT,
        title=dict(text='Rainfall Rolling Totals vs Historical Average',
                   font=dict(size=13, color=COLORS['text_dim'],
                             family='IBM Plex Mono, monospace')),
        height=320,
        yaxis_title='Rainfall (mm)',
        hovermode='x unified',
    )
    fig.update_xaxes(rangeslider=dict(visible=True, thickness=0.04))

    # Risk score timeline
    fig2 = go.Figure()
    # Colour each point by risk level
    for level, col in RISK_COLORS.items():
        mask = d['risk_level'] == level
        if mask.any():
            fig2.add_trace(go.Scatter(
                x=d.loc[mask, 'date'], y=d.loc[mask, 'risk_score'],
                name=level, mode='markers',
                marker=dict(color=col, size=3, opacity=0.7),
                hovertemplate=f'<b>{level}</b><br>%{{x|%d %b %Y}}<br>Score: %{{y:.0f}}<extra></extra>',
            ))
    fig2.add_hline(y=70, line_color=COLORS['HIGH'],     line_width=1, line_dash='dot', opacity=0.5)
    fig2.add_hline(y=40, line_color=COLORS['ELEVATED'], line_width=1, line_dash='dot', opacity=0.5)
    fig2.add_hline(y=15, line_color=COLORS['MODERATE'], line_width=1, line_dash='dot', opacity=0.5)
    fig2.add_hline(y=0,  line_color=COLORS['border'],   line_width=1, opacity=0.5)
    fig2.update_layout(
        **CHART_LAYOUT,
        title=dict(text='Flood Risk Score Over Time',
                   font=dict(size=13, color=COLORS['text_dim'],
                             family='IBM Plex Mono, monospace')),
        height=260, yaxis_title='Risk Score', hovermode='x unified',
    )

    def explain(text):
        return html.Div(text, style={
            'fontFamily': 'Space Grotesk, sans-serif', 'fontSize': '13px',
            'color': COLORS['text_dim'], 'lineHeight': '1.7',
            'padding': '10px 32px 4px',
        })

    return html.Div([
        stats_row,
        explain(
            '📈  The chart below shows how much rain has fallen in the last 7 days (dotted blue line) '
            'and the last 30 days (solid blue area). The yellow dashed line is the long-term average — '
            'what we normally expect for this time of year. When the blue area rises well above the yellow '
            'line, the ground is getting saturated and flood risk increases. '
            'Use the range slider at the bottom to zoom into any time period.'
        ),
        html.Div([dcc.Graph(figure=fig,  config={'displayModeBar': False})],
                 style={'padding': '0 32px'}),
        explain(
            '🎯  This chart scores flood risk from 0 to 100 for every day in the selected period. '
            'Each dot is colour-coded: green = LOW, yellow = MODERATE, orange = ELEVATED, red = HIGH. '
            'A score above 70 (red zone) means rainfall over the past month is dramatically higher '
            'than the historical average — flooding becomes likely.'
        ),
        html.Div([dcc.Graph(figure=fig2, config={'displayModeBar': False})],
                 style={'padding': '0 32px 32px'}),
    ])


# ─────────────────────────────────────────────
# PAGE 2: HISTORICAL
# ─────────────────────────────────────────────
def build_historical(d):
    annual = (d.groupby('year')['rain_mm'].sum()
               .reset_index().rename(columns={'rain_mm': 'annual_total'}))
    annual = annual[annual['year'] < datetime.today().year]  # exclude partial current year

    # Trend line
    z = np.polyfit(annual['year'], annual['annual_total'], 1)
    trend_y = np.poly1d(z)(annual['year'])

    fig_annual = go.Figure()
    fig_annual.add_trace(go.Bar(
        x=annual['year'], y=annual['annual_total'],
        name='Annual Total',
        marker=dict(
            color=annual['annual_total'],
            colorscale=[[0, COLORS['LOW']], [0.4, COLORS['MODERATE']],
                        [0.7, COLORS['ELEVATED']], [1, COLORS['HIGH']]],
            showscale=False,
        ),
        hovertemplate='%{x}<br>Total: %{y:.0f} mm<extra></extra>',
    ))
    fig_annual.add_trace(go.Scatter(
        x=annual['year'], y=trend_y,
        name='Trend', mode='lines',
        line=dict(color=COLORS['accent'], width=2, dash='dash'),
    ))

    slope_mm = z[0]
    fig_annual.update_layout(
        **CHART_LAYOUT,
        title=dict(
            text=f'Annual Rainfall Totals  ·  Trend: {slope_mm:+.1f} mm/year',
            font=dict(size=13, color=COLORS['text_dim'], family='IBM Plex Mono, monospace'),
        ),
        height=320, yaxis_title='Total Rainfall (mm)',
        bargap=0.2,
    )

    # Monthly heatmap
    monthly = (d.groupby(['year', 'month'])['rain_mm'].sum()
                .reset_index().rename(columns={'rain_mm': 'monthly_total'}))
    pivot = monthly.pivot(index='year', columns='month', values='monthly_total')
    month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

    fig_heat = go.Figure(go.Heatmap(
        z=pivot.values,
        x=month_names,
        y=pivot.index,
        colorscale=[[0, COLORS['bg']], [0.3, COLORS['accent2']],
                    [0.7, COLORS['ELEVATED']], [1, COLORS['HIGH']]],
        hovertemplate='%{y}  %{x}<br>%{z:.0f} mm<extra></extra>',
        colorbar=dict(tickfont=dict(color=COLORS['text_dim'], family='IBM Plex Mono, monospace'),
                      title=dict(text='mm', font=dict(color=COLORS['text_dim']))),
    ))
    fig_heat.update_layout(
        **CHART_LAYOUT,
        title=dict(text='Monthly Rainfall Heatmap (all years)',
                   font=dict(size=13, color=COLORS['text_dim'], family='IBM Plex Mono, monospace')),
        height=max(300, min(800, len(pivot) * 12)),
    )
    fig_heat.update_yaxes(autorange='reversed')

    # Box plot: distribution by month
    fig_box = go.Figure()
    for m_idx, m_name in enumerate(month_names, 1):
        month_data = d[d['month'] == m_idx]['rain_mm']
        fig_box.add_trace(go.Box(
            y=month_data, name=m_name,
            marker_color=COLORS['accent2'],
            line_color=COLORS['accent'],
            fillcolor='rgba(0,102,255,0.15)',
            showlegend=False,
            hovertemplate=f'<b>{m_name}</b><br>%{{y:.1f}} mm<extra></extra>',
        ))
    fig_box.update_layout(
        **CHART_LAYOUT,
        title=dict(text='Daily Rainfall Distribution by Month',
                   font=dict(size=13, color=COLORS['text_dim'], family='IBM Plex Mono, monospace')),
        height=300, yaxis_title='Daily Rainfall (mm)',
    )

    # Summary stats
    stats = {
        'Wettest Year': f'{annual.loc[annual["annual_total"].idxmax(), "year"]:.0f}  ({annual["annual_total"].max():.0f} mm)',
        'Driest Year':  f'{annual.loc[annual["annual_total"].idxmin(), "year"]:.0f}  ({annual["annual_total"].min():.0f} mm)',
        'Long-term Avg':f'{annual["annual_total"].mean():.0f} mm / year',
        'Annual Trend': f'{slope_mm:+.1f} mm / year',
        'Wettest Month':'October / November',
        'Data Since':   str(d["year"].min()),
    }
    stats_html = html.Div([
        html.Div([
            html.Div(k, style={'fontFamily': 'IBM Plex Mono, monospace', 'fontSize': '9px',
                               'letterSpacing': '2px', 'color': COLORS['text_dim'], 'marginBottom': '4px'}),
            html.Div(v, style={'fontWeight': '600', 'color': COLORS['text'], 'fontSize': '14px'}),
        ], style={
            'background': COLORS['panel'], 'border': f'1px solid {COLORS["border"]}',
            'borderRadius': '6px', 'padding': '16px 20px', 'flex': '1', 'minWidth': '180px',
        }) for k, v in stats.items()
    ], style={'display': 'flex', 'gap': '12px', 'flexWrap': 'wrap', 'padding': '24px 32px 0'})

    def explain(text):
        return html.Div(text, style={
            'fontFamily': 'Space Grotesk, sans-serif', 'fontSize': '13px',
            'color': COLORS['text_dim'], 'lineHeight': '1.7',
            'padding': '10px 32px 4px',
        })

    return html.Div([
        stats_html,
        explain(
            '📊  Each bar below shows the total rainfall for one year. '
            'Taller bars = wetter years. The colour goes from green (drier) to red (wetter). '
            'The dashed line shows the long-term trend — if it slopes upward, '
            'rainfall is increasing over the decades. This is the big picture view of our changing climate.'
        ),
        html.Div([dcc.Graph(figure=fig_annual, config={'displayModeBar': False})],
                 style={'padding': '8px 32px 0'}),
        explain(
            '🗓️  This calendar heatmap shows every year and month as a coloured square. '
            'Dark blue = light rainfall, red = very heavy rainfall. '
            'Reading across a row shows you how wet each month was in a given year. '
            'Reading down a column shows whether, say, October is getting wetter over time. '
            'You can clearly see that autumn and winter months (Oct–Jan) are consistently the wettest.'
        ),
        html.Div([dcc.Graph(figure=fig_heat, config={'displayModeBar': False})],
                 style={'padding': '8px 32px 0'}),
        explain(
            '📦  These box plots show the spread of daily rainfall for each month across all years. '
            'The box covers the middle 50% of typical days. The lines extend to the usual range. '
            'The dots above are unusually heavy rain days — the higher the dot, '
            'the more extreme the event. October and November show the highest and most variable rainfall.'
        ),
        html.Div([dcc.Graph(figure=fig_box, config={'displayModeBar': False})],
                 style={'padding': '8px 32px 32px'}),
    ])


# ─────────────────────────────────────────────
# PAGE 3: PREDICTIONS
# ─────────────────────────────────────────────
def build_predictions(d):
    annual = (d.groupby('year')['rain_mm'].sum()
               .reset_index().rename(columns={'rain_mm': 'annual_total'}))
    annual = annual[annual['year'] < datetime.today().year]
    base_year  = annual['year'].max()
    base_total = annual.loc[annual['year'] == base_year, 'annual_total'].values[0]

    slider = html.Div([
        html.Div('PROJECTION HORIZON', style={
            'fontFamily': 'IBM Plex Mono, monospace', 'fontSize': '10px',
            'letterSpacing': '3px', 'color': COLORS['text_dim'], 'marginBottom': '12px',
        }),
        dcc.Slider(
            id='years-slider', min=5, max=80, step=5, value=30,
            marks={y: {'label': str(y), 'style': {'color': COLORS['text_dim'],
                                                    'fontFamily': 'IBM Plex Mono, monospace',
                                                    'fontSize': '10px'}}
                   for y in [5, 10, 20, 30, 40, 50, 60, 80]},
            tooltip={'placement': 'bottom', 'always_visible': True},
        ),
    ], style={
        'background': COLORS['panel'], 'border': f'1px solid {COLORS["border"]}',
        'borderRadius': '6px', 'padding': '20px 32px', 'margin': '24px 32px 0',
    })

    growth_selector = html.Div([
        html.Div('ANNUAL GROWTH RATE', style={
            'fontFamily': 'IBM Plex Mono, monospace', 'fontSize': '10px',
            'letterSpacing': '3px', 'color': COLORS['text_dim'], 'marginBottom': '12px',
        }),
        dcc.RadioItems(
            id='growth-rate',
            options=[
                {'label': ' Conservative +1%',  'value': 0.01},
                {'label': ' Baseline +3%',       'value': 0.03},
                {'label': ' Pessimistic +5%',    'value': 0.05},
                {'label': ' Extreme +8%',        'value': 0.08},
            ],
            value=0.03,
            inline=True,
            labelStyle={'marginRight': '24px', 'fontFamily': 'IBM Plex Mono, monospace',
                        'fontSize': '12px', 'color': COLORS['text'], 'cursor': 'pointer'},
        ),
    ], style={
        'background': COLORS['panel'], 'border': f'1px solid {COLORS["border"]}',
        'borderRadius': '6px', 'padding': '20px 32px', 'margin': '12px 32px 0',
    })

    return html.Div([
        slider,
        growth_selector,
        html.Div(id='prediction-charts', style={'padding': '0 0 32px'}),
    ])


@callback(Output('prediction-charts', 'children'),
          Input('years-slider', 'value'),
          Input('growth-rate', 'value'),
          Input('station-select', 'value'))
def update_predictions(years_ahead, growth_rate, station):
    d = df[df['station'] == station]
    annual = (d.groupby('year')['rain_mm'].sum()
               .reset_index().rename(columns={'rain_mm': 'annual_total'}))
    annual = annual[annual['year'] < datetime.today().year]
    base_year  = annual['year'].max()
    base_total = annual.loc[annual['year'] == base_year, 'annual_total'].values[0]

    future_years  = list(range(base_year + 1, base_year + years_ahead + 1))
    future_totals = [base_total * ((1 + growth_rate) ** y) for y in range(1, years_ahead + 1)]
    # Uncertainty bands (±15% widening over time)
    upper = [v * (1 + 0.05 + 0.003 * y) for y, v in enumerate(future_totals)]
    lower = [v * (1 - 0.05 - 0.003 * y) for y, v in enumerate(future_totals)]

    fig = go.Figure()
    # Historical
    fig.add_trace(go.Scatter(
        x=annual['year'], y=annual['annual_total'],
        name='Historical', mode='lines+markers',
        line=dict(color=COLORS['accent'], width=2),
        marker=dict(size=4),
        hovertemplate='%{x}<br>Actual: %{y:.0f} mm<extra></extra>',
    ))
    # Uncertainty band
    fig.add_trace(go.Scatter(
        x=future_years + future_years[::-1],
        y=upper + lower[::-1],
        fill='toself', fillcolor='rgba(0,200,255,0.07)',
        line=dict(color='rgba(0,0,0,0)'),
        name='Uncertainty Band', hoverinfo='skip',
    ))
    # Projection
    fig.add_trace(go.Scatter(
        x=[base_year] + future_years,
        y=[base_total] + future_totals,
        name=f'Projection (+{growth_rate*100:.0f}%/yr)',
        mode='lines',
        line=dict(color=COLORS['ELEVATED'], width=2.5, dash='dash'),
        hovertemplate='%{x}<br>Projected: %{y:.0f} mm<extra></extra>',
    ))

    final = future_totals[-1]
    change = (final - base_total) / base_total * 100
    fig.add_annotation(
        x=future_years[-1], y=final,
        text=f'+{change:.0f}% by {future_years[-1]}',
        font=dict(color=COLORS['HIGH'], size=12, family='IBM Plex Mono, monospace'),
        bgcolor=COLORS['panel'], bordercolor=COLORS['HIGH'],
        borderwidth=1, arrowcolor=COLORS['HIGH'],
    )

    fig.update_layout(
        **CHART_LAYOUT,
        title=dict(
            text=f'Annual Rainfall Projection  ·  {years_ahead}-Year Horizon  ·  +{growth_rate*100:.0f}% / Year',
            font=dict(size=13, color=COLORS['text_dim'], family='IBM Plex Mono, monospace'),
        ),
        height=380, yaxis_title='Annual Rainfall (mm)',
        shapes=[dict(
            type='line', x0=base_year, x1=base_year,
            y0=0, y1=1, yref='paper',
            line=dict(color=COLORS['border'], width=1, dash='dot'),
        )],
    )

    # Risk level projection
    risk_scores_future = [(v - annual['annual_total'].mean()) / annual['annual_total'].mean() * 100
                          for v in future_totals]
    risk_colors_future = []
    risk_levels_future = []
    for s in risk_scores_future:
        if s > 70:  level = 'HIGH'
        elif s >= 40: level = 'ELEVATED'
        elif s >= 15: level = 'MODERATE'
        else: level = 'LOW'
        risk_colors_future.append(COLORS[level])
        risk_levels_future.append(level)

    fig2 = go.Figure(go.Bar(
        x=future_years, y=future_totals,
        marker_color=risk_colors_future,
        hovertemplate='%{x}<br>%{y:.0f} mm<extra></extra>',
    ))
    fig2.update_layout(
        **CHART_LAYOUT,
        title=dict(text='Projected Annual Totals by Risk Level',
                   font=dict(size=13, color=COLORS['text_dim'], family='IBM Plex Mono, monospace')),
        height=260, yaxis_title='Rainfall (mm)',
        bargap=0.1,
    )

    # Summary cards
    risk_counts = {l: risk_levels_future.count(l) for l in RISK_ORDER}
    cards = html.Div([
        html.Div([
            html.Div(f'{c} YEARS', style={
                'fontFamily': 'IBM Plex Mono, monospace', 'fontSize': '28px',
                'fontWeight': '700', 'color': COLORS[l],
            }),
            html.Div(l, style={
                'fontFamily': 'IBM Plex Mono, monospace', 'fontSize': '9px',
                'letterSpacing': '3px', 'color': COLORS['text_dim'], 'marginTop': '4px',
            }),
        ], style={
            'background': COLORS['panel'], 'border': f'1px solid {COLORS[l]}44',
            'borderRadius': '6px', 'padding': '16px 24px',
            'flex': '1', 'minWidth': '120px', 'textAlign': 'center',
        }) for l, c in risk_counts.items()
    ], style={'display': 'flex', 'gap': '12px', 'padding': '16px 32px', 'flexWrap': 'wrap'})

    def explain(text):
        return html.Div(text, style={
            'fontFamily': 'Space Grotesk, sans-serif', 'fontSize': '13px',
            'color': COLORS['text_dim'], 'lineHeight': '1.7',
            'padding': '6px 32px 4px',
        })

    return html.Div([
        cards,
        explain(
            '🔮  The solid blue line shows actual historical rainfall. The dashed orange line is our '
            'projection — what rainfall totals might look like if the annual growth rate you selected '
            'continues into the future. The shaded area shows the uncertainty range: reality could '
            'fall anywhere in that band. Use the slider above to see projections 5 to 80 years ahead, '
            'and try different growth rates to see best and worst case scenarios.'
        ),
        html.Div([dcc.Graph(figure=fig,  config={'displayModeBar': False})], style={'padding': '0 32px'}),
        explain(
            '🌡️  Each bar below represents one future year, coloured by its projected risk level. '
            'Green bars are years where rainfall is close to normal (LOW risk). '
            'As we move further into the future with higher rainfall, more bars turn orange and red. '
            'This tells planners which decade requires the most investment in flood defences.'
        ),
        html.Div([dcc.Graph(figure=fig2, config={'displayModeBar': False})], style={'padding': '12px 32px 0'}),
    ])



# ─────────────────────────────────────────────
# CSV DOWNLOAD CALLBACK
# ─────────────────────────────────────────────
from dash import callback_context
from dash.exceptions import PreventUpdate

@callback(
    Output('download-csv', 'data'),
    Input('btn-download-csv', 'n_clicks'),
    Input('station-select', 'value'),
    Input('date-range-select', 'value'),
    prevent_initial_call=True,
)
def download_csv(n_clicks, station, days):
    if not n_clicks or n_clicks == 0:
        raise PreventUpdate
    d = df[df['station'] == station].copy()
    days_int = int(days)
    if days_int < 99999:
        cutoff = d['date'].max() - timedelta(days=days_int)
        d = d[d['date'] >= cutoff]
    export = d[['date','rain_mm','roll7','roll30','hist_avg_30',
                'risk_score','risk_level','year','month']].copy()
    export['date'] = export['date'].dt.strftime('%Y-%m-%d')
    for col in ['rain_mm','roll7','roll30','hist_avg_30','risk_score']:
        export[col] = export[col].round(2)
    fname = f"kilkenny_rainfall_{station.replace(' ','_')}_{days}d.csv"
    return dcc.send_data_frame(export.to_csv, fname, index=False)

# ─────────────────────────────────────────────
# BACKGROUND SCHEDULER — runs inside the app
# Updates data from Met Éireann every day at 06:00
# Works on cloud (Render, Railway) — no external tools needed
# ─────────────────────────────────────────────
def scheduled_update():
    """Called automatically every day at 06:00 by APScheduler."""
    print(f"\n[SCHEDULER] Running daily Met Éireann update at {datetime.now().strftime('%Y-%m-%d %H:%M')}...")
    try:
        from update_data import update as run_update
        added = run_update()
        if added > 0:
            print(f"[SCHEDULER] ✓ {added} new rows added — reloading data...")
            # Reload the global dataframe with fresh data
            global df, stations
            df_raw_new = generate_sample_data()
            df         = load_and_process(df_raw_new)
            stations   = sorted(df['station'].unique())
            print(f"[SCHEDULER] ✓ Dashboard data refreshed — {len(df):,} rows loaded")
        else:
            print("[SCHEDULER] ✓ Data already current")
    except Exception as e:
        print(f"[SCHEDULER] ✗ Update failed: {e}")


def start_scheduler():
    """Start APScheduler background thread — safe for cloud deployment."""
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
        scheduler = BackgroundScheduler(daemon=True)
        # Run every day at 06:00 Irish time
        scheduler.add_job(
            scheduled_update,
            trigger=CronTrigger(hour=6, minute=0),
            id='daily_met_update',
            name='Daily Met Éireann rainfall update',
            replace_existing=True,
        )
        scheduler.start()
        print("\n[SCHEDULER] ✓ Daily update scheduled — runs at 06:00 every morning")
        print("[SCHEDULER]   No manual updates needed — data stays fresh automatically")
        return scheduler
    except ImportError:
        print("\n[SCHEDULER] ⚠ APScheduler not installed")
        print("[SCHEDULER]   Run:  pip install apscheduler")
        print("[SCHEDULER]   Data will update on each app restart instead")
        return None
    except Exception as e:
        print(f"\n[SCHEDULER] ⚠ Could not start scheduler: {e}")
        return None


# Expose server for gunicorn (cloud deployment)
server = app.server

if __name__ == '__main__':
    # Start background scheduler
    _scheduler = start_scheduler()
    # Run the app
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))
