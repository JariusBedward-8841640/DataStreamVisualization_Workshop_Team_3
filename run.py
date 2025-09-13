
# animate_streaming_window10_grow_then_slide.py
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("TkAgg")  # or "QtAgg"
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation
from scipy.interpolate import make_interp_spline
import datetime as dt
import os
from dotenv import load_dotenv
import psycopg

CSV_PATH = "data/RMBR4-2_export_test.csv"  # adjust path if needed

# Load and prepare
df = pd.read_csv(CSV_PATH)
df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
df = df.dropna(subset=['Time']).sort_values('Time').reset_index(drop=True)

axes_cols = [c for c in df.columns if c.startswith("Axis")]
df[axes_cols] = df[axes_cols].apply(pd.to_numeric, errors='coerce').fillna(0.0)

n = len(df)
WINDOW = 10  # grow 1..10, then slide (2..11, 3..12, ...)

fig, ax = plt.subplots(figsize=(12, 5))


load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

def run_sql(sql: str, params=None):
    with psycopg.connect(DB_URL, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or [])
            try:
                return cur.fetchall()
            except Exception:
                return []

def insert_data():
    inserted_record = run_sql(
        """
        INSERT INTO CATDC_DATA_FEED
            (PART_ID, TYPE_ID, SOURCE_ID, FEED_ID, READING, TIMESTAMP, STATE)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING ID, PART_ID, TYPE_ID, SOURCE_ID, FEED_ID, READING, TIMESTAMP, STATE
        """,
        [1, 1, 1, 2, 33, "2022-04-22 09:00:00", "RUNNING"]
    )


    print("Inserted:", inserted_record)

def truncate_table():
    run_sql("TRUNCATE TABLE CATDC_DATA_FEED")

truncate_table()

def smooth_stack(sub_time, sub_vals, n_points=200):
    x_num = mdates.date2num(sub_time.to_numpy())
    x_unique = np.unique(x_num)

    if x_unique.size < 2:
        x_dense = np.array([x_num[0], x_num[0] + 1e-9])
        smooth_vals = sub_vals.iloc[[0, 0]].to_numpy(dtype=float).T
    else:
        xmin, xmax = x_num.min(), x_num.max()
        x_dense = np.linspace(xmin, xmax, max(n_points, x_unique.size * 20))
        smooth_vals = []
        for col in axes_cols:
            y = sub_vals[col].to_numpy(dtype=float)
            k = min(3, len(x_unique) - 1)  # adaptive: 1..3
            if k >= 1:
                y_on_unique = np.interp(x_unique, x_num, y)
                spline = make_interp_spline(x_unique, y_on_unique, k=k)
                y_s = spline(x_dense)
            else:
                y_s = np.interp(x_dense, x_num, y)
            smooth_vals.append(y_s)
        smooth_vals = np.vstack(smooth_vals)

    smooth_vals = np.clip(smooth_vals, -10, 100)
    cum = np.cumsum(smooth_vals, axis=0)
    x_dense_dt = mdates.num2date(x_dense)
    return x_dense_dt, cum

def draw_frame(i):
    ax.cla()

    # Window logic:
    # i = 0..WINDOW-1  -> rows [0 .. i]  (growing 1, 1..2, ..., 1..10)
    # i >= WINDOW      -> rows [i-WINDOW+1 .. i] (sliding 2..11, 3..12, ...)
    start = 0 if i < WINDOW else i - WINDOW + 1
    end = i + 1
    sub = df.iloc[start:end]
    sub_time = sub['Time']
    sub_vals = sub[axes_cols]

    x_dense_dt, cum = smooth_stack(sub_time, sub_vals)

    prev = np.zeros(cum.shape[1], dtype=float)
    for k, col in enumerate(axes_cols):
        print(f"Frame {i+1}/{n}, plotting {col}")
        y2 = cum[k]
        poly = ax.fill_between(x_dense_dt, prev, y2, alpha=0.6, label=col)
        ax.plot(x_dense_dt, y2, linewidth=1.6, color=poly.get_facecolor()[0])
        prev = y2

    left = sub_time.iloc[0]
    right = sub_time.iloc[-1]
    if right <= left:
        right = left + dt.timedelta(seconds=1)

    ax.set_title("Streaming stacked area, grow to 10 then slide (curved borders)")
    ax.set_xlabel("Time")
    ax.set_ylabel("Amps")
    ax.set_ylim(-10, 200)
    ax.set_xlim(left, right)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left", ncol=4, fontsize=8)

    ax.xaxis.set_major_locator(mdates.SecondLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    fig.autofmt_xdate()

    

    insert_data()





ani = FuncAnimation(
    fig,
    draw_frame,
    frames=n,          # one frame per record
    interval=2000,     # show a new record every 2 seconds
    repeat=False,
    cache_frame_data=False
)

plt.show()



