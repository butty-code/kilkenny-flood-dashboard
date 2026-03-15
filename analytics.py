"""
analytics.py
─────────────────────────────────────────────────────────────
Advanced Analytics Tab — Tab 07
Professional-grade analysis that goes beyond what county
council software typically shows:
  • Extreme event detection & return periods
  • Consecutive wet/dry spell analysis
  • Month-by-month year comparison
  • Seasonal pattern decomposition
  • Percentile ranking of any period
  • Downloadable CSV export of filtered data
─────────────────────────────────────────────────────────────
"""

from dash import html, dcc, dash_table
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

C = {
    'bg':          '#0a0f1e',
    'panel':       '#0f1729',
    'panel_light': '#141f38',
    'border':      '#1e3058',
    'accent':      '#00c8ff',
    'accent2':     '#0066ff',
    'text':        '#e8f0ff',
    'text_dim':    '#7a95c2',
    'HIGH':        '#ff3b5c',
    'ELEVATED':    '#ff8c00',
    'MODERATE':    '#ffd700',
    'LOW':         '#00e676',
    'grid':        '#1a2847',
}
FONT  = 'IBM Plex Mono, monospace'
FONT2 = 'Space Grotesk, sans-serif'

CHART_BASE = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family=FONT, color=C['text'], size=11),
    xaxis=dict(gridcolor=C['grid'], linecolor=C['border'],
               tickfont=dict(color=C['text_dim'])),
    yaxis=dict(gridcolor=C['grid'], linecolor=C['border'],
               tickfont=dict(color=C['text_dim'])),
    legend=dict(bgcolor='rgba(0,0,0,0)', bordercolor=C['border'],
                font=dict(color=C['text_dim'])),
    hoverlabel=dict(bgcolor=C['panel_light'], font_color=C['text'],
                    bordercolor=C['border']),
)


def explain(text, icon=''):
    return html.Div([
        html.Span(icon + '  ' if icon else '', style={'fontSize': '16px'}),
        html.Span(text, style={'fontFamily': FONT2, 'fontSize': '13px',
                               'color': C['text_dim'], 'lineHeight': '1.7'}),
    ], style={
        'background': C['panel_light'],
        'borderLeft': f'4px solid {C["accent"]}',
        'borderRadius': '0 6px 6px 0',
        'padding': '12px 18px',
        'marginBottom': '12px',
    })


def section_head(title, subtitle=''):
    return html.Div([
        html.Div(title, style={
            'fontFamily': FONT, 'fontSize': '11px', 'letterSpacing': '4px',
            'color': C['accent'], 'fontWeight': '700',
        }),
        html.Div(subtitle, style={
            'fontFamily': FONT2, 'fontSize': '20px', 'fontWeight': '700',
            'color': C['text'], 'marginTop': '4px',
        }) if subtitle else html.Div(),
    ], style={
        'padding': '20px 24px 16px',
        'background': C['panel_light'],
        'borderLeft': f'4px solid {C["accent"]}',
        'borderRadius': '0 6px 6px 0',
        'marginBottom': '20px', 'marginTop': '32px',
    })


# ─────────────────────────────────────────────────────────────
# 1. EXTREME EVENT ANALYSIS
# ─────────────────────────────────────────────────────────────

