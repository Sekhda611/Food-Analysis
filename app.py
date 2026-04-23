import streamlit as st
import pandas as pd
import folium 
from streamlit_folium import st_folium
import plotly.express as px
import json

st.set_page_config(layout="wide")

st.markdown("""
    <h1 style='text-align: center;
               color: white;
               background: linear-gradient(120deg, #1f4037, #99f2c8);
               padding: 20px;
               border-radius: 12px;'>
        Socioeconomic Spatial Analysis of US Food Access
    </h1>
""", unsafe_allow_html=True)

#load data set
def load_data():
    return(pd.read_csv('master_dataset_only_common_counties.csv'))

df = load_data()
# Ensure FIPS is string
df["CountyFIPS"] = df["CountyFIPS"].astype(str).str.zfill(5)
df['Food Insecurity Rate'] =(df['Overall Food Insecurity Rate']*100).round(2)
df['Population'] = df['Pop2010'].round(1)
df['Food Access Vulnerability Rate'] = ((df['Vulnerability_Score_PCA']).round(2)).copy()
df['snap_participation_rate'] = (df['snap_participation_rate']*100).round(2)
df['food_insecurity_risk_index'] = (df['food_insecurity_risk_index']*100).round(2)

# Load GeoJSON 
with open("geojson-counties-fips.json") as f:
    counties_geojson = json.load(f)

#Data preview
st.subheader('Data Preview')
st.dataframe(df.head(5))

# SIDEBAR
st.sidebar.header("Filters")

level = st.sidebar.radio('Select Level', ['County', 'State'])

selected_states = st.sidebar.multiselect(
    "Select State(s)",
    options=sorted(df["State"].unique()),
    default=None
)

if selected_states:
    df = df[df["State"].isin(selected_states)]

# Aggregate if state level
if level == "State":
    df_grouped = df.groupby("State").mean(numeric_only=True).round(2).reset_index()
    df_grouped["Name"] = df_grouped["State"]
else:
    df_grouped = df.copy()
    # df_grouped["County_State"] = df["County"] + ", " + df["State"]
    df_grouped["Name"] = df_grouped["County"]

top_n = st.sidebar.slider("Top N", 5, 20, 10)

tab1, tab2, tab3, tab4 = st.tabs([
    "Overview",
    "Drivers",
    "Map",
    "Insights"
])

#Tab 1: Overview 
with tab1:
    st.markdown('###')
    st.subheader("Key Insights")

    col1, col2, col3, col4, col5 = st.columns(5)
    def kpi_card(title, value, color):
        st.markdown(f"""
            <div style="
                background: {color};
                padding: 14px;
                border-radius: 10px;
                text-align: center;
                color: white;
                box-shadow: 2px 2px 8px rgba(0,0,0,0.15);
            ">
                <h5 style='margin-bottom:5px'>{title}</h5>
                <h2>{value}</h2>
            </div>
        """, unsafe_allow_html=True)

    with col1:
        kpi_card("Food Insecurity",
                    f"{df['Food Insecurity Rate'].mean():.2f}%", "#ff6b6b")

    with col2:
        kpi_card("Vulnerability",
                    f"{df['Food Access Vulnerability Rate'].mean():.2f}", "#4ecdc4")

    with col3:
        kpi_card("SNAP",
                    f"{df['snap_participation_rate'].mean():.2f}%", "#1a535c")

    with col4:
        kpi_card("Risk Index",
                    f"{df['food_insecurity_risk_index'].mean():.2f}%", "#ffa600")

    with col5:
        kpi_card("Population",
                    f"{int(df['Population'].sum()):,}", "#6a4c93")

    st.markdown("---")
    st.subheader("Top Vulnerable Regions")
    metric = st.selectbox(
        "Select Metric",
        [
            "Food Access Vulnerability Rate",
            "Food Insecurity Rate",
            "snap_participation_rate"
        ],
        key="bar_metric"
    )
       
    st.subheader(f"Top {top_n} {level} by {metric}")
    if metric not in df_grouped.columns:
        st.error(f"{metric} not found in data")
    else:
        top_df = df_grouped.sort_values(metric, ascending=False).round(2).head(top_n)
    
    y_col = 'Name'
    fig_bar = px.bar(
        top_df,
        x=metric,
        y=y_col,
        orientation="h",
        hover_data=["Population", "PovertyRate", "MedianFamilyIncome"]
    )

    st.plotly_chart(fig_bar, width='stretch')
