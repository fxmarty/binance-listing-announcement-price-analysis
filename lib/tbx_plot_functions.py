import numpy as np
import pandas as pd
import mplfinance as mpf


def plot_candles(candles_list, unit, title="", save_path=None, index_marker=None):
    """
    This function is wrapper method to either plot on the fly candles' graph
    or save it

    `unit` is either "ms' or "s".
    """

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

    print(dataset)
    if save_path is not None:
        save_params = dict(fname=save_path, dpi=300, bbox_inches="tight")
        mpf.plot(dataset, type="candle", volume=True, show_nontrading=True,
                 style="charles", title=title, addplot=plots_list, savefig=save_params)
    else:
        mpf.plot(dataset, type="candle", volume=True, show_nontrading=True,
                 style="charles", title=title, addplot=plots_list)
