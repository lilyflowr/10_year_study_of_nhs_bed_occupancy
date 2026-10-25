import pandas as pd 
#read
df = pd.read_csv("NHS_KH03_Cleaned_Data/cleaned_data.csv")

#streamline percentage col7mns
percent_cols = ["Percent_Total", "Percentage_Gen_Acute","Percentage_LD", "Percentage_Maternity", "Percentage_Mental"]
for col in percent_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

#macrotrend dataset group by year
macro_df = df.groupby('Year').agg(
    total_available_gen_acute=('Available_Gen_Acute', 'sum'),
    total_occupied_gen_acute=('Occupied_Gen_Acute', 'sum')
    ).reset_index()

# calculate the weighted percentage
macro_df['average_occupied_percentage'] = round(
    macro_df['total_occupied_gen_acute'] / macro_df['total_available_gen_acute'] * 100, 2
)
#export macro trend
macro_df.to_csv("NHS_KH03_Cleaned_Data/tableau_macro_trend.csv", index=False)
print("Exported taleau_macro_trend.csv successfully!")

#sector breakdown 
sector_df = df.groupby('Year').agg(
    gen_acute_available=('Available_Gen_Acute', 'sum'),
    gen_acute_occupied=('Occupied_Gen_Acute', 'sum'),
    ld_available=('Available_LD', 'sum'),
    ld_occupied=('Occupied_LD', 'sum'),
    maternity_available=('Available_Maternity', 'sum'),
    maternity_occupied=('Occupied_Maternity', 'sum'),
    mental_available=('Available_Mental', 'sum'),
    mental_occupied=('Occupied_Mental', 'sum')
).reset_index()

#percentages for each sector
sector_df['gen_acute_percentage'] = round(
    sector_df['gen_acute_occupied'] / sector_df['gen_acute_available'] * 100, 2
)

sector_df['ld_percentage'] = round(
    sector_df['ld_occupied'] / sector_df['ld_available'] * 100, 2
)   
sector_df['maternity_percentage'] = round(
    sector_df['maternity_occupied'] / sector_df['maternity_available'] *  100, 2
)
sector_df['mental_percentage'] = round(
    sector_df['mental_occupied'] / sector_df['mental_available'] *  100, 2
)

sector_df.to_csv("NHS_KH03_Cleaned_Data/tableau_sector_breakdown.csv", index=False)
print("Exported tableau_sector_breakdown.csv successfully!")

# Filter for the latest year and active acute beds
df_2526 = df[(df['Year'] == '2025-26') & (df['Available_Gen_Acute'] > 0)]

# Group by trust identifiers and aggregate the bed sums
trust_df = df_2526.groupby(['Org_Code', 'Org_Name', 'Region_Code']).agg(
    total_available_gen_acute=('Available_Gen_Acute', 'sum'),
    total_occupied_gen_acute=('Occupied_Gen_Acute', 'sum')
).reset_index()

# calculate the percentage, sort descending, and take the top 10
trust_df['average_occupied_percentage'] = round(
    (trust_df['total_occupied_gen_acute'] / trust_df['total_available_gen_acute']) * 100, 2
)

top10_in_crisis_df = trust_df.sort_values(by='average_occupied_percentage', ascending=False).head(10)

# Export to CSV
top10_in_crisis_df.to_csv('NHS_KH03_Cleaned_Data/tableau_top_10_crisis.csv', index=False)
print("Exported tableau_top_10_crisis.csv successfully!")