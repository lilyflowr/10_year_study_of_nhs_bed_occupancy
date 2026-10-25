import pandas as pd
import plotly.express as px
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="NHS Bed Capacity & Flow Crisis Dashboard",
    page_icon="🏥",
    layout="wide",
)


# Load and process dataset
@st.cache_data
def load_and_process_data():
  df = pd.read_csv("NHS_KH03_Cleaned_Data/cleaned_data.csv")

  # Streamline percentage columns
  percent_cols = [
      "Percent_Total",
      "Percentage_Gen_Acute",
      "Percentage_LD",
      "Percentage_Maternity",
      "Percentage_Mental",
  ]
  for col in percent_cols:
    if col in df.columns:
      df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

  # 1. Macrotrend dataset grouped by year
  macro_df = (
      df.groupby("Year")
      .agg(
          total_available_gen_acute=("Available_Gen_Acute", "sum"),
          total_occupied_gen_acute=("Occupied_Gen_Acute", "sum"),
      )
      .reset_index()
  )
  macro_df["average_occupied_percentage"] = round(
      macro_df["total_occupied_gen_acute"]
      / macro_df["total_available_gen_acute"]
      * 100,
      2,
  )

  # 2. Sector breakdown
  sector_df = (
      df.groupby("Year")
      .agg(
          gen_acute_available=("Available_Gen_Acute", "sum"),
          gen_acute_occupied=("Occupied_Gen_Acute", "sum"),
          ld_available=("Available_LD", "sum"),
          ld_occupied=("Occupied_LD", "sum"),
          maternity_available=("Available_Maternity", "sum"),
          maternity_occupied=("Occupied_Maternity", "sum"),
          mental_available=("Available_Mental", "sum"),
          mental_occupied=("Occupied_Mental", "sum"),
      )
      .reset_index()
  )

  sector_df["gen_acute_percentage"] = round(
      sector_df["gen_acute_occupied"] / sector_df["gen_acute_available"] * 100, 2
  )
  sector_df["ld_percentage"] = round(
      sector_df["ld_occupied"] / sector_df["ld_available"] * 100, 2
  )
  sector_df["maternity_percentage"] = round(
      sector_df["maternity_occupied"] / sector_df["maternity_available"] * 100,
      2,
  )
  sector_df["mental_percentage"] = round(
      sector_df["mental_occupied"] / sector_df["mental_available"] * 100, 2
  )

  # 3. Top 10 Crisis Trusts (2025-26)
  df_2526 = df[(df["Year"] == "2025-26") & (df["Available_Gen_Acute"] > 0)]
  trust_df = (
      df_2526.groupby(["Org_Code", "Org_Name", "Region_Code"])
      .agg(
          total_available_gen_acute=("Available_Gen_Acute", "sum"),
          total_occupied_gen_acute=("Occupied_Gen_Acute", "sum"),
      )
      .reset_index()
  )
  trust_df["average_occupied_percentage"] = round(
      (
          trust_df["total_occupied_gen_acute"]
          / trust_df["total_available_gen_acute"]
      )
      * 100,
      2,
  )
  top10_in_crisis_df = trust_df.sort_values(
      by="average_occupied_percentage", ascending=False
  ).head(10)

  return macro_df, sector_df, top10_in_crisis_df, df


macro_df, sector_df, top10_in_crisis_df, raw_df = load_and_process_data()

# Sidebar - Author Info & Navigation
st.sidebar.title("🏥 NHS Analytics Hub")
st.sidebar.markdown("""
**Author:** Ibinabo Adiela  
*Healthcare Data Analyst & Registered Nurse*
""")
st.sidebar.divider()

view_mode = st.sidebar.radio(
    "Select Interface View",
    ["📖 Article & Integrated Analytics", "📊 Interactive Dashboard Explorer"],
)

