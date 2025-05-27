import pandas as pd
import json
import math
from tqdm import tqdm
import io
import os

# --- Your CSV Data (as a string for this example) ---
csv_data_string = """uuid,req,rsp
0,"GET /archive/CZ/KS3/123204004672858633/image/123204004672858633/cz2ypacs/19457137_43720549/63_1.2.840.113619.2.416.1540962070904000344540203675837229346.63.dcm?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20240821T054308Z&X-Amz-SignedHeaders=host&X-Amz-Expires=6000&X-Amz-Credential=AKLTgV1HoqgGTw-L4iMPyBEOOA%2F20240821%2FCN-SHANGHAI-2%2Fs3%2Faws4_request&X-Amz-Signature=31043c7d50d1ea26f53f83b5ecc785f412755cd3b792b1ffa764737a42392c62 HTTP/1.1
Host: 20.16.10.114:8082
Accept-Encoding: identity
User-Agent: python-urllib3/2.2.2

","HTTP/1.1 200 OK
Server: nginx/1.24.0
Date: Wed, 21 Aug 2024 05:45:54 GMT
Content-Type: application/octet-stream
Content-Length: 230296
Connection: keep-alive
X-Application-Context: application
x-kss-request-id: 2ead4310eba24113893271c78def3473
ETag: ""492a07921e34ce0a01b2d443af79cee6""
Content-MD5: SSoHkh40zgoBstRDr3nO5g==
Last-Modified: Fri, 08 Sep 2023 07:06:31 GMT
x-amz-request-id: 2ead4310eba24113893271c78def3473
Accept-Ranges: bytes

"
1,"GET /archive/CZ/KS3/123204004672858633/2022-07/19/1.2.345.6.789.3.1.2.64219988.13204.1658187395.2-1.3.12.2.1107.5.1.4.75831.30000022071512241475700155529/243-1.3.12.2.1107.5.1.4.75831.30000022071512241475700155772.dcm?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20240821T053617Z&X-Amz-SignedHeaders=host&X-Amz-Expires=6000&X-Amz-Credential=AKLTgV1HoqgGTw-L4iMPyBEOOA%2F20240821%2FCN-SHANGHAI-2%2Fs3%2Faws4_request&X-Amz-Signature=33dafdf0f38110e32caa697894fb590ee84591e585fb326b557fbde34e070bf6 HTTP/1.1
Host: 20.16.10.114:8082
Accept-Encoding: identity
User-Agent: python-urllib3/2.2.2

","HTTP/1.1 200 OK
Server: nginx/1.24.0
Date: Wed, 21 Aug 2024 05:45:54 GMT
Content-Type: application/octet-stream
Content-Length: 286080
Connection: keep-alive
X-Application-Context: application
x-kss-request-id: 36748ab6e10b41f99cb25545c021ef7c
ETag: ""44825292f3c9df0238546497210bfaa6""
Content-MD5: RIJSkvPJ3wI4VGSXIQv6pg==
Last-Modified: Wed, 20 Jul 2022 02:40:01 GMT
x-amz-request-id: 36748ab6e10b41f99cb25545c021ef7c
Accept-Ranges: bytes

"
2,"GET /archive/CZ/KS3/123204004672858633/2022-07/19/1.2.345.6.789.3.1.2.64219988.13204.1658187395.2-1.3.12.2.1107.5.1.4.75831.30000022071512241475700155529/244-1.3.12.2.1107.5.1.4.75831.30000022071512241475700155773.dcm?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20240821T053617Z&X-Amz-SignedHeaders=host&X-Amz-Expires=6000&X-Amz-Credential=AKLTgV1HoqgGTw-L4iMPyBEOOA%2F20240821%2FCN-SHANGHAI-2%2Fs3%2Faws4_request&X-Amz-Signature=612641f1c954565c6ab91e3a196d8d820ac424f92e0081a7c27ccbba4f79877e HTTP/1.1
Host: 20.16.10.114:8082
Accept-Encoding: identity
User-Agent: python-urllib3/2.2.2

","HTTP/1.1 404 Not Found
Server: nginx/1.24.0
Date: Wed, 21 Aug 2024 05:45:55 GMT
Content-Type: application/xml
Content-Length: 200
Connection: keep-alive
X-Application-Context: application
x-kss-request-id: 6666fca478814b32be3ba2d721c3eb78
ETag: ""d130db26814fc7782cf93642d315e8c5""
Content-MD5: 0TDbJoFPx3gs+TZC0xXoxQ==
Last-Modified: Wed, 20 Jul 2022 02:40:03 GMT
x-amz-request-id: 6666fca478814b32be3ba2d721c3eb78
Accept-Ranges: bytes

"
3,"GET /archive/CZ/KS3/123204004672858633/2022-07/19/1.2.345.6.789.3.1.2.64219988.13204.1658187395.2-1.3.12.2.1107.5.1.4.75831.30000022071512241475700155529/245-1.3.12.2.1107.5.1.4.75831.30000022071512241475700155774.dcm?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20240821T053617Z&X-Amz-SignedHeaders=host&X-Amz-Expires=6000&X-Amz-Credential=AKLTgV1HoqgGTw-L4iMPyBEOOA%2F20240821%2FCN-SHANGHAI-2%2Fs3%2Faws4_request&X-Amz-Signature=5c0a4681af7d9e333f07e26318bc7b8f7f5b730f73875ba1b3e120b2756b0efb HTTP/1.1
Host: 20.16.10.114:8082
Accept-Encoding: identity
User-Agent: python-urllib3/2.2.2

","HTTP/1.1 200 OK
Server: nginx/1.24.0
Date: Wed, 21 Aug 2024 05:45:56 GMT
Content-Type: application/octet-stream
Content-Length: 285746
Connection: keep-alive
X-Application-Context: application
x-kss-request-id: f4f266b513b046179b185fe1d071049d
ETag: ""7f0fb930bcdc4d9245c93fcceeeee784""
Content-MD5: fw+5MLzcTZJFyT/M7u7nhA==
Last-Modified: Wed, 20 Jul 2022 02:40:03 GMT
x-amz-request-id: f4f266b513b046179b185fe1d071049d
Accept-Ranges: bytes

"
"""


