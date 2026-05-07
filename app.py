import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Aviation Leasing Dashboard", layout="wide")

st.title("✈️ Aviation Leasing Market Dashboard")
st.markdown("Analysing fleet composition, aircraft values and lessee credit risk")

# --- DATA ---
fleet_data = pd.DataFrame({
    "Airline": ["Ryanair", "Delta", "Emirates", "Southwest", "IndiGo",
                "IAG", "Air France-KLM", "AirAsia", "United", "Lufthansa"],
    "Fleet Size": [584, 960, 260, 770, 330, 544, 550, 225, 940, 763],
    "Avg Age (Years)": [6.5, 16.2, 10.1, 13.4, 4.2, 12.8, 11.9, 7.3, 17.1, 13.2],
    "% Leased": [52, 48, 25, 83, 92, 65, 58, 95, 61, 44],
    "Region": ["Europe", "North America", "Middle East", "North America", "Asia",
               "Europe", "Europe", "Asia", "North America", "Europe"]
})

aircraft_mix = pd.DataFrame({
    "Airline": ["Ryanair", "Delta", "Emirates", "Southwest", "IndiGo",
                "IAG", "Air France-KLM", "AirAsia", "United", "Lufthansa"],
    "Narrowbody %": [100, 62, 0, 100, 100, 74, 61, 100, 67, 58],
    "Widebody %": [0, 38, 100, 0, 0, 26, 39, 0, 33, 42],
})

aircraft_types = {
    "A320neo":  {"base_value": 108, "depreciation": 0.055, "monthly_lease": 390},
    "A321neo":  {"base_value": 130, "depreciation": 0.050, "monthly_lease": 470},
    "B737 MAX8":{"base_value": 110, "depreciation": 0.057, "monthly_lease": 395},
    "A350-900": {"base_value": 317, "depreciation": 0.045, "monthly_lease": 1050},
    "B787-9":   {"base_value": 292, "depreciation": 0.048, "monthly_lease": 950},
}

years = list(range(0, 26))
value_rows = []
for aircraft, info in aircraft_types.items():
    for year in years:
        value = info["base_value"] * ((1 - info["depreciation"]) ** year)
        value_rows.append({
            "Aircraft": aircraft,
            "Age (Years)": year,
            "Value ($M)": round(value, 1),
            "Monthly Lease Rate ($K)": info["monthly_lease"]
        })
value_df = pd.DataFrame(value_rows)

credit_data = pd.DataFrame({
    "Airline": ["Ryanair", "Delta", "Emirates", "Southwest", "IndiGo",
                "IAG", "Air France-KLM", "AirAsia", "United", "Lufthansa"],
    "Debt/Equity Ratio": [1.2, 3.8, 1.5, 2.1, 4.2, 3.5, 3.9, 5.1, 4.6, 2.8],
    "Operating Margin %": [18, 12, 9, 11, 8, 7, 5, 6, 11, 6],
    "Revenue Growth %": [12, 8, 15, 5, 22, 6, 4, 18, 7, 3],
    "Interest Coverage": [8.2, 3.1, 5.4, 4.2, 2.8, 2.5, 2.1, 1.8, 2.9, 3.4],
})

# Credit score: higher is safer for lessor
credit_data["Credit Score"] = (
    (10 - credit_data["Debt/Equity Ratio"]) * 0.3 +
    credit_data["Operating Margin %"] * 0.3 +
    credit_data["Revenue Growth %"] * 0.2 +
    credit_data["Interest Coverage"] * 0.2
).round(2)

credit_data["Risk Rating"] = credit_data["Credit Score"].apply(
    lambda x: "🟢 Low Risk" if x > 6 else "🟡 Medium Risk" if x > 4 else "🔴 High Risk"
)

tab1, tab2, tab3, tab4 = st.tabs([
    "Market Overview",
    "Fleet Analysis",
    "Aircraft Value Curves",
    "Lessee Credit Risk"
])

