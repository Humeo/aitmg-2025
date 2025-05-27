import json
import math

import pandas as pd
from tqdm import tqdm

df = pd.read_csv("../demo_data/labeled_demo_data_aitmg_202504.csv")


def convert_to_json_batches(df, batch_size=2):
    """
    Converts the DataFrame to a list of JSON array strings, processed in batches.
    Each JSON array string corresponds to one batch of data.
    """
    if df is None or df.empty:
        print("DataFrame is not loaded or is empty. Cannot process.")
        return []

    num_rows = len(df)
    if num_rows == 0:
        print("DataFrame has 0 rows.")
        return []

    num_batches = math.ceil(num_rows / batch_size)
    all_json_batches_strings = []

    print(f"Processing {num_rows} rows in {num_batches} batches of size {batch_size}...")

    for i in tqdm(range(0, num_rows, batch_size), total=num_batches, desc="Converting Batches to JSON", ncols=100):
        start_idx = i
        end_idx = min(i + batch_size, num_rows)

        batch_df = df.iloc[start_idx:end_idx]

        if batch_df.empty:
            continue

        # Convert the current batch_df to a list of dictionaries
        # The orient='records' parameter does exactly what you need:
        # [{'column1': value, 'column2': value, ...}, ...]
        # We need to ensure the column names match "uuid", "req", "rsp"
        # If your CSV columns are already named this way, it's direct.
        # If not, you might need to rename them before this step or select specific columns.
        # Assuming columns are already 'uuid', 'req', 'rsp'

        # Ensure the columns exist before trying to convert
        required_cols = ['uuid', 'req', 'rsp']
        if not all(col in batch_df.columns for col in required_cols):
            print(f"Error: Batch is missing one of the required columns: {required_cols}")
            print(f"Available columns: {batch_df.columns.tolist()}")
            continue  # Skip this batch or handle error appropriately

        # Select only the required columns in the correct order for to_dict
        # (though to_dict(orient='records') preserves original column order from the df)
        records_list = batch_df[required_cols].to_dict(orient='records')

        # Convert the list of dictionaries to a JSON array string
        # indent=2 is for pretty-printing, remove if you need compact JSON
        json_array_string = json.dumps(records_list, indent=2)
        all_json_batches_strings.append(json_array_string)

        # --- You can process each json_array_string here ---
        # For example, print it, save it to a file, send it over a network, etc.
        # print(f"\n--- JSON for Batch starting at index {start_idx} ---")
        # print(json_array_string)
        # ----------------------------------------------------

    print("Finished converting all batches to JSON strings.")
    return all_json_batches_strings

convert_to_json_batches(df, 10)