import streamlit as st
import pandas as pd
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
df['Vulnerability Score'] = ((df['Vulnerability_Score_PCA']).round(2)).copy()
df['snap_participation_rate'] = (df['snap_participation_rate']*100).round(2)
df['food_insecurity_risk_index'] = (df['food_insecurity_risk_index']*100).round(2)
df["unemployment_rate"] = (df["unemployment_rate"]*100).round(2)
df['no_vehicle_rate'] = (df["no_vehicle_rate"]*100).round(2)

state_level_count = pd.read_csv("county_level_count.csv")
county_level_count = pd.read_csv("food_deserts_count.csv")

# Load GeoJSON 
with open("geojson-counties-fips.json") as f:
    counties_geojson = json.load(f)

# Map state names to abbreviations
# Reason: locationmode="USA-states" only supports state abbreviations 
us_state_abbrev = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY"
}

df["State_code"] = df["State"].map(us_state_abbrev)
# SIDEBAR
st.subheader("Filter data based on state filter selection")

selected_states = st.multiselect(
    "Select State(s)",
    options=sorted(df["State"].unique()),
    default=None
)

if selected_states:
    df = df[df["State"].isin(selected_states)]

st.markdown('#####')
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
    kpi_card("Population",
                f"{int(df['Population'].sum()):,}", "#6a4c93")

with col2:
    kpi_card("Number of Counties",
                f"{len(df)}", "#ffa600")

with col3:
    kpi_card("SNAP",
                f"{df['snap_participation_rate'].mean():.2f}%", "#1a535c")

with col4:
    kpi_card("Vulnerability",
                f"{df['Vulnerability Score'].mean():.2f}%", "#4ecdc4")
    
with col5:
    
    kpi_card("Food Insecurity",
                f"{df['Food Insecurity Rate'].mean():.2f}%", "#ff6b6b")
st.markdown('####')
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview",
    "State Breakdown",
    "Drivers",
    "Map",
    "Insights"
])

#Tab 1: Overview 

with tab1:  # or whatever position you gave

    if df is not None:

        metrics = ["MedianFamilyIncome", "PovertyRate", "unemployment_rate", 
                "Cost Per Meal", "SNAP Participation Rate", "# of Food Insecure Persons Overall", 
                "no_vehicle_rate", "Population, low access to store (%), 2019", 
                "Children, low access to store (%), 2019", "Seniors, low access to store (%), 2019", 
                "White, low access to store (%), 2019", "Black, low access to store (%), 2019", 
                "Hispanic ethnicity, low access to store (%), 2019", "Asian, low access to store (%), 2019",
                "American Indian or Alaska Native, low access to store (%), 2019", 
                "Hawaiian or Pacific Islander, low access to store (%), 2019", "obesity_pct", "diabetes_pct"]

        available_metrics = [m for m in metrics if m in df.columns]

        col1, col2 = st.columns([1, 1], gap="large")

        # LEFT: MAP
        with col1:
            st.subheader("Nationwide Spatial Distribution")

            selected_metric = st.selectbox(
                "Choose Metric",
                available_metrics,
                key="metric_select"
            )

            df_state = df.groupby(
                ["State", "State_code"], as_index=False
            )[selected_metric].mean()

            fig = px.choropleth(
                df_state,
                locations="State_code",
                locationmode="USA-states",
                color=selected_metric,
                scope="usa",
                color_continuous_scale="blues",
                hover_data=['State', selected_metric]
            )

            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig, use_container_width=True)

        # RIGHT: HISTOGRAM
        with col2:
            st.subheader("Statewide Metric Distribution")

            if selected_states == "All States":
                    df_filtered = df.copy()
                    title_suffix = "Across all US Counties"
            else:
                df_filtered = df[df["State"].isin(selected_states)]
                title_suffix = f"in {selected_states}"
            fig_hist = px.histogram(
                df_filtered,   
                x=selected_metric,
                nbins=30,
                title=f"Distribution of {selected_metric}",
                color_discrete_sequence=["#eee600"]
            )

            fig_hist.update_layout(
                showlegend=False,
                margin=dict(l=20, r=20, t=50, b=20),
                height=400
            )

            st.plotly_chart(fig_hist, use_container_width=True)

