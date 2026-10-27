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
st.sidebar.title("🏥 NHS Bed Analytics")
st.sidebar.markdown("""
**Author:** Ibinabo Adiela  
*Healthcare Data Analyst & Registered Nurse*
""")
st.sidebar.divider()

view_mode = st.sidebar.radio(
    "Select Interface View",
    ["📖 Article & Integrated Analytics", "📊 Interactive Dashboard Explorer"],
)

st.sidebar.markdown("### Connect with Me")
st.sidebar.markdown(
    "🔗 **[LinkedIn](https://www.linkedin.com/in/ibinaboadiela)** | "
    "📝 **[Medium](https://ibinaboadiela.medium.com/)** | "
    "🐦 **[X (Twitter)](https://x.com/DTechNurse)**"
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

    Anyone who has worked an evening shift in an NHS ward during the busy winter months knows how stressful it can be to manage a ward at full capacity. Call bells ring for patients waiting on delayed discharge letters. Paramedics wait in hallways with patients on stretchers. The tension is obvious when a hospital is pushed to its limit.

    For years, public debates about healthcare reform have focused on bed numbers. Usually, the response is to add funding, open more beds, and hire extra staff.

    After analysing 10 years of NHS KH03 bed occupancy data (2016 to 2026) and thousands of quarterly records from every acute trust in England, it is clear that the NHS faces more than just a physical capacity problem. The real issue is a systemic patient flow problem.
    """)

  # Part 1 + Interactive Plot
  st.markdown("""
    ---
    ### Operating Above Safety Limits for a Decade

    In healthcare policy, two main benchmarks define bed pressure. Clinically, groups like the Royal College of Emergency Medicine (RCEM) and the Royal College of Surgeons say 85% is the safe maximum to keep infection control buffers and handle emergency surges. Operationally, NHS planning guidance (including frameworks cited by [The King’s Fund](https://www.kingsfund.org.uk/)) sets a maximum ceiling of 92%.

    Even the official 92% ceiling was often exceeded before 2019. When hospitals run above these levels for long periods, bed turnaround times slow down and patient safety margins disappear.

    Here is what my analysis of NHS bed capacity over the past decade shows:
    - **2016–2020 Baseline:** National General & Acute (G&A) occupancy hovered close to critical limits, averaging **~90.2%** year after year.
    - **The 2020–21 Anomaly:** During the peak of COVID-19 restrictions, mandatory social distancing and the halt of elective surgeries caused national occupancy to drop to **76.76%**.
    - **The Post-COVID-19 Overshoot:** Instead of returning to safe levels, occupancy went up again. By **2025–26, the national General & Acute occupancy rate hit a 10-year high of 91.58%**.
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
      annotation_text="NICE / RCEM 85% Safe Ceiling",
      annotation_position="bottom right",
  )
  fig_macro.update_layout(yaxis_range=[60, 100])
  st.plotly_chart(fig_macro, use_container_width=True)

  # Part 2 + Interactive Plot
  st.markdown("""
    ---
    ### The 99% Bed Capacity Gridlock

    National averages can hide local problems. When I filtered the 2025–26 data to look at individual hospital trusts and left out specialist centres like Moorfields Eye Hospital to focus on general acute care, the numbers showed some trusts were nearly at a standstill:

    1. **Buckinghamshire Healthcare NHS Trust:** 99.43% G&A Occupancy
    2. **York Teaching Hospital NHS Foundation Trust:** 99.09% G&A Occupancy
    3. **George Eliot Hospital NHS Trust:** 98.79% G&A Occupancy
    4. **University Hospitals Coventry and Warwickshire:** 98.75% G&A Occupancy

    When an acute trust runs at **99% average annual occupancy**, there’s no room for delays. Once you factor in turnaround times, cleaning, and emergency cases, the hospital has no buffer.
    """)

  fig_top10 = px.bar(
      top10_in_crisis_df,
      x="average_occupied_percentage",
      y="Org_Name",
      orientation="h",
      title="Figure 2: Top 10 Acute NHS Trusts in Bed Capacity Crisis (2025–26)",
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

    Why doesn’t adding more beds fix the problem? Research from reports like [Re:State’s Hospital of the Future](https://re-state.co.uk/publications/hospital-of-the-future-ending-the-patient-gridloc/), findings from [The Health Foundation](https://www.health.org.uk/), and reviews by the [British Medical Association (BMA)](https://www.bma.org.uk/) all show that acute hospitals face three main bottlenecks:

    1. **The Front Door (A&E Overload):** Emergency departments absorb unscheduled admissions when demand is high, and primary care or community response pathways are saturated.
    2. **The Internal Engine (In-Hospital Bottlenecks):** Delays in diagnosis, slow consultations, and not having consultants make discharge decisions on weekends all slow down care.
    3. **The Back Door (Social Care Deficit):** This is the system's main bottleneck. Thousands of hospital beds are filled by patients who are ready to leave but can’t because of delays in social care packages, community rehab, or local authority housing.

    [BMA NHS Bed Data Analysis shows that](https://www.bma.org.uk/advice-and-support/nhs-delivery-and-workforce/pressures/nhs-hospital-beds-data-analysis) keeping a patient who is ready for discharge in an acute bed costs the NHS over £400 per day. It also raises the risk of hospital-acquired infections and deconditioning.

    ---
    ### Sector Divergence, Acute vs Speciality Pathways

    One key finding from the 10-year analysis comes from comparing different sectors:
    - **General & Acute (91.58%)** and **Mental Health (89.07%)** operate under perpetual stress.
    - **Maternity Services (61.08%)** maintain healthy operational buffers because admission streams are predictable.
    - **Learning Disabilities (61.38%)** show a structural decline over a decade, reflecting policy transformations toward community-focused care models.

    This difference shows that expanding capacity everywhere isn’t efficient. Investments and operational changes should focus on **Acute Care and Mental Health pathways**.
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

    A common reaction in healthcare policy is to treat software as a quick fix, assuming that going digital will solve the problem.

    In its tactical planning guidance (such as the [NHS Priorities and Operational Planning Guidance](https://www.england.nhs.uk/wp-content/uploads/2023/04/PRN01625-25-26-priorities-and-operational-planning-guidance-january-2025.pdf)) and national transformation frameworks, NHS England formally pushed for the rollout of Electronic Patient Record (EPR) systems to replace traditional bedside whiteboards.

    On paper, procurement figures look solid: [Building Better Healthcare’s](https://buildingbetterhealthcare.com/exclusive-91-of-nhs-trusts-have-an-epr) industry tracking reports that over **90% of NHS trusts** have deployed an active EPR system.

    But when you look at how these systems work together in practice, a major operational gap stands out:
    - **The System Integration Effort Deficit:** Independent think tanks like [The Health Foundation show that](https://www.health.org.uk/) just buying software doesn’t mean full system integration. Many providers still use fragmented software that doesn’t communicate well with regional social care or community networks.
    - **The Operational Bottleneck:** Frontline clinical reviews show that when record systems don’t have advanced features like automated bed-turnover triggers or real-time workflow tools, staff have to rely on manual workarounds.

    ---
    ### Recommendations

    To end chronic gridlock, the NHS needs to move from reacting to bed shortages to predicting and managing patient flow more proactively:
    
    1. **Bridge the Functional Integration Gap:** Instead of just ticking off EPR procurement milestones, healthcare leaders should invest in advanced, connected modules like automated bed-turnover triggers and live tracking platforms. These tools help systems coordinate patient movement, not just record data.
    2. **Unblock the Back Door with Automated Discharge Coordination:** Use electronic workflow tools for discharge summaries and pharmacy sign-offs to save hours of admin time on discharge day.
    3. **Rebalance Acute and Community Resources:** Acute wards can’t fix patient flow on their own. Resources need to match social care demand so patients who are ready to leave can move out of acute beds without waiting.

    ---
   
    ### Connect with Me
    🔗 **[LinkedIn](https://www.linkedin.com/in/ibinaboadiela)** | 📝 **[Medium](https://ibinaboadiela.medium.com/)** | 🐦 **[X (Twitter)](https://x.com/DTechNurse)**
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