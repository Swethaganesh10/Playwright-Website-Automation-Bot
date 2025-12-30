import csv
import sys
import time
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright
import pandas as pd
import re
from dotenv import load_dotenv
import os
# IMPORT THE PENNSYLVANIA CORE MODULE
import full_code_pa as m

import argparse

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("input_file", nargs='?', default=None)
parser.add_argument("output_file", nargs='?', default=None)
parser.add_argument("--headless", action="store_true")
parser.add_argument("--quotes-only", action="store_true")
args = parser.parse_args()

RUNS = Path("runs")
RUNS.mkdir(exist_ok=True)
HOME_URL = "https://agentweb1mod.plymouthrock.com/aiui/home"

EXTRA_FIELDS = [
    "row_index",
    "quote_number", 
    "policy_number",
    "status",
    "error", 
    "run_at"
]

# PA specific defaults
PA_BRANCH_FILTER = "Palisades"
PA_BRANCH_NAME = "Palisades"  
PA_AGENCY_FILTER = "A.H. Meyers"
PA_AGENCY_NAME = "A.H. Meyers and Company"
PA_PRODUCER_FILTER = "A.H. Meyers"
PA_PRODUCER_NAME = "A.H. Meyers and Company"


def snap(page, tag):
    try:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        page.screenshot(path=str(RUNS / f"{tag}_{ts}.png"), full_page=True)
    except Exception:
        pass


def normalize_dob(dob_str: str) -> str:
    if not dob_str:
        return ""
    try:
        dt = datetime.strptime(dob_str.strip(), "%m/%d/%Y")
        return dt.strftime("%m/%d/%Y")
    except ValueError:
        return dob_str.strip()


def normalize_address(addr: str) -> str:
    """Normalize address with both commas: Street, City, State Zip"""
    if not addr:
        return ""

    addr = addr.strip()

    if addr.count(",") >= 2:
        return addr

    # Match: [street with type] [city] [state] [zip]
    match = re.match(
        r"(\d+\s+.+?(?:St|Street|Ave|Avenue|Rd|Road|Ln|Lane|Dr|Drive|Ct|Court|Blvd|Boulevard|Way|Pl|Place|Cir|Circle|Pkwy|Parkway)\.?)\s+(.+?)\s+(MA|CT|NH|NJ|NY|PA)\s+(\d{5})",
        addr,
        re.I,
    )
    
    if match:
        street = match.group(1).strip().title()
        city = match.group(2).strip().title()
        state = match.group(3).upper()
        zipc = match.group(4)
        return f"{street}, {city}, {state} {zipc}"
    
    match2 = re.match(
        r"(\d+\s+.+?(?:St|Street|Ave|Avenue|Rd|Road|Ln|Lane|Dr|Drive|Ct|Court|Blvd|Boulevard|Way|Pl|Place|Cir|Circle|Pkwy|Parkway)\.?)\s+(.+)",
        addr,
        re.I,
    )
    
    if match2:
        street = match2.group(1).strip().title()
        rest = match2.group(2).strip().title()
        return f"{street}, {rest}"
    
    return addr


