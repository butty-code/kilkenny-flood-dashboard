"""
guide.py
─────────────────────────────────────────────────────────────
Community Guide Tab — Tab 06
Readable in-app version of the booklet + download button.
Called by app.py as build_guide()
─────────────────────────────────────────────────────────────
"""

from dash import html, dcc

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
FONT  = 'IBM Plex Mono, monospace'
FONT2 = 'Space Grotesk, sans-serif'

# ── small helpers ────────────────────────────────────────────

def section_title(num, title):
    return html.Div([
        html.Span(num, style={
            'fontFamily': FONT, 'fontSize': '10px', 'letterSpacing': '3px',
            'color': C['accent'], 'marginRight': '14px', 'fontWeight': '700',
        }),
        html.Span(title, style={
            'fontFamily': FONT2, 'fontSize': '20px', 'fontWeight': '700',
            'color': C['text'],
        }),
    ], style={
        'padding': '16px 24px',
        'background': C['panel_light'],
        'borderLeft': f'4px solid {C["accent"]}',
        'borderRadius': '0 6px 6px 0',
        'marginBottom': '16px',
        'marginTop': '32px',
    })


def prose(text):
    return html.P(text, style={
        'fontFamily': FONT2, 'fontSize': '14px', 'color': C['text'],
        'lineHeight': '1.8', 'marginBottom': '12px',
    })


def tip_box(icon, label, text, color=None):
    color = color or C['accent']
    return html.Div([
        html.Div([
            html.Span(icon, style={'fontSize': '18px', 'marginRight': '10px'}),
            html.Span(label, style={
                'fontFamily': FONT, 'fontSize': '10px', 'letterSpacing': '2px',
                'fontWeight': '700', 'color': color,
            }),
        ], style={'marginBottom': '6px'}),
        html.Div(text, style={
            'fontFamily': FONT2, 'fontSize': '13px', 'color': C['text'],
            'lineHeight': '1.7',
        }),
    ], style={
        'background': C['panel_light'],
        'borderLeft': f'4px solid {color}',
        'borderRadius': '0 6px 6px 0',
        'padding': '14px 20px',
        'marginBottom': '14px',
    })


def risk_row(level, score, text):
    colors = {
        'LOW':      C['LOW'],
        'MODERATE': C['MODERATE'],
        'ELEVATED': C['ELEVATED'],
        'HIGH':     C['HIGH'],
    }
    col = colors.get(level, C['text_dim'])
    return html.Div([
        html.Div([
            html.Div(level, style={
                'fontFamily': FONT, 'fontSize': '11px', 'letterSpacing': '2px',
                'fontWeight': '700', 'color': col,
            }),
            html.Div(score, style={
                'fontFamily': FONT, 'fontSize': '10px', 'color': C['text_dim'],
            }),
        ], style={'minWidth': '120px'}),
        html.Div(text, style={
            'fontFamily': FONT2, 'fontSize': '13px', 'color': C['text'],
            'lineHeight': '1.6', 'flex': '1',
        }),
    ], style={
        'display': 'flex', 'alignItems': 'flex-start', 'gap': '20px',
        'padding': '12px 16px',
        'borderLeft': f'3px solid {col}',
        'background': C['panel'],
        'borderRadius': '0 6px 6px 0',
        'marginBottom': '8px',
    })


def bul(text, color=None):
    return html.Div([
        html.Span('▸ ', style={
            'color': color or C['accent'], 'fontFamily': FONT,
            'fontSize': '12px', 'marginRight': '8px',
        }),
        html.Span(text, style={
            'fontFamily': FONT2, 'fontSize': '13px', 'color': C['text'],
            'lineHeight': '1.6',
        }),
    ], style={'marginBottom': '6px', 'paddingLeft': '8px'})


def two_col(left_items, right_items):
    return html.Div([
        html.Div(left_items,  style={'flex': '1', 'minWidth': '240px'}),
        html.Div(right_items, style={'flex': '1', 'minWidth': '240px'}),
    ], style={'display': 'flex', 'gap': '24px', 'flexWrap': 'wrap'})


