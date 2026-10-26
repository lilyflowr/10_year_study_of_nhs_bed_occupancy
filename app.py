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
      "The Patient Flow Crisis Of The NHS: A 10-Year Data Analysis (2016–2026)"
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
    ### The View From the Ward Floor

    If you have worked an evening shift in an acute NHS ward during winter peak periods, you know the signs of a patient gridlock long before you check the status board. You hear call bells chiming continuously for patients waiting on delayed discharge letters. You see paramedics waiting in hallways beside patients on stretchers. You feel the definite tension of a hospital running at full operational capacity.

    For years, public debates around healthcare reform have fixated on a single metric: bed numbers. The policy response has been predictable: add funding, open beds, hire staff.

    Yet, after analysing 10 years of NHS KH03 bed occupancy data (2016 through 2026), thousands of quarterly records across every acute trust in England, the empirical reality is clear: the NHS does not simply have a physical capacity problem; it has a systemic patient flow problem.
    """)

  # Part 1 + Interactive Plot
  st.markdown("""
    ---
    ### Operating Above Safety Limits for a Decade

    Clinical guidelines from the National Institute for Health and Care Excellence (NICE) and healthcare think tanks like The King’s Fund establish 85% occupancy as the safe upper threshold for acute hospital operation. *(NHS Hospital Bed Numbers: Past, Present, Future, 2019)* Above 85%, hospitals lose the functional flexibility to manage emergency admissions, bed turnaround times collapse, and infection-control buffers break down. *(O'Dowd, 2021)*

    My 10-year national data analysis shows a sharp operational trajectory:
    - **2016–2020 Baseline:** National General & Acute (G&A) occupancy hovered close to critical limits, averaging ~90.2% year after year. *(Critical Care Bed Capacity and Urgent Operations Cancelled 2016-17 Data, n.d.)*
    - **The 2020–21 Anomaly:** During peak COVID-19 restrictions, mandatory social distancing and elective surgery halts artificially drove national occupancy down to 76.76%. *(Hospital Admitted Patient Care Activity 2020-21, n.d.)*
    - **The Post-COVID-19 Overshoot:** Rather than stabilising near safe thresholds, occupancy rebounded. By 2025–26, national G&A occupancy reached a 10-year peak of 91.58%. *(Hospital bed occupancy, 2025)*
    """)

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
    ### The 99% Gridlock

    National averages often cushion local pain points. When filtering the 2025–26 dataset down to individual hospital trusts (and excluding specialist centres like Moorfields Eye Hospital to focus exclusively on general acute care), the data exposes acute trusts functioning at virtual gridlock:
    
    1. **Buckinghamshire Healthcare NHS Trust:** 99.43% G&A Occupancy
    2. **York Teaching Hospital NHS Foundation Trust:** 99.09% G&A Occupancy
    3. **George Eliot Hospital NHS Trust:** 98.79% G&A Occupancy
    4. **University Hospitals Coventry and Warwickshire:** 98.75% G&A Occupancy

    Running an acute trust at 99% average annual occupancy means that after accounting for turnaround times, room cleaning, and emergency holdovers, the facility has no operational buffer.
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

  # Part 3 & 4
  st.markdown("""
    ---
    ### The Front Door, Internal Engine, and the “Back Door” Trap

    Why does adding beds fail to resolve gridlock? Policy research from reports like Re:State’s *Hospital of the Future*, independent findings from *The Health Foundation*, and evaluations from the British Medical Association (BMA) confirm that acute hospitals are trapped across three operational friction points:

    1. **The Front Door (A&E Overload):** Emergency departments absorb unscheduled care demand when primary care or community response pathways are saturated.
    2. **The Internal Engine (In-Hospital Bottlenecks):** Diagnostic delays, slow consultations, and a lack of weekend consultant decision-making on discharges slow care progression.
    3. **The Back Door (Social Care Deficit):** This represents the primary systemic bottleneck. Thousands of hospital beds are occupied by patients who are clinically fit for discharge but remain hospitalised due to delayed social care packages, community rehabilitation, or local authority housing arrangements.

    As BMA NHS Bed Data Analysis highlights, keeping a clinically ready patient in an acute bed costs the system over £400 per day and increases the risk of hospital-acquired infections and deconditioning.

    ---
    ### Sector Divergence, Acute vs Speciality Pathways

    A critical finding from the 10-year analysis lies in sector comparison:
    - **General & Acute (91.58%)** and **Mental Health (89.07%)** operate under perpetual stress.
    - **Maternity Services (61.08%)** maintain healthy operational buffers because admission streams are predictable.
    - **Learning Disabilities (61.38%)** show a structural decline over a decade, reflecting policy transformations toward community-focused care models.

    This difference shows that blanket capacity expansion is inefficient: capital investment and operational flow interventions must target Acute Care and Mental Health pathways.
    """)

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

  # Tech Adoption & Recommendations
  st.markdown("""
    ---
    ### The Realities of NHS Tech Adoption

    A common reflex in healthcare policy is treating software as an instant remedy: if we digitise, gridlock clears.

    In its tactical planning guidance (such as the NHS Priorities and Operational Planning Guidance) and national transformation frameworks, NHS England formally pushed for the rollout of Electronic Patient Record (EPR) systems to replace traditional bedside whiteboards.

    On paper, procurement figures look solid: industry tracking reported via *Building Better Healthcare* confirms that over 90% of NHS trusts have deployed an active EPR system.

    However, examining functional integration reveals a major operational gap:
    - **The Integration Effort Deficit:** Reviews by independent think tanks like *The Health Foundation* show that basic software procurement does not equal full system integration. Many providers maintain fragmented software that fails to communicate effectively with regional social care or downstream community networks.
    - **The Operational Bottleneck:** Frontline clinical evaluations observe that installing basic record systems without advanced automated bed-turnover triggers or real-time workflow modules forces clinical staff back onto manual workarounds.

    ---
    ### Actionable Policy & Recommendations

    To break chronic gridlock, the NHS must move from reactive bed management to predictive operational flow:
    
    1. **Bridge the Functional Integration Gap:** Rather than celebrating baseline EPR procurement milestones, healthcare leadership must fund advanced, interoperable modules, such as automated bed-turnover triggers and real-time tracking platforms, so systems actively coordinate patient movement rather than just recording static data.
    2. **Unblock the Back Door via Automated Discharge Coordination:** Deploy structured electronic workflow tools for discharge summaries and pharmacy sign-offs to cut hours of administrative delay on discharge day.
    3. **Rebalance Acute and Community Resources:** Acute wards alone can't solve systemic flow. Allocation must correspond to social care demand so that “fit-to-discharge” patients transition out of acute beds without delay.
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