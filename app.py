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
    "B737 MAX8":{"base_value": 80, "depreciation": 0.057, "monthly_lease": 395},
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

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Market Overview",
    "Fleet Analysis",
    "Aircraft Value Curves",
    "Lessee Credit Risk",
    "Lease Rate Calculator",
    "Lessor Portfolios",
    "Market News"
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

with tab5:
    st.header("✈️ Lease Rate Calculator")
    st.markdown("Calculate the minimum monthly lease rate a lessor must charge to cover costs and hit their return target.")

    # --- EXPLANATION ---
    with st.expander("📖 How does this calculator work?"):
        st.markdown("""
        When a lessor like AerCap buys an aircraft, they need to charge airlines enough rent to:
        1. **Pay back their debt** — they borrow ~75% of the purchase price from banks
        2. **Earn a return on their own money** — the 25% they put in themselves
        3. **Cover maintenance reserves** — money set aside for future engine overhauls
        4. **Cover insurance** — typically 0.5% of aircraft value per year
        5. **Account for depreciation** — the aircraft loses value over time
        
        The **Lease Rate Factor (LRF)** is the key metric: it's the monthly lease rate divided by the aircraft value.
        A typical LRF ranges from **0.7% to 1.2%** depending on aircraft type and market conditions.
        """)

    st.subheader("🔧 Aircraft & Deal Parameters")

    col1, col2 = st.columns(2)

    with col1:
        aircraft_choice = st.selectbox(
            "Select Aircraft Type",
            list(aircraft_types.keys())
        )
        aircraft_age = st.slider("Aircraft Age at Lease Start (Years)", 0, 15, 0)
        lease_term = st.slider("Lease Term (Years)", 1, 12, 6)

    with col2:
        ltv = st.slider("Loan-to-Value Ratio (%)", 50, 90, 75,
                        help="% of aircraft value financed by debt. Typically 70-80% in aviation.")
        interest_rate = st.slider("Interest Rate on Debt (%)", 2.0, 8.0, 5.0, step=0.1,
                                  help="Annual interest rate on the debt used to buy the aircraft.")
        target_equity_return = st.slider("Target Equity Return (%)", 5.0, 20.0, 12.0, step=0.5,
                                         help="The annual return the lessor wants on their own invested money.")

    st.subheader("🔧 Operating Cost Parameters")
    col3, col4 = st.columns(2)

    with col3:
        maintenance_reserve = st.slider("Monthly Maintenance Reserve ($K)", 50, 300, 120,
                                        help="Monthly amount set aside for future engine and airframe overhauls.")
        insurance_rate = st.slider("Annual Insurance Rate (% of value)", 0.1, 1.0, 0.5, step=0.1)

    with col4:
        residual_pct = st.slider("Residual Value at Lease End (% of current value)", 40, 85, 65,
                                 help="What % of the aircraft's value the lessor expects to recover when the lease ends.")

    # --- CALCULATIONS ---
    # Step 1: Work out aircraft value at lease start
    base_value = aircraft_types[aircraft_choice]["base_value"]
    depreciation = aircraft_types[aircraft_choice]["depreciation"]
    current_value = base_value * ((1 - depreciation) ** aircraft_age)

    # Step 2: Work out debt and equity split
    debt_amount = current_value * 1000 * (ltv / 100)
    equity_amount = current_value * 1000 * (1 - ltv / 100)

    # Step 3: Monthly debt service (principal + interest over lease term)
    monthly_interest_rate = (interest_rate / 100) / 12
    n_payments = lease_term * 12
    if monthly_interest_rate > 0:
        monthly_debt_service = debt_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** n_payments) / \
                               ((1 + monthly_interest_rate) ** n_payments - 1)
    else:
        monthly_debt_service = debt_amount / n_payments

    # Step 4: Monthly equity return required
    monthly_equity_return = equity_amount * (target_equity_return / 100) / 12

    # Step 5: Monthly insurance cost
    monthly_insurance = (current_value * 1000 * insurance_rate / 100) / 12

    # Step 6: Residual value benefit (reduces how much you need to charge)
    residual_value = current_value * 1000 * (residual_pct / 100)
    monthly_residual_benefit = residual_value / n_payments

    # Step 7: Minimum monthly lease rate
    min_lease_rate = (monthly_debt_service + monthly_equity_return +
                      maintenance_reserve + monthly_insurance - monthly_residual_benefit)

    # Step 8: Lease Rate Factor
    lrf = (min_lease_rate / (current_value * 1000)) * 100

    # Step 9: Market lease rate for comparison
    market_rate = aircraft_types[aircraft_choice]["monthly_lease"]

    # --- DISPLAY RESULTS ---
    st.markdown("---")
    st.subheader("📊 Results")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Aircraft Value at Lease Start", f"${current_value:.1f}M")
    with col2:
        st.metric("Min Monthly Lease Rate", f"${min_lease_rate:.0f}K")
    with col3:
        st.metric("Lease Rate Factor", f"{lrf:.3f}%",
                  help="Monthly lease rate as % of aircraft value. Healthy range: 0.7%-1.2%")
    with col4:
        market_diff = min_lease_rate - market_rate
        st.metric("vs Market Rate", f"${market_rate}K",
                  delta=f"${market_diff:.0f}K {'above' if market_diff > 0 else 'below'} market")

    # --- COST BREAKDOWN CHART ---
    st.subheader("💰 Monthly Cost Breakdown")

    breakdown_df = pd.DataFrame({
        "Cost Component": [
            "Debt Service",
            "Equity Return",
            "Maintenance Reserve",
            "Insurance",
            "Residual Value Benefit (deducted)"
        ],
        "Amount ($K)": [
            round(monthly_debt_service, 1),
            round(monthly_equity_return, 1),
            maintenance_reserve,
            round(monthly_insurance, 1),
            round(-monthly_residual_benefit, 1)
        ]
    })

    fig8 = px.bar(
        breakdown_df,
        x="Cost Component",
        y="Amount ($K)",
        title="Monthly Lease Rate — Cost Breakdown",
        color="Cost Component",
        text="Amount ($K)"
    )
    fig8.update_traces(texttemplate='$%{text}K', textposition='outside')
    st.plotly_chart(fig8, use_container_width=True)

    # --- LEASE TERM SUMMARY ---
    st.subheader(f"📅 Full Lease Summary ({lease_term} Years)")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Lease Revenue", f"${min_lease_rate * n_payments / 1000:.1f}M")
    with col2:
        st.metric("Equity Invested", f"${equity_amount/ 1000:.1f}M")
    with col3:
        total_return = (min_lease_rate * n_payments / 1000) + (residual_value/ 1000) - current_value
        st.metric("Total Lessor Profit", f"${total_return:.1f}M")

    # --- RISK FLAGS ---
    st.markdown("---")
    if lrf > 1.2:
        st.warning("⚠️ Your lease rate factor is above 1.2% — this may price you out of the market. Consider reducing your equity return target or extending the lease term.")
    elif lrf < 0.7:
        st.error("🔴 Your lease rate factor is below 0.7% — you're likely underpricing. Review your debt structure or residual value assumptions.")
    else:
        st.success(f"✅ Lease Rate Factor of {lrf:.3f}% is within the healthy market range of 0.7%–1.2%.")
