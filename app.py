"""
import streamlit as st
import pandas as pd
import folium 
from streamlit_folium import st_folium


APP_TITLE = 'Food Access and Analysis'

def display_map():
    #df = df[df['State'] == state]

    m =folium.Map(location = [38,-96.5], zoom_start = 5, scrollWheelZoom = False)
    return m

def main():
    st.set_page_config(APP_TITLE)
    st.title(APP_TITLE)

    # Load Data
    df_main = pd.read_csv('s_master_dataset_only_common_counties.csv')

    st.write(df_main.head())
    st.write(df_main.shape)
    st.write(df_main.isna().sum())

    #Display filters and map
    state = 'Alabama'
    m = display_map()
    st_folium(m, width = 700, height = 500)

    # Display metrics



if __name__ == '__main__':
    main()

"""
import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
df = pd.read_csv("master_dataset_only_common_counties.csv")

st.title("Food Insecurity & Socioeconomic Dashboard")

# Sidebar controls
st.sidebar.header("Filters")

level = st.sidebar.radio("Select Level", ["County", "State"])

# Create a combined name column
df["County_State"] = df["County"] + ", " + df["State"]

# Select variable for ranking
metric = st.sidebar.selectbox(
    "Select Metric for Top 10",
    [
        "Overall Foo Insecurity Rate",
        "PovertyRate",
        "MedianFamilyIncome",
        "snap_participation_rate"
    ]
)

# Select variables for scatter plot
x_var = st.sidebar.selectbox("X-axis", df.select_dtypes(include='number').columns)
y_var = st.sidebar.selectbox("Y-axis", df.select_dtypes(include='number').columns)

# Aggregate if state level
if level == "State":
    df_grouped = df.groupby("State").mean(numeric_only=True).reset_index()
    df_grouped["Name"] = df_grouped["State"]
else:
    df_grouped = df.copy()
    df_grouped["Name"] = df_grouped["County_State"]

# Top 10
top10 = df_grouped.sort_values(metric, ascending=False).head(10)

st.subheader(f"Top 10 {level}s by {metric}")

# BAR CHART
fig_bar = px.bar(
    top10,
    x=metric,
    y="Name",
    orientation="h",
    hover_data={
        "Population": True if "Population" in df.columns else False,
        "PovertyRate": True,
        "MedianFamilyIncome": True
    },
    title=f"Top 10 {level}s by {metric}"
)

st.plotly_chart(fig_bar, use_container_width=True)

# SCATTER PLOT
st.subheader("Scatter Plot Analysis")

fig_scatter = px.scatter(
    df_grouped,
    x=x_var,
    y=y_var,
    hover_name="Name",
    size="Population" if "Population" in df.columns else None,
    color="PovertyRate" if "PovertyRate" in df.columns else None,
    title=f"{x_var} vs {y_var}"
)

st.plotly_chart(fig_scatter, use_container_width=True)

# DATA TABLE
st.subheader("Data Preview")
st.dataframe(top10)
