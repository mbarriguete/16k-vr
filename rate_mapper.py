from dataclasses import dataclass
from typing import Dict, Tuple, Optional

@dataclass
class McsEntry:
    snr_req: float        # Required SNR [dB] for PER ≈ 10⁻⁵
    eta: float            # MAC/PHY efficiency
    bits_per_Hz: float    # Raw spectral efficiency

# Wi-Fi 7 (IEEE 802.11be Draft D7)
wifi7_table: Dict[int, McsEntry] = {
     7: McsEntry(32, 0.60,  5.0),   # 64-QAM 5/6  → net ≈ 0.96 Gb/s @320 MHz
     9: McsEntry(34, 0.68,  8.0),   # 256-QAM 5/6
    11: McsEntry(35, 0.65, 10.0),   # 1024-QAM 5/6
    13: McsEntry(38, 0.60, 12.0),   # 4096-QAM 5/6
}

# 5G NR FR2 (28 GHz) — Table 5.1.3.1-2
nr_table: Dict[int, McsEntry] = {
    14: McsEntry(18, 0.78,  2.34),  # 64-QAM  r ≈ 0.78
    27: McsEntry(26, 0.80,  5.89),  # 256-QAM r ≈ 0.95
}

def select_mcs(snr: float, table: Dict[int, McsEntry], margin=3.0
              ) -> Tuple[Optional[int], Optional[McsEntry]]:
    """Returns the highest MCS whose SNR_req + margin ≤ SNR."""
    elig = {m: e for m, e in table.items() if e.snr_req + margin <= snr}
    if not elig:
        return None, None
    best = max(elig)
    return best, table[best]

