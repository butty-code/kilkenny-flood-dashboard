# Kilkenny Flood Risk Dashboard

A production-grade interactive flood risk dashboard built with Plotly Dash.

## Features
- Real-time risk scoring (0–100 scale)
- Rolling 7-day and 30-day rainfall totals
- Historical baseline comparison
- Climate projections with adjustable growth rates (1–8%/yr)
- Interactive 80-year prediction horizon slider
- Full data table with sort/filter

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add your real data
Edit the top of `app.py` and replace the `generate_sample_data()` call:

```python
# Replace this block in load_and_process():
df1 = pd.read_csv('kilkenny.csv',        parse_dates=['date'])
df2 = pd.read_csv('graiguenamanagh.csv', parse_dates=['date'])
df_raw = pd.concat([df1, df2])
```

Your CSV columns should be: `date, rain_mm, ind, station`

### 3. Run locally
```bash
python app.py
# Open http://localhost:8050
```

## Deploy for Free on Render.com

1. Push this folder to a GitHub repo
2. Go to render.com → New → Web Service
3. Connect your GitHub repo
4. Set:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:server --bind 0.0.0.0:$PORT`
   - Instance: Free tier
5. Click Deploy → you get a free public URL

## Deploy on Railway.app (alternative)

```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

## Structure
```
kilkenny_flood_dashboard/
├── app.py           # Main dashboard application
├── requirements.txt # Python dependencies
├── Procfile         # For Render/Railway/Heroku
└── README.md        # This file
```
