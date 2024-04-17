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