# ------------------------------------------------------------------------------
# VIEW 1: ARTICLE & INTEGRATED ANALYTICS
# ------------------------------------------------------------------------------
if view_mode == "📖 Article & Integrated Analytics":
  st.title(
      "Why the NHS Doesn’t Just Have a Bed Crisis—It Has a Flow Crisis: A"
      " 10-Year Data Analysis (2016–2026)"
  )
  st.caption(
      "**By Ibinabo Adiela** | Healthcare Data Analyst & Registered Nurse"
  )
  st.divider()

  # Metric Highlights Banner
  m1, m2, m3, m4 = st.columns(4)
  m1.metric("2025-26 G&A Peak Occupancy", "91.58%", "Over 85% Safe Limit")
  m2.metric("2020-21 Pandemic Low", "76.76%", "Physical Distancing")
  m3.metric("Top Acute Trust Crisis", "99.43%", "Buckinghamshire Healthcare")
  m4.metric("Social Care Delay Cost", "~£400 / day", "Per fit-to-discharge bed")

  st.divider()

  # Introduction
  st.markdown("""
    ### Introduction: The View From the Ward Floor

    If you have ever worked an evening shift inside an acute NHS ward during winter pressures, you know the sensory indicators of gridlock before you even check the status board. You hear the chime of call bells from patients waiting for discharge letters, you see paramedics waiting in corridors with stretcher patients, and you feel the operational tension of a hospital running at 100% capacity.

    For years, public debates around healthcare reform have focused almost exclusively on a single metric: **bed numbers**. The political response has been consistent: *add more funding, open more beds, hire more staff.*

    Yet, after analyzing **10 years of NHS KH03 bed occupancy data (2016 through 2026)**—encompassing thousands of quarterly records across every acute trust in England—the empirical reality is undeniable: **the NHS does not simply have a physical capacity problem; it has a systemic patient flow problem.**
    """)

  # Part 1 + Interactive Plot
  st.markdown("""
    ---
    ### Part 1: The Macro Reality—Operating Above Safety Limits for a Decade

    Clinical guidelines from the National Institute for Health and Care Excellence (NICE) and healthcare think tanks like The King’s Fund establish **85% occupancy** as the safe ceiling for acute hospital operation. Past 85%, hospitals lose the operational flexibility to handle emergency admissions, bed turnover times collapse, and infection prevention buffers break down.

    My 10-year national data analysis reveals a stark trajectory:
    - **2016–2020 Baseline:** National General & Acute (G&A) occupancy hovered near critical limits, averaging **~90.2%** year after year.
    - **The 2020–21 Anomaly:** During peak COVID-19 restrictions, mandatory physical distancing and elective surgery halts artificially drove national occupancy down to **76.76%**.
    - **The Post-Pandemic Overshoot:** Rather than stabilizing near safe thresholds, occupancy surged post-2021. By **2025–26, national G&A occupancy reached a 10-year peak of 91.58%**.
    """)

  # Plot 1: Macro Trend
  fig_macro = px.line(
      macro_df,
      x="Year",
      y="average_occupied_percentage",
      markers=True,
      title="Figure 1: NHS General & Acute Bed Occupancy Trend (2016–2026)",
      labels={
          "average_occupied_percentage": "Occupancy Rate (%)",
          "Year": "Financial Year",
      },
      color_discrete_sequence=["#d9534f"],
  )
  fig_macro.add_hline(
      y=85,
      line_dash="dash",
      line_color="darkorange",
      annotation_text="NICE 85% Safe Ceiling",
      annotation_position="bottom right",
  )
  fig_macro.update_layout(yaxis_range=[60, 100])
  st.plotly_chart(fig_macro, use_container_width=True)

  # Part 2 + Interactive Plot
  st.markdown("""
    ---
    ### Part 2: The Micro Epicenter—The 99% Gridlock

    National averages soften local pain points. When filtering the 2025–26 dataset down to individual hospital trusts (and excluding specialist centers to evaluate general acute care), the data identifies specific acute trusts operating at virtual gridlock.

    Running a general acute trust at **99% average annual occupancy** means that once turnaround times, room cleaning, and emergency holdovers are accounted for, the facility is functioning with zero operational buffer.
    """)

  fig_top10 = px.bar(
      top10_in_crisis_df,
      x="average_occupied_percentage",
      y="Org_Name",
      orientation="h",
      title="Figure 2: Top 10 Acute NHS Trusts in Crisis (2025–26)",
      text="average_occupied_percentage",
      labels={
          "average_occupied_percentage": "Occupancy Rate (%)",
          "Org_Name": "NHS Trust",
      },
      color="average_occupied_percentage",
      color_continuous_scale="Reds",
  )
  fig_top10.update_layout(
      yaxis={"categoryorder": "total ascending"}, showlegend=False
  )
  st.plotly_chart(fig_top10, use_container_width=True)

  # Part 3 & Part 4
  st.markdown("""
    ---
    ### Part 3: The Front Door, Internal Flow, and the "Back Door" Trap

    Why does adding beds fail to resolve gridlock? Think-tank analysis from *Re:State* and research from *The Health Foundation* confirm that acute hospitals are trapped between three operational friction points:

    1. **The Front Door (A&E Overload):** Emergency departments absorb unscheduled care demand when primary care or community response pathways are saturated.
    2. **The Internal Engine (In-Hospital Bottlenecks):** Diagnostic delays, slow consultations, and lack of 7-day consultant decision-making slow down care progression.
    3. **The Back Door (Social Care Deficit):** This represents the primary systemic failure. Thousands of hospital beds are occupied by patients who are clinically fit for discharge but remain hospitalized due to a lack of social care packages, community rehabilitation, or step-down placement.

    As noted in recent policy evaluations by the BMA, holding a clinically ready patient in an acute bed costs the system over £400 per day—while increasing risks of hospital-acquired infections and deconditioning.

    ---
    ### Part 4: Sector Divergence—Acute vs. Specialty Pathways

    A key finding from the 10-year analysis lies in sector comparison:
    - **General & Acute (91.58%)** and **Mental Health (89.07%)** operate in perpetual stress states.
    - **Maternity Services (61.08%)** maintain healthy operational buffers due to predictable admission streams.
    - **Learning Disabilities (61.38%)** show a structural decline over a decade, reflecting policy shifts toward community-focused care.
    """)

  # Sector Melted Chart
  melted_sector = pd.melt(
      sector_df,
      id_vars=["Year"],
      value_vars=[
          "gen_acute_percentage",
          "ld_percentage",
          "maternity_percentage",
          "mental_percentage",
      ],
      var_name="Sector",
      value_name="Occupancy_Percentage",
  )
  melted_sector["Sector"] = (
      melted_sector["Sector"]
      .str.replace("_percentage", "")
      .str.replace("_", " ")
      .str.title()
  )

  fig_sector = px.line(
      melted_sector,
      x="Year",
      y="Occupancy_Percentage",
      color="Sector",
      markers=True,
      title="Figure 3: 10-Year Occupancy Trajectory by Sector",
      labels={"Occupancy_Percentage": "Occupancy Rate (%)"},
  )
  st.plotly_chart(fig_sector, use_container_width=True)

  # Part 5 & Recommendations
  st.markdown("""
    ---
    ### Part 5: From Reaction to Prediction—Actionable Policy & Tech Recommendations

    To break the gridlock, the NHS must move from reactive bed management to predictive operational flow:

    1. **Mandate Automated Bed Turnover Tracking:** Transitioning from manual ward whiteboards to automated bed tracking and teletracking platforms provides real-time visibility into bed readiness across entire regional networks.
    2. **Unblock the Back Door via Ambient AI & Automated Summaries:** Deploying ambient AI tools for discharge paperwork and instant pharmacy scripting eliminates hours of administrative delays on discharge day.
    3. **Rebalance Acute and Community Resources:** Systemic flow cannot be solved in acute wards alone. Investment must match social care demand to ensure "fit-to-discharge" patients transition out of acute beds without delay.
    """)

