from dataclasses import dataclass
from typing import List

@dataclass
class Segment:
    name: str
    delay_ms: float

class LatencyBudget:
    def __init__(self, segs: List[Segment]): self.segs = segs
    def total_ms(self): return sum(s.delay_ms for s in self.segs)

wifi_default = LatencyBudget([
    Segment('Air',0.15), Segment('Access',0.50),
    Segment('HARQ',1.00), Segment('Back-haul',0.10),
    Segment('Core+App',1.00)])
nr_default = LatencyBudget([
    Segment('Air',0.25), Segment('Scheduling',0.20),
    Segment('HARQ',0.80), Segment('Back-haul',0.10),
    Segment('Core+App',1.00)])

def default_wifi_latency_ms(): return wifi_default.total_ms()
def default_nr_latency_ms():   return nr_default.total_ms()