# --- LESSOR DATA ---
lessor_data = pd.DataFrame({
    "Lessor": ["AerCap", "SMBC Aviation Capital", "Air Lease Corp", "Avolon", "BOC Aviation", "Aircastle", "BBAM", "Carlyle Aviation"],
    "HQ": ["Dublin", "Dublin", "Los Angeles", "Dublin", "Singapore", "Dublin", "San Francisco", "Dublin"],
    "Total Aircraft": [1700, 750, 480, 570, 550, 280, 490, 260],
    "Avg Fleet Age": [6.8, 7.2, 4.1, 6.5, 5.9, 8.4, 9.1, 10.2],
    "Utilisation %": [99.2, 98.8, 99.6, 98.5, 99.1, 97.8, 96.9, 97.2],
    "Narrowbody %": [68, 72, 75, 70, 65, 60, 55, 50],
    "Widebody %": [32, 28, 25, 30, 35, 40, 45, 50],
})

lessor_customers = {
    "AerCap": {"Ryanair": 8, "IndiGo": 6, "Air France-KLM": 5, "Delta": 4, "Others": 77},
    "SMBC Aviation Capital": {"ANA": 7, "Southwest": 6, "IAG": 5, "Lufthansa": 4, "Others": 78},
    "Air Lease Corp": {"IndiGo": 6, "Norwegian": 5, "Air Canada": 5, "Others": 84},
    "Avolon": {"Ryanair": 7, "Air China": 6, "Emirates": 5, "Others": 82},
    "BOC Aviation": {"Air China": 9, "China Southern": 8, "AirAsia": 6, "Others": 77},
    "Aircastle": {"Various": 20, "Asian Carriers": 30, "European": 25, "Others": 25},
    "BBAM": ["Mixed Portfolio"],
    "Carlyle Aviation": ["Mixed Portfolio"],
}

