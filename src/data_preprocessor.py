""" preprocessing utilizes:
    1.keep original documents intact (flight number, aircraft, from, to, std, atd, sta, ata)
    2.remove rows where 'data' column equals '00:00:00' (if 'data' col exists),
    3.add derived columns: departure_delay_mins, arrival_delay_mins,
    4.do light parsing to convert std/atd/sta/ata to datetimes only for calculation,
    5.return a copy of dataframe with new columns appended.                                  """

import pandas as pd
import numpy as np
from typing import Optional

def safe_parse_datetime(cell) -> Optional[pd.Timestamp]:
    """Try to parse a time or datetime from a cell; return pd.NaT on failure."""
    if pd.isna(cell):
        return pd.NaT
    return pd.to_datetime(cell, errors='coerce', infer_datetime_format=True)

def find_col(df, possible_names):
    """Find a column name in df that matches any variant from possible_names."""
    for name in df.columns:
        for variant in possible_names:
            if variant.lower() in str(name).lower():
                return name
    return None

def preprocess_from_excel(path: str) -> pd.DataFrame:
    df = pd.read_excel(path, engine="openpyxl", dtype=object)

    # Remove '00:00:00' rows if column 'data' exists
    if 'data' in df.columns:
        df = df[df['data'] != '00:00:00'].copy()

    out = df.copy()

    # Identify time columns flexibly
    std_col = find_col(out, ['STD', 'Scheduled Departure', 'Schedule Departure', 'Dep Std'])
    atd_col = find_col(out, ['ATD', 'Actual Departure', 'Actual Dep', 'Departure Time'])
    sta_col = find_col(out, ['STA', 'Scheduled Arrival', 'Schedule Arrival', 'Arr Sta'])
    ata_col = find_col(out, ['ATA', 'Actual Arrival', 'Arrival Time', 'Actual Arr'])

    # Parse columns for delay calculation
    if std_col: out['__STD'] = out[std_col].apply(safe_parse_datetime)
    if atd_col: out['__ATD'] = out[atd_col].apply(safe_parse_datetime)
    if sta_col: out['__STA'] = out[sta_col].apply(safe_parse_datetime)
    if ata_col: out['__ATA'] = out[ata_col].apply(safe_parse_datetime)

    # Calculate delays
    if '__ATD' in out.columns and '__STD' in out.columns:
        out['departure_delay_mins'] = (out['__ATD'] - out['__STD']).dt.total_seconds() / 60
    else:
        out['departure_delay_mins'] = np.nan

    if '__ATA' in out.columns and '__STA' in out.columns:
        out['arrival_delay_mins'] = (out['__ATA'] - out['__STA']).dt.total_seconds() / 60
    else:
        out['arrival_delay_mins'] = np.nan

    # Convert to numeric
    out['departure_delay_mins'] = out['departure_delay_mins'].astype(float)
    out['arrival_delay_mins'] = out['arrival_delay_mins'].astype(float)

    # Drop helper cols
    for key in ['__STD','__ATD','__STA','__ATA']:
        if key in out.columns:
            out.drop(columns=[key], inplace=True)

    return out


# ------------------ MAIN EXECUTION BLOCK ------------------
if __name__ == "__main__":
    input_path = r"D:\flight_scheduling_system\data\cleaned_flight_scheduling.xlsx"
    output_path = r"D:\flight_scheduling_system\data\final_flight_data_with_delays.xlsx"

    processed_df = preprocess_from_excel(input_path)
    processed_df.to_excel(output_path, index=False)

    print("✅ File processed successfully!")
    print(f"➡️ Saved as: {output_path}")
    print("📊 Columns detected:", processed_df.columns.tolist())