with tab2:
    
    level = st.radio('Select Level', ['County', 'State'], horizontal=True)
    top_n = st.slider("Top N", 5, 20, 10)
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top Vulnerable Regions")

        # Aggregate if state level
        if level == "State":
            df_grouped = df.groupby("State").mean(numeric_only=True).round(2).reset_index()
            df_grouped["Name"] = df_grouped["State"]
        else:
            df_grouped = df.copy()
            # df_grouped["County_State"] = df["County"] + ", " + df["State"]
            df_grouped["Name"] = df_grouped["County"]

        metric = st.selectbox(
            "Select Metric",
            [
                "Vulnerability Score",
                "Food Insecurity Rate",
                "snap_participation_rate"
            ],
            key="bar_metric"
        )
         #st.subheader(f"Top {top_df} {level} by {metric}")
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
            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
            

            st.plotly_chart(fig_bar, width='stretch')

    with col2:
        #levels = st.radio('Select Level', ['County', 'State'], horizontal=True,key="level_selector_main")
        st.subheader("Top Food desert Count by Definitions")
        food_desert_map = {
            "Food Desert Count (0.5 & 10 miles)": {"County" : "LILATracts_halfAnd10", 
                                                "State" : "LILATracts_halfAnd10_flag"},
            "Food Desert Count (1 & 10 miles)": {"County" : "LILATracts_1And10", 
                                                "State" : "LILATracts_1And10_flag"},
            "Food Desert Count (1 & 20 miles)": {"County" : "LILATracts_1And20", 
                                                "State" : "LILATracts_1And20_flag"},
            "Food Desert Count (Vehicle)": {"County" : "LILATracts_Vehicle", 
                                                "State" : "LILATracts_Vehicle_flag"}
        }
        food_metric = st.selectbox(
            "Select Metric to Rank",
            [ 
                "Food Desert Count (0.5 & 10 miles)", 
                "Food Desert Count (1 & 10 miles)", 
                "Food Desert Count (1 & 20 miles)", 
                "Food Desert Count (Vehicle)"
            ],
            key="bar_metric_main"
        )
        #top_n = st.slider("Top N", 5, 20, 10)
        target_col = food_desert_map[food_metric][level]
                
        if level == "State":
            top_df = state_level_count.sort_values(target_col, ascending=False).head(top_n)
            top_df["Name"] = top_df["State"]
            hover_cols = [target_col] 
        else:
            # Create a temporary copy of the county counts
            temp_county_df = county_level_count.copy()
        
            # Filter the data 
            if selected_states:
                temp_county_df = temp_county_df[temp_county_df["State"].isin(selected_states)]
        
            # Sort 
            top_df = temp_county_df.sort_values(target_col, ascending=False).head(top_n)
            top_df["Name"] = top_df["County"] + ", " + top_df["State"]
            hover_cols = ["State", target_col]
        valid_hover_cols = [c for c in hover_cols if c in top_df.columns]
        fig_bar = px.bar(
            top_df,
            x=target_col,
            y='Name',
            orientation="h",
            hover_data=valid_hover_cols, 
            labels={
                
                target_col: food_metric
            }
        )
        # Make the chart shows the highest value at the top
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
            
        st.plotly_chart(fig_bar, use_container_width=True)


    st.subheader("Data Summary")
    
    st.dataframe(df_grouped, use_container_width=True, height=450)

#Tab 2 Drivers
with tab3:

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
            df_grouped,
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
            "Vulnerability Score"
        ]].corr().round(2)

        fig_heat = px.imshow(corr, text_auto=True, color_continuous_scale="Viridis")
        st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("""
        **Insight:** Poverty and income are the strongest drivers of food insecurity.
        """)
    
# Tab 3 MAP
with tab4:

    st.subheader("Geographic Distribution")

    # ✅ Metric selector (fixes undefined variable bug)
    map_metric = st.selectbox(
        "Select Metric for Map",
        [
            "Food Insecurity Rate",
            "Vulnerability Score",
            "PovertyRate",
            "snap_participation_rate"
        ],
        key="map_metric"
    )

    # ✅ Filter data safely
    df_filtered = df.copy()
    if selected_states:
        df_filtered = df_filtered[df_filtered["State"].isin(selected_states)]

    # ✅ Check data
    if df_filtered.empty:
        st.warning("No data available for selected states")
        st.stop()

    if map_metric not in df_filtered.columns:
        st.error(f"{map_metric} not found in dataset")
        st.stop()

    fig_map = px.choropleth(
        df_filtered,
        geojson=counties_geojson,
        locations="CountyFIPS",
        #featureidkey="id",  # 🔥 CRITICAL FIX
        color=map_metric,
        color_continuous_scale="Reds",
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

    fig_map.update_geos(
        fitbounds="locations" if selected_states else None,
        visible=False
    )

    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    st.plotly_chart(fig_map, use_container_width=True, height=700)


# tab4 INSIGHTS
with tab5:

    col1, col2 = st.columns(2)
    with col1:

        df["Risk_Level"] = pd.qcut(
            df["Vulnerability Score"],
            q=3,
            labels=["Low", "Medium", "High"]
        )
        st.subheader("Food Insecurity Distribution by Risk Level")

        fig_box = px.box(
            df,
            x="Risk_Level",
            y="Food Insecurity Rate",
            color="Risk_Level",
            points="outliers",
            color_discrete_map= { 
                "Low" : "#8DD3C7",
                "Medium" : "#E3E318", 
                "High" : "#FB8072" 
            }
            
        )

        st.plotly_chart(fig_box, use_container_width=True)
    
    with col2:
        df["Income_Group"] = pd.qcut(df["MedianFamilyIncome"], q=3, labels=["Low", "Mid", "High"])
        st.subheader("Risk Level Comaprison by Income Groups")

        fig_stack = px.histogram(
            df,
            x="Income_Group",
            color="Risk_Level",
            barmode="stack",
            category_orders={
                "Income_Group": ["Low", "Mid", "High"],
                "Risk_Level": ["Low Risk", "Medium Risk", "High Risk"] 
                },
                color_discrete_map= { 
                    "Low" : "#8DD3C7",
                    "Medium" : "#E3E318", 
                    "High" : "#FB8072" 
                }
        )

        st.plotly_chart(fig_stack, use_container_width=True)

    st.markdown(""" ## Policy Insights""")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
            ### Key Findings:
            - High food insecurity strongly correlates with poverty levels
            - Vulnerability clusters in specific geographic regions
            - SNAP participation alone is insufficient """)

    with col2:
        st.markdown("""
            ### Recommendations:
            1. Expand SNAP coverage in high-risk counties
            2. Improve food access infrastructure (transport, stores)
            3. Combine income support + food programs """)

    
    st.markdown(""" ### Impact: 
                Targeting top 10% vulnerable counties could significantly reduce national food insecurity rates.
        """)
