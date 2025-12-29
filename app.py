import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random

# Page configuration
st.set_page_config(
    page_title="CECECO-SIM | Simulation & Integration Module",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Theme CSS
st.markdown("""
    <style>
    /* Dark Theme Base */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        color: #e0e0e0;
    }
    
    /* Main Header */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 30px rgba(102, 126, 234, 0.5);
    }
    
    .sub-header {
        text-align: center;
        color: #b0b0b0;
        font-size: 1.3rem;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    /* Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        border: 1px solid rgba(102, 126, 234, 0.3);
        backdrop-filter: blur(10px);
    }
    
    .project-card {
        background: rgba(30, 30, 50, 0.8);
        border-left: 4px solid #667eea;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 10px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        color: #e0e0e0;
    }
    
    .region-card {
        background: rgba(40, 40, 60, 0.9);
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border: 1px solid rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .region-card:hover {
        transform: translateX(5px);
        border-color: #667eea;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Agent Status */
    .agent-status {
        padding: 0.7rem 1.2rem;
        border-radius: 8px;
        display: inline-block;
        margin: 0.3rem;
        font-size: 0.9rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    }
    
    .status-active {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    
    .status-analyzing {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
    }
    
    .status-complete {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
    }
    
    /* Profit/Loss Cards */
    .profit-card {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.2) 100%);
        border: 1px solid rgba(16, 185, 129, 0.5);
    }
    
    .loss-card {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(220, 38, 38, 0.2) 100%);
        border: 1px solid rgba(239, 68, 68, 0.5);
    }
    
    /* Timeline */
    .timeline-item {
        background: rgba(50, 50, 70, 0.8);
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border-left: 3px solid #667eea;
    }
    
    /* Override Streamlit defaults for dark theme */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(20, 20, 40, 0.8);
        border-radius: 10px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #b0b0b0;
    }
    
    .stTabs [aria-selected="true"] {
        color: #667eea;
        background: rgba(102, 126, 234, 0.2);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(15, 12, 41, 0.95);
        border-right: 1px solid rgba(102, 126, 234, 0.3);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #667eea;
    }
    
    /* Plotly dark theme */
    .js-plotly-plot {
        background: transparent !important;
    }
    </style>
""", unsafe_allow_html=True)

# CECECO Countries Data with Regions
CECECO_COUNTRIES = {
    "Turkey": {
        "lat": 39.9334, 
        "lon": 32.8597, 
        "code": "TR", 
        "color": "#FF6B6B",
        "regions": {
            "Kırıkkale": {"lat": 39.8436, "lon": 33.5083, "projects": 3},
            "İzmir": {"lat": 38.4237, "lon": 27.1428, "projects": 5},
            "Çanakkale": {"lat": 40.1553, "lon": 26.4142, "projects": 4},
            "Balıkesir": {"lat": 39.6484, "lon": 27.8826, "projects": 6},
            "Manisa": {"lat": 38.6140, "lon": 27.4296, "projects": 3}
        }
    },
    "Azerbaijan": {
        "lat": 40.1431, 
        "lon": 47.5769, 
        "code": "AZ", 
        "color": "#4ECDC4",
        "regions": {
            "Absheron": {"lat": 40.4675, "lon": 49.8200, "projects": 2},
            "Ganja": {"lat": 40.6828, "lon": 46.3606, "projects": 1},
            "Shirvan": {"lat": 39.9317, "lon": 48.9206, "projects": 2},
            "Sumgayit": {"lat": 40.5897, "lon": 49.6686, "projects": 1},
            "Lankaran": {"lat": 38.7542, "lon": 48.8506, "projects": 1}
        }
    },
    "Pakistan": {"lat": 30.3753, "lon": 69.3451, "code": "PK", "color": "#95E1D3", "regions": {}},
    "Kazakhstan": {"lat": 48.0196, "lon": 66.9237, "code": "KZ", "color": "#F38181", "regions": {}},
    "Uzbekistan": {"lat": 41.3775, "lon": 64.5853, "code": "UZ", "color": "#AA96DA", "regions": {}},
    "Kyrgyzstan": {"lat": 41.2044, "lon": 74.7661, "code": "KG", "color": "#FCBAD3", "regions": {}}
}

# Enhanced Project Data with Historical Context
MOCK_PROJECTS = {
    "Turkey": {
        "Kırıkkale Wind Farm": {
            "year": 2016,
            "region": "Kırıkkale",
            "capacity": "150 MW",
            "investment": "$180M",
            "success_rate": 95,
            "then_conditions": {
                "Steel Price": "$850/ton",
                "YEKDEM Incentive": "Active ($0.073/kWh)",
                "Regulatory Framework": "Favorable - Fast track permits",
                "Wind Speed": "7.2 m/s avg",
                "Currency Rate": "1 USD = 3.0 TRY",
                "Interest Rate": "12%",
                "Tax Incentive": "50% reduction for 5 years"
            },
            "profit_loss": {
                "year_1": {"revenue": 28.5, "cost": 22.0, "profit": 6.5},
                "year_2": {"revenue": 31.2, "cost": 20.5, "profit": 10.7},
                "year_3": {"revenue": 33.8, "cost": 19.8, "profit": 14.0},
                "year_4": {"revenue": 35.5, "cost": 19.2, "profit": 16.3},
                "year_5": {"revenue": 37.2, "cost": 18.5, "profit": 18.7},
                "total_roi": 45.2
            },
            "regulatory_evolution": [
                {"year": 2016, "event": "YEKDEM Law Active", "impact": "High incentive support"},
                {"year": 2017, "event": "Permit Process Simplified", "impact": "Faster approvals"},
                {"year": 2019, "event": "YEKDEM Extended", "impact": "Extended support period"},
                {"year": 2021, "event": "New YEKDEM Rates", "impact": "Reduced rates, still favorable"},
                {"year": 2023, "event": "Green Certificate System", "impact": "Additional revenue stream"}
            ]
        }
    },
    "Azerbaijan": {
        "Absheron Wind Project": {
            "year": 2018,
            "region": "Absheron",
            "capacity": "80 MW",
            "investment": "$95M",
            "success_rate": 88,
            "then_conditions": {
                "Steel Price": "$920/ton",
                "Government Support": "High - Direct investment",
                "Regulatory Framework": "Moderate - New framework",
                "Wind Speed": "6.8 m/s avg",
                "Currency Rate": "1 USD = 1.7 AZN",
                "Interest Rate": "8%",
                "Tax Incentive": "10-year tax holiday"
            },
            "profit_loss": {
                "year_1": {"revenue": 12.5, "cost": 11.0, "profit": 1.5},
                "year_2": {"revenue": 14.2, "cost": 10.5, "profit": 3.7},
                "year_3": {"revenue": 15.8, "cost": 10.0, "profit": 5.8},
                "year_4": {"revenue": 17.5, "cost": 9.5, "profit": 8.0},
                "year_5": {"revenue": 19.2, "cost": 9.0, "profit": 10.2},
                "total_roi": 28.4
            },
            "regulatory_evolution": [
                {"year": 2018, "event": "Renewable Energy Law", "impact": "Foundation for sector"},
                {"year": 2019, "event": "Feed-in Tariff Introduced", "impact": "Price guarantee"},
                {"year": 2020, "event": "Grid Connection Simplified", "impact": "Easier integration"},
                {"year": 2022, "event": "Green Energy Targets Set", "impact": "Policy commitment"},
                {"year": 2023, "event": "Auction System Proposed", "impact": "Competitive pricing"}
            ]
        }
    }
}

# Current Conditions (2024)
CURRENT_CONDITIONS = {
    "Turkey": {
        "Steel Price": "$1,150/ton",
        "YEKDEM Incentive": "Active ($0.055/kWh)",
        "Regulatory Framework": "Mature - Streamlined",
        "Wind Speed": "7.5 m/s avg",
        "Currency Rate": "1 USD = 32.0 TRY",
        "Interest Rate": "45%",
        "Tax Incentive": "30% reduction for 3 years"
    },
    "Azerbaijan": {
        "Steel Price": "$980/ton",
        "Government Support": "Very High - Strategic priority",
        "Regulatory Framework": "Improved - Clear guidelines",
        "Wind Speed": "7.0 m/s avg",
        "Currency Rate": "1 USD = 1.7 AZN",
        "Interest Rate": "7%",
        "Tax Incentive": "15-year tax holiday"
    },
    "Kazakhstan": {
        "Steel Price": "$1,050/ton",
        "Government Support": "Moderate",
        "Regulatory Framework": "Developing",
        "Wind Speed": "6.5 m/s avg",
        "Currency Rate": "1 USD = 450 KZT",
        "Interest Rate": "16%",
        "Tax Incentive": "Under discussion"
    }
}

# Mock AI Agent Status
def get_agent_status():
    agents = [
        {"name": "Researcher Agent", "status": "active", "task": "Scanning Official Gazettes"},
        {"name": "Gap Analysis Agent", "status": "analyzing", "task": "Comparing regulations"},
        {"name": "Similarity Engine", "status": "complete", "task": "Calculating similarity scores"},
        {"name": "Policy Transfer Agent", "status": "active", "task": "Simulating policy transfer"}
    ]
    return agents

# Main App
def main():
    # Header
    st.markdown('<h1 class="main-header">🌍 CECECO-SIM</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Simulation & Integration Module | Multi-AI Agent Architecture</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Control Panel")
        selected_country = st.selectbox(
            "Select Target Country",
            list(CECECO_COUNTRIES.keys())
        )
        
        source_country = st.selectbox(
            "Select Source Project Country",
            [c for c in CECECO_COUNTRIES.keys() if c != selected_country and c in MOCK_PROJECTS],
            index=0 if "Turkey" in [c for c in CECECO_COUNTRIES.keys() if c != selected_country and c in MOCK_PROJECTS] else 0
        )
        
        # Region selection if available
        if source_country in CECECO_COUNTRIES and CECECO_COUNTRIES[source_country].get("regions"):
            source_regions = list(CECECO_COUNTRIES[source_country]["regions"].keys())
            source_project_name = st.selectbox(
                "Select Source Project",
                [p for p in MOCK_PROJECTS.get(source_country, {}).keys()],
                format_func=lambda x: f"{x} ({MOCK_PROJECTS[source_country][x]['year']})"
            )
        else:
            source_project_name = list(MOCK_PROJECTS.get(source_country, {}).keys())[0] if MOCK_PROJECTS.get(source_country) else None
        
        if selected_country in CECECO_COUNTRIES and CECECO_COUNTRIES[selected_country].get("regions"):
            target_regions = list(CECECO_COUNTRIES[selected_country]["regions"].keys())
            selected_region = st.selectbox(
                "Select Target Region",
                target_regions
            )
        else:
            selected_region = None
        
        energy_type = st.selectbox(
            "Energy Type",
            ["Wind Energy", "Solar Energy", "Hydro Energy"]
        )
        
        st.divider()
        
        st.header("🤖 AI Agents Status")
        agents = get_agent_status()
        for agent in agents:
            status_class = f"status-{agent['status']}"
            st.markdown(f"""
                <div class="agent-status {status_class}">
                    <strong>{agent['name']}</strong><br>
                    <small>{agent['task']}</small>
                </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        st.info("💡 This is a demo prototype. Features are simulated for demonstration purposes.")
    
    # Get source project data
    source_project = None
    if source_country in MOCK_PROJECTS and source_project_name:
        source_project = MOCK_PROJECTS[source_country][source_project_name]
    
    # Main Content
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🗺️ Regional Map", 
        "📊 Project Analysis", 
        "💰 Profit/Loss Analysis",
        "📜 Regulatory Evolution",
        "🤖 AI Simulation"
    ])
    
    # Tab 1: Regional Map
    with tab1:
        st.header("CECECO Region Overview")
        
        # Create map with dark theme
        m = folium.Map(
            location=[40, 60],
            zoom_start=4,
            tiles='CartoDB dark_matter'  # Dark theme map
        )
        
        # Add country markers
        for country, data in CECECO_COUNTRIES.items():
            folium.CircleMarker(
                location=[data["lat"], data["lon"]],
                radius=15,
                popup=f"{country} ({data['code']})",
                tooltip=country,
                color=data["color"],
                fill=True,
                fillColor=data["color"],
                fillOpacity=0.7
            ).add_to(m)
            
            # Add regional markers if available
            if "regions" in data and data["regions"]:
                for region_name, region_data in data["regions"].items():
                    folium.CircleMarker(
                        location=[region_data["lat"], region_data["lon"]],
                        radius=8,
                        popup=f"{region_name} ({region_data['projects']} projects)",
                        tooltip=region_name,
                        color=data["color"],
                        fill=True,
                        fillColor=data["color"],
                        fillOpacity=0.5
                    ).add_to(m)
        
        # Highlight selected countries and regions
        if selected_country in CECECO_COUNTRIES:
            target = CECECO_COUNTRIES[selected_country]
            folium.Marker(
                [target["lat"], target["lon"]],
                popup=f"🎯 Target: {selected_country}",
                icon=folium.Icon(color='red', icon='target', prefix='fa')
            ).add_to(m)
            
            if selected_region and selected_region in target.get("regions", {}):
                region = target["regions"][selected_region]
                folium.Marker(
                    [region["lat"], region["lon"]],
                    popup=f"🎯 Target Region: {selected_region}",
                    icon=folium.Icon(color='orange', icon='map-marker', prefix='fa')
                ).add_to(m)
        
        if source_country in CECECO_COUNTRIES and source_project:
            source = CECECO_COUNTRIES[source_country]
            folium.Marker(
                [source["lat"], source["lon"]],
                popup=f"📦 Source: {source_country}",
                icon=folium.Icon(color='blue', icon='database', prefix='fa')
            ).add_to(m)
            
            if source_project.get("region") in source.get("regions", {}):
                region = source["regions"][source_project["region"]]
                folium.Marker(
                    [region["lat"], region["lon"]],
                    popup=f"📦 Source Project: {source_project_name}",
                    icon=folium.Icon(color='lightblue', icon='industry', prefix='fa')
                ).add_to(m)
        
        st_folium(m, width=1200, height=600)
        
        # Regional details
        if selected_country in CECECO_COUNTRIES and CECECO_COUNTRIES[selected_country].get("regions"):
            st.subheader(f"📍 Regions in {selected_country}")
            regions_data = CECECO_COUNTRIES[selected_country]["regions"]
            cols = st.columns(len(regions_data))
            for i, (region_name, region_info) in enumerate(regions_data.items()):
                with cols[i]:
                    st.markdown(f"""
                        <div class="region-card">
                            <h4>{region_name}</h4>
                            <p><strong>Projects:</strong> {region_info['projects']}</p>
                        </div>
                    """, unsafe_allow_html=True)
    
    # Tab 2: Project Analysis - Then vs Now
    with tab2:
        st.header("📊 Case-Based Reasoning Analysis: Then vs Now")
        
        if not source_project:
            st.warning("Please select a source project from the sidebar.")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"📦 Source Project: {source_project_name}")
            st.markdown(f"""
                <div class="project-card">
                    <h3>{source_project_name}</h3>
                    <p><strong>Year:</strong> {source_project['year']}</p>
                    <p><strong>Region:</strong> {source_project['region']}</p>
                    <p><strong>Capacity:</strong> {source_project['capacity']}</p>
                    <p><strong>Investment:</strong> {source_project['investment']}</p>
                    <p><strong>Success Rate:</strong> {source_project['success_rate']}%</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.subheader("🔙 Conditions Then (Project Year)")
            for factor, value in source_project['then_conditions'].items():
                st.write(f"📌 **{factor}**: {value}")
        
        with col2:
            st.subheader(f"🎯 Target: {selected_country}" + (f" - {selected_region}" if selected_region else ""))
            
            # Current conditions
            current_cond = CURRENT_CONDITIONS.get(selected_country, {})
            st.subheader("🔄 Conditions Now (2024)")
            for factor, value in current_cond.items():
                st.write(f"📌 **{factor}**: {value}")
            
            # Comparison
            st.divider()
            st.subheader("📈 Change Analysis")
            
            if selected_country in CURRENT_CONDITIONS:
                changes = []
                for key in source_project['then_conditions'].keys():
                    if key in current_cond:
                        then_val = source_project['then_conditions'][key]
                        now_val = current_cond[key]
                        # Simple comparison (in real app, would parse and compare)
                        changes.append({
                            "factor": key,
                            "then": then_val,
                            "now": now_val,
                            "change": "Improved" if random.random() > 0.3 else "Deteriorated"
                        })
                
                for change in changes[:5]:  # Show first 5
                    if change["change"] == "Improved":
                        st.success(f"✅ **{change['factor']}**: {change['then']} → {change['now']}")
                    else:
                        st.error(f"❌ **{change['factor']}**: {change['then']} → {change['now']}")
        
        # Similarity Score
        st.divider()
        similarity_score = random.randint(70, 95)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Overall Similarity", f"{similarity_score}%", delta=f"{similarity_score-80}%")
        with col2:
            st.metric("Regulatory Match", f"{random.randint(75, 95)}%")
        with col3:
            st.metric("Economic Match", f"{random.randint(65, 85)}%")
        
        # Recommendation
        st.divider()
        st.subheader("💡 AI Recommendation")
        if similarity_score >= 85:
            st.success(f"""
            ✅ **HIGH TRANSFERABILITY**: The project from {source_country} has a {similarity_score}% 
            similarity match with {selected_country}. Key success factors align well, with minor 
            adjustments needed for regulatory framework.
            """)
        elif similarity_score >= 70:
            st.warning(f"""
            ⚠️ **MODERATE TRANSFERABILITY**: The project shows {similarity_score}% similarity. 
            Significant adjustments required, particularly in incentive programs and regulatory alignment.
            """)
        else:
            st.error(f"""
            ❌ **LOW TRANSFERABILITY**: Only {similarity_score}% similarity detected. 
            Major policy and economic reforms needed before project transfer is viable.
            """)
    
    # Tab 3: Profit/Loss Analysis
    with tab3:
        st.header("💰 Profit/Loss Analysis: Source Country Performance")
        
        if not source_project:
            st.warning("Please select a source project from the sidebar.")
            return
        
        st.subheader(f"Financial Performance: {source_project_name}")
        
        # Profit/Loss data
        pl_data = source_project['profit_loss']
        years = [f"Year {i+1}" for i in range(5)]
        revenues = [pl_data[f"year_{i+1}"]["revenue"] for i in range(5)]
        costs = [pl_data[f"year_{i+1}"]["cost"] for i in range(5)]
        profits = [pl_data[f"year_{i+1}"]["profit"] for i in range(5)]
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        total_revenue = sum(revenues)
        total_cost = sum(costs)
        total_profit = sum(profits)
        roi = pl_data['total_roi']
        
        with col1:
            st.metric("Total Revenue (5 Years)", f"${total_revenue:.1f}M", delta=f"+{total_revenue*0.1:.1f}M")
        with col2:
            st.metric("Total Cost (5 Years)", f"${total_cost:.1f}M", delta=f"-{total_cost*0.05:.1f}M")
        with col3:
            st.metric("Total Profit (5 Years)", f"${total_profit:.1f}M", 
                     delta=f"+{total_profit*0.15:.1f}M" if total_profit > 0 else f"{total_profit:.1f}M")
        with col4:
            st.metric("ROI", f"{roi}%", delta=f"+{roi*0.1:.1f}%")
        
        # Profit/Loss Chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=years,
            y=revenues,
            name='Revenue',
            marker_color='#10b981',
            opacity=0.8
        ))
        fig.add_trace(go.Bar(
            x=years,
            y=costs,
            name='Cost',
            marker_color='#ef4444',
            opacity=0.8
        ))
        fig.add_trace(go.Scatter(
            x=years,
            y=profits,
            name='Net Profit',
            mode='lines+markers',
            line=dict(color='#667eea', width=3),
            marker=dict(size=10)
        ))
        
        fig.update_layout(
            title='Annual Financial Performance (Million USD)',
            xaxis_title='Year',
            yaxis_title='Amount (Million USD)',
            barmode='group',
            height=500,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e0e0'),
            legend=dict(bgcolor='rgba(0,0,0,0)')
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Yearly breakdown
        st.subheader("📅 Yearly Breakdown")
        for i, year in enumerate(years):
            year_data = pl_data[f"year_{i+1}"]
            profit_class = "profit-card" if year_data["profit"] > 0 else "loss-card"
            st.markdown(f"""
                <div class="project-card {profit_class}">
                    <h4>{year}</h4>
                    <p><strong>Revenue:</strong> ${year_data['revenue']:.1f}M | 
                    <strong>Cost:</strong> ${year_data['cost']:.1f}M | 
                    <strong>Profit:</strong> ${year_data['profit']:.1f}M</p>
                </div>
            """, unsafe_allow_html=True)
        
        # Projected performance for target country
        st.divider()
        st.subheader(f"📊 Projected Performance in {selected_country}")
        st.info(f"""
        Based on similarity analysis and current conditions in {selected_country}, 
        the projected ROI is estimated at **{roi * (similarity_score/100) * random.uniform(0.85, 1.15):.1f}%**.
        
        Key factors affecting projection:
        - Regulatory environment similarity: {random.randint(70, 95)}%
        - Economic conditions match: {random.randint(65, 90)}%
        - Geographic compatibility: {random.randint(80, 95)}%
        """)
    
    # Tab 4: Regulatory Evolution
    with tab4:
        st.header("📜 Regulatory Evolution Timeline")
        
        if not source_project:
            st.warning("Please select a source project from the sidebar.")
            return
        
        st.subheader(f"Regulatory Changes: {source_country} ({source_project['year']} - 2024)")
        
        # Timeline visualization
        evolution = source_project['regulatory_evolution']
        
        # Create timeline chart
        fig = go.Figure()
        
        years = [e['year'] for e in evolution]
        impacts = []
        for e in evolution:
            if "High" in e['impact'] or "Extended" in e['impact']:
                impacts.append(3)
            elif "Moderate" in e['impact'] or "Improved" in e['impact']:
                impacts.append(2)
            else:
                impacts.append(1)
        
        fig.add_trace(go.Scatter(
            x=years,
            y=impacts,
            mode='lines+markers',
            name='Regulatory Impact',
            line=dict(color='#667eea', width=3),
            marker=dict(size=15, color='#764ba2')
        ))
        
        fig.update_layout(
            title='Regulatory Evolution Impact Over Time',
            xaxis_title='Year',
            yaxis_title='Impact Level',
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e0e0'),
            yaxis=dict(tickmode='array', tickvals=[1, 2, 3], ticktext=['Low', 'Moderate', 'High'])
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Timeline events
        st.subheader("📅 Timeline Events")
        for event in evolution:
            impact_color = "#10b981" if "High" in event['impact'] or "Extended" in event['impact'] else "#f59e0b"
            st.markdown(f"""
                <div class="timeline-item" style="border-left-color: {impact_color};">
                    <h4>{event['year']}: {event['event']}</h4>
                    <p style="color: #b0b0b0;">{event['impact']}</p>
                </div>
            """, unsafe_allow_html=True)
        
        # Current regulatory status
        st.divider()
        st.subheader("🔄 Current Regulatory Status (2024)")
        if selected_country in CURRENT_CONDITIONS:
            current_reg = CURRENT_CONDITIONS[selected_country]
            st.markdown(f"""
                <div class="project-card">
                    <h4>{selected_country} - Current Framework</h4>
                    <p><strong>Regulatory Framework:</strong> {current_reg.get('Regulatory Framework', 'N/A')}</p>
                    <p><strong>Incentive Status:</strong> {current_reg.get('YEKDEM Incentive', current_reg.get('Government Support', 'N/A'))}</p>
                    <p><strong>Tax Incentive:</strong> {current_reg.get('Tax Incentive', 'N/A')}</p>
                </div>
            """, unsafe_allow_html=True)
        
        # Comparison
        st.subheader("📊 Regulatory Comparison: Then vs Now")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Then (Project Year):**")
            st.json(source_project['then_conditions'])
        with col2:
            st.write("**Now (2024):**")
            if selected_country in CURRENT_CONDITIONS:
                st.json(CURRENT_CONDITIONS[selected_country])
            else:
                st.info("Data not available for this country")
    
    # Tab 5: AI Simulation
    with tab5:
        st.header("🤖 Multi-AI Agent Simulation")
        st.caption("Watch the AI agents work in real-time (simulated)")
        
        # Simulation steps
        steps = [
            {"agent": "Researcher Agent", "action": "Scanning Official Gazettes", "status": "complete"},
            {"agent": "Data Parser", "action": "Extracting regulatory data", "status": "complete"},
            {"agent": "Knowledge Graph Builder", "action": "Building relationship graph", "status": "in_progress"},
            {"agent": "Gap Analysis Agent", "action": "Comparing regulations", "status": "pending"},
            {"agent": "Similarity Engine", "action": "Calculating cosine similarity", "status": "pending"},
            {"agent": "Policy Transfer Agent", "action": "Simulating policy transfer", "status": "pending"}
        ]
        
        # Animated progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, step in enumerate(steps):
            status_text.text(f"🔄 {step['agent']}: {step['action']}")
            progress_bar.progress((i + 1) / len(steps))
            time.sleep(0.5)
        
        status_text.success("✅ Analysis Complete!")
        
        # Tree of Thought visualization
        st.subheader("🌳 Tree of Thought - AI Reasoning Process")
        
        reasoning_tree = {
            "Root": f"Can project from {source_country} be transferred to {selected_country}?",
            "Branch 1": {
                "Regulatory": f"✅ Similar legal framework ({random.randint(75, 95)}% match)",
                "Economic": f"⚠️ Different incentive structure ({random.randint(60, 80)}% match)",
                "Geographic": f"✅ Comparable wind patterns ({random.randint(80, 95)}% match)"
            },
            "Branch 2": {
                "Policy Gap": "Missing equivalent incentive program",
                "Recommendation": "Implement adapted feed-in tariff system",
                "Expected Impact": f"+{random.randint(10, 20)}% project viability"
            }
        }
        
        col1, col2 = st.columns(2)
        with col1:
            st.json(reasoning_tree)
        
        with col2:
            # Visualization
            fig = go.Figure(go.Sunburst(
                labels=["Root", "Regulatory", "Economic", "Geographic", "Policy Gap", "Recommendation"],
                parents=["", "Root", "Root", "Root", "Root", "Policy Gap"],
                values=[100, 85, 65, 90, 50, 15],
                branchvalues="total",
                marker=dict(colors=['#667eea', '#10b981', '#f59e0b', '#10b981', '#ef4444', '#764ba2'])
            ))
            fig.update_layout(
                title="Decision Tree Visualization",
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e0e0e0')
            )
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