class DataProcessorJSON:
    def __init__(self, csv_path_or_buffer):
        self.df = None
        try:
            self.df = pd.read_csv(csv_path_or_buffer, dtype=str)
            for col in self.df.columns:
                if self.df[col].dtype == 'object':
                    self.df[col] = self.df[col].str.strip()
        except FileNotFoundError:
            print(f"Error: Input file not found at {csv_path_or_buffer}")
            self.df = pd.DataFrame()
        except Exception as e:
            print(f"Error loading or parsing input CSV: {e}")
            self.df = pd.DataFrame()

    def _determine_reason_and_label(self, row):
        """
        Processes a single row (Pandas Series) to determine 'reason' and 'label'.
        This is where your custom logic goes.
        """
        reason = "No specific reason"
        label = "UNKNOWN"

        if pd.isna(row['rsp']):
            reason = "Response data is missing"
            label = "ERROR_MISSING_RSP"
            return reason, label

        rsp_text = str(row['rsp'])

        if "HTTP/1.1 200 OK" in rsp_text:
            label = "SUCCESS"
            reason = "Request successful (200 OK)"
        elif "HTTP/1.1 404 Not Found" in rsp_text:
            label = "NOT_FOUND"
            reason = "Resource not found (404)"
        elif "HTTP/1.1 5" in rsp_text:
            label = "SERVER_ERROR"
            reason = "Server error detected in response"
        else:
            label = "OTHER_ERROR"
            reason = "Response indicates an issue (not 200 or 404)"
            status_line = rsp_text.splitlines()[0] if rsp_text else "N/A"
            reason += f" - Status: {status_line}"

        return reason, label

    def process_and_save_to_json(self, output_json_path, batch_size=2, json_lines=False):
        """
        Processes the DataFrame in batches, adds 'reason' and 'label' columns,
        and saves the result to a JSON file.

        Args:
            output_json_path (str): Path to save the output JSON file.
            batch_size (int): Number of rows to process in each batch.
            json_lines (bool): If True, saves as JSON Lines format (one JSON object per line).
                               If False (default), saves as a single JSON array.
        """
        if self.df is None or self.df.empty:
            print("DataFrame is not loaded or is empty. Cannot process.")
            return

        num_rows = len(self.df)
        if num_rows == 0:
            print("DataFrame has 0 rows.")
            return

        num_batches = math.ceil(num_rows / batch_size)

        output_dir = os.path.dirname(output_json_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")

        if os.path.exists(output_json_path):
            os.remove(output_json_path)
            print(f"Removed existing output file: {output_json_path}")

        print(f"Processing {num_rows} rows in {num_batches} batches of size {batch_size}...")
        print(
            f"Output will be saved to: {output_json_path} (Format: {'JSON Lines' if json_lines else 'Single JSON Array'})")

        all_processed_records = []  # Used only if json_lines is False

        with open(output_json_path, 'w', encoding='utf-8') as f_out:
            if not json_lines:
                # For single JSON array, we'll write '[' at the beginning if we stream,
                # but it's simpler to collect all and dump once if memory allows.
                # Here, we collect all records and dump at the end.
                pass  # We will dump all_processed_records at the end.

            first_record_in_file = True  # For handling commas in streamed JSON array (more complex)

            for i in tqdm(range(0, num_rows, batch_size), total=num_batches, desc="Processing & Converting Batches",
                          ncols=100):
                start_idx = i
                end_idx = min(i + batch_size, num_rows)

                batch_df = self.df.iloc[start_idx:end_idx].copy()

                if batch_df.empty:
                    continue

                reasons = []
                labels = []
                for _, row_data in batch_df.iterrows():
                    reason, label = self._determine_reason_and_label(row_data)
                    reasons.append(reason)
                    labels.append(label)

                batch_df['reason'] = reasons
                batch_df['label'] = labels

                # Convert the processed batch DataFrame to a list of dictionaries
                # Each dictionary will be a JSON object
                records_in_batch = batch_df.to_dict(orient='records')

                if json_lines:
                    for record in records_in_batch:
                        json.dump(record, f_out, ensure_ascii=False)  # ensure_ascii=False for non-ASCII chars
                        f_out.write('\n')
                        f_out.flush()
                else:
                    all_processed_records.extend(records_in_batch)

            if not json_lines:
                json.dump(all_processed_records, f_out, indent=2, ensure_ascii=False)

        print(f"Finished processing. Output saved to {output_json_path}")


# --- Example Usage ---
if __name__ == '__main__':
    csv_file_buffer = io.StringIO(csv_data_string)

    processor = DataProcessorJSON(csv_file_buffer)

    output_file_single_array = "output_processed_data.json"
    output_file_json_lines = "output_processed_data.jsonl"

    if processor.df is not None and not processor.df.empty:
        # 1. Save as a single JSON array
        processor.process_and_save_to_json(output_file_single_array, batch_size=2, json_lines=False)
        if os.path.exists(output_file_single_array):
            print(f"\n--- Content of {output_file_single_array} (first ~300 chars) ---")
            with open(output_file_single_array, 'r', encoding='utf-8') as f:
                print(f.read(300) + "...")
            # To verify the full content:
            # with open(output_file_single_array, 'r', encoding='utf-8') as f:
            #     data = json.load(f)
            #     print(f"\nLoaded {len(data)} records from {output_file_single_array}")

        print("-" * 30)

        # 2. Save as JSON Lines
        processor.process_and_save_to_json(output_file_json_lines, batch_size=2, json_lines=True)
        if os.path.exists(output_file_json_lines):
            print(f"\n--- Content of {output_file_json_lines} (first few lines) ---")
            with open(output_file_json_lines, 'r', encoding='utf-8') as f:
                for _ in range(min(3, processor.df.shape[0])):  # Print first few lines
                    line = f.readline()
                    if not line: break
                    print(line.strip())
            # To verify:
            # loaded_json_lines = []
            # with open(output_file_json_lines, 'r', encoding='utf-8') as f:
            #     for line in f:
            #         loaded_json_lines.append(json.loads(line))
            # print(f"\nLoaded {len(loaded_json_lines)} records from {output_file_json_lines}")

    else:
        print("Could not load data to process.")
