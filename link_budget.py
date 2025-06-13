"""Link-budget helpers (3GPP TR 38.901 Indoor-Office LOS)."""
import numpy as np

def path_loss_InH(fc_GHz: float, d_m):
    """LOS path-loss in dB (valid for 0.5–100 GHz, d ≥ 1 m)."""
    d_m = np.asarray(d_m)
    if np.any(d_m < 1.0):
        raise ValueError("Distance must be ≥ 1 m.")
    return 32.4 + 17.3 * np.log10(d_m) + 20 * np.log10(fc_GHz)

def thermal_noise_dbm(bw_Hz: float, nf_dB: float):
    """kTB + NF in dBm."""
    return -174 + 10 * np.log10(bw_Hz) + nf_dB

def snr_db(ptx_dBm, gtx_dBi, grx_dBi, pl_dB, noise_dBm):
    prx = ptx_dBm + gtx_dBi + grx_dBi - pl_dB
    return prx - noise_dBm, prx