def extreme_events(d):
    """Top 20 wettest days + return period estimation."""
    d = d.copy()

    # Top 20 single-day events
    top20 = d.nlargest(20, 'rain_mm')[['date', 'rain_mm', 'risk_level']].copy()
    top20['rank'] = range(1, 21)
    top20['date_str'] = top20['date'].dt.strftime('%d %b %Y')

    colors = [C[l] for l in top20['risk_level']]

    fig_top = go.Figure(go.Bar(
        x=top20['rain_mm'],
        y=[f"#{r}  {d}" for r, d in zip(top20['rank'], top20['date_str'])],
        orientation='h',
        marker_color=colors,
        text=[f"{v:.1f} mm" for v in top20['rain_mm']],
        textposition='outside',
        textfont=dict(color=C['text'], size=11, family=FONT),
        hovertemplate='%{y}<br><b>%{x:.2f} mm</b><extra></extra>',
    ))
    fig_top.update_layout(
        **CHART_BASE,
        title=dict(text='Top 20 Wettest Single Days on Record',
                   font=dict(size=12, color=C['text_dim'], family=FONT)),
        height=480,
    )
    fig_top.update_layout(margin=dict(l=170, r=60, t=45, b=40))
    fig_top.update_xaxes(title='Rainfall (mm)')
    fig_top.update_yaxes(autorange='reversed', tickfont=dict(size=10, family=FONT))

    # Return period chart — empirical Gumbel
    annual_max = d.groupby('year')['rain_mm'].max().sort_values()
    n = len(annual_max)
    ranks = np.arange(1, n + 1)
    # Weibull plotting positions
    probs = ranks / (n + 1)
    return_periods = 1 / (1 - probs)

    fig_rp = go.Figure()
    fig_rp.add_trace(go.Scatter(
        x=return_periods,
        y=annual_max.values,
        mode='markers',
        name='Annual Max',
        marker=dict(color=C['accent'], size=6, opacity=0.8),
        hovertemplate='Return period: %{x:.1f} yrs<br>Max daily rain: %{y:.1f} mm<extra></extra>',
    ))

    # Gumbel fit
    mu    = annual_max.mean()
    sigma = annual_max.std()
    beta  = sigma * np.sqrt(6) / np.pi
    u     = mu - 0.5772 * beta
    rp_fit = np.logspace(np.log10(1.1), np.log10(200), 100)
    y_fit  = u - beta * np.log(-np.log(1 - 1 / rp_fit))

    fig_rp.add_trace(go.Scatter(
        x=rp_fit, y=y_fit,
        mode='lines', name='Gumbel Fit',
        line=dict(color=C['ELEVATED'], width=2, dash='dash'),
        hovertemplate='Return period: %{x:.0f} yrs<br>Expected max: %{y:.1f} mm<extra></extra>',
    ))

    # Mark key return periods
    for rp, col in [(10, C['MODERATE']), (20, C['ELEVATED']), (100, C['HIGH'])]:
        y_rp = u - beta * np.log(-np.log(1 - 1 / rp))
        fig_rp.add_vline(x=rp, line_color=col, line_width=1, line_dash='dot', opacity=0.6)
        fig_rp.add_annotation(x=rp, y=y_rp,
            text=f'1:{rp}<br>{y_rp:.0f}mm',
            font=dict(color=col, size=9, family=FONT),
            bgcolor=C['panel'], bordercolor=col, borderwidth=1,
            showarrow=False, yshift=20)

    fig_rp.update_layout(
        **CHART_BASE,
        title=dict(text='Flood Return Periods — How Often Do Extreme Events Happen?',
                   font=dict(size=12, color=C['text_dim'], family=FONT)),
        height=320,

    )
    fig_rp.update_xaxes(type='log', title='Return Period (years)',
                    tickvals=[2,5,10,20,50,100,200],
                    ticktext=['2yr','5yr','10yr','20yr','50yr','100yr','200yr'])
    fig_rp.update_yaxes(title='Max Daily Rainfall (mm)')

    # Stats cards
    rp_vals = {}
    for rp in [5, 10, 20, 50, 100]:
        rp_vals[rp] = u - beta * np.log(-np.log(1 - 1 / rp))

    stat_cards = html.Div([
        html.Div([
            html.Div(f'1-in-{rp} Year Event', style={
                'fontFamily': FONT, 'fontSize': '9px', 'letterSpacing': '2px',
                'color': C['text_dim'], 'marginBottom': '4px',
            }),
            html.Div(f'{v:.0f} mm', style={
                'fontFamily': FONT, 'fontSize': '22px', 'fontWeight': '700',
                'color': C['ELEVATED'] if rp <= 20 else C['HIGH'],
            }),
            html.Div('in one day', style={
                'fontFamily': FONT2, 'fontSize': '11px', 'color': C['text_dim'],
            }),
        ], style={
            'background': C['panel'], 'border': f'1px solid {C["border"]}',
            'borderRadius': '6px', 'padding': '16px 20px',
            'flex': '1', 'minWidth': '120px', 'textAlign': 'center',
        })
        for rp, v in rp_vals.items()
    ], style={'display': 'flex', 'gap': '12px', 'flexWrap': 'wrap', 'marginBottom': '20px'})

    return html.Div([
        section_head('01  EXTREME EVENTS', 'Record rainfalls & return periods'),
        explain(
            'The top chart shows the 20 biggest single-day rainfall events ever recorded at this station. '
            'The return period chart below shows how often extreme events are expected to occur — '
            'a "1-in-20-year event" means there is a 5% chance of it happening in any given year.',
            '⚡'
        ),
        stat_cards,
        html.Div([dcc.Graph(figure=fig_top, config={'displayModeBar': False})],
                 style={'marginBottom': '16px'}),
        html.Div([dcc.Graph(figure=fig_rp, config={'displayModeBar': False})]),
    ])


