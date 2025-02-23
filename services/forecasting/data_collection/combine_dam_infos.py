import os
import glob
import pandas as pd

def combine_filtered_csv(directory, target_dam="Тича"):
    """
    Combines rows from CSV files in the given directory where the 'dam_name'
    column equals target_dam. The CSV files are expected to have filenames in the
    format {day}_{month}_{year}.csv. A new 'timestamp' column is added based on the filename.

    Parameters:
        directory (str): The path to the directory containing CSV files.
        target_dam (str): The dam name to filter by. Default is "Тича".

    Returns:
        pd.DataFrame: A concatenated DataFrame with filtered rows and an added 'timestamp' column.
    """
    # Find all CSV files in the directory
    csv_files = glob.glob(os.path.join(directory, '*.csv'))
    filtered_dfs = []

    for file in csv_files:
        base_name = os.path.basename(file)
        name_part, _ = os.path.splitext(base_name)

        # Expecting filename format: day_month_year.csv
        try:
            day, month, year = name_part.split('_')
        except ValueError:
            print(f"Skipping file {base_name} because it does not match the expected format.")
            continue

        # Construct a timestamp; adjust format as needed
        timestamp = f"{year}-{month}-{day}"

        # Read the CSV file
        df = pd.read_csv(file)

        # Filter rows where 'dam_name' equals target_dam
        filtered = df[df['dam_name'] == target_dam].copy()

        # If there are matching rows, add a 'timestamp' column and collect the DataFrame
        if not filtered.empty:
            filtered['timestamp'] = timestamp
            filtered_dfs.append(filtered)

    # Combine all filtered DataFrames into a single DataFrame
    if filtered_dfs:
        return pd.concat(filtered_dfs, ignore_index=True)
    else:
        return pd.DataFrame()

if __name__ == "__main__":
    new_df = pd.read_csv("Cleaned_Merged_Ticha_Data.csv")
    #new_df = new_df.reindex(columns=['timestamp', 'number', 'water_body_directorate', 'dam_name', 'total_volume', 'dead_volume', 'available_volume', 'available_volume_percent', 'available_useful_volume', 'available_useful_volume_percent', 'water_intake', 'water_drain'])
    #new_df.to_csv("Cleaned_Merged_Ticha_Data.csv", index=False)

    combined_df = combine_filtered_csv("/home/kala/Documents/Hackathon-Burgas-2025/code-of-the-future-25-false-positive/services/moew-scraping/dam_data")
    combined_df.to_csv("combined_filtered_data.csv", index=False)

    print(combined_df)