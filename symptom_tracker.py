import argparse
import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any

DATA_FILE = "symptoms.json"

@dataclass
class Entry:
    name: str
    severity: int
    timestamp: str
    notes: str = ""

    def validate(self) -> None:
        if not self.name:
            raise ValueError("Symptom name required")
        if not (1 <= self.severity <= 10):
            raise ValueError("Severity must be between 1 and 10")
        try:
            datetime.fromisoformat(self.timestamp)
        except ValueError as exc:
            raise ValueError("Invalid timestamp format. Use YYYY-MM-DD HH:MM") from exc


def load_entries() -> List[Entry]:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Entry(**e) for e in data]


def save_entries(entries: List[Entry]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([asdict(e) for e in entries], f, indent=2)


def add_entry(name: str, severity: int, timestamp: Optional[str], notes: str) -> Entry:
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = Entry(name=name, severity=severity, timestamp=timestamp, notes=notes)
    entry.validate()
    entries = load_entries()
    entries.append(entry)
    entries.sort(key=lambda e: e.timestamp)
    save_entries(entries)
    return entry


def filter_entries(entries: List[Entry], start: Optional[str], end: Optional[str], name: Optional[str]) -> List[Entry]:
    def in_range(e: Entry) -> bool:
        ts = datetime.fromisoformat(e.timestamp)
        if start and ts < datetime.fromisoformat(start):
            return False
        if end and ts > datetime.fromisoformat(end):
            return False
        if name and e.name != name:
            return False
        return True
    return [e for e in entries if in_range(e)]


def print_history(entries: List[Entry]) -> None:
    for e in entries:
        print(f"{e.timestamp} | {e.name} | {e.severity} | {e.notes}")


def summarize(entries: List[Entry]) -> Dict[str, Any]:
    summary = {}
    for e in entries:
        summary.setdefault(e.name, {
            "count": 0,
            "total": 0,
            "peak": (e.severity, e.timestamp)
        })
        rec = summary[e.name]
        rec["count"] += 1
        rec["total"] += e.severity
        if e.severity > rec["peak"][0]:
            rec["peak"] = (e.severity, e.timestamp)
    for name, rec in summary.items():
        rec["average"] = rec["total"] / rec["count"]
    return summary


def print_summary(summary: Dict[str, Any]) -> None:
    for name, rec in summary.items():
        print(f"Symptom: {name}")
        print(f"  Entries: {rec['count']}")
        print(f"  Average Severity: {rec['average']:.2f}")
        sev, ts = rec['peak']
        print(f"  Peak Severity: {sev} at {ts}")


def ascii_plot(entries: List[Entry], names: List[str]) -> None:
    data = {}
    all_ts = []
    for name in names:
        points = sorted([(datetime.fromisoformat(e.timestamp), e.severity) for e in entries if e.name == name])
        data[name] = points
        all_ts.extend(t for t, _ in points)
    if not all_ts:
        print("No data to plot")
        return
    start = min(all_ts)
    end = max(all_ts)
    span = (end - start).total_seconds() or 1
    width = 50
    height = 10
    grid = [[" " for _ in range(width)] for _ in range(height)]
    chars = "ABCDEFGHIJKLMNO"
    for idx, name in enumerate(names):
        points = data.get(name, [])
        char = chars[idx % len(chars)]
        for ts, sev in points:
            x = int(((ts - start).total_seconds() / span) * (width - 1))
            y = height - int((sev - 1) / 9 * (height - 1)) - 1
            if grid[y][x] == " ":
                grid[y][x] = char
            else:
                grid[y][x] = "*"
    for y in range(height):
        print("".join(grid[y]))
    print("".ljust(width, "-") )
    print(start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d").rjust(width - len(start.strftime("%Y-%m-%d"))))
    for idx, name in enumerate(names):
        char = chars[idx % len(chars)]
        print(f"{char}: {name}")


def get_last_entry(entries: List[Entry], name: str) -> Optional[Entry]:
    for e in reversed(entries):
        if e.name == name:
            return e
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Symptom Severity Tracker")
    sub = parser.add_subparsers(dest="cmd")

    add_p = sub.add_parser("add", help="Add a symptom entry")
    add_p.add_argument("name")
    add_p.add_argument("severity", type=int)
    add_p.add_argument("--notes", default="")
    add_p.add_argument("--time", help="YYYY-MM-DD HH:MM")
    add_p.add_argument("--quick", action="store_true", help="Quick log using last entry")

    hist_p = sub.add_parser("history", help="Show symptom history")
    hist_p.add_argument("--start")
    hist_p.add_argument("--end")
    hist_p.add_argument("--name")

    graph_p = sub.add_parser("graph", help="Plot severity over time")
    graph_p.add_argument("names", nargs="*", help="Symptom names")

    rep_p = sub.add_parser("report", help="Show summary report")

    args = parser.parse_args()
    entries = load_entries()

    if args.cmd == "add":
        if args.quick:
            last = get_last_entry(entries, args.name)
            if last:
                if not args.notes:
                    args.notes = last.notes
                if args.time is None:
                    args.time = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = add_entry(args.name, args.severity, args.time, args.notes)
        print(f"Added: {entry}")
    elif args.cmd == "history":
        result = filter_entries(entries, args.start, args.end, args.name)
        print_history(result)
    elif args.cmd == "graph":
        names = args.names if args.names else sorted({e.name for e in entries})
        ascii_plot(entries, names)
    elif args.cmd == "report":
        summary = summarize(entries)
        print_summary(summary)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
