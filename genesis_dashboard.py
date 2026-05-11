import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Genesis Aircraft Services — Portfolio Dashboard", layout="wide")

st.title("✈️ Genesis Aircraft Services — Portfolio Dashboard")
st.markdown("Live fleet analysis powered by real Genesis Aircraft Services data")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    df = pd.read_excel("genesis data.xlsx", header=1)
    df.columns = [
        "MSN", "Manufacturer", "Type", "Model", "Body Type", "Manager",
        "Legal Owner", "Beneficial Owner", "Operator", "Registration",
        "Contract Date", "Status", "Last Event", "Last Event Date",
        "Year Built", "Lease End Date", "Engine", "Hex ID",
        "MV $m", "DMV $m", "MLRT $k", "BV $m"
    ]
    df = df[pd.to_numeric(df["MSN"], errors="coerce").notna() | df["MSN"].astype(str).str.strip().ne("")]
    df = df[~df["Manufacturer"].isin(["Manufacturer", "Type", "manufacturer"])]
    df = df.dropna(subset=["MSN", "Manufacturer"], how="all")
    df = df.reset_index(drop=True)

    # Convert Excel serial dates to proper dates
    excel_epoch = datetime(1899, 12, 30)
    def serial_to_date(val):
        try:
            return excel_epoch + timedelta(days=int(val))
        except:
            return None

    df["Lease End Date"] = df["Lease End Date"].apply(serial_to_date)
    df["Year Built"] = pd.to_numeric(df["Year Built"], errors="coerce")
    df["MV $m"] = pd.to_numeric(df["MV $m"], errors="coerce")
    df["DMV $m"] = pd.to_numeric(df["DMV $m"], errors="coerce")
    df["MLRT $k"] = pd.to_numeric(df["MLRT $k"], errors="coerce")
    df["BV $m"] = pd.to_numeric(df["BV $m"], errors="coerce")
    df["Age"] = datetime.now().year - df["Year Built"]
    df["Aircraft"] = df["Type"] + " " + df["Model"].astype(str)
    return df

df = load_data()

# --- TABS ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Portfolio Overview",
    "Fleet Details",
    "Portfolio Valuation",
    "Customer Exposure",
    "Lease Expiry Schedule",
    "Lease Rate Analysis"
])

