"""
prevention.py
─────────────────────────────────────────────────────────────
Flood Prevention & Solutions Tab
Called by app.py as Tab 05.
Receives the processed dataframe (df) and current station data
and returns a fully self-contained Dash layout.
─────────────────────────────────────────────────────────────
"""

from dash import html, dcc
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ── Colour palette (must match app.py COLORS) ─────────────
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
    'green':       '#00e676',
    'grid':        '#1a2847',
}

FONT = 'IBM Plex Mono, monospace'
FONT2 = 'Space Grotesk, sans-serif'

CHART_BASE = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family=FONT, color=C['text'], size=11),
    margin=dict(l=50, r=20, t=45, b=40),
    xaxis=dict(gridcolor=C['grid'], linecolor=C['border'], tickfont=dict(color=C['text_dim'])),
    yaxis=dict(gridcolor=C['grid'], linecolor=C['border'], tickfont=dict(color=C['text_dim'])),
    legend=dict(bgcolor='rgba(0,0,0,0)', bordercolor=C['border'], font=dict(color=C['text_dim'])),
    hoverlabel=dict(bgcolor=C['panel_light'], font_color=C['text'], bordercolor=C['border']),
)

# ─────────────────────────────────────────────────────────────
# KNOWLEDGE BASE — interventions, strategies, measures
# ─────────────────────────────────────────────────────────────

INTERVENTIONS = [
    # (category, name, cost_band, lead_time_yrs, effectiveness_pct, description)
    ('Nature-Based', 'River Floodplain Restoration',    'Medium',  3,  75, 'Restore natural floodplain along the Nore to absorb excess flow during high rainfall events'),
    ('Nature-Based', 'Riparian Buffer Planting',        'Low',     2,  45, 'Plant native trees and shrubs along riverbanks to slow runoff and stabilise soil'),
    ('Nature-Based', 'Upstream Wetland Creation',       'Medium',  4,  65, 'Create retention wetlands upstream of Kilkenny city to hold water during storm events'),
    ('Nature-Based', 'Reforestation of Catchment',     'Low',     10, 55, 'Long-term upland reforestation to reduce peak flows by increasing interception and infiltration'),
    ('Nature-Based', 'Green Roof Schemes',              'Low',     2,  20, 'Incentivise green roofs on urban buildings to reduce surface runoff in built-up areas'),

    ('Infrastructure', 'Flood Embankment Upgrade',      'High',    5,  85, 'Raise and reinforce existing flood defences along the Nore through Kilkenny city centre'),
    ('Infrastructure', 'Pumping Station Network',       'High',    4,  80, 'Install automated pumping stations at known flood hotspots for rapid water removal'),
    ('Infrastructure', 'Sustainable Urban Drainage',    'Medium',  3,  50, 'Retrofit permeable paving and soakaways in roads and car parks across the catchment'),
    ('Infrastructure', 'Retention Reservoir',           'High',    7,  90, 'Construct an upstream holding reservoir on the Nore to buffer extreme rainfall events'),
    ('Infrastructure', 'Culvert & Bridge Upgrade',      'Medium',  3,  40, 'Increase capacity of undersized culverts and bridges that restrict flow during floods'),

    ('Early Warning',  'Real-Time Gauge Network',       'Low',     1,  60, 'Expand automated river and rainfall gauge network with SMS/app alerts for residents'),
    ('Early Warning',  'Flood Forecasting Model',       'Medium',  2,  70, 'Deploy hydrological forecasting model giving 48–72 hour advance flood warnings'),
    ('Early Warning',  'Community Alert System',        'Low',     1,  55, 'WhatsApp/web community network for rapid sharing of local flood observations'),
    ('Early Warning',  'Satellite Monitoring',          'Medium',  2,  65, 'Use Copernicus satellite data to detect soil saturation and snowmelt risk upstream'),

    ('Policy',         'Flood Risk Zoning',             'Low',     2,  50, 'Update planning guidelines to restrict development in high flood-risk zones in the catchment'),
    ('Policy',         'Catchment-Wide Land Use Plan',  'Low',     3,  60, 'Coordinate farming and forestry practices across the Nore catchment to reduce peak runoff'),
    ('Policy',         'Insurance & Compensation Fund', 'Medium',  2,  30, 'Establish a flood compensation fund for residents and businesses in repeat flood areas'),
    ('Policy',         'Climate Adaptation Strategy',   'Low',     1,  40, 'Formal OPW/council strategy integrating climate projections into all infrastructure decisions'),
]