with tab1:
    st.header("Market Overview")
    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.bar(
            fleet_data.sort_values("Fleet Size", ascending=True),
            x="Fleet Size", y="Airline", orientation="h",
            title="Fleet Size by Airline", color="Region",
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.bar(
            fleet_data.sort_values("% Leased", ascending=True),
            x="% Leased", y="Airline", orientation="h",
            title="% of Fleet Leased by Airline", color="Region",
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.info("💡 **Key Insight:** Asian carriers like AirAsia and IndiGo lease over 90% of their fleets — making them heavily dependent on lessors like AerCap and SMBC.")

with tab2:
    st.header("Fleet Analysis")

    selected_airline = st.selectbox("Select an Airline", fleet_data["Airline"])
    airline_row = fleet_data[fleet_data["Airline"] == selected_airline].iloc[0]
    mix_row = aircraft_mix[aircraft_mix["Airline"] == selected_airline].iloc[0]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Fleet Size", f"{int(airline_row['Fleet Size'])} aircraft")
    with col2:
        avg_age = airline_row["Avg Age (Years)"]
        age_color = "🟢" if avg_age < 8 else "🟡" if avg_age < 13 else "🔴"
        st.metric("Average Fleet Age", f"{age_color} {avg_age} years")
    with col3:
        st.metric("% Leased", f"{int(airline_row['% Leased'])}%")

    col1, col2 = st.columns(2)
    with col1:
        mix_df = pd.DataFrame({
            "Type": ["Narrowbody", "Widebody"],
            "Percentage": [mix_row["Narrowbody %"], mix_row["Widebody %"]]
        })
        fig3 = px.pie(mix_df, names="Type", values="Percentage",
                      title=f"{selected_airline} — Narrowbody vs Widebody Split",
                      color_discrete_sequence=["#1f77b4", "#ff7f0e"])
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        fig4 = px.bar(
            fleet_data, x="Airline", y="Avg Age (Years)",
            title="Average Fleet Age Comparison",
            color="Avg Age (Years)", color_continuous_scale="RdYlGn_r"
        )
        fig4.add_hline(y=airline_row["Avg Age (Years)"], line_dash="dash",
                       annotation_text=selected_airline)
        st.plotly_chart(fig4, use_container_width=True)

    if avg_age > 13:
        st.warning(f"⚠️ {selected_airline} has an ageing fleet — higher maintenance costs and residual value risk for lessors.")
    elif avg_age < 8:
        st.success(f"✅ {selected_airline} has a young, modern fleet — lower technical risk and strong residual values.")
    else:
        st.info(f"ℹ️ {selected_airline} has a mid-age fleet — monitor for upcoming heavy maintenance cycles.")

with tab3:
    st.header("Aircraft Value Curves")

    col1, col2 = st.columns([2, 1])
    with col1:
        selected_aircraft = st.multiselect(
            "Select Aircraft Types to Compare",
            options=list(aircraft_types.keys()),
            default=["A320neo", "B737 MAX8"]
        )
    with col2:
        selected_age = st.slider("Mark a Specific Age", 0, 25, 10)

    if selected_aircraft:
        filtered_df = value_df[value_df["Aircraft"].isin(selected_aircraft)]
        fig5 = px.line(
            filtered_df, x="Age (Years)", y="Value ($M)",
            color="Aircraft", title="Aircraft Value Depreciation Curves",
            markers=True
        )
        fig5.add_vline(x=selected_age, line_dash="dash",
                       annotation_text=f"Age {selected_age}y")
        st.plotly_chart(fig5, use_container_width=True)

        st.subheader(f"📊 Values at Age {selected_age} Years")
        cols = st.columns(len(selected_aircraft))
        for i, aircraft in enumerate(selected_aircraft):
            row = value_df[(value_df["Aircraft"] == aircraft) &
                          (value_df["Age (Years)"] == selected_age)].iloc[0]
            original = aircraft_types[aircraft]["base_value"]
            depreciated = round((1 - row["Value ($M)"] / original) * 100, 1)
            cols[i].metric(
                aircraft,
                f"${row['Value ($M)']}M",
                f"-{depreciated}% from new"
            )

        st.info("💡 **Key Insight:** Narrowbody aircraft depreciate faster initially but retain stronger demand — making them the backbone of most leasing portfolios.")
    else:
        st.warning("Please select at least one aircraft type.")

with tab4:
    st.header("Lessee Credit Risk")
    st.markdown("A lessor's biggest risk is an airline defaulting on lease payments. This tab scores each airline's financial health.")

    col1, col2 = st.columns([3, 1])

    with col1:
        fig6 = px.scatter(
            credit_data,
            x="Debt/Equity Ratio",
            y="Operating Margin %",
            size="Interest Coverage",
            color="Risk Rating",
            text="Airline",
            title="Airline Credit Risk Map — Debt vs Profitability",
            color_discrete_map={
                "🟢 Low Risk": "green",
                "🟡 Medium Risk": "orange",
                "🔴 High Risk": "red"
            }
        )
        fig6.update_traces(textposition="top center")
        st.plotly_chart(fig6, use_container_width=True)

    with col2:
        st.subheader("Risk Rankings")
        rankings = credit_data[["Airline", "Credit Score", "Risk Rating"]]\
            .sort_values("Credit Score", ascending=False)\
            .reset_index(drop=True)
        rankings.index += 1
        st.dataframe(rankings, use_container_width=True)

    st.subheader("Detailed Metrics")
    fig7 = px.bar(
        credit_data.sort_values("Credit Score", ascending=True),
        x="Credit Score", y="Airline", orientation="h",
        color="Risk Rating",
        title="Overall Lessee Credit Score by Airline",
        color_discrete_map={
            "🟢 Low Risk": "green",
            "🟡 Medium Risk": "orange",
            "🔴 High Risk": "red"
        }
    )
    st.plotly_chart(fig7, use_container_width=True)

    st.warning("⚠️ **Key Insight:** High-lease-dependency carriers like AirAsia also carry the weakest balance sheets — concentrated exposure here represents significant default risk for lessors.")