#Tab 2 Drivers
with tab2:

    st.subheader("What Drives Food Insecurity?")
    df['PovertyRate'] = df['PovertyRate'].round(2)
    df['MedianFamilyIncome'] = df['MedianFamilyIncome'].round(2)
    features = [
        "PovertyRate",
        "MedianFamilyIncome",
        "snap_participation_rate"
    ]

    target = "Food Insecurity Rate"

    col1, col2 = st.columns(2)

    # Scatter
    with col1:

        st.subheader("Scatter Analysis")
        c1, c2 = st.columns(2)
        with c1:
            x_var = st.selectbox(
                "X-axis",
                features,
            key="scatter_x"
            )

        with c2:
            y_var = st.selectbox(
            "Y-axis",
            ["Food Insecurity Rate"],
            key="scatter_y"
        )

        fig_scatter = px.scatter(
            top_df,
            x=x_var,
            y=y_var,
            size="Population",
            color="food_insecurity_risk_index",
            hover_name="Name"
        )

        st.plotly_chart(fig_scatter, width='stretch')

    # Heatmap
    
    with col2:
       
        st.subheader('Correlation heatmap')
        st.markdown("###")
        corr = df[[
            "PovertyRate",
            "Food Insecurity Rate",
            "MedianFamilyIncome",
            "snap_participation_rate",
            "Food Access Vulnerability Rate"
        ]].corr().round(2)

        fig_heat = px.imshow(corr, text_auto=True, color_continuous_scale="Viridis")
        st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("""
        **Insight:** Poverty and income are the strongest drivers of food insecurity.
        """)
    
# Tab 3 MAP
with tab3:

    st.subheader("Geographic Distribution")

    fig_map = px.choropleth(
        df,
        geojson=counties_geojson,
        locations="CountyFIPS",
        color=metric,
        color_continuous_scale=[
            [0, "#fff5eb"],
            [0.5, "#fd8d3c"],
            [1, "#bd0026"]
        ],
        scope="usa",
        hover_data=[
            "County",
            "State",
            "Population",
            "PovertyRate",
            "MedianFamilyIncome",
            "Food Insecurity Rate"
            
        ]

    )

    if selected_states:
        fig_map.update_geos(fitbounds="locations", visible=False)
    else:
        fig_map.update_geos(visible=False)
    st.plotly_chart(fig_map, use_container_width=True, height=700)

# tab4 INSIGHTS
with tab4:

    df["Risk_Level"] = pd.qcut(
        df["Food Access Vulnerability Rate"],
        q=3,
        labels=["Low", "Medium", "High"]
    )
    st.subheader("Food Insecurity Distribution by Risk Level")

    fig_box = px.box(
        df,
        x="Risk_Level",
        y="Food Insecurity Rate",
        color="Risk_Level",
        points="outliers"
    )

    st.plotly_chart(fig_box, use_container_width=True)
    
    df["Income_Group"] = pd.qcut(df["MedianFamilyIncome"], q=3, labels=["Low", "Mid", "High"])

    fig_stack = px.histogram(
        df,
        x="Income_Group",
        color="Risk_Level",
        barmode="stack"
    )

    st.plotly_chart(fig_stack, use_container_width=True)
    st.markdown("""
        ## Policy Insights

        ### Key Findings:
        - High food insecurity strongly correlates with poverty levels
        - Vulnerability clusters in specific geographic regions
        - SNAP participation alone is insufficient

        ### Recommendations:
        1. Expand SNAP coverage in high-risk counties
        2. Improve food access infrastructure (transport, stores)
        3. Combine income support + food programs

        ### Impact:
        Targeting top 10% vulnerable counties could significantly reduce national food insecurity rates.
        """)
    
