import numpy as np
import pandas as pd
import mplfinance as mpf

from lib.tbx_data_utils import filter_out_nontrading, next_non_nan


def create_fill(dataset):
    """
    Where `dataset` is a OHLCV dataframe, this function allows to recover
    meaningful data to pass as `fill_between` for mplfinance, for aesthetical
    reasons.
    """
    y1 = np.copy(dataset['Low'].values)
    y2 = np.copy(dataset['High'].values)

    spread_mean = np.mean(np.abs(dataset['Open'].values - dataset['Close'].values))

    for i, k in enumerate(y1):
        if y2[i] - y1[i] < spread_mean:
            y1[i] = y1[i] - spread_mean/2
            y2[i] = y2[i] + spread_mean/2

    res = dict(y1=y1, y2=y2, alpha=0.2)
    return res


def plot_candles(candles_list, unit, title="",
                 plot_type="candle", show_nontrading=True, style="binance",
                 fill_between=None, save_path=None, index_marker=None):
    """
    This function is wrapper method to either plot on the fly candles' graph
    or save it

    `unit` is either "ms' or "s".
    """

    if show_nontrading is False:
        index_marker = next_non_nan(index_marker, candles_list)
        candles_list = filter_out_nontrading(candles_list)

    candles_array = np.array(candles_list)
    index_df = pd.DataFrame({"Date": candles_array[:, 0].astype(int)})
    index_df["Date"] = pd.to_datetime(index_df["Date"], unit=unit)
    dataset = pd.DataFrame(
        {
            "Open": candles_array[:, 1],
            "High": candles_array[:, 2],
            "Low": candles_array[:, 3],
            "Close": candles_array[:, 4],
            "Volume": candles_array[:, 5],
        },
        index=pd.DatetimeIndex(index_df["Date"]),
    )
    dataset.index.name = "Date"

    plots_list = []
    if index_marker:
        signal = [np.nan] * len(candles_list)
        signal[index_marker] = candles_list[index_marker][3]  # low
        apd = mpf.make_addplot(signal, type="scatter", markersize=30, marker="^", alpha=0.5)
        plots_list.append(apd)
    else:
        plots_list = None

    if save_path is not None:
        savefig = dict(fname=save_path, dpi=300, bbox_inches="tight")
    else:
        savefig = None

    if fill_between is True:
        fill_between = create_fill(dataset)

    kwargs = dict(addplot=plots_list,
                  fill_between=fill_between,
                  savefig=savefig)
    kwargs = {k: v for k, v in kwargs.items() if v is not None}

    #print(dataset)

    # pass only non-None arguments, as e.g. for `fill_between` passing None fails
    mpf.plot(dataset, type=plot_type, volume=True, style=style,
             show_nontrading=show_nontrading, title=title,
             **kwargs)