RISK_ACTIONS = {
    'LOW': [
        ('Monitor', 'Continue routine monitoring of rainfall and river levels'),
        ('Maintain', 'Inspect and maintain existing flood defences and drainage'),
        ('Plan',    'Review and update flood emergency response plans'),
        ('Engage',  'Run community flood awareness workshops'),
    ],
    'MODERATE': [
        ('Alert',   'Issue advisory notifications to residents in flood-prone areas'),
        ('Inspect', 'Deploy field teams to check river levels and drainage capacity'),
        ('Prepare', 'Pre-position sandbags and emergency equipment at key locations'),
        ('Restrict','Consider temporary restrictions on non-essential water use'),
        ('Review',  'Activate multi-agency flood coordination group'),
    ],
    'ELEVATED': [
        ('Warn',    'Issue formal flood warnings to all affected communities'),
        ('Deploy',  'Activate pumping stations and temporary flood barriers'),
        ('Evacuate','Prepare evacuation plans for highest-risk properties'),
        ('Close',   'Close at-risk roads and redirect traffic'),
        ('Mobilise','Put emergency services on standby across the catchment'),
        ('Contact', 'Notify OPW, Kilkenny County Council and Met Éireann'),
    ],
    'HIGH': [
        ('EVACUATE','Initiate evacuation of identified at-risk properties immediately'),
        ('CLOSE',   'Close all flood-risk roads, bridges and public areas'),
        ('DEPLOY',  'Full deployment of emergency services and civil defence'),
        ('SHELTER', 'Open emergency shelters at designated community centres'),
        ('MEDIA',   'Issue emergency broadcast on all local media channels'),
        ('OPW',     'Activate national flood emergency coordination with OPW'),
        ('RECORD',  'Begin detailed flood damage documentation for insurance/recovery'),
    ],
}

CATCHMENT_FACTS = [
    ('River',          'River Nore'),
    ('Catchment Area', '~2,460 km²'),
    ('Main Stations',  'Kilkenny (Lavistown), Graiguenamanagh (Ballyogan)'),
    ('Annual Avg Rain','~850–950 mm'),
    ('Wettest Months', 'October – January'),
    ('Flood History',  '1947, 1990, 2000, 2009, 2015–16 (major events)'),
    ('At-Risk Areas',  'Kilkenny city centre, Inistioge, Graiguenamanagh'),
    ('Key Risk Factor', 'Prolonged rainfall saturating clay soils in catchment'),
]


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def section_header(title, subtitle=None):
    return html.Div([
        html.Div(title, style={
            'fontFamily': FONT, 'fontSize': '11px', 'letterSpacing': '4px',
            'color': C['accent'], 'fontWeight': '700', 'marginBottom': '4px',
        }),
        html.Div(subtitle or '', style={
            'fontFamily': FONT2, 'fontSize': '22px', 'fontWeight': '600',
            'color': C['text'], 'marginBottom': '24px',
        }) if subtitle else html.Div(),
    ])


def card(children, accent_color=None, style_override=None):
    base = {
        'background': C['panel'],
        'border': f'1px solid {accent_color or C["border"]}',
        'borderRadius': '8px',
        'padding': '20px 24px',
    }
    if style_override:
        base.update(style_override)
    return html.Div(children, style=base)


def risk_pill(level):
    colors = {'HIGH': C['HIGH'], 'ELEVATED': C['ELEVATED'],
              'MODERATE': C['MODERATE'], 'LOW': C['LOW']}
    col = colors.get(level, C['text_dim'])
    return html.Span(level, style={
        'background': col,
        'color': '#000' if level in ('MODERATE', 'LOW') else '#fff',
        'padding': '2px 10px', 'borderRadius': '3px',
        'fontFamily': FONT, 'fontSize': '10px',
        'fontWeight': '700', 'letterSpacing': '2px',
    })


# ─────────────────────────────────────────────────────────────
# SECTION 1 — Current Risk Response
# ─────────────────────────────────────────────────────────────

