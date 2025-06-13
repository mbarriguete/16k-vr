# sweep_full.py  –  1 800-point grid  (+ Monte-Carlo shadow if --mc N)
#
# Generated columns:
# d_m | wall_dB | bf_dB | hb_pen | fb_pen | shadow_dB |
# snr_wifi | mcs_wifi | snr_nr | mcs_nr
#
# Examples:
#   python sweep_full.py --outfile sweep.csv
#   python sweep_full.py --outfile sweep_mc.csv --mc 50

import numpy as np
import csv
import argparse
from itertools import product
from link_budget import path_loss_InH, thermal_noise_dbm, snr_db
from rate_mapper import wifi7_table, nr_table, select_mcs

# Constants 
NF   = 7.0
WIFI = dict(fc=6.0,  bw=320e6, ptx=20, gtx=7,  grx=0)
NR   = dict(fc=28.0, bw=400e6, ptx=23, gtx=20, grx=10)

DIST    = np.arange(3, 10.1, 0.5)       # 15 values
WALL    = np.arange(0, 10.1, 2)[:5]     # 0–8 dB, 5 values
BF_ERR  = np.arange(0, 6.1, 2)          # 0–6 dB, 4 values
HB_PEN  = [0, 3, 6]                     # Human body
FB_PEN  = [0, 13]                       # Furniture / door
# Grid: 15 × 5 × 4 × 3 × 2 = 1,800 scenarios

# Evaluation Function 
def eval_point(d, wall, bf, hb, fb, shadow):
    # Wi-Fi 6E
    noise_w  = thermal_noise_dbm(WIFI['bw'], NF)
    pl_w     = path_loss_InH(WIFI['fc'], d) + wall + hb + fb + shadow
    snr_w, _ = snr_db(WIFI['ptx'], WIFI['gtx'], WIFI['grx'], pl_w, noise_w)
    mcs_w, _ = select_mcs(snr_w, wifi7_table)

    # 5G NR FR2
    noise_n  = thermal_noise_dbm(NR['bw'], NF)
    pl_n     = path_loss_InH(NR['fc'], d) + wall + bf + hb + fb + shadow
    snr_n, _ = snr_db(NR['ptx'], NR['gtx'], NR['grx'], pl_n, noise_n)
    mcs_n, _ = select_mcs(snr_n, nr_table)

    return dict(d_m=d, wall_dB=wall, bf_dB=bf, hb_pen=hb, fb_pen=fb,
                shadow_dB=shadow,
                snr_wifi=snr_w, mcs_wifi=mcs_w,
                snr_nr=snr_n,   mcs_nr=mcs_n)

#  Main Loop 
def main(outfile: str, mc_reps: int, sigma: float, seed: int):
    rng  = np.random.default_rng(seed)
    rows = []

    for d, w, b, hb, fb in product(DIST, WALL, BF_ERR, HB_PEN, FB_PEN):
        reps = mc_reps if mc_reps > 0 else 1
        for _ in range(reps):
            sh = rng.normal(0, sigma) if mc_reps else 0.0
            rows.append(eval_point(d, w, b, hb, fb, sh))

    with open(outfile, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader(); writer.writerows(rows)

    print(f"[✓] {len(rows)} rows → {outfile}")

# CLI 
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--outfile", default="sweep.csv",
                        help="Output CSV file")
    parser.add_argument("--mc", type=int, default=0,
                        help="Monte Carlo replicas per point (0 = deterministic)")
    parser.add_argument("--sigma", type=float, default=3.0,
                        help="σ of log-normal shadowing [dB]")
    parser.add_argument("--seed", type=int, default=42,
                        help="RNG seed")
    args = parser.parse_args()

    main(outfile=args.outfile,
         mc_reps=args.mc,
         sigma=args.sigma,
         seed=args.seed)



