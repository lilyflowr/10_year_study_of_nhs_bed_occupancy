import os

import pandas as pd
import numpy as np
import glob

file_list = glob.glob("NHS_KH03_Raw_Data/KH03_*.xlsx") 

clean_columns = [
    "Year","Period","Region_Code","Org_Code","Org_Name",
    "Available_Total","Available_Gen_Acute","Available_LD",
    "Available_Maternity","Available_Mental",
    "Occupied_Total","Occupied_Gen_Acute","Occupied_LD",
    "Occupied_Maternity", "Occupied_Mental",
    "Percent_Total","Percentage_Gen_Acute","Percentage_LD",
    "Percentage_Maternity","Percentage_Mental"
]

all_data =[]
for file in file_list:
    try:
        df = pd.read_excel(
            file,
            sheet_name="NHS Trust by Sector",
            skiprows=14,
            usecols="B:K,M:Q,S:W",
            names=clean_columns
        )

        df = df.dropna(subset=['Org_Code'])

        df = df.replace('-', 0).fillna(0)

        percent_cols = ["Percent_Total", "Percentage_Gen_Acute","Percentage_LD", "Percentage_Maternity", "Percentage_Mental"]
        for col in percent_cols:
            df[col] = df[col].astype(str).str.strip().replace('-', '0')
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

        df['Source_File'] = os.path.basename(file)

        all_data.append(df)
        print(f"Successfuly processed: {file}")

    except Exception as e:
        print(f"Error processing {file}: {e}")


master_df = pd.concat(all_data, ignore_index=True)

master_df.to_csv("NHS_KH03_Cleaned_Data/cleaned_data.csv", index=False)
print(f"ETL Complete. Master file saved with {len(master_df)} rows.")