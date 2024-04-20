# TfL iBus announcement files

This repository has a collection of all TfL iBus announcement files released under the Freedom of Information Act 2000.

The most recently uploaded file(s) on TfL's Sharepoint were on `2024-02-09`.

## Structure

All files with their original names (`.wav` files have been converted to `.mp3` for file size reasons) are found in the [Original](./Original/) directory.

The names generally follow a pattern, with the first character or two dictating the type of announcement, and the rest of the file name generally representing its contents.

| Prefix | Description                                  |
| ------ | -------------------------------------------- |
| `A`    | Transport information and points of interest |
| `D`    | Destinations                                 |
| `R`    | Routes                                       |
| `S`    | Stops                                        |

Various additional files also exist with non-conforming names, some have "v2" copies, some are duplicates, and there are also two Excel spreadsheets with transcripts of a few hundred files thrown in for good measure.

## Renaming

Some files (and more soon) have been renamed to allow for easier use by people and automated tools.

Eventually, most NAPTAN codes will be linked to their respective audio files to allow for automated announcement tools to be created. This is done through fuzzy file matching, manual linking, and automted Python scripts.

## Scripts

Automated scripts are found in this repository to help with renaming and linking files.

### Prerequisites

- Modern enough version of Python 3
- `pip install -r requirements.txt`
- TfL API key saved to `.env`:

```
TFL_APP_ID=xyz
TFL_APP_KEY=xyz
```

### `get-stops.py`

This uses the [TfL Unified API](https://api.tfl.gov.uk/) with your app ID/key to download information about every bus stop served by TfL, and every TfL-operated bus route, and saves them to a SQLite database named `tfl.db`.

### `linker.py`

This amends the aforementioned SQLite database and uses `thefuzz` to try to find matching audio files for each bus stop as well as every route origin and destination.

If no match can be found, the stop name and its NAPTAN or route section id will be printed to the console for manual matching.

Manual matches can be done using a SQLite editor, such as [DB Browser for SQLite](https://sqlitebrowser.org/).
