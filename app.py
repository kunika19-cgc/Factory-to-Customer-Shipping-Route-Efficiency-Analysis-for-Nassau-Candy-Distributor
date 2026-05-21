import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Nassau Candy | Shipping Intelligence",
    page_icon="🍬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .metric-card {
        background: linear-gradient(135deg, #1e2130 0%, #252a3a 100%);
        border: 1px solid #2d3250; border-radius: 16px;
        padding: 18px 20px; text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .metric-value { font-size: 1.9rem; font-weight: 700; color: #a78bfa; line-height:1; margin: 4px 0; }
    .metric-label { font-size: 0.72rem; color: #8892b0; text-transform: uppercase; letter-spacing: 1px; font-weight: 500; }
    .section-header {
        font-size: 1.05rem; font-weight: 600; color: #e2e8f0;
        border-left: 4px solid #7c3aed; padding-left: 12px; margin: 20px 0 14px 0;
    }
    .insight-box {
        background: linear-gradient(135deg, #1a1f35 0%, #1e2540 100%);
        border: 1px solid #2d3a6b; border-radius: 12px;
        padding: 14px 18px; margin: 8px 0;
        font-size: 0.88rem; color: #c8d0e7; line-height: 1.65;
    }
    div[data-testid="stSidebar"] { background: #141824; border-right: 1px solid #2d3250; }
    .stTabs [data-baseweb="tab-list"] { background: #1a1f2e; border-radius: 12px; padding: 4px; gap: 4px; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px; color: #8892b0 !important; font-weight: 500; font-size: 0.85rem; }
    .stTabs [aria-selected="true"] { background: #7c3aed !important; color: #fff !important; }
    h1, h2, h3 { color: #e2e8f0 !important; }
    p { color: #c8d0e7; }
</style>
""", unsafe_allow_html=True)

# ── Constants ────────────────────────────────────────────────────────────────
FACTORIES = {
    "Lot's O' Nuts":     (32.881893, -111.768036),
    "Wicked Choccy's":  (32.076176, -81.088371),
    "Sugar Shack":       (48.11914,  -96.18115),
    "Secret Factory":    (41.446333, -90.565487),
    "The Other Factory": (35.1175,   -89.971107),
}
PRODUCT_FACTORY = {
    "Wonka Bar - Nutty Crunch Surprise":  "Lot's O' Nuts",
    "Wonka Bar - Fudge Mallows":          "Lot's O' Nuts",
    "Wonka Bar -Scrumdiddlyumptious":     "Lot's O' Nuts",
    "Wonka Bar - Milk Chocolate":         "Wicked Choccy's",
    "Wonka Bar - Triple Dazzle Caramel":  "Wicked Choccy's",
    "Laffy Taffy":                        "Sugar Shack",
    "SweeTARTS":                          "Sugar Shack",
    "Nerds":                              "Sugar Shack",
    "Fun Dip":                            "Sugar Shack",
    "Fizzy Lifting Drinks":               "Sugar Shack",
    "Everlasting Gobstopper":             "Secret Factory",
    "Hair Toffee":                        "The Other Factory",
    "Lickable Wallpaper":                 "Secret Factory",
    "Wonka Gum":                          "Secret Factory",
    "Kazookles":                          "The Other Factory",
}
STATE_COORDS = {
    'Alabama':(32.8,-86.8),'Alaska':(61.4,-152.0),'Arizona':(33.7,-111.4),'Arkansas':(34.8,-92.2),
    'California':(36.8,-119.4),'Colorado':(39.1,-105.4),'Connecticut':(41.6,-72.7),'Delaware':(39.0,-75.5),
    'Florida':(27.7,-81.5),'Georgia':(32.9,-83.4),'Hawaii':(20.8,-156.3),'Idaho':(44.5,-114.0),
    'Illinois':(40.3,-89.0),'Indiana':(40.0,-86.1),'Iowa':(42.1,-93.5),'Kansas':(38.5,-98.4),
    'Kentucky':(37.6,-84.7),'Louisiana':(31.2,-91.8),'Maine':(44.7,-69.4),'Maryland':(39.0,-76.8),
    'Massachusetts':(42.3,-71.8),'Michigan':(44.3,-85.4),'Minnesota':(46.4,-93.9),'Mississippi':(32.7,-89.7),
    'Missouri':(38.5,-92.5),'Montana':(47.0,-109.6),'Nebraska':(41.5,-99.9),'Nevada':(39.3,-116.6),
    'New Hampshire':(43.5,-71.6),'New Jersey':(40.1,-74.5),'New Mexico':(34.8,-106.2),'New York':(42.2,-74.9),
    'North Carolina':(35.6,-79.8),'North Dakota':(47.5,-100.5),'Ohio':(40.4,-82.8),'Oklahoma':(35.6,-97.5),
    'Oregon':(44.1,-120.5),'Pennsylvania':(40.9,-77.8),'Rhode Island':(41.7,-71.5),'South Carolina':(33.9,-80.9),
    'South Dakota':(44.4,-100.2),'Tennessee':(35.9,-86.7),'Texas':(31.5,-99.3),'Utah':(39.4,-111.5),
    'Vermont':(44.1,-72.7),'Virginia':(37.8,-78.2),'Washington':(47.4,-120.5),'West Virginia':(38.5,-80.6),
    'Wisconsin':(44.3,-89.8),'Wyoming':(43.0,-107.6),'District of Columbia':(38.9,-77.0),
}

PLOT_BG = dict(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
               font=dict(color='#c8d0e7'), margin=dict(l=0,r=0,t=40,b=0))

@st.cache_data
def load_data():
    df = pd.read_csv("Nassau_Candy_Distributor.csv")
    df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True, errors='coerce')
    df['Ship Date']  = pd.to_datetime(df['Ship Date'],  dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Order Date','Ship Date'])
    df['Lead Time'] = (df['Ship Date'] - df['Order Date']).dt.days
    df = df[df['Lead Time'] >= 0]
    df['Factory'] = df['Product Name'].map(PRODUCT_FACTORY)
    df['Route']   = df['Factory'] + " → " + df['State/Province']
    df['Month']   = df['Order Date'].dt.to_period('M').astype(str)
    df['Year']    = df['Order Date'].dt.year
    return df

df_full = load_data()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🍬 Nassau Candy")
    st.markdown("**Shipping Intelligence**")
    st.markdown("---")
    st.markdown("#### 📅 Date Range")
    min_d = df_full['Order Date'].min().date()
    max_d = df_full['Order Date'].max().date()
    date_range = st.date_input("", value=(min_d, max_d), min_value=min_d, max_value=max_d)
    d_start = pd.Timestamp(date_range[0]) if len(date_range)==2 else pd.Timestamp(min_d)
    d_end   = pd.Timestamp(date_range[1]) if len(date_range)==2 else pd.Timestamp(max_d)

    st.markdown("#### 🗺️ Region")
    sel_region  = st.selectbox("", ["All"]+sorted(df_full['Region'].dropna().unique().tolist()))
    st.markdown("#### 🚚 Ship Mode")
    sel_mode    = st.selectbox("", ["All"]+sorted(df_full['Ship Mode'].dropna().unique().tolist()))
    st.markdown("#### 🏭 Factory")
    sel_factory = st.selectbox("", ["All"]+sorted(df_full['Factory'].dropna().unique().tolist()))
    st.markdown("#### ⏱️ Delay Threshold (days)")
    lt_thresh   = st.slider("Flag delayed if ≥", 500, 1600, 1300)
    st.markdown("---")
    st.markdown("<p style='font-size:0.73rem;color:#444;'>BTech Final Year Project<br>Nassau Candy Distributor<br>Logistics Analytics Dashboard</p>", unsafe_allow_html=True)

# ── Filter ───────────────────────────────────────────────────────────────────
df = df_full.copy()
df = df[(df['Order Date']>=d_start)&(df['Order Date']<=d_end)]
if sel_region  != "All": df = df[df['Region']   ==sel_region]
if sel_mode    != "All": df = df[df['Ship Mode'] ==sel_mode]
if sel_factory != "All": df = df[df['Factory']   ==sel_factory]
df['Delayed'] = df['Lead Time'] >= lt_thresh

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style='background:linear-gradient(135deg,#1a0533 0%,#0f172a 50%,#0a1628 100%);
     border:1px solid #2d1b69;border-radius:20px;padding:26px 30px;margin-bottom:22px;'>
  <div style='display:flex;align-items:center;gap:16px;'>
    <div style='font-size:2.8rem;'>🍫</div>
    <div>
      <h1 style='margin:0;font-size:1.75rem;color:#e2e8f0!important;font-weight:700;'>
        Nassau Candy Distributor
      </h1>
      <p style='margin:4px 0 0;color:#a78bfa;font-size:0.95rem;font-weight:500;'>
        Factory-to-Customer Shipping Route Efficiency Analysis
      </p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPIs ─────────────────────────────────────────────────────────────────────
k1,k2,k3,k4,k5,k6 = st.columns(6)
kpis = [
    (k1,"📦", f"{len(df):,}",                     "Total Orders"),
    (k2,"⏱️", f"{df['Lead Time'].mean():.0f}d",   "Avg Lead Time"),
    (k3,"🚨", f"{df['Delayed'].mean()*100:.1f}%", f"Delayed (≥{lt_thresh}d)"),
    (k4,"🛣️", f"{df['Route'].nunique()}",          "Unique Routes"),
    (k5,"💰", f"${df['Sales'].sum()/1000:.0f}K",  "Total Sales"),
    (k6,"📈", f"${df['Gross Profit'].mean():.2f}","Avg Gross Profit"),
]
for col,icon,val,lbl in kpis:
    with col:
        st.markdown(f'<div class="metric-card"><div style="font-size:1.4rem">{icon}</div>'
                    f'<div class="metric-value">{val}</div><div class="metric-label">{lbl}</div></div>',
                    unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ─────────────────────────────────────────────────────────────────────
t1,t2,t3,t4,t5 = st.tabs(["📊 Route Efficiency","🗺️ Geographic Map",
                            "🚚 Ship Mode Analysis","🔍 Route Drill-Down","📋 Executive Summary"])

# ═══════════════════════════════════════════════════════
# TAB 1 — Route Efficiency
# ═══════════════════════════════════════════════════════
with t1:
    route_agg = df.groupby('Route').agg(
        Shipments =('Lead Time','count'),
        Avg_LT    =('Lead Time','mean'),
        Std_LT    =('Lead Time','std'),
        Delay_Rate=('Delayed','mean'),
        Total_Sales=('Sales','sum'),
    ).reset_index()
    route_agg['Efficiency Score'] = (
        100 - (route_agg['Avg_LT']-route_agg['Avg_LT'].min()) /
              (route_agg['Avg_LT'].max()-route_agg['Avg_LT'].min()+1) * 60
            - route_agg['Delay_Rate']*40
    ).clip(0,100).round(1)
    route_agg = route_agg.sort_values('Efficiency Score', ascending=False).reset_index(drop=True)

    st.markdown('<div class="section-header">Route Performance Leaderboard</div>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        top10 = route_agg.head(10)
        fig = px.bar(top10, x='Efficiency Score', y='Route', orientation='h',
                     color='Efficiency Score', color_continuous_scale='Greens',
                     text=top10['Efficiency Score'].apply(lambda x:f"{x:.0f}"),
                     title="🏆 Top 10 Most Efficient Routes",
                     hover_data={'Avg_LT':':.0f','Shipments':True})
        fig.update_layout(height=360, **PLOT_BG, coloraxis_showscale=False,
                          yaxis=dict(autorange='reversed',gridcolor='#2d3250'),
                          xaxis=dict(gridcolor='#2d3250'),title_font_color='#e2e8f0')
        fig.update_traces(textposition='inside', textfont_size=10)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        bot10 = route_agg.tail(10).sort_values('Avg_LT', ascending=False)
        fig = px.bar(bot10, x='Avg_LT', y='Route', orientation='h',
                     color='Avg_LT', color_continuous_scale='Reds',
                     text=bot10['Avg_LT'].apply(lambda x:f"{x:.0f}d"),
                     title="🔴 Bottom 10 Slowest Routes",
                     hover_data={'Efficiency Score':':.1f','Shipments':True})
        fig.update_layout(height=360, **PLOT_BG, coloraxis_showscale=False,
                          yaxis=dict(autorange='reversed',gridcolor='#2d3250'),
                          xaxis=dict(gridcolor='#2d3250',title='Avg Lead Time (days)'),
                          title_font_color='#e2e8f0')
        fig.update_traces(textposition='inside', textfont_size=10)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-header">Lead Time Distribution by Factory</div>', unsafe_allow_html=True)
    c3,c4 = st.columns(2)
    with c3:
        fig = px.box(df, x='Factory', y='Lead Time', color='Factory',
                     color_discrete_sequence=px.colors.qualitative.Vivid, points='outliers')
        fig.update_layout(height=340, **PLOT_BG, showlegend=False,
                          xaxis=dict(tickangle=-20,gridcolor='#2d3250'),
                          yaxis=dict(gridcolor='#2d3250',title='Lead Time (days)'),
                          xaxis_title='')
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        fig = px.histogram(df, x='Lead Time', color='Region', nbins=40,
                           barmode='overlay',
                           color_discrete_sequence=['#6366f1','#8b5cf6','#f59e0b','#10b981'],
                           title="Lead Time Distribution by Region")
        fig.update_layout(height=340, **PLOT_BG,
                          xaxis=dict(gridcolor='#2d3250',title='Lead Time (days)'),
                          yaxis=dict(gridcolor='#2d3250',title='Count'),
                          legend=dict(bgcolor='rgba(0,0,0,0)',font=dict(color='#c8d0e7')),
                          title_font_color='#e2e8f0')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-header">All Routes — Summary Table</div>', unsafe_allow_html=True)
    disp = route_agg.copy()
    disp['Avg Lead Time (d)'] = disp['Avg_LT'].round(0).astype(int)
    disp['Delay Rate'] = (disp['Delay_Rate']*100).round(1).astype(str)+'%'
    disp['Total Sales'] = disp['Total_Sales'].apply(lambda x:f"${x:,.0f}")
    st.dataframe(disp[['Route','Shipments','Avg Lead Time (d)','Delay Rate','Total Sales','Efficiency Score']],
                 use_container_width=True, height=300)

# ═══════════════════════════════════════════════════════
# TAB 2 — Geographic Map
# ═══════════════════════════════════════════════════════
with t2:
    state_agg = df.groupby('State/Province').agg(
        Avg_LT    =('Lead Time','mean'),
        Shipments =('Lead Time','count'),
        Delay_Rate=('Delayed','mean'),
        Total_Sales=('Sales','sum'),
    ).reset_index()
    state_agg['lat'] = state_agg['State/Province'].map(lambda s: STATE_COORDS.get(s,(None,None))[0])
    state_agg['lon'] = state_agg['State/Province'].map(lambda s: STATE_COORDS.get(s,(None,None))[1])
    state_agg = state_agg.dropna(subset=['lat','lon'])
    state_agg['Delay%'] = (state_agg['Delay_Rate']*100).round(1)

    st.markdown('<div class="section-header">US Shipping Efficiency Map</div>', unsafe_allow_html=True)
    m1,m2 = st.columns(2)
    def base_geo():
        return dict(bgcolor='rgba(0,0,0,0)', landcolor='#1e2130',
                    coastlinecolor='#2d3250', showlakes=False,
                    subunitcolor='#2d3250', lakecolor='rgba(0,0,0,0)')

    with m1:
        fig = px.scatter_geo(state_agg, lat='lat', lon='lon', scope='usa',
                             size='Shipments', color='Avg_LT',
                             hover_name='State/Province',
                             hover_data={'Avg_LT':':.0f','Shipments':True,'Delay%':':.1f'},
                             color_continuous_scale='RdYlGn_r', size_max=45,
                             title="⏱️ Avg Lead Time by State")
        for fn,(flat,flon) in FACTORIES.items():
            fig.add_trace(go.Scattergeo(lat=[flat],lon=[flon],mode='markers+text',
                marker=dict(size=14,color='#fbbf24',symbol='star'),
                text=[fn.split("'")[0]], textposition='top center',
                textfont=dict(size=8,color='#fbbf24'),
                showlegend=False, hovertemplate=f"<b>🏭 {fn}</b><extra></extra>"))
        fig.update_layout(height=420, paper_bgcolor='rgba(0,0,0,0)',
                          geo=base_geo(), font=dict(color='#c8d0e7'),
                          coloraxis_colorbar=dict(title='Days'),
                          title_font_color='#e2e8f0', margin=dict(l=0,r=0,t=40,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with m2:
        fig = px.scatter_geo(state_agg, lat='lat', lon='lon', scope='usa',
                             size='Shipments', color='Delay%',
                             hover_name='State/Province',
                             hover_data={'Delay%':':.1f','Shipments':True},
                             color_continuous_scale='YlOrRd', size_max=45,
                             title=f"🚨 Delay Rate by State (≥{lt_thresh}d)")
        fig.update_layout(height=420, paper_bgcolor='rgba(0,0,0,0)',
                          geo=base_geo(), font=dict(color='#c8d0e7'),
                          coloraxis_colorbar=dict(title='Delay %'),
                          title_font_color='#e2e8f0', margin=dict(l=0,r=0,t=40,b=0))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("⭐ **Yellow stars** = Factory locations &nbsp;|&nbsp; **Bubble size** = shipment volume", unsafe_allow_html=True)

    st.markdown('<div class="section-header">Regional Bottleneck Analysis</div>', unsafe_allow_html=True)
    reg = df.groupby('Region').agg(Avg_LT=('Lead Time','mean'),
                                    Shipments=('Lead Time','count'),
                                    Delay_Rate=('Delayed','mean'),
                                    Sales=('Sales','sum')).reset_index()
    r1,r2 = st.columns(2)
    with r1:
        fig = px.bar(reg.sort_values('Avg_LT',ascending=False),
                     x='Region', y='Avg_LT', color='Region',
                     color_discrete_sequence=['#6366f1','#8b5cf6','#f59e0b','#10b981'],
                     text=reg.sort_values('Avg_LT',ascending=False)['Avg_LT'].apply(lambda x:f"{x:.0f}d"),
                     title="Avg Lead Time by Region")
        fig.update_layout(height=300, **PLOT_BG, showlegend=False,
                          xaxis=dict(gridcolor='#2d3250'), yaxis=dict(gridcolor='#2d3250',title='Days'),
                          title_font_color='#e2e8f0', xaxis_title='')
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    with r2:
        fig = px.scatter(reg, x='Avg_LT', y='Shipments', size='Delay_Rate',
                         color='Region', text='Region',
                         color_discrete_sequence=['#6366f1','#8b5cf6','#f59e0b','#10b981'],
                         title="Volume vs Lead Time (bubble = delay rate)",
                         size_max=50)
        fig.update_layout(height=300, **PLOT_BG,
                          xaxis=dict(gridcolor='#2d3250',title='Avg Lead Time (days)'),
                          yaxis=dict(gridcolor='#2d3250',title='Shipments'),
                          title_font_color='#e2e8f0',
                          legend=dict(bgcolor='rgba(0,0,0,0)',font=dict(color='#c8d0e7')))
        fig.update_traces(textposition='top center', textfont_size=10)
        st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════
# TAB 3 — Ship Mode Analysis
# ═══════════════════════════════════════════════════════
with t3:
    mode_agg = df.groupby('Ship Mode').agg(
        Avg_LT    =('Lead Time','mean'),
        Median_LT =('Lead Time','median'),
        Shipments =('Lead Time','count'),
        Delay_Rate=('Delayed','mean'),
        Avg_Sales =('Sales','mean'),
    ).reset_index().sort_values('Avg_LT')
    COLORS = ['#34d399','#6366f1','#f59e0b','#f87171']

    st.markdown('<div class="section-header">Ship Mode Performance Comparison</div>', unsafe_allow_html=True)
    sm1,sm2,sm3 = st.columns(3)
    with sm1:
        fig = px.bar(mode_agg, x='Ship Mode', y='Avg_LT', color='Ship Mode',
                     color_discrete_sequence=COLORS,
                     text=mode_agg['Avg_LT'].apply(lambda x:f"{x:.0f}d"),
                     title="Avg Lead Time")
        fig.update_layout(height=310, **PLOT_BG, showlegend=False,
                          xaxis=dict(gridcolor='#2d3250',tickangle=-15),
                          yaxis=dict(gridcolor='#2d3250',title='Days'),
                          title_font_color='#e2e8f0', xaxis_title='')
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    with sm2:
        fig = px.pie(mode_agg, values='Shipments', names='Ship Mode',
                     color_discrete_sequence=COLORS, hole=0.45, title="Shipment Volume Share")
        fig.update_layout(height=310, paper_bgcolor='rgba(0,0,0,0)',
                          font=dict(color='#c8d0e7'), title_font_color='#e2e8f0',
                          legend=dict(font=dict(color='#c8d0e7')), margin=dict(l=0,r=0,t=40,b=0))
        st.plotly_chart(fig, use_container_width=True)
    with sm3:
        fig = px.bar(mode_agg, x='Ship Mode', y='Delay_Rate', color='Ship Mode',
                     color_discrete_sequence=COLORS,
                     text=mode_agg['Delay_Rate'].apply(lambda x:f"{x*100:.1f}%"),
                     title="Delay Rate")
        fig.update_layout(height=310, **PLOT_BG, showlegend=False,
                          xaxis=dict(gridcolor='#2d3250',tickangle=-15),
                          yaxis=dict(gridcolor='#2d3250',tickformat='.0%',title='Delay Rate'),
                          title_font_color='#e2e8f0', xaxis_title='')
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-header">Lead Time Violin Plot by Ship Mode</div>', unsafe_allow_html=True)
    fig = px.violin(df, x='Ship Mode', y='Lead Time', color='Ship Mode',
                    color_discrete_sequence=COLORS, box=True, points='outliers')
    fig.update_layout(height=360, **PLOT_BG, showlegend=False,
                      xaxis=dict(gridcolor='#2d3250'), yaxis=dict(gridcolor='#2d3250',title='Lead Time (days)'),
                      xaxis_title='')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-header">Factory × Ship Mode Heatmap (Avg Lead Time)</div>', unsafe_allow_html=True)
    hm = df.groupby(['Factory','Ship Mode'])['Lead Time'].mean().reset_index()
    hm_piv = hm.pivot(index='Factory', columns='Ship Mode', values='Lead Time').fillna(0)
    fig = px.imshow(hm_piv, color_continuous_scale='RdYlGn_r', text_auto='.0f', aspect='auto')
    fig.update_layout(height=310, **PLOT_BG, coloraxis_colorbar=dict(title='Days'))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-header">Ship Mode × Region Cross Analysis</div>', unsafe_allow_html=True)
    cr = df.groupby(['Ship Mode','Region'])['Lead Time'].mean().reset_index()
    fig = px.bar(cr, x='Region', y='Lead Time', color='Ship Mode', barmode='group',
                 color_discrete_sequence=COLORS)
    fig.update_layout(height=320, **PLOT_BG,
                      xaxis=dict(gridcolor='#2d3250'), yaxis=dict(gridcolor='#2d3250',title='Avg Lead Time (days)'),
                      legend=dict(bgcolor='rgba(0,0,0,0)',font=dict(color='#c8d0e7')),
                      xaxis_title='')
    st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════
# TAB 4 — Route Drill-Down
# ═══════════════════════════════════════════════════════
with t4:
    st.markdown('<div class="section-header">State-Level Deep Dive</div>', unsafe_allow_html=True)
    col_l, col_r = st.columns([1,2])
    with col_l:
        sel_state = st.selectbox("Select State", sorted(df['State/Province'].dropna().unique()))
    sdf = df[df['State/Province']==sel_state]
    with col_r:
        monthly = sdf.groupby('Month').agg(Avg_LT=('Lead Time','mean'),Orders=('Lead Time','count')).reset_index()
        fig = make_subplots(specs=[[{"secondary_y":True}]])
        fig.add_trace(go.Scatter(x=monthly['Month'], y=monthly['Avg_LT'], name='Avg Lead Time',
                                 line=dict(color='#a78bfa',width=2.5),
                                 fill='tozeroy', fillcolor='rgba(124,58,237,0.12)'), secondary_y=False)
        fig.add_trace(go.Bar(x=monthly['Month'], y=monthly['Orders'], name='Orders',
                             marker_color='rgba(99,102,241,0.35)'), secondary_y=True)
        fig.update_layout(height=260, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          font=dict(color='#c8d0e7',size=10), margin=dict(l=0,r=10,t=10,b=50),
                          xaxis=dict(gridcolor='#2d3250',tickangle=-45),
                          legend=dict(bgcolor='rgba(0,0,0,0)',font=dict(color='#c8d0e7')))
        fig.update_yaxes(title_text="Lead Time (days)", gridcolor='#2d3250', secondary_y=False)
        fig.update_yaxes(title_text="Orders", showgrid=False, secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)

    # State stats cards
    s1,s2,s3,s4 = st.columns(4)
    for col,icon,val,lbl in [
        (s1,"📦",f"{len(sdf):,}","Orders"),
        (s2,"⏱️",f"{sdf['Lead Time'].mean():.0f}d","Avg Lead Time"),
        (s3,"🚨",f"{sdf['Delayed'].mean()*100:.1f}%","Delay Rate"),
        (s4,"💰",f"${sdf['Sales'].sum():,.0f}","Total Sales"),
    ]:
        with col:
            st.markdown(f'<div class="metric-card"><div style="font-size:1.3rem">{icon}</div>'
                        f'<div class="metric-value">{val}</div><div class="metric-label">{lbl}</div></div>',
                        unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)

    d1,d2 = st.columns(2)
    with d1:
        st.markdown('<div class="section-header">Factory Performance → ' + sel_state + '</div>', unsafe_allow_html=True)
        fa = sdf.groupby('Factory').agg(Orders=('Lead Time','count'),
                                         Avg_LT=('Lead Time','mean'),
                                         Delay_Rate=('Delayed','mean')).reset_index().sort_values('Avg_LT')
        fig = px.bar(fa, x='Factory', y='Avg_LT', color='Delay_Rate',
                     color_continuous_scale='YlOrRd',
                     text=fa['Avg_LT'].apply(lambda x:f"{x:.0f}d"))
        fig.update_layout(height=280, **PLOT_BG,
                          xaxis=dict(gridcolor='#2d3250',tickangle=-20),
                          yaxis=dict(gridcolor='#2d3250',title='Avg Lead Time (days)'),
                          coloraxis_colorbar=dict(title='Delay Rate'), xaxis_title='')
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    with d2:
        st.markdown('<div class="section-header">Product Breakdown</div>', unsafe_allow_html=True)
        pa = sdf.groupby('Product Name').agg(Orders=('Lead Time','count'),
                                               Avg_LT=('Lead Time','mean'),
                                               Revenue=('Sales','sum')).reset_index().sort_values('Avg_LT')
        fig = px.bar(pa, x='Avg_LT', y='Product Name', orientation='h',
                     color='Revenue', color_continuous_scale='Purples',
                     text=pa['Avg_LT'].apply(lambda x:f"{x:.0f}d"))
        fig.update_layout(height=280, **PLOT_BG,
                          yaxis=dict(autorange='reversed',gridcolor='#2d3250'),
                          xaxis=dict(gridcolor='#2d3250',title='Avg Lead Time (days)'),
                          coloraxis_colorbar=dict(title='Revenue'), yaxis_title='')
        fig.update_traces(textposition='inside', textfont_size=9)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-header">Order-Level Shipment Log (Top 100 by Lead Time)</div>', unsafe_allow_html=True)
    raw = sdf[['Order ID','Order Date','Ship Date','Lead Time','Ship Mode','Factory','Product Name','Sales']].copy()
    raw['Order Date'] = raw['Order Date'].dt.strftime('%Y-%m-%d')
    raw['Ship Date']  = raw['Ship Date'].dt.strftime('%Y-%m-%d')
    raw['Sales'] = raw['Sales'].apply(lambda x:f"${x:,.2f}")
    st.dataframe(raw.sort_values('Lead Time',ascending=False).head(100), use_container_width=True, height=260)

# ═══════════════════════════════════════════════════════
# TAB 5 — Executive Summary
# ═══════════════════════════════════════════════════════
with t5:
    st.markdown('<div class="section-header">Executive Summary — Logistics Intelligence Report</div>', unsafe_allow_html=True)

    best_route   = route_agg.iloc[0]
    worst_route  = route_agg.iloc[-1]
    mode_lt      = df.groupby('Ship Mode')['Lead Time'].mean()
    best_mode    = mode_lt.idxmin()
    worst_mode   = mode_lt.idxmax()
    worst_region = df.groupby('Region')['Lead Time'].mean().idxmax()
    best_factory = df.groupby('Factory')['Lead Time'].mean().idxmin()
    worst_factory= df.groupby('Factory')['Lead Time'].mean().idxmax()

    e1,e2 = st.columns(2)
    with e1:
        st.markdown(f"""
        <div class="insight-box">
            <b>🏢 Company Overview</b><br><br>
            Nassau Candy Distributor operates a nationwide distribution network shipping specialty 
            candy products from <b>5 factories</b> across the United States to customers in <b>{df['State/Province'].nunique()} states</b>.
            This dashboard provides route-level efficiency intelligence to enable data-driven logistics decisions.
        </div>
        <div class="insight-box">
            <b>✅ Top Performing Route</b><br><br>
            <b>{best_route['Route']}</b><br>
            Efficiency Score: <b>{best_route['Efficiency Score']}</b> &nbsp;|&nbsp;
            Avg Lead Time: <b>{best_route['Avg_LT']:.0f} days</b> &nbsp;|&nbsp;
            Shipments: <b>{int(best_route['Shipments']):,}</b>
        </div>
        <div class="insight-box">
            <b>⚠️ Underperforming Route (Needs Attention)</b><br><br>
            <b>{worst_route['Route']}</b><br>
            Efficiency Score: <b>{worst_route['Efficiency Score']}</b> &nbsp;|&nbsp;
            Avg Lead Time: <b>{worst_route['Avg_LT']:.0f} days</b>
        </div>
        <div class="insight-box">
            <b>🚚 Ship Mode Insights</b><br><br>
            Fastest mode: <b>{best_mode}</b> — recommended for time-sensitive orders.<br>
            Slowest mode: <b>{worst_mode}</b> — avoid for priority customers.<br>
            Avg lead time variance across modes: <b>{mode_lt.max()-mode_lt.min():.0f} days</b> — 
            significant enough to justify mode-switching strategies.
        </div>""", unsafe_allow_html=True)

    with e2:
        st.markdown(f"""
        <div class="insight-box">
            <b>🗺️ Geographic Bottlenecks</b><br><br>
            Highest avg lead time region: <b>{worst_region}</b><br>
            This region requires immediate logistics review. Consider re-routing shipments through 
            nearer factories or upgrading ship modes for high-value orders in this corridor.
        </div>
        <div class="insight-box">
            <b>🏭 Factory Performance</b><br><br>
            Most efficient: <b>{best_factory}</b><br>
            Least efficient: <b>{worst_factory}</b><br>
            Factory-level lead time variability indicates differences in processing capacity 
            or dispatch workflows that should be audited and standardized.
        </div>
        <div class="insight-box">
            <b>💡 Strategic Recommendations</b><br><br>
            1. <b>Reroute</b> high-delay corridors through alternative factories where feasible.<br>
            2. <b>Upgrade ship mode</b> on routes with persistent delay rates above 40%.<br>
            3. <b>Benchmark</b> top-10 routes as operational SOPs for underperforming routes.<br>
            4. <b>Audit</b> {worst_factory} processing workflows — consistently slowest lead times.<br>
            5. <b>Pre-order incentives</b> for far-region customers to reduce last-minute urgency.
        </div>
        <div class="insight-box">
            <b>📊 Dataset Snapshot</b><br><br>
            Records analyzed: <b>{len(df_full):,}</b> &nbsp;|&nbsp;
            Products: <b>{df_full['Product Name'].nunique()}</b> &nbsp;|&nbsp;
            Factories: <b>{df_full['Factory'].nunique()}</b><br>
            Order period: <b>{df_full['Order Date'].min().strftime('%b %Y')}</b> → 
            <b>{df_full['Order Date'].max().strftime('%b %Y')}</b><br>
            Total Revenue: <b>${df_full['Sales'].sum():,.0f}</b> &nbsp;|&nbsp;
            Total Gross Profit: <b>${df_full['Gross Profit'].sum():,.0f}</b>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">Monthly Shipping Trend (Full Dataset)</div>', unsafe_allow_html=True)
    monthly_full = df_full.groupby('Month').agg(
        Avg_LT=('Lead Time','mean'), Orders=('Lead Time','count')
    ).reset_index()
    fig = make_subplots(specs=[[{"secondary_y":True}]])
    fig.add_trace(go.Scatter(x=monthly_full['Month'], y=monthly_full['Avg_LT'],
                             name='Avg Lead Time', line=dict(color='#a78bfa',width=2.5),
                             fill='tozeroy', fillcolor='rgba(124,58,237,0.1)'), secondary_y=False)
    fig.add_trace(go.Bar(x=monthly_full['Month'], y=monthly_full['Orders'],
                         name='Orders', marker_color='rgba(99,102,241,0.3)'), secondary_y=True)
    fig.update_layout(height=320, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      font=dict(color='#c8d0e7',size=10), margin=dict(l=0,r=40,t=10,b=60),
                      xaxis=dict(gridcolor='#2d3250',tickangle=-45),
                      legend=dict(bgcolor='rgba(0,0,0,0)',font=dict(color='#c8d0e7')))
    fig.update_yaxes(title_text="Avg Lead Time (days)", gridcolor='#2d3250', secondary_y=False)
    fig.update_yaxes(title_text="Orders", showgrid=False, secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-header">Division-Level Performance</div>', unsafe_allow_html=True)
    div_agg = df.groupby(['Division','Ship Mode']).agg(
        Avg_LT=('Lead Time','mean'), Orders=('Lead Time','count')
    ).reset_index()
    fig = px.bar(div_agg, x='Division', y='Avg_LT', color='Ship Mode', barmode='group',
                 color_discrete_sequence=['#34d399','#6366f1','#f59e0b','#f87171'])
    fig.update_layout(height=300, **PLOT_BG,
                      xaxis=dict(gridcolor='#2d3250'), yaxis=dict(gridcolor='#2d3250',title='Avg Lead Time (days)'),
                      legend=dict(bgcolor='rgba(0,0,0,0)',font=dict(color='#c8d0e7')), xaxis_title='')
    st.plotly_chart(fig, use_container_width=True)

st.markdown("""
<div style='text-align:center;padding:28px 0 14px;color:#2d3250;font-size:0.78rem;'>
    Nassau Candy Distributor · Shipping Route Efficiency Analysis · 
    Streamlit + Plotly · BTech Data Analytics Project
</div>""", unsafe_allow_html=True)
