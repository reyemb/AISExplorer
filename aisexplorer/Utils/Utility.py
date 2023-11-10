import pandas as pd

# Define columns and their respective data types
COLUMN_TYPES = {
    "int": [
        "SHIP_ID",
        "IMO",
        "MMSI",
        "TYPE_COLOR",
        "TIMEZONE",
        "COUNT_PHOTOS",
        "NEXT_PORT_ID",
        "COURSE",
        "YOB",
        "DWT",
        "ETA_OFFSET",
        "DISTANCE_TO_GO",
        "PORT_ID",
        "INLAND_ENI",
    ],
    "float": ["LON", "LAT", "SPEED", "DRAUGHT", "LENGTH", "WIDTH"],
    "bool": ["CTA_ROUTE_FORECAST"],
    "str": [
        "CALLSIGN",
        "SHIPNAME",
        "CODE2",
        "COUNTRY",
        "NEXT_PORT_NAME",
        "NEXT_PORT_COUNTRY",
        "DESTINATION",
        "TYPE_SUMMARY",
        "STATUS_NAME",
        "CURRENT_PORT_UNLOCODE",
        "CURRENT_PORT_COUNTRY",
        "AREA_CODE",
        "STATUS",
        "AREA_NAME",
        "CURRENT_PORT",
        "COLLECTION_NAME",
    ],
    "unix": ["LAST_POS"],
    "unix_masked": ["ETA"],
    "timestamp": ["ETA_UPDATED"],
}


def set_types_df(df):
    """
    Set the data types for a DataFrame's columns based on predefined mappings.

    Args:
        df (pd.DataFrame): The DataFrame whose data types are to be set.

    Returns:
        pd.DataFrame: The DataFrame with updated data types.
    """
    df = df.copy()

    # Apply types for each group of columns
    for dtype, cols in COLUMN_TYPES.items():
        if dtype == "int":
            df[cols] = df[cols].apply(pd.to_numeric, errors="coerce")
        elif dtype == "float":
            df[cols] = df[cols].apply(pd.to_numeric, errors="coerce")
        elif dtype == "bool":
            df[cols] = df[cols].astype(bool)
        elif dtype == "str":
            df[cols] = df[cols].astype(str)
        elif dtype in ["unix", "unix_masked"]:
            for col in cols:
                if dtype == "unix_masked":
                    df[col] = df[col].apply(lambda x: x if x != "masked" else None)
                df[col] = pd.to_numeric(df[col], errors="coerce")
                df[col] = pd.to_datetime(df[col], unit="s", errors="coerce")
        elif dtype == "timestamp":
            df[cols] = df[cols].apply(pd.to_datetime, errors="coerce")

    return df
