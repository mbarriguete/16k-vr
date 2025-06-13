# Usage: python plot_results_simple.py <csv> <wifi|nr>
#        [--stat mean|median|p75] [--split]
import sys, argparse, pandas as pd, numpy as np, matplotlib.pyplot as plt
from rate_mapper import wifi7_table, nr_table

TARGET = 0.9
DIST_COL, WALL_COL = "d_m", "wall_dB"

def mcs2rate(mcs, tab, bw):
    if pd.isna(mcs): return 0.0
    e = tab.get(int(mcs));  return 0.0 if e is None else e.bits_per_Hz * e.eta * bw / 1e9

def add_rates(df):
    df["rate_wifi"] = df["mcs_wifi"].apply(lambda m: mcs2rate(m, wifi7_table, 320e6))
    df["rate_nr"]   = df["mcs_nr"].apply(lambda m: mcs2rate(m, nr_table, 400e6))
    return df

def agg(series, mode):
    if mode == "mean":   return series.mean()
    if mode == "p75":    return series.quantile(0.75)
    return series.median()  # default = median

def make_curve(df, radio, stat, los_only):
    mask = (df["bf_dB"] == 0) & (df["hb_pen"] == 0) & (df["fb_pen"] == 0) if los_only else slice(None)
    grouped = df.loc[mask].groupby(DIST_COL)["rate_wifi" if radio == "wifi" else "rate_nr"]
    return grouped.apply(lambda s: agg(s, stat))

def plot_two(df, radio, stat, base, split):
    los = make_curve(df, radio, stat, los_only=True)
    blk = make_curve(df, radio, stat, los_only=False)

    def single(x, y, label, fname):
        plt.figure(); plt.plot(x, y, marker="o"); plt.axhline(TARGET, ls="--")
        plt.xlabel("Distance [m]"); plt.ylabel("Net rate [Gb/s]")
        plt.title(f"Rate vs Distance – {radio.upper()}  ({label})")
        plt.grid(alpha=.3)
        plt.tight_layout(); plt.savefig(fname, dpi=300); plt.close()

    if split:
        single(los.index, los.values, "ideal LOS",   f"{base}_rate_los.png")
        single(blk.index, blk.values, "with obstacles", f"{base}_rate_blk.png")
    else:
        plt.figure()
        plt.plot(los.index, los.values, marker="o", label="Ideal LOS")
        plt.plot(blk.index, blk.values, marker="s", label="With obstacles")
        plt.axhline(TARGET, ls="--", color="gray", label="0.9 Gb/s")
        plt.xlabel("Distance [m]"); plt.ylabel("Net rate [Gb/s]")
        plt.title(f"Rate vs Distance – {radio.upper()}  ({stat})")
        plt.grid(alpha=.3); plt.legend(); plt.tight_layout()
        plt.savefig(f"{base}_rate.png", dpi=300); plt.close()

def waterfall(png):
    labels = ["Air", "Access/Sched.", "HARQ", "Back-haul", "Core+App"]
    wifi = [0.15, 0.50, 1.00, 0.10, 1.00]; nr = [0.25, 0.20, 0.80, 0.10, 1.00]
    x = np.arange(2); bottom = np.zeros_like(x, float)
    plt.figure()
    for w, n, l in zip(wifi, nr, labels):
        plt.bar(x, [w, n], bottom=bottom, label=l); bottom += [w, n]
    plt.xticks(x, ["Wi-Fi 7", "5G NR"]); plt.ylabel("Latency [ms]")
    plt.title("End-to-End Latency Waterfall"); plt.legend(); plt.tight_layout()
    plt.savefig(png, dpi=300); plt.close()

def heat(df, radio, png):
    rate_col = "rate_wifi" if radio == "wifi" else "rate_nr"
    df["fail"] = df[rate_col] < TARGET
    pivot = df.pivot_table(index=DIST_COL, columns=WALL_COL,
                           values="fail", aggfunc="mean")
    plt.figure(); plt.imshow(pivot, origin="lower", aspect="auto")
    plt.colorbar(label="Fail probability (all obstacles)")
    plt.xticks(range(len(pivot.columns)), pivot.columns)
    plt.yticks(range(len(pivot.index)), pivot.index)
    plt.xlabel("Wall attenuation [dB]"); plt.ylabel("Distance [m]")
    plt.title(f"Heat-map – {radio.upper()}"); plt.tight_layout(); plt.savefig(png, dpi=300); plt.close()

def main():
    pa = argparse.ArgumentParser()
    pa.add_argument("csv"); pa.add_argument("radio", choices=["wifi", "nr"])
    pa.add_argument("--stat", choices=["median", "mean", "p75"], default="median")
    pa.add_argument("--split", action="store_true",
                    help="generate two separate PNGs (LOS, obstacles)")
    args = pa.parse_args()

    df = add_rates(pd.read_csv(args.csv))
    base = args.csv.rsplit(".", 1)[0] + f"_{args.radio}"
    plot_two(df, args.radio, args.stat, base, args.split)
    waterfall(f"{base}_latency.png")
    heat(df, args.radio, f"{base}_heat.png")
    print("Saved figures to:", base + "_*.png")

if __name__ == "__main__":
    main()



