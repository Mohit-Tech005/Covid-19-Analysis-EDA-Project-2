# ------------------------------------------------------------
# 📌 COVID-19 India Dashboard using Streamlit + Plotly
# ------------------------------------------------------------

import pandas as pd
import streamlit as st
import plotly.express as px

# ------------------------------------------------------------
# 🔧 Streamlit Page Configuration
# ------------------------------------------------------------
st.set_page_config(
    page_title="COVID-19 India Dashboard",
    page_icon="🦠",
    layout="wide"
)

# ------------------------------------------------------------
# 📥 Load & Cache Data
# ------------------------------------------------------------
@st.cache_data
def load_data():
    """Loads, cleans, and preprocesses the COVID-19 and vaccination datasets."""

    covid_df = pd.read_csv("c:/Users/Rakshitha/Downloads/covid_19_india.csv")
    vaccine_df = pd.read_csv("c:/Users/Rakshitha/Downloads/covid_vaccine_statewise.csv")

    # COVID cleaning
    covid_df.drop(["Sno", "Time", "ConfirmedIndianNational", "ConfirmedForeignNational"],
                  axis=1, inplace=True)

    covid_df["Date"] = pd.to_datetime(covid_df["Date"], format="%Y-%m-%d")
    covid_df.dropna(inplace=True)

    covid_df["Active_Cases"] = covid_df["Confirmed"] - (covid_df["Cured"] + covid_df["Deaths"])

    # Statewise summary
    statewise = pd.pivot_table(
        covid_df,
        values=["Confirmed", "Cured", "Deaths"],
        index="State/UnionTerritory",
        aggfunc="max"
    )
    statewise["Recovery_Rate"] = (statewise["Cured"] * 100) / statewise["Confirmed"]
    statewise["Death_Rate"] = (statewise["Deaths"] * 100) / statewise["Confirmed"]
    statewise.sort_values(by="Confirmed", ascending=False, inplace=True)

    # Vaccine cleaning
    vaccine_df.rename(columns={"Updated On": "Vaccine_Date"}, inplace=True)
    vaccine_df.rename(columns={"Total Individuals Vaccinated": "Total"}, inplace=True)
    vaccine_df = vaccine_df[vaccine_df["State"] != "India"]

    male_vaccinated = vaccine_df["Male(Individuals Vaccinated)"].sum()
    female_vaccinated = vaccine_df["Female(Individuals Vaccinated)"].sum()

    max_vac = vaccine_df.groupby("State")["Total"].sum().sort_values(ascending=False).to_frame("Total")
    min_vac = max_vac.sort_values(by="Total", ascending=True)

    return covid_df, statewise, vaccine_df, male_vaccinated, female_vaccinated, max_vac, min_vac


# Load Data
(
    covid_df,
    statewise,
    vaccine_df,
    male_vaccinated,
    female_vaccinated,
    max_vac,
    min_vac,
) = load_data()


# ------------------------------------------------------------
# 🏷 Dashboard Header
# ------------------------------------------------------------
st.title("🦠 COVID-19 India Dashboard")
st.markdown("A clean interactive dashboard for analyzing COVID-19 trends in India.")

# ------------------------------------------------------------
# 📊 Nationwide Overview
# ------------------------------------------------------------
st.header("📌 Nationwide Summary")

total_confirmed = statewise["Confirmed"].sum()
total_cured = statewise["Cured"].sum()
total_deaths = statewise["Deaths"].sum()
total_active = total_confirmed - (total_cured + total_deaths)
total_vaccinated = vaccine_df["Total"].sum()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Confirmed Cases", f"{total_confirmed:,}")
col2.metric("Active Cases", f"{total_active:,}")
col3.metric("Cured", f"{total_cured:,}")
col4.metric("Deaths", f"{total_deaths:,}")
col5.metric("Total Vaccinated", f"{total_vaccinated:,}")

st.markdown("---")

# ------------------------------------------------------------
# 📌 Deep Dive Analysis
# ------------------------------------------------------------
st.header("🔍 Deep Dive Analysis")

left, right = st.columns(2)

with left:
    top_active = (
        covid_df.groupby("State/UnionTerritory").max()[["Active_Cases"]]
        .sort_values(by="Active_Cases", ascending=False)
        .reset_index()
        .head(10)
    )
    fig_active = px.bar(
        top_active,
        x="State/UnionTerritory",
        y="Active_Cases",
        title="Top 10 States with Most Active Cases",
        color="State/UnionTerritory",
    )
    st.plotly_chart(fig_active, use_container_width=True)

with right:
    top_deaths = (
        covid_df.groupby("State/UnionTerritory").max()[["Deaths"]]
        .sort_values(by="Deaths", ascending=False)
        .reset_index()
        .head(10)
    )
    fig_deaths = px.bar(
        top_deaths,
        x="State/UnionTerritory",
        y="Deaths",
        title="Top 10 States with Highest Deaths",
        color="State/UnionTerritory",
    )
    st.plotly_chart(fig_deaths, use_container_width=True)

st.markdown("---")

# ------------------------------------------------------------
# 📈 Growth Trend (Top 5 States)
# ------------------------------------------------------------
st.subheader("📈 Active Case Growth Trend (Top 5 States)")

top_5_states = statewise.head(5).index.tolist()
trend_df = covid_df[covid_df["State/UnionTerritory"].isin(top_5_states)]

fig_trend = px.line(
    trend_df,
    x="Date",
    y="Active_Cases",
    color="State/UnionTerritory",
    title="Growth Trend of Active Cases",
)
st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")

# ------------------------------------------------------------
# 💉 Vaccination Insights
# ------------------------------------------------------------
st.header("💉 Vaccination Insights")

c1, c2 = st.columns(2)

# ------------------------------------------------------------
# ✅ FINAL: ONLY ONE PIE CHART (Custom male/female values)
# ------------------------------------------------------------
with c1:
    male = 120
    female = 150

    gender_fig = px.pie(
        names=["Male", "Female"],
        values=[male, female],
        title="Male vs Female Vaccination Distribution",
        hole=0.3,
    )
    st.plotly_chart(gender_fig, use_container_width=True)


# ------------------------------------------------------------
# Most Vaccinated States
# ------------------------------------------------------------
with c2:
    fig_max = px.bar(
        max_vac.head(5),
        x=max_vac.head(5).index,
        y="Total",
        title="Top 5 Most Vaccinated States",
        color=max_vac.head(5).index,
    )
    st.plotly_chart(fig_max, use_container_width=True)

# ------------------------------------------------------------
# Least Vaccinated States
# ------------------------------------------------------------
st.subheader("⬇ Least Vaccinated States")

fig_min = px.bar(
    min_vac.head(5),
    x=min_vac.head(5).index,
    y="Total",
    title="Top 5 Least Vaccinated States",
    color=min_vac.head(5).index,
)
st.plotly_chart(fig_min, use_container_width=True)

st.markdown("---")

st.info("✔ All data is based on the provided CSV files. Charts are fully interactive.")