def build_risk_response(d):
    latest      = d.iloc[-1]
    risk_level  = latest['risk_level']
    risk_score  = latest['risk_score']
    roll30      = latest['roll30']
    hist_avg    = latest['hist_avg_30']
    actions     = RISK_ACTIONS.get(risk_level, RISK_ACTIONS['LOW'])

    level_color = C[risk_level]
    action_rows = []
    for action, desc in actions:
        action_rows.append(html.Div([
            html.Div(action, style={
                'fontFamily': FONT, 'fontSize': '10px', 'letterSpacing': '2px',
                'color': level_color, 'fontWeight': '700',
                'minWidth': '100px',
            }),
            html.Div(desc, style={
                'fontFamily': FONT2, 'fontSize': '13px', 'color': C['text'],
                'flex': '1',
            }),
        ], className='risk-row', style={
            'display': 'flex', 'gap': '20px', 'alignItems': 'flex-start',
            'padding': '10px 14px', 'borderRadius': '4px',
            'borderLeft': f'3px solid {level_color}',
            'marginBottom': '6px', 'background': C['panel_light'],
        }))

    status_card = card([
        html.Div([
            html.Div([
                html.Div('CURRENT STATUS', style={
                    'fontFamily': FONT, 'fontSize': '9px', 'letterSpacing': '3px',
                    'color': C['text_dim'], 'marginBottom': '8px',
                }),
                risk_pill(risk_level),
                html.Div(f'{risk_score:.0f} / 100', style={
                    'fontFamily': FONT, 'fontSize': '36px', 'fontWeight': '700',
                    'color': level_color, 'marginTop': '8px',
                    'textShadow': f'0 0 20px {level_color}66',
                }),
                html.Div('Risk Score', style={
                    'fontFamily': FONT, 'fontSize': '10px', 'color': C['text_dim'],
                }),
            ], style={'flex': '1'}),
            html.Div([
                html.Div([
                    html.Div('30-Day Total', style={'fontFamily': FONT, 'fontSize': '9px',
                                                    'letterSpacing': '2px', 'color': C['text_dim'], 'marginBottom': '4px'}),
                    html.Div(f'{roll30:.1f} mm', style={'fontFamily': FONT, 'fontSize': '20px',
                                                         'fontWeight': '700', 'color': C['text']}),
                ], style={'marginBottom': '16px'}),
                html.Div([
                    html.Div('Historical Avg', style={'fontFamily': FONT, 'fontSize': '9px',
                                                       'letterSpacing': '2px', 'color': C['text_dim'], 'marginBottom': '4px'}),
                    html.Div(f'{hist_avg:.1f} mm', style={'fontFamily': FONT, 'fontSize': '20px',
                                                           'fontWeight': '700', 'color': C['text_dim']}),
                ]),
            ], style={'flex': '1', 'borderLeft': f'1px solid {C["border"]}', 'paddingLeft': '24px'}),
        ], style={'display': 'flex', 'gap': '24px'}),
    ], accent_color=level_color, style_override={'flex': '1'})

    actions_card = card([
        html.Div('RECOMMENDED ACTIONS — NOW', style={
            'fontFamily': FONT, 'fontSize': '9px', 'letterSpacing': '3px',
            'color': C['text_dim'], 'marginBottom': '14px',
        }),
        html.Div(action_rows),
    ], style_override={'flex': '2'})

    return html.Div([
        section_header('01  CURRENT RISK RESPONSE', 'What to do right now'),
        html.Div([status_card, actions_card],
                 style={'display': 'flex', 'gap': '16px', 'flexWrap': 'wrap'}),
    ])


# ─────────────────────────────────────────────────────────────
# SECTION 2 — Intervention Matrix
# ─────────────────────────────────────────────────────────────

