

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
# IMPORT THE NEW HAMPSHIRE CORE MODULE
import full_code_nh as m

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

# NH specific defaults
NH_BRANCH_FILTER = "New England"
NH_BRANCH_NAME = "BHIC0035 | New England"  
NH_AGENCY_FILTER = "columbia"
NH_AGENCY_NAME = "Columbia Insurance Agency"


def snap(page, tag):
    try:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        page.screenshot(path=str(RUNS / f"{tag}_{ts}.png"), full_page=True)
    except Exception:
        pass


def normalize_dob(dob_str: str) -> str:
    """Convert date strings like '1/1/1950' → '01/01/1950'."""
    if not dob_str:
        return ""
    try:
        dt = datetime.strptime(dob_str.strip(), "%m/%d/%Y")
        return dt.strftime("%m/%d/%Y")
    except ValueError:
        return dob_str.strip()


def normalize_address(addr: str) -> str:
    """
    Normalize US address for Plymouth Rock format.
    Ensures proper comma placement: Street, City, State Zip
    """
    if not addr:
        return ""

    addr = addr.strip()

    # If already has 2+ commas, assume it's properly formatted
    if addr.count(",") >= 2:
        return addr

    # Match full address: [number street type] [city] [state] [zip]
    # Example: "117 Revere Ave Manchester NH 03104"
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
        # Return with BOTH commas: Street, City, State Zip
        return f"{street}, {city}, {state} {zipc}"
    
    # Try simpler match without zip code
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
    in_csv="input_nh.csv", 
    out_csv="output_nh.csv", 
    out_xlsx=None, 
    headless=False,
    quotes_only=False 
):
    print("[INFO] New Hampshire Complete Processing Script (Quote + Policy)")
    print(f"[INFO] Using NH-specific core module with policy issuance")
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

                    # UPDATED: Added effective_date support
                    applicant = {
                        "first_name": (row.get("first_name") or "").strip(),
                        "last_name": (row.get("last_name") or "").strip(),
                        "dob": normalize_dob(row.get("dob") or ""),
                        "address": normalize_address(row.get("address") or ""),
                        "phone": (row.get("phone") or "555-555-5555").strip(),
                        "effective_date": normalize_dob(row.get("effective_date") or ""),
                        "line_of_business": (row.get("line_of_business") or "HO3").strip().upper(),  
                    }

                    # NH specific configuration
                    load_dotenv(override=True)
                    
                    state = "New Hampshire"
                    
                    # Read from .env, fallback to CSV, then hardcoded defaults
                    env_branch = os.getenv("PR_NH_BRANCH", "").strip()
                    env_agency = os.getenv("PR_NH_AGENCY", "").strip()
                    env_producer = os.getenv("PR_NH_PRODUCER", "").strip()
                    
                    branch_name = env_branch or row.get("branch_name") or NH_BRANCH_NAME
                    agency_name = env_agency or row.get("agency_name") or NH_AGENCY_NAME
                    producer_name = env_producer or row.get("producer_name") or ""  # ✅ Empty default!
                    
                    # Auto-generate filters from names
                    branch_filter = branch_name.split("|")[0].strip() if "|" in branch_name else branch_name.split()[0]
                    agency_filter = agency_name.split()[0].lower()
                    producer_filter = producer_name.split()[0].lower() if producer_name else ""

                    print(f"[INFO] Processing: {applicant['first_name']} {applicant['last_name']}")
                    print(f"[INFO] State: {state}")
                    print(f"[INFO] Branch: {branch_name}")
                    print(f"[INFO] Agency: {agency_name}")
                    if applicant['effective_date']:
                        print(f"[INFO] Effective Date: {applicant['effective_date']}")

                    # Reset context periodically for stability
                    if successful_policies > 0 and successful_policies % 10 == 0:
                        print("[INFO] Resetting browser context for stability...")
                        try:
                            context.close()
                        except Exception:
                            pass
                        context = browser.new_context(
                            storage_state=None
                        )
                        page = context.new_page()
                        try:
                            context.clear_cookies()  # Clear cache
                        except:
                            pass
                        m.login(page)

                    # --- Retry loop for each row ---
                    for attempt in range(2):  # try twice max
                        try:
                            m.create_new_quote(page, state, applicant['effective_date'], applicant['line_of_business'])  # ✅ UPDATED
                            m.fill_applicant_info(page, applicant)
                            m.select_branch_and_agency(
                                page,
                                branch_filter,
                                branch_name,
                                agency_filter,
                                agency_name,
                                producer_filter,  # For states with producer field
                                producer_name, 
                            )
                            
                            # Use the complete quote_and_issue function
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

                        # --- Special DTQ handling ---
                        except m.DTQError as e:
                            print(f"[DTQ] DTQ decline detected: {e}")
                            snap(page, f"row{i}_dtqerror")
                            
                            failed_policies += 1  # FIX #1: Count DTQ in stats
                            
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
                            
                            # FIX #2: Don't reset - DTQ handlers already navigate to home!
                            break  # stop retry, go next row

                        # --- Generic error handling with retry ---
                        except Exception as e:
                            print(f"[ERROR] Attempt {attempt + 1} failed: {e}")

                            if attempt == 0:
                                print(f"[INFO] Row {i} failed first attempt, resetting context and retrying...")
                                try:
                                    context.close()
                                except Exception:
                                    pass
                                context = browser.new_context()
                                page = context.new_page()
                                m.login(page)
                                continue  # retry
                            else:
                                # Second failure → log as error
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
                                
                                # Try to navigate home for next row
                                try:
                                    page.goto(HOME_URL, timeout=15000)
                                except Exception:
                                    context.close()
                                    context = browser.new_context()
                                    page = context.new_page()
                                    m.login(page)
                                break  # move to next row

        finally:
            context.close()
            browser.close()

    print("\n" + "=" * 60)
    print("NEW HAMPSHIRE COMPLETE PROCESSING FINISHED")
    print(f"Successful policies issued: {successful_policies}")
    print(f"Failed policies: {failed_policies}")
    print(f"Total processed: {successful_policies + failed_policies}")
    print(f"Success rate: {(successful_policies / (successful_policies + failed_policies)) * 100:.1f}%" if (successful_policies + failed_policies) > 0 else "0%")
    print(f"Results saved to: {out_csv}")

    # Optional Excel export  
    if out_xlsx:
        try:
            df = pd.read_csv(out_csv)
            df.to_excel(out_xlsx, index=False)
            print(f"Excel export saved to: {out_xlsx}")
        except Exception as e:
            print(f"[WARN] Excel export failed: {e}")

    print("=" * 60)


if __name__ == "__main__":
    in_csv = sys.argv[1] if len(sys.argv) > 1 else "input_nh.csv"
    out_csv = (
        sys.argv[2]
        if len(sys.argv) > 2
        else f"output_nh_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
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