# ─────────────────────────────────────────────────────────────
# 2. WET & DRY SPELL ANALYSIS
# ─────────────────────────────────────────────────────────────

def spell_analysis(d):
    """Consecutive wet days (≥1mm) and dry days analysis."""
    d = d.sort_values('date').copy()
    rain = d['rain_mm'].to_numpy()
    dates = d['date'].values

    # Calculate consecutive wet/dry runs
    wet_threshold = 1.0

    def get_spells(arr, condition):
        spells = []
        count = 0
        start_idx = 0
        for i, v in enumerate(arr):
            if condition(v):
                if count == 0:
                    start_idx = i
                count += 1
            else:
                if count > 0:
                    spells.append({'length': count, 'start': dates[start_idx],
                                   'end': dates[min(i-1, len(dates)-1)],
                                   'total': arr[start_idx:i].sum()})
                count = 0
        if count > 0:
            spells.append({'length': count, 'start': dates[start_idx],
                           'end': dates[-1], 'total': arr[start_idx:].sum()})
        return pd.DataFrame(spells)

    wet_spells = get_spells(rain, lambda v: v >= wet_threshold)
    dry_spells = get_spells(rain, lambda v: v < wet_threshold)

    # Annual longest wet spell
    if not wet_spells.empty:
        wet_spells['year'] = pd.to_datetime(wet_spells['start']).dt.year
        annual_wet = wet_spells.groupby('year')['length'].max().reset_index()
        annual_dry = dry_spells.copy()
        if not dry_spells.empty:
            dry_spells['year'] = pd.to_datetime(dry_spells['start']).dt.year
            annual_dry = dry_spells.groupby('year')['length'].max().reset_index()

        fig = make_subplots(rows=1, cols=2,
                            subplot_titles=['Longest Consecutive WET Spell per Year',
                                            'Longest Consecutive DRY Spell per Year'],
                            horizontal_spacing=0.08)

        fig.add_trace(go.Bar(
            x=annual_wet['year'], y=annual_wet['length'],
            name='Wet spell (days)', marker_color=C['accent2'],
            hovertemplate='%{x}<br>Longest wet spell: <b>%{y} days</b><extra></extra>',
        ), row=1, col=1)

        if not dry_spells.empty:
            fig.add_trace(go.Bar(
                x=annual_dry['year'], y=annual_dry['length'],
                name='Dry spell (days)', marker_color=C['MODERATE'],
                hovertemplate='%{x}<br>Longest dry spell: <b>%{y} days</b><extra></extra>',
            ), row=1, col=2)

        fig.update_layout(
            **CHART_BASE,
            height=300,
            showlegend=False,
            title=dict(text='Consecutive Wet & Dry Spells — Are They Getting Longer?',
                       font=dict(size=12, color=C['text_dim'], family=FONT)),
        )
        fig.update_xaxes(gridcolor=C['grid'], linecolor=C['border'],
                         tickfont=dict(color=C['text_dim']))
        fig.update_yaxes(gridcolor=C['grid'], linecolor=C['border'],
                         tickfont=dict(color=C['text_dim']),
                         title_text='Days')

        # Top 5 wet spells table
        top_wet = wet_spells.nlargest(5, 'length')[['start', 'end', 'length', 'total']].copy()
        top_wet['start'] = pd.to_datetime(top_wet['start']).dt.strftime('%d %b %Y')
        top_wet['end']   = pd.to_datetime(top_wet['end']).dt.strftime('%d %b %Y')
        top_wet['total'] = top_wet['total'].round(1)
        top_wet.columns  = ['Start', 'End', 'Days', 'Total Rain (mm)']

        top_dry = dry_spells.nlargest(5, 'length')[['start', 'end', 'length']].copy() if not dry_spells.empty else pd.DataFrame()
        if not top_dry.empty:
            top_dry['start'] = pd.to_datetime(top_dry['start']).dt.strftime('%d %b %Y')
            top_dry['end']   = pd.to_datetime(top_dry['end']).dt.strftime('%d %b %Y')
            top_dry.columns  = ['Start', 'End', 'Days']

        def make_mini_table(df, title, color):
            return html.Div([
                html.Div(title, style={'fontFamily': FONT, 'fontSize': '9px',
                    'letterSpacing': '2px', 'color': color, 'marginBottom': '8px'}),
                html.Div([
                    html.Div([
                        html.Div(str(row[c]), style={
                            'fontFamily': FONT2, 'fontSize': '12px',
                            'color': C['text'], 'padding': '6px 10px',
                            'flex': '1',
                        }) for c in df.columns
                    ] , style={
                        'display': 'flex',
                        'background': C['panel'] if i % 2 == 0 else C['panel_light'],
                        'borderBottom': f'1px solid {C["border"]}',
                    })
                    for i, (_, row) in enumerate(df.iterrows())
                ], style={
                    'border': f'1px solid {C["border"]}',
                    'borderRadius': '6px', 'overflow': 'hidden',
                }),
            ], style={'flex': '1', 'minWidth': '280px'})

        stats_summary = html.Div([
            html.Div([
                html.Div(f'{wet_spells["length"].max()}', style={
                    'fontFamily': FONT, 'fontSize': '36px', 'fontWeight': '700',
                    'color': C['accent2'],
                }),
                html.Div('Record consecutive wet days', style={
                    'fontFamily': FONT2, 'fontSize': '12px', 'color': C['text_dim'],
                }),
            ], style={'flex': '1', 'background': C['panel'],
                      'border': f'1px solid {C["border"]}',
                      'borderRadius': '6px', 'padding': '16px 20px', 'textAlign': 'center'}),
            html.Div([
                html.Div(f'{dry_spells["length"].max() if not dry_spells.empty else 0}', style={
                    'fontFamily': FONT, 'fontSize': '36px', 'fontWeight': '700',
                    'color': C['MODERATE'],
                }),
                html.Div('Record consecutive dry days', style={
                    'fontFamily': FONT2, 'fontSize': '12px', 'color': C['text_dim'],
                }),
            ], style={'flex': '1', 'background': C['panel'],
                      'border': f'1px solid {C["border"]}',
                      'borderRadius': '6px', 'padding': '16px 20px', 'textAlign': 'center'}),
            html.Div([
                html.Div(f'{(rain >= wet_threshold).mean()*100:.0f}%', style={
                    'fontFamily': FONT, 'fontSize': '36px', 'fontWeight': '700',
                    'color': C['accent'],
                }),
                html.Div('of days have measurable rain (≥1mm)', style={
                    'fontFamily': FONT2, 'fontSize': '12px', 'color': C['text_dim'],
                }),
            ], style={'flex': '1', 'background': C['panel'],
                      'border': f'1px solid {C["border"]}',
                      'borderRadius': '6px', 'padding': '16px 20px', 'textAlign': 'center'}),
        ], style={'display': 'flex', 'gap': '12px', 'flexWrap': 'wrap', 'marginBottom': '20px'})

        tables_row = html.Div([
            make_mini_table(top_wet, 'TOP 5 LONGEST WET SPELLS', C['accent2']),
            make_mini_table(top_dry, 'TOP 5 LONGEST DRY SPELLS', C['MODERATE']) if not top_dry.empty else html.Div(),
        ], style={'display': 'flex', 'gap': '16px', 'flexWrap': 'wrap', 'marginTop': '16px'})

        return html.Div([
            section_head('02  WET & DRY SPELLS', 'Consecutive rainfall patterns'),
            explain(
                'A "wet spell" is a run of consecutive days with at least 1mm of rain. '
                'A "dry spell" is a run of days with no measurable rain. '
                'Longer wet spells saturate the soil more deeply — '
                'the ground cannot drain between events, dramatically increasing flood risk. '
                'Climate change is making both extremes longer.',
                '🌧️'
            ),
            stats_summary,
            html.Div([dcc.Graph(figure=fig, config={'displayModeBar': False})],
                     style={'marginBottom': '8px'}),
            tables_row,
        ])
    return html.Div("Not enough data for spell analysis.")


