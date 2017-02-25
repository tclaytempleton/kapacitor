import pandas as pd


def index_by_date(dates, rates, format):
    formatted_dates = [pd.to_datetime(item, format=format) for item in dates.values]
    return pd.DataFrame(rates.values, index=formatted_dates)