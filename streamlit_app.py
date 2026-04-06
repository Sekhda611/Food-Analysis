import streamlit as st
import pandas as pd
import folium 
from streamlit_folium import st_folium
import plotly.express as px
import json
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

st.set_page_config(layout="wide")

st.title("Food Insecurity & Food Desert Analytics Dashboard")

# LOAD DATA
df = pd.read_csv("s_master_dataset_only_common_counties.csv")

# Load GeoJSON (you need US counties geojson file)
with open("st.set_page_config(layout="wide")

st.title("Food Insecurity & Food Desert Analytics Dashboard")

# LOAD DATA
df = pd.read_csv("s_master_dataset_only_common_counties.csv")

# Load GeoJSON (you need US counties geojson file)
with open("geojson-counties-fips.json") as f:
    counties_geojson = json.load(f)

# Ensure FIPS is string
df["CountyFIPS"] = df["CountyFIPS"].astype(str).str.zfill(5)

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

# -----------------------------
# MACHINE LEARNING MODEL
# -----------------------------
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
st.sidebar.header("Controls")

metric = st.sidebar.selectbox(
    "Select Metric",
    [
        "Food_Desert_Index",
        "Food_Insecurity_Rate",
        "Predicted_Food_Insecurity"
    ]
)

top_n = st.sidebar.slider("Top N", 5, 20, 10)

# -----------------------------
# TOP COUNTIES
# -----------------------------
df["County_State"] = df["County"] + ", " + df["State"]

top_df = df.sort_values(metric, ascending=False).head(top_n)

st.subheader(f"Top {top_n} Counties by {metric}")

fig_bar = px.bar(
    top_df,
    x=metric,
    y="County_State",
    orientation="h",
    hover_data=["Population", "PovertyRate", "MedianFamilyIncome"]
)

st.plotly_chart(fig_bar, use_container_width=True)

# -----------------------------
# CHOROPLETH MAP
# -----------------------------
st.subheader("US Choropleth Map")

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
        "Food_Desert_Index",
        "Predicted_Food_Insecurity"
    ]
)

fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

st.plotly_chart(fig_map, use_container_width=True)

# -----------------------------
# SCATTER PLOT
# -----------------------------
st.subheader("Scatter Analysis")

x_var = st.selectbox("X-axis", features)
y_var = st.selectbox("Y-axis", ["Food_Insecurity_Rate", "Predicted_Food_Insecurity"])

fig_scatter = px.scatter(
    df,
    x=x_var,
    y=y_var,
    size="Population",
    color="Food_Desert_Index",
    hover_name="County_State"
)

st.plotly_chart(fig_scatter, use_container_width=True)

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

# -----------------------------
# DATA TABLE
# -----------------------------
st.subheader("Data Preview")
st.dataframe(df.head(50))") as f:
    counties_geojson = json.load(f)

# Ensure FIPS is string
df["CountyFIPS"] = df["CountyFIPS"].astype(str).str.zfill(5)

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

# -----------------------------
# MACHINE LEARNING MODEL
# -----------------------------
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
st.sidebar.header("Controls")

metric = st.sidebar.selectbox(
    "Select Metric",
    [
        "Food_Desert_Index",
        "Food_Insecurity_Rate",
        "Predicted_Food_Insecurity"
    ]
)

top_n = st.sidebar.slider("Top N", 5, 20, 10)

# -----------------------------
# TOP COUNTIES
# -----------------------------
df["County_State"] = df["County"] + ", " + df["State"]

top_df = df.sort_values(metric, ascending=False).head(top_n)

st.subheader(f"Top {top_n} Counties by {metric}")

fig_bar = px.bar(
    top_df,
    x=metric,
    y="County_State",
    orientation="h",
    hover_data=["Population", "PovertyRate", "MedianFamilyIncome"]
)

st.plotly_chart(fig_bar, use_container_width=True)

# -----------------------------
# CHOROPLETH MAP
# -----------------------------
st.subheader("US Choropleth Map")

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
        "Food_Desert_Index",
        "Predicted_Food_Insecurity"
    ]
)

fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

st.plotly_chart(fig_map, use_container_width=True)


# SCATTER PLOT
st.subheader("Scatter Analysis")

x_var = st.selectbox("X-axis", features)
y_var = st.selectbox("Y-axis", ["Food_Insecurity_Rate", "Predicted_Food_Insecurity"])

fig_scatter = px.scatter(
    df,
    x=x_var,
    y=y_var,
    size="Population",
    color="Food_Desert_Index",
    hover_name="County_State"
)

st.plotly_chart(fig_scatter, use_container_width=True)

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

# -----------------------------
# DATA TABLE
# -----------------------------
st.subheader("Data Preview")
st.dataframe(df.head(50))