def build_intervention_matrix():
    categories  = list(dict.fromkeys(i[0] for i in INTERVENTIONS))
    cat_colors  = {
        'Nature-Based':   C['LOW'],
        'Infrastructure': C['accent2'],
        'Early Warning':  C['MODERATE'],
        'Policy':         C['text_dim'],
    }

    # Scatter: cost band → effectiveness, sized by lead time
    cost_map = {'Low': 1, 'Medium': 2, 'High': 3}
    fig = go.Figure()

    for cat in categories:
        items = [i for i in INTERVENTIONS if i[0] == cat]
        x     = [cost_map[i[2]] + np.random.uniform(-0.12, 0.12) for i in items]
        y     = [i[4] for i in items]
        sizes = [i[3] * 4 + 8 for i in items]
        names = [i[1] for i in items]
        descs = [i[5] for i in items]
        leads = [i[3] for i in items]

        fig.add_trace(go.Scatter(
            x=x, y=y, mode='markers+text',
            name=cat,
            text=[n.split()[-1] for n in names],
            textposition='top center',
            textfont=dict(size=8, color=cat_colors[cat], family=FONT),
            marker=dict(
                size=sizes, color=cat_colors[cat],
                opacity=0.8, line=dict(width=1, color='rgba(255,255,255,0.2)'),
            ),
            customdata=list(zip(names, descs, leads)),
            hovertemplate=(
                '<b>%{customdata[0]}</b><br>'
                'Effectiveness: %{y}%<br>'
                'Lead time: %{customdata[2]} years<br>'
                '<i>%{customdata[1]}</i><extra></extra>'
            ),
        ))

    fig.update_layout(
        **CHART_BASE,
        title=dict(text='Intervention Matrix — Cost vs Effectiveness (bubble size = lead time)',
                   font=dict(size=12, color=C['text_dim'], family=FONT)),
        height=400,
    )
    fig.update_xaxes(tickvals=[1, 2, 3], ticktext=['Low Cost', 'Medium Cost', 'High Cost'],
                     range=[0.5, 3.5], title='Implementation Cost')
    fig.update_yaxes(title='Effectiveness (%)', range=[0, 100])

    # Intervention cards by category
    cat_cards = []
    for cat in categories:
        items = [i for i in INTERVENTIONS if i[0] == cat]
        col   = cat_colors[cat]
        rows  = []
        for item in items:
            _, name, cost, lead, eff, desc = item
            rows.append(html.Div([
                html.Div([
                    html.Div(name, style={'fontFamily': FONT2, 'fontSize': '13px',
                                          'fontWeight': '600', 'color': C['text'], 'marginBottom': '2px'}),
                    html.Div(desc, style={'fontFamily': FONT2, 'fontSize': '11px',
                                          'color': C['text_dim'], 'lineHeight': '1.4'}),
                ], style={'flex': '1'}),
                html.Div([
                    html.Div(f'{eff}%', style={'fontFamily': FONT, 'fontSize': '16px',
                                                'fontWeight': '700', 'color': col, 'textAlign': 'right'}),
                    html.Div(f'{cost} cost · {lead}yr', style={'fontFamily': FONT, 'fontSize': '9px',
                                                                 'color': C['text_dim'], 'textAlign': 'right',
                                                                 'letterSpacing': '1px'}),
                ]),
            ], style={
                'display': 'flex', 'gap': '12px', 'alignItems': 'flex-start',
                'padding': '10px 0', 'borderBottom': f'1px solid {C["border"]}',
            }))

        cat_cards.append(card([
            html.Div(cat.upper(), style={
                'fontFamily': FONT, 'fontSize': '9px', 'letterSpacing': '3px',
                'color': col, 'marginBottom': '14px', 'fontWeight': '700',
            }),
            html.Div(rows),
        ], accent_color=col, style_override={
            'flex': '1', 'minWidth': '280px',
        }))

    return html.Div([
        section_header('02  INTERVENTION STRATEGIES', 'Prevention & mitigation options for the Nore catchment'),
        html.Div([dcc.Graph(figure=fig, config={'displayModeBar': False})],
                 style={'marginBottom': '24px'}),
        html.Div(cat_cards, style={'display': 'flex', 'gap': '16px', 'flexWrap': 'wrap'}),
    ])


# ─────────────────────────────────────────────────────────────
# SECTION 3 — Cost–Benefit Timeline
# ─────────────────────────────────────────────────────────────