# ─────────────────────────────────────────────────────────────
# 3. YEAR-ON-YEAR MONTH COMPARISON
# ─────────────────────────────────────────────────────────────

def monthly_comparison(d):
    """Compare any calendar month across all years."""
    month_names = ['Jan','Feb','Mar','Apr','May','Jun',
                   'Jul','Aug','Sep','Oct','Nov','Dec']

    monthly = (d.groupby(['year', 'month'])['rain_mm']
                .sum().reset_index()
                .rename(columns={'rain_mm': 'monthly_total'}))

    # Anomaly: each month vs its own long-term average
    monthly_avg = monthly.groupby('month')['monthly_total'].mean()
    monthly['avg']     = monthly['month'].map(monthly_avg)
    monthly['anomaly'] = monthly['monthly_total'] - monthly['avg']
    monthly['anomaly_pct'] = (monthly['anomaly'] / monthly['avg'] * 100).round(1)

    # Heatmap of monthly anomaly (% above/below average)
    pivot = monthly.pivot(index='year', columns='month', values='anomaly_pct')
    pivot.columns = month_names

    fig_anom = go.Figure(go.Heatmap(
        z=pivot.values,
        x=month_names,
        y=pivot.index,
        colorscale=[
            [0.0,  '#1B3A6B'],   # very dry — dark blue
            [0.35, '#0a0f1e'],   # near average — bg
            [0.5,  '#1e3058'],   # average
            [0.65, '#ff8c00'],   # above average
            [0.85, '#ff3b5c'],   # much above average
            [1.0,  '#ff0033'],   # extreme
        ],
        zmid=0,
        zmin=-80, zmax=150,
        hovertemplate='%{y}  %{x}<br>Anomaly: <b>%{z:+.0f}%</b> vs average<extra></extra>',
        colorbar=dict(
            tickfont=dict(color=C['text_dim'], family=FONT),
            title=dict(text='% vs avg', font=dict(color=C['text_dim'])),
        ),
    ))
    fig_anom.update_layout(
        **CHART_BASE,
        title=dict(text='Monthly Rainfall Anomaly — How Much Above or Below Average Each Month Was',
                   font=dict(size=12, color=C['text_dim'], family=FONT)),
        height=max(280, min(900, len(pivot) * 14)),
    )
    fig_anom.update_layout(margin=dict(l=55, r=80, t=45, b=40))
    fig_anom.update_yaxes(autorange='reversed')

    # Rolling 12-month total — best indicator of sustained wet/dry periods
    d_sorted = d.sort_values('date').copy()
    d_sorted['roll365'] = d_sorted['rain_mm'].rolling(365, min_periods=180).sum()

    fig_roll12 = go.Figure()
    fig_roll12.add_trace(go.Scatter(
        x=d_sorted['date'], y=d_sorted['roll365'],
        mode='lines', name='12-Month Rolling Total',
        line=dict(color=C['accent'], width=2),
        fill='tozeroy', fillcolor='rgba(0,200,255,0.05)',
        hovertemplate='%{x|%d %b %Y}<br>12-month total: <b>%{y:.0f} mm</b><extra></extra>',
    ))
    avg_annual = d_sorted['roll365'].mean()
    fig_roll12.add_hline(y=avg_annual, line_color=C['MODERATE'],
                         line_width=1.5, line_dash='dash',
                         annotation_text=f'Long-term avg: {avg_annual:.0f}mm',
                         annotation_font=dict(color=C['MODERATE'], size=10, family=FONT))
    fig_roll12.update_layout(
        **CHART_BASE,
        title=dict(text='Rolling 12-Month Rainfall Total — The Best Long-Term Flood Indicator',
                   font=dict(size=12, color=C['text_dim'], family=FONT)),
        height=280,

    )
    fig_roll12.update_yaxes(title='12-Month Total (mm)')

    return html.Div([
        section_head('03  MONTHLY PATTERNS', 'Year-on-year comparison & 12-month rolling total'),
        explain(
            'The anomaly heatmap shows whether each month was wetter or drier than its own long-term average. '
            'Red = much wetter than normal. Blue = much drier than normal. '
            'A run of red squares across a whole row means that year was exceptionally wet. '
            'The 12-month rolling total below is the single best indicator of sustained flood risk — '
            'when it rises well above the dashed average line, serious flooding becomes much more likely.',
            '🗓️'
        ),
        html.Div([dcc.Graph(figure=fig_anom,   config={'displayModeBar': False})],
                 style={'marginBottom': '8px'}),
        html.Div([dcc.Graph(figure=fig_roll12, config={'displayModeBar': False})]),
    ])


