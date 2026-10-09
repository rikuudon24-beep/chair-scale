#!/usr/bin/env python3
"""Write an explicit UNKNOWN state when the exit monitor cannot complete."""
import json
import sys
from pathlib import Path
import pandas as pd

config=json.loads(Path("config/active_positions.json").read_text())
run_id=sys.argv[1] if len(sys.argv)>1 else "unknown"
reason=f"Monitor failed during workflow run {run_id}; exit status is UNKNOWN, not HOLD_NO_EXIT."
state_columns=[
    "id","pair","direction","entry_timestamp","reference_entry_price","source","status","state",
    "exit_signal_timestamp","exit_signal_price","exit_reason","latest_completed_h4","latest_close"
]
rows=[]
for pos in config.get("positions",[]):
    if pos.get("status")!="open":
        continue
    rows.append({
        "id":pos.get("id",""),"pair":pos.get("pair",""),"direction":pos.get("direction",""),
        "entry_timestamp":pos.get("entry_timestamp",""),"reference_entry_price":pos.get("reference_entry_price",""),
        "source":pos.get("source",""),"status":pos.get("status","open"),"state":"UNKNOWN",
        "exit_signal_timestamp":"","exit_signal_price":"","exit_reason":reason,
        "latest_completed_h4":"","latest_close":""
    })
Path("reports").mkdir(exist_ok=True)
pd.DataFrame(rows,columns=state_columns).to_csv("reports/current_position_exit_state.csv",index=False)
Path("reports/current_exit_monitor_failure.txt").write_text(reason+"\n",encoding="utf-8")
print(reason)