def build_cost_benefit():
    years = list(range(2025, 2051))

    # Scenario A: Do nothing — flood damage grows with climate
    base_damage = 8.5   # €M per year
    damage_none = [base_damage * (1.03 ** (y - 2025)) for y in years]

    # Scenario B: Nature-based only
    nbs_cost    = [2.0 if y < 2028 else 0.3 for y in years]
    nbs_damage  = [base_damage * (1.03 ** (y - 2025)) * (0.45 if y >= 2028 else 1.0) for y in years]
    nbs_net     = [d + c for d, c in zip(nbs_damage, nbs_cost)]

    # Scenario C: Full infrastructure programme
    inf_cost    = [5.0 if y < 2032 else 0.5 for y in years]
    inf_damage  = [base_damage * (1.03 ** (y - 2025)) * (0.15 if y >= 2032 else 0.85) for y in years]
    inf_net     = [d + c for d, c in zip(inf_damage, inf_cost)]

    # Scenario D: Combined (NBS + Infrastructure + Early Warning)
    com_cost    = [6.5 if y < 2030 else 0.8 for y in years]
    com_damage  = [base_damage * (1.03 ** (y - 2025)) * (0.10 if y >= 2030 else 0.7) for y in years]
    com_net     = [d + c for d, c in zip(com_damage, com_cost)]

    fig = go.Figure()

    scenarios = [
        ('Do Nothing',                  damage_none, C['HIGH'],     'dash'),
        ('Nature-Based Only',           nbs_net,     C['LOW'],      'dot'),
        ('Infrastructure Programme',    inf_net,     C['accent2'],  'dashdot'),
        ('Combined Strategy (optimal)', com_net,     C['MODERATE'], 'solid'),
    ]

    for name, data, color, dash in scenarios:
        fig.add_trace(go.Scatter(
            x=years, y=data, name=name, mode='lines',
            line=dict(color=color, width=2.5 if dash == 'solid' else 1.5, dash=dash),
            hovertemplate=f'<b>{name}</b><br>%{{x}}: €%{{y:.1f}}M<extra></extra>',
            fill='tozeroy' if dash == 'solid' else None,
            fillcolor='rgba(255,215,0,0.04)' if dash == 'solid' else None,
        ))

    # Annotations
    fig.add_annotation(x=2030, y=com_net[5],
        text='Combined strategy<br>breaks even ~2030',
        font=dict(color=C['MODERATE'], size=10, family=FONT),
        bgcolor=C['panel'], bordercolor=C['MODERATE'], borderwidth=1,
        arrowcolor=C['MODERATE'], ax=60, ay=-40)

    fig.update_layout(
        **CHART_BASE,
        title=dict(text='Projected Annual Cost (Damage + Implementation) by Scenario  ·  €M',
                   font=dict(size=12, color=C['text_dim'], family=FONT)),
        height=380,
        hovermode='x unified',
    )
    fig.update_yaxes(title='Annual Cost (€M)')

    # Summary comparison table
    final_year = 2050
    rows = []
    for name, data, color, _ in scenarios:
        total = sum(data)
        saving = sum(damage_none) - total
        rows.append(html.Div([
            html.Div(name, style={'fontFamily': FONT2, 'fontSize': '13px',
                                   'color': color, 'flex': '2', 'fontWeight': '600'}),
            html.Div(f'€{total:.0f}M', style={'fontFamily': FONT, 'fontSize': '13px',
                                               'color': C['text'], 'flex': '1', 'textAlign': 'right'}),
            html.Div(f'€{max(saving,0):.0f}M saved' if saving > 0 else '—',
                     style={'fontFamily': FONT, 'fontSize': '12px',
                             'color': C['LOW'] if saving > 0 else C['text_dim'],
                             'flex': '1', 'textAlign': 'right'}),
        ], style={
            'display': 'flex', 'padding': '10px 14px',
            'borderBottom': f'1px solid {C["border"]}',
            'background': C['panel_light'] if name == 'Combined Strategy (optimal)' else C['panel'],
        }))

    table = html.Div([
        html.Div([
            html.Div('Scenario', style={'fontFamily': FONT, 'fontSize': '9px', 'letterSpacing': '2px',
                                         'color': C['text_dim'], 'flex': '2'}),
            html.Div('Total 2025–2050', style={'fontFamily': FONT, 'fontSize': '9px', 'letterSpacing': '2px',
                                                'color': C['text_dim'], 'flex': '1', 'textAlign': 'right'}),
            html.Div('vs Do Nothing', style={'fontFamily': FONT, 'fontSize': '9px', 'letterSpacing': '2px',
                                              'color': C['text_dim'], 'flex': '1', 'textAlign': 'right'}),
        ], style={'display': 'flex', 'padding': '10px 14px',
                  'borderBottom': f'1px solid {C["border"]}'}),
        html.Div(rows),
    ], style={
        'background': C['panel'], 'border': f'1px solid {C["border"]}',
        'borderRadius': '8px', 'overflow': 'hidden', 'marginTop': '16px',
    })

    return html.Div([
        section_header('03  COST–BENEFIT ANALYSIS', '25-year scenario comparison (2025–2050)'),
        html.Div([dcc.Graph(figure=fig, config={'displayModeBar': False})]),
        table,
    ])


