import pandas as pd

from darts import TimeSeries

def extend_covariates(ts: TimeSeries, required_start: pd.Timestamp) -> TimeSeries:
    """
    Extends a TimeSeries backwards to cover the required history by padding it
    with the earliest available value.
    """
    # Get current start time and frequency
    current_start = ts.start_time()
    freq = ts.freq  # Ensure consistent frequency

    if current_start <= required_start:
        # Already sufficient
        return ts

    # Create missing timestamps from required_start to current_start - 1 step
    new_dates = pd.date_range(start=required_start, end=current_start - pd.Timedelta(weeks=1), freq=freq)

    # Get the first available row's values to fill missing timestamps
    first_values = ts.pd_dataframe().iloc[0]

    # Create DataFrame with repeated first values
    df_extension = pd.DataFrame([first_values] * len(new_dates), index=new_dates, columns=ts.columns)

    # Convert the extension DataFrame into a TimeSeries
    ts_extension = TimeSeries.from_dataframe(df_extension, freq=freq)

    # Concatenate the extension and original TimeSeries
    ts_extended = ts_extension.append(ts)

    return ts_extended