def info_table(headers, rows, col_flex=None):
    col_flex = col_flex or ['1'] * len(headers)
    hdr = html.Div([
        html.Div(h, style={
            'flex': col_flex[i], 'fontFamily': FONT, 'fontSize': '9px',
            'letterSpacing': '2px', 'color': C['text_dim'], 'fontWeight': '700',
            'padding': '8px 12px',
        }) for i, h in enumerate(headers)
    ], style={
        'display': 'flex', 'background': C['panel_light'],
        'borderBottom': f'1px solid {C["border"]}',
    })
    data_rows = [
        html.Div([
            html.Div(cell, style={
                'flex': col_flex[j], 'fontFamily': FONT2, 'fontSize': '12px',
                'color': C['text'], 'padding': '8px 12px', 'lineHeight': '1.5',
            }) for j, cell in enumerate(row)
        ], style={
            'display': 'flex',
            'background': C['panel'] if i % 2 == 0 else C['panel_light'],
            'borderBottom': f'1px solid {C["border"]}',
        })
        for i, row in enumerate(rows)
    ]
    return html.Div([hdr] + data_rows, style={
        'border': f'1px solid {C["border"]}',
        'borderRadius': '6px',
        'overflow': 'hidden',
        'marginBottom': '16px',
    })


# ── Download banner ───────────────────────────────────────────

def download_banner():
    return html.Div([
        html.Div([
            html.Div('📄', style={'fontSize': '32px', 'marginBottom': '8px'}),
            html.Div('COMMUNITY GUIDE BOOKLET', style={
                'fontFamily': FONT, 'fontSize': '11px', 'letterSpacing': '4px',
                'color': C['accent'], 'marginBottom': '6px',
            }),
            html.Div('Kilkenny Flood Risk — Plain Language Edition', style={
                'fontFamily': FONT2, 'fontSize': '20px', 'fontWeight': '700',
                'color': C['text'], 'marginBottom': '8px',
            }),
            html.Div(
                '17 sections · Plain English · Print-ready · For residents, farmers & businesses',
                style={'fontFamily': FONT2, 'fontSize': '13px', 'color': C['text_dim'], 'marginBottom': '20px'},
            ),
            html.A(
                '⬇  Download Full Booklet (.docx)',
                href='/assets/Kilkenny_Flood_Risk_Community_Guide.docx',
                download='Kilkenny_Flood_Risk_Community_Guide.docx',
                style={
                    'display': 'inline-block',
                    'background': C['accent'],
                    'color': '#000',
                    'fontFamily': FONT,
                    'fontSize': '12px',
                    'fontWeight': '700',
                    'letterSpacing': '2px',
                    'padding': '12px 32px',
                    'borderRadius': '4px',
                    'textDecoration': 'none',
                    'boxShadow': f'0 0 24px {C["accent"]}44',
                    'transition': 'all 0.2s',
                },
            ),
            html.Div('Opens in Microsoft Word, LibreOffice, or Google Docs', style={
                'fontFamily': FONT, 'fontSize': '10px', 'color': C['text_dim'],
                'marginTop': '10px', 'letterSpacing': '1px',
            }),
        ], style={'textAlign': 'center', 'maxWidth': '600px', 'margin': '0 auto'}),
    ], style={
        'background': f'linear-gradient(135deg, {C["panel"]} 0%, #0a1830 100%)',
        'border': f'1px solid {C["accent"]}33',
        'borderRadius': '8px',
        'padding': '40px 32px',
        'marginBottom': '32px',
        'textAlign': 'center',
    })


# ── Guide content ─────────────────────────────────────────────

