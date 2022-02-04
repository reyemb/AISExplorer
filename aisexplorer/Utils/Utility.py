import pandas as pd

int_cols = ['SHIP_ID', 'IMO', 'MMSI', 'TYPE_COLOR', 'TIMEZONE', 'COUNT_PHOTOS', 'NEXT_PORT_ID', 'COURSE', 'YOB', 'DWT',
            'ETA_OFFSET', 'DISTANCE_TO_GO', 'PORT_ID', 'INLAND_ENI']
float_cols = ['LON', 'LAT', 'SPEED', 'DRAUGHT', 'LENGTH', 'WIDTH']
bool_cols = ['CTA_ROUTE_FORECAST']
string_cols = ['CALLSIGN', 'SHIPNAME', 'CODE2', 'COUNTRY', 'NEXT_PORT_NAME', 'NEXT_PORT_COUNTRY', 'DESTINATION',
               'TYPE_SUMMARY', 'STATUS_NAME', 'CURRENT_PORT_UNLOCODE', 'CURRENT_PORT_COUNTRY', 'AREA_CODE', 'STATUS',
               'AREA_NAME', 'CURRENT_PORT', 'COLLECTION_NAME']
unix_cols = ['LAST_POS', 'ETA']
timestamp_cols = ['ETA_UPDATED']


def set_types_df(df):
    df = df.copy()
    for column in df.columns:
        if column in int_cols:
            df[column] = pd.to_numeric(df[column])
        elif column in float_cols:
            df[column] = pd.to_numeric(df[column])
        elif column in bool_cols:
            df[column] = df[column].astype(bool)
        elif column in string_cols:
            df[column] = df[column].astype(str)
        elif column in unix_cols:
            df[column] = pd.to_numeric(df[column])
            df[column] = pd.to_datetime(df[column], unit="s")
        elif column in timestamp_cols:
            df[column] = pd.to_datetime(df[column])
    return df
