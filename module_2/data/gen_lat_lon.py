import numpy as np
import math

import pandas as pd


def gen_lat_lon():
    df = pd.read_parquet("driver_stats.parquet")

    latitude = np.arccos(np.random.random(size=(1807, 1)) * 2 - 1)
    longitude = np.random.random(size=(1807, 1)) * math.pi * 2
    df["lat"] = latitude
    df["lon"] = longitude
    df.to_parquet("driver_stats_lat_lon.parquet")


if __name__ == "__main__":
    gen_lat_lon()