# ── TAB 1: PORTFOLIO OVERVIEW ──
with tab1:
    st.header("Portfolio Overview")

    total_aircraft = len(df)
    total_mv = df["MV $m"].sum()
    avg_age = df["Age"].mean()
    active = len(df[df["Status"] == "Active"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Aircraft", total_aircraft)
    col2.metric("Total Portfolio Value", f"${total_mv:.0f}M")
    col3.metric("Average Fleet Age", f"{avg_age:.1f} years")
    col4.metric("Active Aircraft", f"{active} / {total_aircraft}")

    col1, col2 = st.columns(2)

    with col1:
        mfr_counts = df["Manufacturer"].value_counts().reset_index()
        mfr_counts.columns = ["Manufacturer", "Count"]
        fig1 = px.pie(mfr_counts, names="Manufacturer", values="Count",
                      title="Fleet Split: Boeing vs Airbus",
                      color_discrete_sequence=["#1B3A6B", "#2E75B6"])
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        type_counts = df["Aircraft"].value_counts().reset_index()
        type_counts.columns = ["Aircraft", "Count"]
        fig2 = px.bar(type_counts, x="Count", y="Aircraft", orientation="h",
                      title="Fleet Breakdown by Aircraft Type",
                      color="Count", color_continuous_scale="Blues")
        st.plotly_chart(fig2, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        status_counts = df["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig3 = px.pie(status_counts, names="Status", values="Count",
                      title="Fleet Status: Active vs Stored",
                      color_discrete_sequence=["#2ECC71", "#E74C3C"])
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        fig4 = px.histogram(df, x="Age", nbins=10,
                            title="Fleet Age Distribution",
                            color_discrete_sequence=["#1B3A6B"])
        st.plotly_chart(fig4, use_container_width=True)

    st.info(f"💡 Genesis manages a {total_aircraft}-aircraft portfolio worth ${total_mv:.0f}M with an average fleet age of {avg_age:.1f} years.")

# ── TAB 2: FLEET DETAILS ──
with tab2:
    st.header("Fleet Details")
    st.markdown("Full searchable and filterable Genesis fleet register")

    col1, col2, col3 = st.columns(3)
    with col1:
        mfr_filter = st.multiselect("Manufacturer", df["Manufacturer"].unique(),
                                    default=df["Manufacturer"].unique())
    with col2:
        status_filter = st.multiselect("Status", df["Status"].unique(),
                                       default=df["Status"].unique())
    with col3:
        search = st.text_input("Search Operator", "")

    filtered = df[
        (df["Manufacturer"].isin(mfr_filter)) &
        (df["Status"].isin(status_filter))
    ]
    if search:
        filtered = filtered[filtered["Operator"].str.contains(search, case=False, na=False)]

    display_cols = ["MSN", "Manufacturer", "Aircraft", "Operator", "Registration",
                    "Year Built", "Age", "Status", "MV $m", "MLRT $k", "Lease End Date"]
    st.dataframe(filtered[display_cols].reset_index(drop=True), use_container_width=True)
    st.caption(f"Showing {len(filtered)} of {total_aircraft} aircraft")

# ── TAB 3: PORTFOLIO VALUATION ──
with tab3:
    st.header("Portfolio Valuation")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Market Value (MV)", f"${df['MV $m'].sum():.1f}M")
    col2.metric("Total Depreciated Market Value (DMV)", f"${df['DMV $m'].sum():.1f}M")
    col3.metric("Total Base Value (BV)", f"${df['BV $m'].sum():.1f}M")

    st.subheader("MV vs DMV vs BV by Aircraft Type")
    val_by_type = df.groupby("Aircraft")[["MV $m", "DMV $m", "BV $m"]].mean().reset_index()
    val_melted = val_by_type.melt(id_vars="Aircraft", var_name="Valuation Type", value_name="Value ($M)")
    fig5 = px.bar(val_melted, x="Aircraft", y="Value ($M)", color="Valuation Type",
                  barmode="group", title="Average Aircraft Values by Type",
                  color_discrete_sequence=["#1B3A6B", "#2E75B6", "#A8C8E8"])
    st.plotly_chart(fig5, use_container_width=True)

    st.subheader("Value vs Age Relationship")
    fig6 = px.scatter(df.dropna(subset=["MLRT $k", "Age", "MV $m"]), x="Age", y="MV $m", color="Aircraft",
                  size="MLRT $k", hover_data=["Operator", "Registration"],
                  title="Market Value vs Aircraft Age (bubble size = monthly lease rate)")
    st.plotly_chart(fig6, use_container_width=True)

    st.info("💡 **MV** = Market Value (what it would sell for today). **DMV** = Depreciated Market Value (appraiser estimate). **BV** = Base Value (theoretical equilibrium value). A large gap between MV and BV signals market stress or oversupply.")

# ── TAB 4: CUSTOMER EXPOSURE ──
with tab4:
    st.header("Customer Exposure")
    st.markdown("Which airlines are operating Genesis aircraft — and how concentrated is the exposure?")

    operator_counts = df.groupby("Operator").agg(
        Aircraft_Count=("MSN", "count"),
        Total_MV=("MV $m", "sum"),
        Avg_MLRT=("MLRT $k", "mean")
    ).reset_index().sort_values("Aircraft_Count", ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        fig7 = px.bar(operator_counts.head(15),
                      x="Aircraft_Count", y="Operator", orientation="h",
                      title="Aircraft Count by Operator",
                      color="Aircraft_Count", color_continuous_scale="Blues")
        st.plotly_chart(fig7, use_container_width=True)

    with col2:
        fig8 = px.pie(operator_counts.head(10), names="Operator", values="Total_MV",
                      title="Portfolio Value Concentration by Operator (Top 10)")
        st.plotly_chart(fig8, use_container_width=True)

    st.subheader("Operator Exposure Table")
    operator_counts["Total_MV"] = operator_counts["Total_MV"].round(1)
    operator_counts["Avg_MLRT"] = operator_counts["Avg_MLRT"].round(0)
    operator_counts.columns = ["Operator", "Aircraft Count", "Total MV ($M)", "Avg Monthly Lease ($K)"]
    st.dataframe(operator_counts, use_container_width=True)

    top_operator = operator_counts.iloc[0]["Operator"]
    top_count = operator_counts.iloc[0]["Aircraft Count"]
    top_pct = round(top_count / total_aircraft * 100, 1)
    if top_pct > 15:
        st.warning(f"⚠️ {top_operator} represents {top_pct}% of Genesis's fleet — significant single-operator concentration risk.")

# ── TAB 5: LEASE EXPIRY SCHEDULE ──
with tab5:
    st.header("Lease Expiry Schedule")
    st.markdown("When are Genesis leases expiring? This drives remarketing risk.")

    lease_df = df[df["Lease End Date"].notna()].copy()
    lease_df["Expiry Year"] = lease_df["Lease End Date"].apply(lambda x: x.year)
    lease_df["Expiry Quarter"] = lease_df["Lease End Date"].apply(
        lambda x: f"{x.year} Q{((x.month - 1) // 3) + 1}")

    expiry_by_year = lease_df.groupby("Expiry Year").agg(
        Count=("MSN", "count"),
        Total_MV=("MV $m", "sum")
    ).reset_index()

    col1, col2 = st.columns(2)
    with col1:
        fig9 = px.bar(expiry_by_year, x="Expiry Year", y="Count",
                      title="Number of Leases Expiring by Year",
                      color="Count", color_continuous_scale="RdYlGn_r",
                      text="Count")
        fig9.update_traces(textposition="outside")
        st.plotly_chart(fig9, use_container_width=True)

    with col2:
        fig10 = px.bar(expiry_by_year, x="Expiry Year", y="Total_MV",
                       title="Value of Aircraft with Expiring Leases ($M)",
                       color="Total_MV", color_continuous_scale="Reds",
                       text="Total_MV")
        fig10.update_traces(texttemplate="$%{text:.0f}M", textposition="outside")
        st.plotly_chart(fig10, use_container_width=True)

    st.subheader("Upcoming Lease Expirations")
    upcoming = lease_df[lease_df["Expiry Year"] <= datetime.now().year + 3]\
        .sort_values("Lease End Date")[
        ["Aircraft", "Operator", "Registration", "Lease End Date", "MV $m", "MLRT $k"]
    ].reset_index(drop=True)

    if len(upcoming) > 0:
        st.dataframe(upcoming, use_container_width=True)
        st.warning(f"⚠️ {len(upcoming)} aircraft have leases expiring within 3 years — these require active remarketing.")
    else:
        st.success("✅ No lease expirations within the next 3 years.")

# ── TAB 6: LEASE RATE ANALYSIS ──
with tab6:
    st.header("Lease Rate Analysis")

    col1, col2 = st.columns(2)
    with col1:
        lease_by_type = df.groupby("Aircraft")["MLRT $k"].mean().reset_index()
        lease_by_type.columns = ["Aircraft", "Avg Monthly Lease ($K)"]
        fig11 = px.bar(lease_by_type.sort_values("Avg Monthly Lease ($K)", ascending=True),
                       x="Avg Monthly Lease ($K)", y="Aircraft", orientation="h",
                       title="Average Monthly Lease Rate by Aircraft Type",
                       color="Avg Monthly Lease ($K)", color_continuous_scale="Blues")
        st.plotly_chart(fig11, use_container_width=True)

    with col2:
        fig12 = px.scatter(df.dropna(subset=["Age", "MLRT $k"]), x="Age", y="MLRT $k", color="Aircraft",
                   hover_data=["Operator", "MV $m"],
                   title="Monthly Lease Rate vs Aircraft Age",
                   trendline="ols")
        st.plotly_chart(fig12, use_container_width=True)

    st.subheader("Lease Rate Factor Analysis")
    df["LRF %"] = ((df["MLRT $k"] / 1000) / df["MV $m"] * 100).round(3)
    lrf_df = df[["Aircraft", "Operator", "Age", "MV $m", "MLRT $k", "LRF %"]]\
        .dropna().sort_values("LRF %", ascending=False)

    fig13 = px.box(df.dropna(subset=["LRF %"]), x="Aircraft", y="LRF %",
                   title="Lease Rate Factor Distribution by Aircraft Type",
                   color="Aircraft")
    fig13.add_hline(y=0.7, line_dash="dash", annotation_text="Min healthy LRF (0.7%)")
    fig13.add_hline(y=1.2, line_dash="dash", annotation_text="Max healthy LRF (1.2%)")
    st.plotly_chart(fig13, use_container_width=True)

    st.dataframe(lrf_df.reset_index(drop=True), use_container_width=True)
    st.info("💡 **Lease Rate Factor (LRF)** = Monthly lease rate ÷ Aircraft value. Healthy range is 0.7%–1.2%. Values outside this range signal mispricing or market stress.")