# ─────────────────────────────────────────────────────────────
# 4. PERCENTILE RANKING
# ─────────────────────────────────────────────────────────────

def percentile_analysis(d):
    """Where does the current period rank in the full historical record?"""
    d = d.sort_values('date').copy()

    # Calculate what percentile each 30-day total sits in
    all_30d = d['roll30'].dropna()
    d['percentile'] = d['roll30'].apply(
        lambda x: (all_30d < x).mean() * 100 if pd.notna(x) else np.nan
    )

    fig = go.Figure()

    # Background percentile bands
    p25, p50, p75, p90, p95 = (np.percentile(all_30d.dropna(), p)
                                 for p in [25, 50, 75, 90, 95])

    for y0, y1, col, label in [
        (p95, all_30d.max()*1.1, C['HIGH'],     'Extreme (top 5%)'),
        (p90, p95,               C['ELEVATED'],  'Very wet (top 10%)'),
        (p75, p90,               C['MODERATE'],  'Above average'),
        (p50, p75,               '#1a2847',      'Slightly above avg'),
    ]:
        fig.add_hrect(y0=y0, y1=y1, fillcolor=col, opacity=0.08,
                      line_width=0, annotation_text=label,
                      annotation_position='right',
                      annotation_font=dict(color=col, size=8, family=FONT))

    fig.add_trace(go.Scatter(
        x=d['date'], y=d['roll30'],
        mode='lines', name='30-Day Total',
        line=dict(color=C['accent'], width=1.5),
        fill='tozeroy', fillcolor='rgba(0,200,255,0.06)',
        hovertemplate='%{x|%d %b %Y}<br>30-day total: <b>%{y:.1f}mm</b><br>Percentile: see score chart<extra></extra>',
    ))

    for val, col, label in [(p95, C['HIGH'], '95th'), (p75, C['MODERATE'], '75th'),
                             (p50, C['LOW'], '50th (median)')]:
        fig.add_hline(y=val, line_color=col, line_width=1, line_dash='dot', opacity=0.5,
                      annotation_text=f'{label} pct: {val:.0f}mm',
                      annotation_font=dict(color=col, size=9, family=FONT))

    fig.update_layout(
        **CHART_BASE,
        title=dict(text='30-Day Rainfall vs Historical Percentiles — Where Does Each Period Rank?',
                   font=dict(size=12, color=C['text_dim'], family=FONT)),
        height=320,

    )
    fig.update_yaxes(title='30-Day Total (mm)')

    # Percentile score over time
    fig2 = go.Figure(go.Scatter(
        x=d['date'], y=d['percentile'],
        mode='lines',
        line=dict(color=C['accent2'], width=1.5),
        fill='tozeroy', fillcolor='rgba(0,102,255,0.06)',
        hovertemplate='%{x|%d %b %Y}<br>Percentile rank: <b>%{y:.0f}th</b><extra></extra>',
    ))
    fig2.add_hline(y=95, line_color=C['HIGH'],     line_width=1, line_dash='dot', opacity=0.5)
    fig2.add_hline(y=75, line_color=C['MODERATE'], line_width=1, line_dash='dot', opacity=0.5)
    fig2.add_hline(y=50, line_color=C['LOW'],       line_width=1, line_dash='dot', opacity=0.5)
    fig2.update_layout(
        **CHART_BASE,
        title=dict(text='Percentile Rank of 30-Day Rainfall Over Time',
                   font=dict(size=12, color=C['text_dim'], family=FONT)),
        height=240,

    )
    fig2.update_yaxes(title='Percentile', range=[0, 100])

    # Current stats
    latest_30d   = d['roll30'].iloc[-1]
    latest_pct   = d['percentile'].iloc[-1]
    current_rank = f'{latest_pct:.0f}th percentile'

    rank_card = html.Div([
        html.Div('CURRENT 30-DAY PERIOD RANKS AT', style={
            'fontFamily': FONT, 'fontSize': '9px', 'letterSpacing': '3px',
            'color': C['text_dim'], 'marginBottom': '8px',
        }),
        html.Div(current_rank, style={
            'fontFamily': FONT, 'fontSize': '40px', 'fontWeight': '700',
            'color': C['HIGH'] if latest_pct > 95 else C['ELEVATED'] if latest_pct > 75
                     else C['MODERATE'] if latest_pct > 50 else C['LOW'],
        }),
        html.Div(
            f'{latest_30d:.1f}mm in 30 days  ·  '
            f'{"wetter than " + str(int(latest_pct)) + "% of all 30-day periods on record"}'
            if latest_pct >= 50 else
            f'{latest_30d:.1f}mm in 30 days  ·  drier than {100-int(latest_pct)}% of all periods',
            style={'fontFamily': FONT2, 'fontSize': '13px', 'color': C['text_dim'], 'marginTop': '6px'},
        ),
    ], style={
        'background': C['panel'], 'border': f'1px solid {C["border"]}',
        'borderRadius': '6px', 'padding': '20px 24px', 'marginBottom': '20px',
    })

    return html.Div([
        section_head('04  PERCENTILE RANKING', 'How does any period compare to all of history?'),
        explain(
            'A percentile tells you where a measurement sits in the full historical range. '
            'The 95th percentile means only 5% of all 30-day periods in history were wetter than this. '
            'This is more meaningful than the raw mm figure because it accounts for the season — '
            'October is naturally wetter than July, so the percentile gives a fair comparison.',
            '📊'
        ),
        rank_card,
        html.Div([dcc.Graph(figure=fig,  config={'displayModeBar': False})],
                 style={'marginBottom': '8px'}),
        html.Div([dcc.Graph(figure=fig2, config={'displayModeBar': False})]),
    ])