def build_guide():
    return html.Div([

        # ── Hero ────────────────────────────────────────────
        html.Div([
            html.Div('◈  COMMUNITY GUIDE & HELP', style={
                'fontFamily': FONT, 'fontSize': '10px', 'letterSpacing': '4px',
                'color': C['accent'], 'marginBottom': '8px',
            }),
            html.Div('Everything you need to know about flood risk in Kilkenny', style={
                'fontFamily': FONT2, 'fontSize': '26px', 'fontWeight': '700',
                'color': C['text'], 'marginBottom': '8px',
            }),
            html.Div(
                'Plain language. No jargon. For everyone in the Nore valley community.',
                style={'fontFamily': FONT2, 'fontSize': '14px', 'color': C['text_dim'],
                       'lineHeight': '1.6'},
            ),
        ], style={
            'padding': '32px 32px 24px',
            'background': f'linear-gradient(135deg, {C["panel"]} 0%, #0a1830 100%)',
            'borderBottom': f'1px solid {C["border"]}',
            'marginBottom': '32px',
        }),

        html.Div([

            # ── Download banner ──────────────────────────────
            download_banner(),

            # ── Quick navigation chips ───────────────────────
            html.Div([
                html.Div('JUMP TO SECTION', style={
                    'fontFamily': FONT, 'fontSize': '9px', 'letterSpacing': '3px',
                    'color': C['text_dim'], 'marginBottom': '12px',
                }),
                html.Div([
                    html.A(label, href=f'#{anchor}', style={
                        'fontFamily': FONT, 'fontSize': '10px', 'letterSpacing': '1px',
                        'color': C['accent'], 'textDecoration': 'none',
                        'border': f'1px solid {C["border"]}',
                        'borderRadius': '4px', 'padding': '6px 14px',
                        'background': C['panel'],
                        'marginRight': '8px', 'marginBottom': '8px',
                        'display': 'inline-block',
                    })
                    for label, anchor in [
                        ('What is a flood?', 'what-is-flood'),
                        ('Risk levels', 'risk-levels'),
                        ('What to do', 'what-to-do'),
                        ('Early warning', 'early-warning'),
                        ('After a flood', 'after-flood'),
                        ('Nature solutions', 'nature'),
                        ('The 25yr plan', 'plan'),
                        ('Contacts', 'contacts'),
                        ('FAQ', 'faq'),
                        ('Glossary', 'glossary'),
                    ]
                ], style={'flexWrap': 'wrap', 'display': 'flex'}),
            ], style={
                'background': C['panel'], 'border': f'1px solid {C["border"]}',
                'borderRadius': '8px', 'padding': '20px 24px', 'marginBottom': '32px',
            }),

            # ══════════════════════════════════════════════════
            # SECTION 1 — What is a flood
            # ══════════════════════════════════════════════════
            html.Div(id='what-is-flood'),
            section_title('01', 'What is a Flood?'),
            prose('A flood is simply too much water in the wrong place at the wrong time. It happens when rain falls faster than the ground can soak it up, or when a river fills beyond its banks.'),
            html.Div([
                html.Div([
                    html.Div('RIVER FLOOD', style={'fontFamily': FONT, 'fontSize': '10px',
                        'letterSpacing': '2px', 'color': C['accent'], 'marginBottom': '6px'}),
                    prose('The Nore rises and spills over its banks. Usually follows several days of heavy rain. Warning time: hours to days.'),
                ], style={'background': C['panel'], 'border': f'1px solid {C["border"]}',
                          'borderRadius': '6px', 'padding': '16px 20px', 'flex': '1', 'minWidth': '220px'}),
                html.Div([
                    html.Div('SURFACE WATER FLOOD', style={'fontFamily': FONT, 'fontSize': '10px',
                        'letterSpacing': '2px', 'color': C['ELEVATED'], 'marginBottom': '6px'}),
                    prose('Rain falls so fast the drains cannot cope. Water runs along streets into buildings. Warning time: minutes.'),
                ], style={'background': C['panel'], 'border': f'1px solid {C["border"]}',
                          'borderRadius': '6px', 'padding': '16px 20px', 'flex': '1', 'minWidth': '220px'}),
            ], style={'display': 'flex', 'gap': '16px', 'flexWrap': 'wrap', 'marginBottom': '16px'}),
            tip_box('💧', 'KEY FACT',
                'The River Nore drains ~2,460 km² — roughly the size of County Clare. Every drop '
                'of rain across that entire area eventually passes through Kilkenny city.'),

            # ══════════════════════════════════════════════════
            # SECTION 2 — Risk levels
            # ══════════════════════════════════════════════════
            html.Div(id='risk-levels'),
            section_title('02', 'The Four Risk Levels — What They Mean For You'),
            prose('Our dashboard scores flood risk from 0 to 100 by comparing current 30-day rainfall to the long-term historical average. Here is what each level means for your daily life:'),
            risk_row('LOW',      'Score below 15', 'Normal conditions. Carry on as usual. Good time to check gutters and drains.'),
            risk_row('MODERATE', 'Score 15–39',    'Wetter than usual. Move valuables upstairs. Check forecasts more often. Farmers: check livestock in low fields.'),
            risk_row('ELEVATED', 'Score 40–70',    'Significantly above normal. Risk of flooding to low-lying areas. Get flood barriers ready. Alert vulnerable neighbours. Move vehicles to higher ground.'),
            risk_row('HIGH',     'Score above 70', 'Flooding is likely or already happening. Follow all official instructions. Turn off electricity at the fuse board. Move to upper floors. Call 999 if in danger.'),
            tip_box('⚠️', 'NEVER IGNORE',
                'A HIGH risk score combined with heavy forecast rain means act NOW, not in an hour. '
                'The difference between acting at 6pm and 8pm can be everything.',
                C['HIGH']),

            # ══════════════════════════════════════════════════
            # SECTION 3 — What to do
            # ══════════════════════════════════════════════════
            html.Div(id='what-to-do'),
            section_title('03', 'What to Do — Step by Step'),
            prose('Print this section and keep it on your fridge. When a warning comes, you will not have to think.'),
            info_table(
                ['When', 'Action'],
                [
                    ['Score rises above 15 / Yellow warning',  'Check forecasts. Clear gutters. Move outdoor furniture. Warn vulnerable neighbours.'],
                    ['Score above 40 / Orange warning',        'Move vehicles to high ground. Move valuables upstairs. Prepare flood barriers. Charge all devices. Alert elderly relatives.'],
                    ['Score above 70 / Red warning',           'Deploy barriers. Turn off electricity at fuse board. Turn off gas. Move to upper floors. Do NOT drive. Call 999 if needed.'],
                    ['During flooding',                        'Stay upstairs. Do not re-enter flooded rooms. Do not walk through flood water — it contains sewage.'],
                ],
                ['1', '2'],
            ),
            html.Div([
                html.Div('YOUR EMERGENCY BAG — keep it packed', style={
                    'fontFamily': FONT, 'fontSize': '10px', 'letterSpacing': '2px',
                    'color': C['MODERATE'], 'marginBottom': '12px',
                }),
                two_col(
                    [bul('Passports, insurance documents', C['accent']),
                     bul('Phone charger + power bank',    C['accent']),
                     bul('3 days of medications',         C['accent']),
                     bul('Warm clothes and waterproofs',  C['accent']),
                     bul('Torch and batteries',           C['accent']),
                     bul('Cash (ATMs may not work)',       C['accent'])],
                    [bul('First aid kit'),
                     bul('Bottled water — 3 days supply'),
                     bul('Non-perishable food'),
                     bul('Baby / pet supplies if needed'),
                     bul('Battery-powered radio'),
                     bul('Waterproof bag for documents')],
                ),
            ], style={
                'background': C['panel'], 'border': f'1px solid {C["MODERATE"]}44',
                'borderRadius': '6px', 'padding': '20px 24px', 'marginBottom': '16px',
            }),

            # ══════════════════════════════════════════════════
            # SECTION 4 — Early Warning
            # ══════════════════════════════════════════════════
            html.Div(id='early-warning'),
            section_title('04', 'Early Warning — How to Get Alerts'),
            prose('The most valuable thing in a flood is time. Sign up for these free alerts today — takes 10 minutes.'),
            info_table(
                ['Source', 'What it tells you', 'How to sign up'],
                [
                    ['Met Éireann',         'Weather warnings — Yellow, Orange, Red',          'met.ie → Warnings → Email alerts'],
                    ['OPW Flood Info',      'River levels, flood warnings, flood maps',         'floodinfo.ie → Register → River Nore'],
                    ['Kilkenny Co. Council','Local alerts, road closures, emergency contacts',  '056 779 4000  |  kilkennycoco.ie'],
                    ['This Dashboard',      'Rainfall risk score — 7 and 30 day totals',       'Bookmark this page and check it daily'],
                ],
                ['1', '2', '2'],
            ),
            tip_box('📱', 'SET UP IN 10 MINUTES',
                '1. met.ie → sign up for text/email alerts  '
                '2. floodinfo.ie → register for River Nore alerts  '
                '3. Save 056 779 4000 in your phone as "Flood Emergency"  '
                '4. Save 999 and 112  '
                '5. Join your local community WhatsApp alert group'),

            # ══════════════════════════════════════════════════
            # SECTION 5 — After a flood
            # ══════════════════════════════════════════════════
            html.Div(id='after-flood'),
            section_title('05', 'After a Flood — Recovery'),
            prose('Recovering from a flood takes time. Knowing what to do first saves money and protects your health.'),
            two_col(
                [
                    html.Div('FIRST 24 HOURS', style={'fontFamily': FONT, 'fontSize': '10px',
                        'letterSpacing': '2px', 'color': C['HIGH'], 'marginBottom': '10px'}),
                    bul('Do NOT re-enter until emergency services say it is safe', C['HIGH']),
                    bul('Do NOT turn electricity on — get an electrician first',  C['HIGH']),
                    bul('Wear rubber boots and gloves — water contains sewage',   C['HIGH']),
                    bul('Photograph everything before cleaning — needed for insurance'),
                    bul('Contact your insurer immediately'),
                ],
                [
                    html.Div('FINANCIAL SUPPORT', style={'fontFamily': FONT, 'fontSize': '10px',
                        'letterSpacing': '2px', 'color': C['LOW'], 'marginBottom': '10px'}),
                    bul('Contact your home insurer — log claim reference',             C['LOW']),
                    bul('Kilkenny Co. Council — Humanitarian Assistance Scheme',       C['LOW']),
                    bul('Dept. Social Protection — emergency payments available',      C['LOW']),
                    bul('Keep ALL receipts for emergency spending',                    C['LOW']),
                    bul('St. Vincent de Paul — 01 884 8200 — immediate practical help',C['LOW']),
                ],
            ),
            tip_box('🧠', 'MENTAL HEALTH',
                'Flooding is not just a physical event. Stress, disruption and financial burden '
                'take a real toll. Talk to your GP. Contact Samaritans anytime: 116 123 (free, 24/7).'),

            # ══════════════════════════════════════════════════
            # SECTION 6 — Nature-Based Solutions
            # ══════════════════════════════════════════════════
            html.Div(id='nature'),
            section_title('06', 'Nature-Based Solutions — Working With the River'),
            prose('The cheapest and most long-lasting flood solutions often work with nature rather than against it. A mature oak tree intercepts around 100,000 litres of rainfall per year. Ten thousand trees intercept 1 billion litres — equivalent to a medium reservoir, at a fraction of the cost.'),
            info_table(
                ['Solution', 'How it works', 'Effectiveness'],
                [
                    ['Floodplain restoration', 'Allow the river to spread onto natural floodplain in rural areas. Stores water before it reaches the city.', 'Reduces peak flow by up to 30%'],
                    ['Tree planting',           'Trees intercept rainfall, slow runoff, and roots break up compacted soil.', '5–10% flow reduction per 10% forest cover'],
                    ['Wetland creation',        '1 hectare stores 1,000–2,000 m³ of water. Natural sponge effect.',         'Very high — low cost per €1 spent'],
                    ['Leaky dams',              'Small wooden structures in upland streams slow flow and hold back water.',  'Effective in upper catchment areas'],
                    ['Hedgerow restoration',    'Slows surface runoff across fields, increases infiltration.',               'Moderate — best combined with others'],
                ],
                ['1', '2', '1'],
            ),

            # ══════════════════════════════════════════════════
            # SECTION 7 — The 25-year plan
            # ══════════════════════════════════════════════════
            html.Div(id='plan'),
            section_title('07', 'The 25-Year Plan — What Happens When'),
            prose('Prevention is a long-term commitment. Here is the phased approach recommended for the Nore catchment:'),
            html.Div([
                html.Div([
                    html.Div([
                        html.Div(phase, style={'fontFamily': FONT, 'fontSize': '9px',
                            'letterSpacing': '2px', 'color': color, 'marginBottom': '4px'}),
                        html.Div(years, style={'fontFamily': FONT2, 'fontSize': '15px',
                            'fontWeight': '700', 'color': C['text'], 'marginBottom': '8px'}),
                        html.Div(title, style={'fontFamily': FONT2, 'fontSize': '12px',
                            'color': C['text_dim'], 'marginBottom': '10px'}),
                        html.Div([bul(a, color) for a in actions]),
                    ], style={
                        'background': C['panel'],
                        'border': f'1px solid {color}44',
                        'borderTop': f'3px solid {color}',
                        'borderRadius': '6px', 'padding': '16px 20px',
                        'flex': '1', 'minWidth': '220px',
                    }),
                ])
                for phase, years, title, color, actions in [
                    ('PHASE 1', '2025–2026', 'Quick wins & foundations', C['LOW'], [
                        'Expand real-time gauge network',
                        'Launch community flood alert system',
                        'Begin riparian buffer planting',
                        'Multi-agency coordination group',
                    ]),
                    ('PHASE 2', '2027–2029', 'Nature-based solutions', C['MODERATE'], [
                        'Restore 500ha of Nore floodplain',
                        'Create upstream wetland areas',
                        'Green roof grant scheme',
                        'Catchment land use plan',
                    ]),
                    ('PHASE 3', '2030–2035', 'Infrastructure investment', C['ELEVATED'], [
                        'Upgrade flood embankments in city',
                        'Sustainable urban drainage',
                        'Culvert and bridge upgrades',
                        'Retention reservoir',
                    ]),
                    ('PHASE 4', '2035–2050', 'Climate resilience', C['HIGH'], [
                        'Climate projections in all planning',
                        'Review all measures vs. observed data',
                        'Second-generation NBS expansion',
                        'Full catchment resilience assessment',
                    ]),
                ]
            ], style={'display': 'flex', 'gap': '12px', 'flexWrap': 'wrap', 'marginBottom': '16px'}),
            tip_box('⏰', 'WHY START NOW',
                'Trees planted today take 20 years to reach full effectiveness. '
                'Wetlands take 5–10 years to establish. The benefits of starting now '
                'will be felt by the next generation. The time to act is today.'),

            # ══════════════════════════════════════════════════
            # SECTION 8 — Contacts
            # ══════════════════════════════════════════════════
            html.Div(id='contacts'),
            section_title('08', 'Key Contacts'),
            info_table(
                ['Organisation', 'Role', 'Contact'],
                [
                    ['Office of Public Works (OPW)', 'National flood risk management. Funds major flood schemes.',    'opw.ie/floods  |  1890 213 414'],
                    ['Met Éireann',                  'Weather warnings and rainfall data.',                           'met.ie  |  01 806 4200'],
                    ['Kilkenny County Council',      'Local flood response, roads, planning, minor works.',           'kilkennycoco.ie  |  056 779 4000'],
                    ['EPA',                          'Water quality monitoring.',                                     'epa.ie  |  053 916 0600'],
                    ['Inland Fisheries Ireland',     'River health and catchment management.',                        'fisheriesireland.ie  |  1890 34 74 24'],
                    ['Teagasc',                      'Farm land management advice and agri-environment schemes.',     'teagasc.ie  |  052 617 8100'],
                    ['Irish Red Cross',              'Humanitarian support after floods.',                            'redcross.ie  |  01 642 4600'],
                    ['Emergency Services',           'Fire, Garda, Ambulance — if in immediate danger.',             '999 or 112'],
                    ['Samaritans',                   'Emotional support — 24 hours, 7 days.',                        '116 123 (free)'],
                ],
                ['1', '2', '1'],
            ),

            # ══════════════════════════════════════════════════
            # SECTION 9 — FAQ
            # ══════════════════════════════════════════════════
            html.Div(id='faq'),
            section_title('09', 'Frequently Asked Questions'),
            html.Div([
                html.Div([
                    html.Div(q, style={'fontFamily': FONT2, 'fontSize': '14px',
                        'fontWeight': '700', 'color': C['accent'], 'marginBottom': '6px'}),
                    html.Div(a, style={'fontFamily': FONT2, 'fontSize': '13px',
                        'color': C['text'], 'lineHeight': '1.7'}),
                ], style={
                    'background': C['panel'],
                    'borderLeft': f'3px solid {C["border"]}',
                    'borderRadius': '0 6px 6px 0',
                    'padding': '16px 20px', 'marginBottom': '10px',
                })
                for q, a in [
                    ('My house never flooded before. Why am I at risk now?',
                     'Flood risk is not fixed. Climate change is expanding the areas at risk. What was a 1-in-50-year event is becoming a 1-in-20-year event. Check floodinfo.ie for current flood maps for your address.'),
                    ('Can I get flood insurance if I live in a risk area?',
                     'Insurers in Ireland cannot refuse flood cover to existing policyholders who previously had it (under the Insurance Ireland agreement). If refused, contact the Insurance Ireland Ombudsman.'),
                    ('How accurate is the dashboard risk score?',
                     'The score shows how unusual current rainfall conditions are compared to 60+ years of history. It is a planning and awareness tool — not a replacement for official OPW and Met Éireann warnings. Always follow those for real-time guidance.'),
                    ('Will building a flood wall solve the problem?',
                     'Walls protect up to a certain level but can worsen flooding downstream. The most effective approach combines targeted defences with upstream nature-based measures that reduce the total volume of water reaching the city.'),
                    ('I am a farmer — will this affect my land?',
                     'Some measures like floodplain restoration may temporarily involve land you own. Farmers are compensated under the OPW and ACRES schemes. Flood-tolerant practices are often more profitable long-term than draining marginal land.'),
                    ('Is prevention really worth the cost?',
                     'Every €1 spent on flood prevention saves approximately €5–€8 in flood damage costs. The combined prevention strategy costs less over 25 years than doing nothing, even before counting the non-financial benefits to people\'s lives.'),
                ]
            ]),

            # ══════════════════════════════════════════════════
            # SECTION 10 — Glossary
            # ══════════════════════════════════════════════════
            html.Div(id='glossary'),
            section_title('10', 'Glossary — Plain English Definitions'),
            html.Div([
                html.Div([
                    html.Div(term, style={'fontFamily': FONT, 'fontSize': '11px',
                        'letterSpacing': '1px', 'color': C['accent'],
                        'fontWeight': '700', 'minWidth': '180px'}),
                    html.Div(defn, style={'fontFamily': FONT2, 'fontSize': '13px',
                        'color': C['text'], 'lineHeight': '1.6', 'flex': '1'}),
                ], style={
                    'display': 'flex', 'gap': '20px', 'alignItems': 'flex-start',
                    'padding': '10px 14px',
                    'background': C['panel'] if i % 2 == 0 else C['panel_light'],
                    'borderBottom': f'1px solid {C["border"]}',
                })
                for i, (term, defn) in enumerate([
                    ('Catchment',           'All the land that drains into one river. The Nore catchment is ~2,460 km².'),
                    ('Flood risk score',    'Our 0–100 measure of how unusual current rainfall is compared to the 60-year average.'),
                    ('Floodplain',          'The flat land beside a river that naturally floods. Rivers need their floodplains — removing them makes flooding worse.'),
                    ('Infiltration',        'Water soaking into the ground. Clay soils have low infiltration — water runs off instead.'),
                    ('Nature-Based Solutions','Using natural processes — trees, wetlands, restored rivers — to reduce flood risk.'),
                    ('OPW',                 'Office of Public Works — the Irish government body responsible for national flood management.'),
                    ('Peak flow',           'The highest point river flow reaches during a flood. Defences are designed for a specific peak flow.'),
                    ('Return period',       'A 1-in-100-year flood has a 1% chance of occurring any given year — not that it happens once per century.'),
                    ('Rolling total',       'The total rainfall over the last 7 or 30 days, updated every day.'),
                    ('Run-off',             'Water flowing along the surface rather than soaking in. Hard surfaces and saturated soil increase run-off.'),
                    ('Saturation',          'When soil is full of water and any further rain runs straight into the river.'),
                    ('SuDS',                'Sustainable Urban Drainage Systems — permeable paving, rain gardens, swales that manage water naturally.'),
                    ('Tributary',           'A smaller river flowing into a larger one. The Nore has many — the Kings River, Dinin, Erkina and more.'),
                    ('Wetland',             'Permanently or seasonally waterlogged land. Acts as a natural sponge, absorbing large volumes during floods.'),
                ])
            ], style={
                'border': f'1px solid {C["border"]}',
                'borderRadius': '6px', 'overflow': 'hidden', 'marginBottom': '32px',
            }),

            # ── Footer ───────────────────────────────────────
            html.Div([
                html.Div('◈  KILKENNY FLOOD RISK DASHBOARD', style={
                    'fontFamily': FONT, 'fontSize': '10px', 'letterSpacing': '3px',
                    'color': C['accent'], 'marginBottom': '8px',
                }),
                html.Div(
                    'Built using 60+ years of daily rainfall data from Met Éireann stations at '
                    'Lavistown House (Kilkenny, since 1962) and Ballyogan House (Graiguenamanagh, since 2001).',
                    style={'fontFamily': FONT2, 'fontSize': '12px', 'color': C['text_dim'],
                           'lineHeight': '1.6', 'maxWidth': '600px', 'margin': '0 auto 8px'},
                ),
                html.Div(
                    'For official flood warnings always consult floodinfo.ie and met.ie',
                    style={'fontFamily': FONT2, 'fontSize': '11px', 'color': C['text_dim'],
                           'fontStyle': 'italic'},
                ),
                # Second download button at bottom
                html.Div([
                    html.A('⬇  Download Community Booklet (.docx)',
                        href='/assets/Kilkenny_Flood_Risk_Community_Guide.docx',
                        download='Kilkenny_Flood_Risk_Community_Guide.docx',
                        style={
                            'display': 'inline-block', 'marginTop': '20px',
                            'background': 'transparent',
                            'color': C['accent'],
                            'fontFamily': FONT, 'fontSize': '11px',
                            'letterSpacing': '2px', 'fontWeight': '700',
                            'padding': '10px 24px', 'borderRadius': '4px',
                            'textDecoration': 'none',
                            'border': f'1px solid {C["accent"]}',
                        },
                    ),
                ]),
            ], style={
                'textAlign': 'center',
                'borderTop': f'1px solid {C["border"]}',
                'padding': '32px',
                'marginTop': '16px',
            }),

        ], style={'padding': '0 32px 32px'}),
    ])
