
import streamlit as st
import pandas as pd
import folium 
from streamlit_folium import st_folium
import plotly.express as px
import json
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
#from streamlit_extras.stylable_container import stylable_container

st.set_page_config(layout="wide")
st.markdown("""
    <h1 style='text-align: center;
               color: white;
               background: linear-gradient(100deg, #1f4037, #99f2c8);
               padding: 20px;
               border-radius: 12px;'>
        Food Insecurity & Food Desert Analytics Dashboard
    </h1>
""", unsafe_allow_html=True)

#st.title("Food Insecurity & Food Desert Analytics Dashboard")

# LOAD DATA
df = pd.read_csv("s_master_dataset_only_common_counties.csv")

# Load GeoJSON 
with open("geojson-counties-fips.json") as f:
    counties_geojson = json.load(f)

# Ensure FIPS is string
df["CountyFIPS"] = df["CountyFIPS"].astype(str).str.zfill(5)
df['Food_Insecurity_Rate'] = df['Overall Food Insecurity Rate']
df['Population'] = df['Pop2010']

# -----------------------------
# CREATE FOOD DESERT INDEX
# -----------------------------
# Normalize variables
df["norm_poverty"] = df["PovertyRate"] / df["PovertyRate"].max()
df["norm_snap"] = df["snap_participation_rate"] / df["snap_participation_rate"].max()
df["norm_income"] = 1 - (df["MedianFamilyIncome"] / df["MedianFamilyIncome"].max())

# Custom Index (you can tweak weights)
df["Food_Desert_Index"] = (
    0.4 * df["norm_poverty"] +
    0.3 * df["norm_snap"] +
    0.3 * df["norm_income"]
)

features = [
    "PovertyRate",
    "MedianFamilyIncome",
    "snap_participation_rate"
]

target = "Food_Insecurity_Rate"


df_ml = df.dropna(subset=features + [target])

X = df_ml[features]
y = df_ml[target]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestRegressor(n_estimators=100)
model.fit(X_train, y_train)

df["Predicted_Food_Insecurity"] = model.predict(df[features])


# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.header("Filters")

level = st.sidebar.radio('Select Level', ['County', 'State'])


metric = st.sidebar.selectbox(
    "Select Metric",
    [
        "Food_Desert_Index",
        "Food_Insecurity_Rate",
        "snap_participation_rate"
    ]
)
selected_states = st.sidebar.multiselect(
    "Select State(s)",
    options=sorted(df["State"].unique()),
    default=None
)
if selected_states:
    df = df[df["State"].isin(selected_states)]

# -----------------------------
# TOP COUNTIES
# -----------------------------

# Aggregate if state level
if level == "State":
    df_grouped = df.groupby("State").mean(numeric_only=True).reset_index()
    df_grouped["Name"] = df_grouped["State"]
else:
    df_grouped = df.copy()
    # df_grouped["County_State"] = df["County"] + ", " + df["State"]
    df_grouped["Name"] = df_grouped["County"]

top_n = st.sidebar.slider("Top N", 5, 20, 10)

if metric not in df_grouped.columns:
    st.error(f"{metric} not found in data")
else:
    top_df = df_grouped.sort_values(metric, ascending=False).head(top_n)
top_df = df_grouped.sort_values(metric, ascending=False).head(top_n)

# KPI cards with Food Insecurity, Food Desert Index, SNAP Participation, Risk Index and Populaiton

st.subheader("Key Insights")
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

col1, col2, col3, col4, col5 = st.columns(5)

with col1:kpi_card(
    "Avg Food Insecurity",
    f"{df['Food_Insecurity_Rate'].mean()*100:.2f}%", "#ff6b6b"
)

with col2: kpi_card(
    "Avg Food Desert Index",
    f"{df['Food_Desert_Index'].mean()*100:.2f}" ,"#4ecdc4"
)

with col3: kpi_card(
    "Avg SNAP Participation",
    f"{df['snap_participation_rate'].mean()*100:.2f}%", "#1a535c"
)

with col4: kpi_card(
    "Avg Food Insecurity Index",
    f"{df['food_insecurity_risk_index'].mean()*100:.2f}%","#ffa600"
)

with col5: kpi_card(
    "Total Population",
    f"{int(df['Population'].sum()):,}", "#6a4c93"
)


st.subheader(f"Top {top_n} {level} by {metric}")


y_col = 'Name'
fig_bar = px.bar(
    top_df,
    x=metric,
    y=y_col,
    orientation="h",
    hover_data=["Population", "PovertyRate", "MedianFamilyIncome"]
)

#st.plotly_chart(fig_bar, width='stretch')

# -----------------------------
# SCATTER PLOT
# -----------------------------
st.subheader("Scatter Analysis")

x_var = st.selectbox("X-axis", features)
y_var = st.selectbox("Y-axis", ["Food_Insecurity_Rate"])

fig_scatter = px.scatter(
    top_df,
    x=x_var,
    y=y_var,
    size="Population",
    color="Food_Desert_Index",
    hover_name="Name"
)
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_bar, width='stretch')

with col2:
    st.plotly_chart(fig_scatter, width='stretch')


#st.plotly_chart(fig_scatter, width='stretch')

# -----------------------------
# CHOROPLETH MAP
# -----------------------------
st.subheader("US Map with Counties")

fig_map = px.choropleth(
    df,
    geojson=counties_geojson,
    locations="CountyFIPS",
    color=metric,
    color_continuous_scale="YlOrRd",
    scope="usa",
    hover_data=[
        "County",
        "State",
        "Population",
        "PovertyRate",
        "MedianFamilyIncome",
        "Food_Desert_Index"
        
    ]
)

fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

st.plotly_chart(fig_map, width='stretch')



st.subheader("Poverty vs Food Insecurity")

fig_corr = px.scatter(
    df,
    x="PovertyRate",
    y="Food_Insecurity_Rate",
    trendline="ols",
    title="Higher Poverty → Higher Food Insecurity"
)

st.plotly_chart(fig_corr, use_container_width=True)

# -----------------------------
# MODEL PERFORMANCE
# -----------------------------
st.subheader("Model Insights")

st.write("Feature Importance:")

importance_df = pd.DataFrame({
    "Feature": features,
    "Importance": model.feature_importances_
})

fig_imp = px.bar(importance_df, x="Feature", y="Importance")
st.plotly_chart(fig_imp, use_container_width=True)