lessor_geography = pd.DataFrame({
    "Lessor": ["AerCap", "SMBC Aviation Capital", "Air Lease Corp", "Avolon", "BOC Aviation"],
    "Asia Pacific": [30, 35, 28, 32, 55],
    "Europe": [28, 25, 22, 26, 15],
    "North America": [20, 18, 30, 18, 10],
    "Middle East": [12, 12, 10, 14, 12],
    "Other": [10, 10, 10, 10, 8],
})

with tab6:
    st.header("🏢 Lessor Portfolio Analysis")
    st.markdown("Analysing the world's largest aircraft lessors — their portfolio size, composition and customer exposure.")

    # --- OVERVIEW METRICS ---
    st.subheader("Portfolio Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        fig_size = px.bar(
            lessor_data.sort_values("Total Aircraft", ascending=True),
            x="Total Aircraft", y="Lessor", orientation="h",
            title="Portfolio Size by Lessor",
            color="Total Aircraft",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig_size, use_container_width=True)

    with col2:
        fig_age = px.bar(
            lessor_data.sort_values("Avg Fleet Age", ascending=True),
            x="Avg Fleet Age", y="Lessor", orientation="h",
            title="Average Fleet Age by Lessor",
            color="Avg Fleet Age",
            color_continuous_scale="RdYlGn_r"
        )
        st.plotly_chart(fig_age, use_container_width=True)

    with col3:
        fig_util = px.bar(
            lessor_data.sort_values("Utilisation %", ascending=True),
            x="Utilisation %", y="Lessor", orientation="h",
            title="Fleet Utilisation Rate (%)",
            color="Utilisation %",
            color_continuous_scale="Greens"
        )
        fig_util.update_xaxes(range=[95, 100])
        st.plotly_chart(fig_util, use_container_width=True)

    st.info("💡 **Key Insight:** AerCap is the world's largest lessor with ~1,700 aircraft following its merger with GECAS in 2021 — nearly double its closest competitor.")

    # --- LESSOR COMPARISON ---
    st.subheader("🔍 Compare Two Lessors")
    col1, col2 = st.columns(2)
    with col1:
        lessor_a = st.selectbox("Select Lessor A", lessor_data["Lessor"], index=0)
    with col2:
        lessor_b = st.selectbox("Select Lessor B", lessor_data["Lessor"], index=1)

    row_a = lessor_data[lessor_data["Lessor"] == lessor_a].iloc[0]
    row_b = lessor_data[lessor_data["Lessor"] == lessor_b].iloc[0]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(f"{lessor_a} Fleet", f"{int(row_a['Total Aircraft'])} aircraft",
                  delta=f"{int(row_a['Total Aircraft']) - int(row_b['Total Aircraft'])} vs {lessor_b}")
    with col2:
        st.metric(f"{lessor_a} Avg Age", f"{row_a['Avg Fleet Age']} yrs",
                  delta=f"{round(row_a['Avg Fleet Age'] - row_b['Avg Fleet Age'], 1)} yrs vs {lessor_b}")
    with col3:
        st.metric(f"{lessor_a} Utilisation", f"{row_a['Utilisation %']}%",
                  delta=f"{round(row_a['Utilisation %'] - row_b['Utilisation %'], 1)}% vs {lessor_b}")
    with col4:
        st.metric(f"{lessor_a} Narrowbody", f"{int(row_a['Narrowbody %'])}%",
                  delta=f"{int(row_a['Narrowbody %']) - int(row_b['Narrowbody %'])}% vs {lessor_b}")

    # --- FLEET COMPOSITION ---
    st.subheader("Narrowbody vs Widebody Split")
    comp_df = pd.DataFrame({
        "Lessor": [lessor_a, lessor_a, lessor_b, lessor_b],
        "Type": ["Narrowbody", "Widebody", "Narrowbody", "Widebody"],
        "Percentage": [
            row_a["Narrowbody %"], row_a["Widebody %"],
            row_b["Narrowbody %"], row_b["Widebody %"]
        ]
    })
    fig_comp = px.bar(
        comp_df, x="Lessor", y="Percentage", color="Type",
        title=f"Fleet Composition: {lessor_a} vs {lessor_b}",
        barmode="stack",
        color_discrete_map={"Narrowbody": "#1f77b4", "Widebody": "#ff7f0e"}
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    # --- GEOGRAPHIC EXPOSURE ---
    st.subheader("🌍 Geographic Exposure")
    selected_lessor_geo = st.selectbox(
        "Select Lessor for Geographic Breakdown",
        lessor_geography["Lessor"]
    )
    geo_row = lessor_geography[lessor_geography["Lessor"] == selected_lessor_geo].iloc[0]
    geo_df = pd.DataFrame({
        "Region": ["Asia Pacific", "Europe", "North America", "Middle East", "Other"],
        "Exposure %": [
            geo_row["Asia Pacific"], geo_row["Europe"],
            geo_row["North America"], geo_row["Middle East"], geo_row["Other"]
        ]
    })
    fig_geo = px.pie(
        geo_df, names="Region", values="Exposure %",
        title=f"{selected_lessor_geo} — Geographic Exposure",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig_geo, use_container_width=True)

    st.warning("⚠️ **Key Risk:** BOC Aviation's heavy Asia Pacific concentration (55%) creates significant exposure to Chinese carrier credit risk and geopolitical uncertainty.")

with tab7:
    st.header("📰 Aviation Leasing Market News")
    st.markdown("Latest news and developments from the aviation leasing industry.")

    import feedparser

    # News sources
    feeds = {
        "Aviation Leasing News": "https://news.google.com/rss/search?q=aviation+leasing+AerCap+SMBC+Avolon&hl=en-US&gl=US&ceid=US:en",
        "Aircraft Orders & Deliveries": "https://news.google.com/rss/search?q=aircraft+orders+Boeing+Airbus+deliveries&hl=en-US&gl=US&ceid=US:en",
        "Airline Industry": "https://news.google.com/rss/search?q=airline+industry+fleet+expansion&hl=en-US&gl=US&ceid=US:en",
    }

    selected_feed = st.selectbox("Select News Category", list(feeds.keys()))

    st.subheader(f"Latest: {selected_feed}")

    try:
        feed = feedparser.parse(feeds[selected_feed])
        if feed.entries:
            for i, entry in enumerate(feed.entries[:10]):
                with st.expander(f"📄 {entry.title}"):
                    st.markdown(f"**Published:** {entry.get('published', 'N/A')}")
                    st.markdown(f"**Source:** {entry.get('source', {}).get('title', 'Google News')}")
                    if hasattr(entry, 'summary'):
                        st.markdown(entry.summary[:300] + "...")
                    st.markdown(f"[Read full article]({entry.link})")
        else:
            st.warning("No articles found. Try refreshing.")
    except Exception as e:
        st.error("Unable to load news feed. Check your internet connection.")

    st.info("💡 News updates automatically every time you refresh the page.")