def main(
    in_csv="input_pa.csv", 
    out_csv="output_pa.csv", 
    out_xlsx=None, 
    headless=False,
    quotes_only=False 
):
    print("[INFO] Pennsylvania Complete Processing Script (Quote + Policy)")
    print(f"[INFO] Input: {in_csv}")
    print(f"[INFO] Output: {out_csv}")
    print(f"[INFO] Headless: {headless}")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=headless)
        context = browser.new_context(
            storage_state=None
        )
        page = context.new_page()
        try:
            context.clear_cookies()  # Clear any cached data
        except:
            pass

        try:
            m.login(page)
            print("[INFO] Login successful")

            with (
                open(in_csv, newline="", encoding="utf-8-sig") as f_in,
                open(out_csv, "w", newline="", encoding="utf-8") as f_out,
            ):
                reader = csv.DictReader(f_in)
                base_fields = reader.fieldnames or []
                fieldnames = base_fields + [
                    c for c in EXTRA_FIELDS if c not in base_fields
                ]
                writer = csv.DictWriter(f_out, fieldnames=fieldnames)
                writer.writeheader()

                successful_policies = 0
                failed_policies = 0

                for i, row in enumerate(reader, start=1):
                    print(f"\n===== ROW {i} =====")

                    applicant = {
                        "first_name": (row.get("first_name") or "").strip(),
                        "last_name": (row.get("last_name") or "").strip(),
                        "dob": normalize_dob(row.get("dob") or ""),
                        "address": normalize_address(row.get("address") or ""),
                        "phone": (row.get("phone") or "555-555-5555").strip(),
                        "effective_date": normalize_dob(row.get("effective_date") or ""),
                        "line_of_business": (row.get("line_of_business") or "HO3").strip().upper(),
                    }

                    load_dotenv(override=True)
                    
                    state = "Pennsylvania"
                    
                    # Read from .env, fallback to CSV, then hardcoded defaults
                    env_branch = os.getenv("PR_PA_BRANCH", "").strip()
                    env_agency = os.getenv("PR_PA_AGENCY", "").strip()
                    env_producer = os.getenv("PR_PA_PRODUCER", "").strip()
                    
                    branch_name = env_branch or row.get("branch_name") or PA_BRANCH_NAME
                    agency_name = env_agency or row.get("agency_name") or PA_AGENCY_NAME
                    producer_name = env_producer or row.get("producer_name") or PA_PRODUCER_NAME
                    
                    # Auto-generate filters from names
                    branch_filter = branch_name.split("|")[0].strip() if "|" in branch_name else branch_name.split()[0]
                    agency_filter = agency_name.split()[0].lower()
                    producer_filter = producer_name.split()[0].lower() if producer_name else ""

                    print(f"[INFO] Processing: {applicant['first_name']} {applicant['last_name']}")
                    print(f"[INFO] State: {state}")
                    print(f"[INFO] Branch: {branch_name}")
                    print(f"[INFO] Agency: {agency_name}")
                    print(f"[INFO] Producer: {producer_name}")
                    if applicant['effective_date']:
                        print(f"[INFO] Effective Date: {applicant['effective_date']}")

                    if successful_policies > 0 and successful_policies % 10 == 0:
                        print("[INFO] Resetting browser context...")
                        try:
                            context.close()
                        except Exception:
                            pass
                        context = browser.new_context(
                            storage_state=None  #  Prevents caching
                        )
                        page = context.new_page()
                        try:
                            context.clear_cookies()  # Clear cache
                        except:
                            pass
                        m.login(page)

                    for attempt in range(2):
                        try:
                            m.create_new_quote(page, state, applicant['effective_date'], applicant['line_of_business'])
                            m.fill_applicant_info(page, applicant)
                            m.select_branch_and_agency(
                                page,
                                branch_filter,
                                branch_name,
                                agency_filter,
                                agency_name,
                                producer_filter,
                                producer_name,
                            )
                            
                            if quotes_only:
                                quote_number, policy_number = m.quote_only(page, applicant)
                            else:
                                quote_number, policy_number = m.quote_and_issue(page, applicant)

                            successful_policies += 1
                            print(f"[SUCCESS] Quote: {quote_number}, Policy: {policy_number}")

                            out_row = {**row}
                            out_row.update(
                                {
                                    "row_index": i,
                                    "quote_number": quote_number or "",
                                    "policy_number": policy_number or "N/A - Quote Only", 
                                    "status": "ok",
                                    "error": "",
                                    "run_at": "'" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                }
                            )
                            writer.writerow(out_row)
                            f_out.flush()
                            time.sleep(0.4)
                            break

                        except m.DTQError as e:
                            print(f"[DTQ] DTQ decline: {e}")
                            snap(page, f"row{i}_dtqerror")
                            
                            failed_policies += 1  # FIX #1: Count as processed
                            
                            out_row = {**row}
                            out_row.update(
                                {
                                    "row_index": i,
                                    "quote_number": "",
                                    "policy_number": "",
                                    "status": "error",
                                    "error": str(e),
                                    "run_at": "'" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                }
                            )
                            writer.writerow(out_row)
                            f_out.flush()
                            
                            # FIX #2: Don't reset - already at home!
                            break

                        except Exception as e:
                            print(f"[ERROR] Attempt {attempt + 1} failed: {e}")

                            if attempt == 0:
                                print(f"[INFO] Resetting and retrying...")
                                try:
                                    context.close()
                                except Exception:
                                    pass
                                context = browser.new_context()
                                page = context.new_page()
                                m.login(page)
                                continue
                            else:
                                failed_policies += 1
                                snap(page, f"row{i}_error")
                                out_row = {**row}
                                out_row.update(
                                    {
                                        "row_index": i,
                                        "quote_number": "",
                                        "policy_number": "",
                                        "status": "error", 
                                        "error": str(e),
                                        "run_at": "'" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    }
                                )
                                writer.writerow(out_row)
                                f_out.flush()
                                
                                try:
                                    page.goto(HOME_URL, timeout=15000)
                                except Exception:
                                    context.close()
                                    context = browser.new_context()
                                    page = context.new_page()
                                    m.login(page)
                                break

        finally:
            context.close()
            browser.close()

    print("\n" + "=" * 60)
    print("PENNSYLVANIA COMPLETE PROCESSING FINISHED")
    print(f"Successful policies: {successful_policies}")
    print(f"Failed policies: {failed_policies}")
    print(f"Total processed: {successful_policies + failed_policies}")
    if (successful_policies + failed_policies) > 0:
        print(f"Success rate: {(successful_policies / (successful_policies + failed_policies)) * 100:.1f}%")
    print(f"Results saved to: {out_csv}")

    if out_xlsx:
        try:
            df = pd.read_csv(out_csv)
            df.to_excel(out_xlsx, index=False)
            print(f"Excel export: {out_xlsx}")
        except Exception as e:
            print(f"[WARN] Excel export failed: {e}")

    print("=" * 60)


if __name__ == "__main__":
    in_csv = sys.argv[1] if len(sys.argv) > 1 else "input_pa.csv"
    out_csv = (
        sys.argv[2]
        if len(sys.argv) > 2
        else f"output_pa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )
    out_xlsx = sys.argv[3] if len(sys.argv) > 3 else out_csv.replace(".csv", ".xlsx")

    if out_xlsx == "":
        out_xlsx = None

    headless = "--headless" in sys.argv

    try:
        main(
            args.input_file or in_csv, 
            args.output_file or out_csv, 
            out_xlsx, 
            args.headless or headless,
            args.quotes_only  
        )
    except KeyboardInterrupt:
        print("\n\nBatch processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)