# ─────────────────────────────────────────────────────────────
# SECTION 4 — Implementation Roadmap
# ─────────────────────────────────────────────────────────────

def build_roadmap():
    phases = [
        {
            'phase': 'PHASE 1',
            'years': '2025 – 2026',
            'title': 'Foundation & Quick Wins',
            'color': C['LOW'],
            'items': [
                ('Q1 2025', 'Deploy real-time gauge network across Nore catchment'),
                ('Q2 2025', 'Launch community flood alert WhatsApp/app system'),
                ('Q3 2025', 'Begin riparian buffer planting along upper Nore'),
                ('Q4 2025', 'Complete flood risk zone mapping update'),
                ('Q1 2026', 'Activate 48-hour flood forecasting model'),
                ('Q2 2026', 'Establish multi-agency flood coordination group'),
            ],
        },
        {
            'phase': 'PHASE 2',
            'years': '2027 – 2029',
            'title': 'Nature-Based Solutions',
            'color': C['MODERATE'],
            'items': [
                ('2027', 'Restore 500ha of floodplain along the Nore valley'),
                ('2027', 'Create upstream wetland retention areas at key locations'),
                ('2028', 'Launch green roof grant scheme for Kilkenny city'),
                ('2028', 'Implement catchment-wide land use management plan'),
                ('2029', 'Begin large-scale reforestation of upper catchment'),
                ('2029', 'Commission independent effectiveness review'),
            ],
        },
        {
            'phase': 'PHASE 3',
            'years': '2030 – 2035',
            'title': 'Infrastructure Investment',
            'color': C['ELEVATED'],
            'items': [
                ('2030', 'Upgrade flood embankments through Kilkenny city'),
                ('2031', 'Install sustainable urban drainage in city centre'),
                ('2031', 'Upgrade undersized culverts and bridges'),
                ('2032', 'Commission upstream retention reservoir feasibility'),
                ('2033', 'Install automated pumping station network'),
                ('2035', 'Full infrastructure programme complete — review outcomes'),
            ],
        },
        {
            'phase': 'PHASE 4',
            'years': '2035 – 2050',
            'title': 'Climate Resilience',
            'color': C['HIGH'],
            'items': [
                ('2035', 'Integrate climate projections into all city planning'),
                ('2037', 'Review and adapt all measures against observed climate data'),
                ('2040', 'Second-generation nature-based solutions expansion'),
                ('2045', 'Full catchment resilience assessment'),
                ('2050', 'Net-zero flood damage target — final programme review'),
            ],
        },
    ]

    phase_cards = []
    for ph in phases:
        col = ph['color']
        items = [
            html.Div([
                html.Div(when, style={'fontFamily': FONT, 'fontSize': '9px', 'letterSpacing': '1px',
                                       'color': col, 'minWidth': '70px', 'paddingTop': '1px'}),
                html.Div(action, style={'fontFamily': FONT2, 'fontSize': '12px',
                                         'color': C['text'], 'lineHeight': '1.5', 'flex': '1'}),
            ], style={'display': 'flex', 'gap': '12px', 'marginBottom': '8px',
                      'alignItems': 'flex-start'})
            for when, action in ph['items']
        ]

        phase_cards.append(html.Div([
            html.Div([
                html.Div(ph['phase'], style={'fontFamily': FONT, 'fontSize': '9px',
                                              'letterSpacing': '3px', 'color': col, 'fontWeight': '700'}),
                html.Div(ph['years'], style={'fontFamily': FONT, 'fontSize': '12px',
                                              'color': C['text_dim'], 'marginTop': '2px'}),
            ], style={
                'background': C['panel_light'], 'padding': '12px 16px',
                'borderBottom': f'2px solid {col}', 'marginBottom': '16px',
            }),
            html.Div(ph['title'], style={
                'fontFamily': FONT2, 'fontSize': '16px', 'fontWeight': '600',
                'color': C['text'], 'marginBottom': '16px', 'padding': '0 16px',
            }),
            html.Div(items, style={'padding': '0 16px 16px'}),
        ], style={
            'background': C['panel'], 'border': f'1px solid {col}33',
            'borderRadius': '8px', 'overflow': 'hidden',
            'flex': '1', 'minWidth': '260px',
        }))

    # Gantt-style timeline chart
    gantt_data = [
        ('Real-Time Gauges',     2025.0, 2025.5, 'Early Warning'),
        ('Community Alerts',     2025.25, 2025.75, 'Early Warning'),
        ('Riparian Planting',    2025.5, 2030.0, 'Nature-Based'),
        ('Flood Risk Zoning',    2025.75, 2026.5, 'Policy'),
        ('Flood Forecasting',    2026.0, 2027.0, 'Early Warning'),
        ('Floodplain Restore',   2027.0, 2031.0, 'Nature-Based'),
        ('Wetland Creation',     2027.5, 2030.0, 'Nature-Based'),
        ('Green Roofs',          2028.0, 2032.0, 'Infrastructure'),
        ('Reforestation',        2029.0, 2045.0, 'Nature-Based'),
        ('Embankment Upgrade',   2030.0, 2033.0, 'Infrastructure'),
        ('Urban Drainage',       2031.0, 2034.0, 'Infrastructure'),
        ('Reservoir',            2032.0, 2036.0, 'Infrastructure'),
        ('Pumping Stations',     2033.0, 2035.0, 'Infrastructure'),
        ('Climate Strategy',     2035.0, 2050.0, 'Policy'),
    ]

    cat_colors_gantt = {
        'Nature-Based':  C['LOW'],
        'Infrastructure':C['accent2'],
        'Early Warning': C['MODERATE'],
        'Policy':        C['text_dim'],
    }

    fig_gantt = go.Figure()
    for i, (name, start, end, cat) in enumerate(gantt_data):
        fig_gantt.add_trace(go.Bar(
            x=[end - start], base=[start],
            y=[name], orientation='h',
            name=cat,
            showlegend=(name == gantt_data[[g[3] for g in gantt_data].index(cat)][0]),
            marker_color=cat_colors_gantt[cat],
            opacity=0.8,
            hovertemplate=f'<b>{name}</b><br>{start:.0f} → {end:.0f}<br>Category: {cat}<extra></extra>',
        ))

    fig_gantt.update_layout(
        **CHART_BASE,
        title=dict(text='Implementation Roadmap Timeline',
                   font=dict(size=12, color=C['text_dim'], family=FONT)),
        height=420,
        barmode='overlay',

        bargap=0.3,
    )
    fig_gantt.update_xaxes(title='Year', range=[2024.5, 2050.5], tickvals=list(range(2025, 2051, 5)))
    fig_gantt.update_yaxes(autorange='reversed')

    return html.Div([
        section_header('04  IMPLEMENTATION ROADMAP', '25-year phased programme for the Nore catchment'),
        html.Div([dcc.Graph(figure=fig_gantt, config={'displayModeBar': False})],
                 style={'marginBottom': '24px'}),
        html.Div(phase_cards, style={'display': 'flex', 'gap': '16px', 'flexWrap': 'wrap'}),
    ])


