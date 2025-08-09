import pandas as pd
import os

"""
Vehicle Ownership Data Cleaning
"""

def vehicle_ownership_cleaning(file_name):
    """
    Cleans the carbon emissions data from the specified file path.
    
    Parameters:
    file_path (str): The path to the CSV file containing carbon emissions data.
    
    Returns:
    pd.DataFrame: A cleaned DataFrame with relevant columns and no missing values.
    """
    # Load the data
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, file_name)
    vehicle_ownership = pd.read_csv(file_path, skiprows=1)
    
    # Rename columns
    vehicle_ownership.columns = [
        "State",
        "2016 - 2017", "%_2016_2017",
        "2017 - 2018", "%_2017_2018",
        "2018 - 2019", "%_2018_2019",
        "2019 - 2020", "%_2019_2020",
        "2020 - 2021", "%_2020_2021"
    ]
    
    # Keep only 'Vic.' and 'Aust.' rows
    vehicle_ownership = vehicle_ownership[vehicle_ownership["State"].isin(["Vic.", "Aust."])]
    
    # Calculate total vehicle ownership for each year
    vehicle_ownership["2016"] = vehicle_ownership["2016 - 2017"].str.replace(',', '').astype(float) * vehicle_ownership["%_2016_2017"].astype(float) / 100
    vehicle_ownership["2017"] = vehicle_ownership["2017 - 2018"].str.replace(',', '').astype(float) * vehicle_ownership["%_2017_2018"].astype(float) / 100
    vehicle_ownership["2018"] = vehicle_ownership["2018 - 2019"].str.replace(',', '').astype(float) * vehicle_ownership["%_2018_2019"].astype(float) / 100
    vehicle_ownership["2019"] = vehicle_ownership["2019 - 2020"].str.replace(',', '').astype(float) * vehicle_ownership["%_2019_2020"].astype(float) / 100
    vehicle_ownership["2020"] = vehicle_ownership["2020 - 2021"].str.replace(',', '').astype(float) * vehicle_ownership["%_2020_2021"].astype(float) / 100
    
    # Keep only the 'State' and total columns
    vehicle_ownership = vehicle_ownership[["State", "2016", "2017", "2018", "2019", "2020"]]

    return vehicle_ownership


def save_cleaned_dataframe(df, file_name):
    """
    Save the cleaned DataFrame to the project folder as a CSV.
    """
    project_dir = os.path.dirname(os.path.dirname(__file__))
    output_path = os.path.join(project_dir, file_name)
    df.to_csv(output_path, index=False)
    print(f"{file_name} saved to {output_path}")


vehicle_ownership_clean = vehicle_ownership_cleaning("vehicle_ownership_raw.csv")

save_cleaned_dataframe(vehicle_ownership_clean, "vehicle_ownership_clean.csv")


