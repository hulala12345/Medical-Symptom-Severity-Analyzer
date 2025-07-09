# Medical Symptom Severity Analyzer

This project provides a simple command line application for tracking medical symptoms and their severity over time.

## Features

- **Log Symptoms**: Add new symptom entries with severity (1-10), timestamp and optional notes.
- **Symptom History**: View recorded symptoms with filtering by date range or symptom name.
- **Trend Graphs**: Generate ASCII line graphs of symptom severity over time. Multiple symptoms can be plotted together.
- **Summary Report**: Get counts, average severity and peak severity moments for each symptom.
- **Quick Log**: Reuse information from the most recent entry of a symptom for faster logging.

## Usage

Run `symptom_tracker.py` with one of the subcommands below. Python 3.12 or newer is required. All data is stored in `symptoms.json` in the project directory.

### Add an Entry
```
python3 symptom_tracker.py add "Headache" 5 --notes "Mild" --time "2025-07-09 10:00"
```
Use `--quick` to reuse the last entry's notes and timestamp.

### View History
```
python3 symptom_tracker.py history --start "2025-07-01" --end "2025-07-10" --name "Headache"
```

### Plot Graphs
```
python3 symptom_tracker.py graph Headache Nausea
```

### Summary Report
```
python3 symptom_tracker.py report
```

## License

This project is provided as-is under the MIT license.