# ─────────────────────────────────────────────────────────────
# SECTION 5 — Catchment Facts & Key Contacts
# ─────────────────────────────────────────────────────────────

def build_facts_contacts():
    facts = html.Div([
        html.Div('CATCHMENT FACTS', style={
            'fontFamily': FONT, 'fontSize': '9px', 'letterSpacing': '3px',
            'color': C['text_dim'], 'marginBottom': '14px',
        }),
        html.Div([
            html.Div([
                html.Div(label, style={'fontFamily': FONT, 'fontSize': '9px', 'letterSpacing': '2px',
                                        'color': C['text_dim'], 'marginBottom': '3px'}),
                html.Div(value, style={'fontFamily': FONT2, 'fontSize': '13px',
                                        'color': C['text'], 'fontWeight': '600'}),
            ], style={'padding': '10px 0', 'borderBottom': f'1px solid {C["border"]}'})
            for label, value in CATCHMENT_FACTS
        ]),
    ], style={
        'background': C['panel'], 'border': f'1px solid {C["border"]}',
        'borderRadius': '8px', 'padding': '20px 24px', 'flex': '1',
    })

    contacts_data = [
        ('Office of Public Works (OPW)',  'Flood Risk Management',    'www.opw.ie/floods',        C['accent']),
        ('Met Éireann',                   'Weather & Rainfall Data',  'www.met.ie',               C['accent2']),
        ('Kilkenny Co. Council',          'Local Emergency Planning', 'www.kilkennycoco.ie',      C['LOW']),
        ('Inland Fisheries Ireland',      'River & Catchment Data',   'www.fisheriesireland.ie',  C['MODERATE']),
        ('Environmental Protection Agency','Water Quality Monitoring', 'www.epa.ie',              C['text_dim']),
        ('Irish Red Cross',               'Emergency Response',       'www.redcross.ie',          C['HIGH']),
    ]

    contacts = html.Div([
        html.Div('KEY CONTACTS & RESOURCES', style={
            'fontFamily': FONT, 'fontSize': '9px', 'letterSpacing': '3px',
            'color': C['text_dim'], 'marginBottom': '14px',
        }),
        html.Div([
            html.Div([
                html.Div([
                    html.Div(name, style={'fontFamily': FONT2, 'fontSize': '13px',
                                          'fontWeight': '600', 'color': col}),
                    html.Div(role, style={'fontFamily': FONT2, 'fontSize': '11px',
                                          'color': C['text_dim'], 'marginTop': '2px'}),
                ], style={'flex': '1'}),
                html.Div(url, style={'fontFamily': FONT, 'fontSize': '10px',
                                      'color': C['text_dim'], 'letterSpacing': '1px'}),
            ], style={
                'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center',
                'padding': '10px 0', 'borderBottom': f'1px solid {C["border"]}',
                'borderLeft': f'3px solid {col}', 'paddingLeft': '12px',
            })
            for name, role, url, col in contacts_data
        ]),
    ], style={
        'background': C['panel'], 'border': f'1px solid {C["border"]}',
        'borderRadius': '8px', 'padding': '20px 24px', 'flex': '2',
    })

    return html.Div([
        section_header('05  REFERENCE', 'Catchment facts & key organisations'),
        html.Div([facts, contacts], style={'display': 'flex', 'gap': '16px', 'flexWrap': 'wrap'}),
    ])