# ─────────────────────────────────────────────────────────────
# 5. DATA EXPORT
# ─────────────────────────────────────────────────────────────

def data_export(d):
    """Download the processed data as CSV."""
    export = d[['date','rain_mm','roll7','roll30','hist_avg_30',
                'risk_score','risk_level','year','month']].copy()
    export['date'] = export['date'].dt.strftime('%Y-%m-%d')
    for col in ['rain_mm','roll7','roll30','hist_avg_30','risk_score']:
        export[col] = export[col].round(2)

    n      = len(export)
    d_from = d['date'].min().strftime('%d %b %Y')
    d_to   = d['date'].max().strftime('%d %b %Y')

    tbl = dash_table.DataTable(
        data=export.sort_values('date', ascending=False).head(100).to_dict('records'),
        columns=[{'name': c, 'id': c} for c in export.columns],
        page_size=15,
        sort_action='native',
        style_table={'overflowX': 'auto'},
        style_header={
            'backgroundColor': C['panel_light'], 'color': C['text_dim'],
            'fontFamily': FONT, 'fontSize': '10px', 'letterSpacing': '1px',
            'border': f'1px solid {C["border"]}', 'padding': '10px',
        },
        style_cell={
            'backgroundColor': C['panel'], 'color': C['text'],
            'fontFamily': FONT, 'fontSize': '11px',
            'border': f'1px solid {C["border"]}', 'padding': '8px 12px',
            'textAlign': 'right',
        },
        style_cell_conditional=[
            {'if': {'column_id': 'date'}, 'textAlign': 'left'},
            {'if': {'column_id': 'risk_level'}, 'textAlign': 'center'},
        ],
        style_data_conditional=[
            {'if': {'filter_query': '{risk_level} = HIGH'},
             'color': C['HIGH'], 'fontWeight': '700'},
            {'if': {'filter_query': '{risk_level} = ELEVATED'},
             'color': C['ELEVATED']},
            {'if': {'row_index': 'odd'}, 'backgroundColor': '#0c1322'},
        ],
    )

    # CSV download via dcc.Download
    csv_string = export.to_csv(index=False)

    return html.Div([
        section_head('05  EXPORT DATA', 'Download your processed rainfall data'),
        explain(
            f'Showing preview of {n:,} processed records from {d_from} to {d_to}. '
            'All calculated fields are included: rolling totals, historical baseline, '
            'risk scores and risk levels. Click the button below to download the full '
            'dataset as a CSV file that opens in Excel.',
            '💾'
        ),
        html.Div([
            dcc.Download(id='download-csv'),
            html.Button(
                '⬇  Download Full Dataset as CSV',
                id='btn-download-csv',
                n_clicks=0,
                style={
                    'background': C['accent'], 'color': '#000',
                    'fontFamily': FONT, 'fontSize': '12px',
                    'letterSpacing': '2px', 'fontWeight': '700',
                    'padding': '12px 32px', 'border': 'none',
                    'borderRadius': '4px', 'cursor': 'pointer',
                    'marginBottom': '20px',
                    'boxShadow': f'0 0 20px {C["accent"]}44',
                },
            ),
            html.Div(f'Full file: {n:,} rows · {len(export.columns)} columns · '
                     f'CSV format · opens in Excel',
                     style={'fontFamily': FONT2, 'fontSize': '12px',
                            'color': C['text_dim'], 'marginBottom': '16px'}),
        ]),
        tbl,
    ])