# ------------------------------------------------------------------------------
# VIEW 2: INTERACTIVE DASHBOARD EXPLORER
# ------------------------------------------------------------------------------
else:
  st.title("📊 Interactive Data Explorer")
  st.markdown("Filter, slice, and investigate the 10-year NHS KH03 dataset.")

  tab1, tab2, tab3 = st.tabs(
      ["Macro Trends", "Sector Comparison", "Trust-Level Filter"]
  )

  with tab1:
    st.subheader("10-Year National Macro Trends")
    st.plotly_chart(
        px.bar(
            macro_df,
            x="Year",
            y=["total_available_gen_acute", "total_occupied_gen_acute"],
            barmode="group",
            title="Available vs Occupied General & Acute Beds",
        ),
        use_container_width=True,
    )
    st.dataframe(macro_df, use_container_width=True)

  with tab2:
    st.subheader("Sector Breakdown")
    st.dataframe(sector_df, use_container_width=True)

  with tab3:
    st.subheader("Explore Trust-Level Performance")
    selected_year = st.selectbox("Select Year", raw_df["Year"].unique())
    filtered_df = raw_df[raw_df["Year"] == selected_year]

    st.write(
        f"Showing data for **{selected_year}** ({len(filtered_df)} records)"
    )
    st.dataframe(filtered_df, use_container_width=True)