# ─────────────────────────────────────────────────────────────
# MAIN ENTRY POINT — called by app.py
# ─────────────────────────────────────────────────────────────

def build_prevention(d):
    """
    Build the complete Prevention & Solutions tab layout.
    d = dataframe filtered to the selected station (all dates).
    """
    return html.Div([
        # ── Hero banner ──────────────────────────────────────
        html.Div([
            html.Div('◈ FLOOD PREVENTION & SOLUTIONS', style={
                'fontFamily': FONT, 'fontSize': '10px', 'letterSpacing': '4px',
                'color': C['accent'], 'marginBottom': '8px',
            }),
            html.Div('Nore Catchment Resilience Strategy', style={
                'fontFamily': FONT2, 'fontSize': '28px', 'fontWeight': '700',
                'color': C['text'], 'marginBottom': '8px',
            }),
            html.Div(
                'Evidence-based interventions, cost-benefit analysis, and a phased '
                'implementation roadmap for reducing flood risk across the Kilkenny / '
                'Nore catchment — informed by historical rainfall data and climate projections.',
                style={'fontFamily': FONT2, 'fontSize': '14px', 'color': C['text_dim'],
                       'maxWidth': '700px', 'lineHeight': '1.6'},
            ),
        ], style={
            'padding': '32px 32px 24px',
            'background': f'linear-gradient(135deg, {C["panel"]} 0%, #0a1830 100%)',
            'borderBottom': f'1px solid {C["border"]}',
            'marginBottom': '32px',
        }),

        # ── Sections ─────────────────────────────────────────
        html.Div(build_risk_response(d),        style={'padding': '0 32px 40px'}),
        html.Div(style={'borderTop': '1px solid #1e3058', 'margin': '0 32px'}),
        html.Div(build_intervention_matrix(),   style={'padding': '40px 32px'}),
        html.Div(style={'borderTop': '1px solid #1e3058', 'margin': '0 32px'}),
        html.Div(build_cost_benefit(),          style={'padding': '40px 32px'}),
        html.Div(style={'borderTop': '1px solid #1e3058', 'margin': '0 32px'}),
        html.Div(build_roadmap(),               style={'padding': '40px 32px'}),
        html.Div(style={'borderTop': '1px solid #1e3058', 'margin': '0 32px'}),
        html.Div(build_facts_contacts(),        style={'padding': '40px 32px 60px'}),
    ])
