# Nassau Candy Distributor — Shipping Route Efficiency Dashboard

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Make sure app.py and Nassau_Candy_Distributor.csv are in the same folder

# 3. Run the dashboard
streamlit run app.py
```

The dashboard will open at: http://localhost:8501

## Project Structure
- `app.py` — Main Streamlit dashboard (all 5 modules)
- `Nassau_Candy_Distributor.csv` — Dataset
- `requirements.txt` — Python dependencies

## Dashboard Modules
1. **Route Efficiency** — Leaderboard, top/bottom 10 routes, lead time distributions
2. **Geographic Map** — US scatter-geo maps for lead time and delay rate + factory pins
3. **Ship Mode Analysis** — Violin plots, heatmaps, cross-analysis
4. **Route Drill-Down** — State-level deep dive with order log
5. **Executive Summary** — KPIs, insights, monthly trend, recommendations

## Sidebar Filters
- Date range selector
- Region, Ship Mode, Factory dropdowns
- Lead-time delay threshold slider

deployed address: https://4vcnwmhsyz25sambda5xvr.streamlit.app/