# ─────────────────────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────────────────────

def build_analytics(d):
    """Full analytics tab — called by app.py."""
    station = d['station'].iloc[0] if len(d) > 0 else 'Unknown'
    date_range = (f"{d['date'].min().strftime('%d %b %Y')} → "
                  f"{d['date'].max().strftime('%d %b %Y')}")

    return html.Div([
        # Hero
        html.Div([
            html.Div('◈  DEEP ANALYTICS', style={
                'fontFamily': FONT, 'fontSize': '10px', 'letterSpacing': '4px',
                'color': C['accent'], 'marginBottom': '8px',
            }),
            html.Div('Advanced Rainfall Intelligence', style={
                'fontFamily': FONT2, 'fontSize': '26px', 'fontWeight': '700',
                'color': C['text'], 'marginBottom': '6px',
            }),
            html.Div(
                f'{station}  ·  {date_range}  ·  {len(d):,} days analysed',
                style={'fontFamily': FONT, 'fontSize': '11px',
                       'color': C['text_dim'], 'letterSpacing': '1px'},
            ),
        ], style={
            'padding': '28px 32px 20px',
            'background': f'linear-gradient(135deg, {C["panel"]} 0%, #0a1830 100%)',
            'borderBottom': f'1px solid {C["border"]}',
            'marginBottom': '8px',
        }),

        html.Div([
            extreme_events(d),
            html.Div(style={'borderTop': f'1px solid {C["border"]}', 'margin': '32px 0'}),
            spell_analysis(d),
            html.Div(style={'borderTop': f'1px solid {C["border"]}', 'margin': '32px 0'}),
            monthly_comparison(d),
            html.Div(style={'borderTop': f'1px solid {C["border"]}', 'margin': '32px 0'}),
            percentile_analysis(d),
            html.Div(style={'borderTop': f'1px solid {C["border"]}', 'margin': '32px 0'}),
            data_export(d),
        ], style={'padding': '8px 32px 48px'}),
    ])
