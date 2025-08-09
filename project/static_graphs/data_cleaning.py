import pandas as pd
import os


def vehicle_ownership_cleaning(file_name):
    """
    Cleans the vehicle ownership data with the specified file name.
    
    Parameters:
    file_name (str): The name of the CSV file containing vehicle ownership data.
    
    Returns:
    pd.DataFrame: A cleaned DataFrame with relevant columns and rows.
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


def population_growth_cleaning(file_name):
    """
    Cleans the population growth data with the specified file name.
    
    Parameters:
    file_name (str): The name of the CSV file containing population growth data.
    
    Returns:
    pd.DataFrame: A cleaned DataFrame with relevant columns and rows.
    """
    # Load the data
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, file_name)
    # Read after skipping 6 rows, no header
    population_growth = pd.read_csv(file_path, skiprows=6, header=None)
    
    # Set header
    header = []
    for column in population_growth.columns:
        # Check if the first row is empty or contains only whitespace
        if pd.isnull(population_growth[column].iloc[0]) or str(population_growth[column].iloc[0]).strip() == '':
            header.append(population_growth[column].iloc[1])
        else:
            header.append(population_growth[column].iloc[0])
    population_growth.columns = header
    
    # Remove unnecessary rows
    population_growth = population_growth.iloc[3:-5].reset_index(drop=True)
    # Remove columns and rows where all values are NaN
    population_growth = population_growth.dropna(axis=1, how='all')
    population_growth = population_growth.dropna(how='all')
    # Remove columns and rows where all values are empty strings (after dropping NaN columns)
    population_growth = population_growth.loc[:, ~(population_growth == '').all()]
    population_growth = population_growth.loc[~(population_growth == '').all(axis=1)]
    
    # Turn numeric columns into float
    population_growth = population_growth.apply(pd.to_numeric, errors='ignore')

    # Add a Total Victoria row
    total_victoria = population_growth[population_growth["S/T name"] == "Victoria"].sum(numeric_only=True)
    total_victoria["SA2 name"] = "Total Victoria"
    population_growth = pd.concat([population_growth, total_victoria.to_frame().T], ignore_index=True)
    # Fix the % and Population Density Columns for the Total Victoria row
    index_vic = population_growth[population_growth["SA2 name"] == "Total Victoria"].index
    index_vic = index_vic[0] if len(index_vic) > 0 else None
    population_growth.at[index_vic, "%"] = population_growth.at[index_vic, "2011-2021"] / population_growth.at[index_vic, "2011"]
    population_growth.at[index_vic, "Population density 2021"] = population_growth.at[index_vic, "2021"] / population_growth.at[index_vic, "Area"]

    # Keep only CBD rows and total Vic row and total Aus row
    keep_names = [
        "Melbourne CBD - East",
        "Melbourne CBD - North",
        "Melbourne CBD - West",
        "Total Victoria",
        "TOTAL AUSTRALIA"
    ]
    population_growth = population_growth[population_growth["SA2 name"].isin(keep_names)].reset_index(drop=True)
    
    # Remove the first 9 columns
    population_growth = population_growth.iloc[:, 9:]
    # Rename the "SA2 name" column to "Region"
    population_growth = population_growth.rename(columns={"SA2 name": "Region"})
    # Rename 'TOTAL AUSTRALIA' to 'Total Australia'
    population_growth["Region"] = population_growth["Region"].replace("TOTAL AUSTRALIA", "Total Australia")

    # Set the desired order for the 'Region' column
    order = ["Melbourne CBD - East", "Melbourne CBD - North", "Melbourne CBD - West", "Total Victoria", "Total Australia"]
    # Reindex the DataFrame to match the desired order
    population_growth = population_growth.set_index("Region").loc[order].reset_index()

    return population_growth


def carbon_emission_cleaning(file_name):
    """
    Cleans the carbon emissions data with the specified file name.
    
    Parameters:
    file_name (str): The name of the CSV file containing carbon emissions data.

    Returns:
    pd.DataFrame: A cleaned DataFrame with relevant columns and rows.
    """
    # Load the data
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, file_name)
    carbon_emission = pd.read_csv(file_path)
    
    # Keep only the "Transport", "Vehicle Type", and "CarbonEmission" columns
    carbon_emission = carbon_emission[["Transport", "Vehicle Type", "CarbonEmission"]]

    # Replace all private vehicle "Transport" values with "Vehicle Type" values
    carbon_emission.loc[carbon_emission["Transport"] == "private", "Transport"] = carbon_emission.loc[carbon_emission["Transport"] == "private", "Vehicle Type"]

    # Remove "Vehicle Type" column
    carbon_emission = carbon_emission.drop(columns=["Vehicle Type"])
    
    # Group by 'Transport' and calculate the mean of 'CarbonEmission'
    average_emission = carbon_emission.groupby("Transport")["CarbonEmission"].mean().reset_index()
    
    return average_emission


def save_cleaned_dataframe(df, file_name):
    """
    Save the cleaned DataFrame to the project folder as a CSV.
    """
    project_dir = os.path.dirname(os.path.dirname(__file__))
    output_path = os.path.join(project_dir, file_name)
    df.to_csv(output_path, index=False)
    
    print(f"{file_name} saved to {output_path}")


# Execute the functions for each dataset

vehicle_ownership_clean = vehicle_ownership_cleaning("vehicle_ownership_raw.csv")
population_growth_clean = population_growth_cleaning("population_growth_raw.csv")
carbon_emission_clean = carbon_emission_cleaning("carbon_emission_raw.csv")

save_cleaned_dataframe(vehicle_ownership_clean, "vehicle_ownership_clean.csv")
save_cleaned_dataframe(population_growth_clean, "population_growth_clean.csv")
save_cleaned_dataframe(carbon_emission_clean, "carbon_emission_clean.csv")