# Profile Fetcher for Azure VM

## Description

This Python script fetches and displays metadata for an Azure VM using Azure's Instance Metadata Service (IMDS).

- Fetches VM metadata including VM details, OS profile, VM compute, VM storage, and VM network.
- Displays the metadata in a visually appealing and organized manner in the console (with color).
- Supports output to a plain text file (no color codes) using the `--output` option.
- Fully PEP8-compliant and robust error handling.

## Usage

To download and run the script directly from GitHub, execute the following command:

```bash
curl -s https://raw.githubusercontent.com/samatild/azvmprofilefetcher/main/azurevmprofile.py | python3
```

Or, if you have the file locally:

```bash
python3 azurevmprofile.py
```

### Command-Line Options

- `--output <filename>`: Append output to the specified file (plain text, no color codes).

#### Example:

```bash
python3 azurevmprofile.py --output myvmprofile.txt
```

## Example Output

Console output:
```
========================================
VM Details
========================================
vmId: 7501ac24-e11a-406d-903d-1d818d15cd3e
...
```



## Requirements

- Python 3.x
- `requests` library (install with `pip install requests`)

## Notes

- When using `--output`, all color formatting is disabled for clean logs.
- The script is designed to run inside an Azure VM (IMDS is only accessible from within the VM).