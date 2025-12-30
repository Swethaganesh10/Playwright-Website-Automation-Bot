import csv
import sys
import time
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright
import pandas as pd
import re
import argparse  
from dotenv import load_dotenv
import os
# Import all state-specific core modules
import full_code_ct as ct
import full_code_ma as ma
import full_code_nh as nh
import full_code_nj as nj
import full_code_ny as ny
import full_code_pa as pa

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
    "processed_state",
    "status",
    "error", 
    "run_at"
]

# STATE-SPECIFIC CONFIGURATIONS WITH DEFAULTS
STATE_CONFIGS = {
    "Connecticut": {
        "module": ct,
        "branch_filter": "New England",
        "branch_name": "BHIC0035 | New England",
        "agency_filter": "columbia",
        "agency_name": "columbia",
        "has_producer": False,
        "has_producer_license": True,
        "producer_license_name": "JONES, MARK",
    },
    "Massachusetts": {
        "module": ma,
        "branch_filter": "New England",
        "branch_name": "BHIC0035 | New England",
        "agency_filter": "columbia",
        "agency_name": "Columbia Insurance Agency",
        "has_producer": True,
        "producer_filter": "columbia",
        "producer_name": "Columbia Insurance Agency, Inc. - 0001001",
        "has_producer_license": False,
    },
    "New Hampshire": {
        "module": nh,
        "branch_filter": "New England",
        "branch_name": "BHIC0035 | New England",
        "agency_filter": "columbia",
        "agency_name": "Columbia Insurance Agency",
        "has_producer": False,
        "has_producer_license": True,
        "producer_license_name": "SMITH, MICHAEL",
    },
    "New Jersey": {
        "module": nj,
        "branch_filter": "Palisades",
        "branch_name": "Palisades",
        "agency_filter": "A & L Insurance",
        "agency_name": "A & L Insurance Agency, LLC",
        "has_producer": False,
        "has_producer_license": False,
    },
    "New York": {
        "module": ny,
        "branch_filter": "Palisades",
        "branch_name": "Palisades",
        "agency_filter": "A.H. Meyers",
        "agency_name": "A.H. Meyers and Company",
        "has_producer": True,
        "producer_filter": "A.H. Meyers",
        "producer_name": "A.H. Meyers and Company",
        "has_producer_license": False,
    },
    "Pennsylvania": {
        "module": pa,
        "branch_filter": "Palisades",
        "branch_name": "Palisades",
        "agency_filter": "A.H. Meyers",
        "agency_name": "A.H. Meyers and Company",
        "has_producer": True,
        "producer_filter": "A.H. Meyers",
        "producer_name": "A.H. Meyers and Company",
        "has_producer_license": True,
        "producer_license_name": "Shimchock, Francine Marie",
    },
}


def write_progress(message):
    """Write progress to file for Streamlit to read"""
    with open("progress.txt", "a") as f:
        f.write(f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")

    
def snap(page, tag):
    try:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        page.screenshot(path=str(RUNS / f"{tag}_{ts}.png"), full_page=True)
    except Exception:
        pass


def normalize_dob(dob_str: str) -> str:
    """Convert date strings like '1/1/1950' → '01/01/1950' or '8/19/1955' → '08/19/1955'."""
    if not dob_str:
        return ""
    try:
        dt = datetime.strptime(dob_str.strip(), "%m/%d/%Y")
        return dt.strftime("%m/%d/%Y")
    except ValueError:
        return dob_str.strip()


def normalize_address(addr: str) -> str:
    """Normalize US address for Plymouth Rock format."""
    if not addr:
        return ""

    addr = addr.strip()

    # If already has 2 commas, assume it's fine
    if addr.count(",") >= 2:
        return addr

    # Match: number + street, city, state, zip
    match = re.match(
        r"(\d+\s+[A-Za-z0-9\s]+)\s+([A-Za-z\s]+)\s+(NJ|NY|PA|CT|MA|NH)\s+(\d{5})",
        addr,
        re.I,
    )
    if match:
        street = match.group(1).strip()
        city = match.group(2).strip().title()
        state = match.group(3).upper()
        zipc = match.group(4)
        return f"{street}, {city}, {state} {zipc}"

    return addr


def normalize_state(state_input):
    """Normalize state input to full state name."""
    state_map = {
        "CT": "Connecticut",
        "NJ": "New Jersey", 
        "NY": "New York",
        "PA": "Pennsylvania",
        "MA": "Massachusetts",
        "NH": "New Hampshire",
        "Connecticut": "Connecticut",
        "New Jersey": "New Jersey",
        "New York": "New York", 
        "Pennsylvania": "Pennsylvania",
        "Massachusetts": "Massachusetts",
        "New Hampshire": "New Hampshire"
    }
    return state_map.get(state_input.strip().upper() if state_input else "", "Connecticut")


def get_state_config(state, row):
    """Get state-specific configuration, with .env and CSV row overrides."""
    load_dotenv(override=True)  
    
    state_normalized = normalize_state(state)
    
    if state_normalized not in STATE_CONFIGS:
        print(f"[WARN] Unknown state '{state_normalized}', using Connecticut defaults")
        state_normalized = "Connecticut"
    
    config = STATE_CONFIGS[state_normalized].copy()
    
    # ✅ PRIORITY 1: Read from .env (Streamlit UI)
    state_abbr = {
        "Connecticut": "CT",
        "Massachusetts": "MA", 
        "New Hampshire": "NH",
        "New Jersey": "NJ",
        "New York": "NY",
        "Pennsylvania": "PA"
    }.get(state_normalized, "CT")
    
    env_branch = os.getenv(f"PR_{state_abbr}_BRANCH", "").strip()
    env_agency = os.getenv(f"PR_{state_abbr}_AGENCY", "").strip()
    env_producer = os.getenv(f"PR_{state_abbr}_PRODUCER", "").strip()
    
    if env_branch:
        config["branch_name"] = env_branch
        config["branch_filter"] = env_branch.split("|")[0].strip() if "|" in env_branch else env_branch.split()[0]
    
    if env_agency:
        config["agency_name"] = env_agency
        config["agency_filter"] = env_agency.split()[0].lower()
    
    if env_producer:
        config["producer_name"] = env_producer
        config["producer_filter"] = env_producer.split()[0].lower()
        config["has_producer"] = True  # Enable producer field if provided
    
    # ✅ PRIORITY 2: Allow CSV row to override .env
    if row.get("branch_filter"):
        config["branch_filter"] = row["branch_filter"].strip()
    if row.get("branch_name"): 
        config["branch_name"] = row["branch_name"].strip()
    if row.get("agency_filter"):
        config["agency_filter"] = row["agency_filter"].strip()
    if row.get("agency_name"):
        config["agency_name"] = row["agency_name"].strip()
    if row.get("producer_filter"):
        config["producer_filter"] = row.get("producer_filter", "").strip()
    if row.get("producer_name"):
        config["producer_name"] = row.get("producer_name", "").strip()
        
    return state_normalized, config



def process_quote(page, state_normalized, config, applicant, quotes_only=False):
    """Process a quote using the appropriate state module with effective_date support."""
    module = config["module"]
    
    # Create new quote with effective_date support
    module.create_new_quote(page, state_normalized, applicant.get('effective_date', ''), applicant.get('line_of_business', 'HO3'))
    
    # Fill applicant info
    module.fill_applicant_info(page, applicant)
    
    # Select branch and agency (with optional producer)
    if config.get("has_producer"):
        # States with producer field (MA, NY, PA)
        module.select_branch_and_agency(
            page,
            config["branch_filter"],
            config["branch_name"],
            config["agency_filter"],
            config["agency_name"],
            config.get("producer_filter", ""),
            config.get("producer_name", ""),
        )
    else:
        # States without producer field (CT, NH, NJ)
        module.select_branch_and_agency(
            page,
            config["branch_filter"],
            config["branch_name"],
            config["agency_filter"],
            config["agency_name"],
        )
    
    #  DECISION: Quote-only OR full policy
    if quotes_only:
        quote_number, policy_number = module.quote_only(page, applicant)
    else:
        quote_number, policy_number = module.quote_and_issue(page, applicant)
    
    return quote_number, policy_number


def main(
    in_csv="input_multistate.csv", 
    out_csv="output_multistate.csv", 
    out_xlsx=None, 
    headless=False,
    quotes_only=False  
):
    print("[INFO] Multi-State Processing Script - ALL STATES")
    print(f"[INFO] Supported states: CT, MA, NH, NJ, NY, PA")
    print(f"[INFO] Input: {in_csv}")
    print(f"[INFO] Output: {out_csv}")
    print(f"[INFO] Headless: {headless}")
    print(f"[INFO] Mode: {'Quote Numbers Only' if quotes_only else 'Full Processing (Quote + Policy)'}")  # ✅ NEW
    
    # Clear/create progress file for Streamlit app 
    with open("progress.txt", "w") as f:
        f.write(f"Starting multi-state processing at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Track stats by state
    state_stats = {}

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
            # Login once at the start
            ct.login(page)  # Use any module for login
            print("[INFO] Login successful")
            
            write_progress("Login successful")

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

                total_successful = 0
                total_failed = 0

                for i, row in enumerate(reader, start=1):
                    print(f"\n===== ROW {i} =====")

                    # Get state configuration
                    input_state = row.get("state", "CT")
                    state_normalized, config = get_state_config(input_state, row)
                    
                    # Initialize state stats
                    if state_normalized not in state_stats:
                        state_stats[state_normalized] = {"success": 0, "failed": 0}

                    applicant = {
                        "first_name": (row.get("first_name") or "").strip(),
                        "last_name": (row.get("last_name") or "").strip(),
                        "dob": normalize_dob(row.get("dob") or ""),
                        "address": normalize_address(row.get("address") or ""),
                        "phone": (row.get("phone") or "555-555-5555").strip(),
                        "effective_date": normalize_dob(row.get("effective_date") or ""),
                        "line_of_business": (row.get("line_of_business") or "HO3").strip().upper(),
                    }

                    print(f"[INFO] Processing: {applicant['first_name']} {applicant['last_name']}")
                    print(f"[INFO] Input: '{input_state}' -> State: '{state_normalized}'")
                    print(f"[INFO] Branch: {config['branch_name']}")
                    print(f"[INFO] Agency: {config['agency_name']}")
                    if config.get("has_producer"):
                        print(f"[INFO] Producer: {config.get('producer_name', 'N/A')}")
                    if applicant['effective_date']:
                        print(f"[INFO] Effective Date: {applicant['effective_date']}")

                    # Reset context periodically for stability
                    if total_successful > 0 and total_successful % 15 == 0:
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
                            context.clear_cookies()  
                        except:
                            pass
                        ct.login(page)

                    # --- Retry loop for each row ---
                    for attempt in range(2):  # try twice max
                        try:
                            # ✅ UPDATED: Pass quotes_only flag
                            quote_number, policy_number = process_quote(
                                page, state_normalized, config, applicant, quotes_only
                            )

                            total_successful += 1
                            state_stats[state_normalized]["success"] += 1
                            print(f"[SUCCESS] {state_normalized} - Quote: {quote_number}, Policy: {policy_number or 'N/A - Quote Only'}")  # ✅ UPDATED
                            
                            write_progress(f"Row {i}: SUCCESS - {applicant['first_name']} {applicant['last_name']} ({state_normalized}) - Quote: {quote_number}")

                            out_row = {**row}
                            out_row.update(
                                {
                                    "row_index": i,
                                    "quote_number": quote_number or "",
                                    "policy_number": policy_number or "N/A - Quote Only",  
                                    "processed_state": state_normalized,
                                    "status": "ok",
                                    "error": "",
                                    "run_at": "'" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                }
                            )
                            writer.writerow(out_row)
                            f_out.flush()
                            time.sleep(0.4)
                            break  

                        # --- Error handling with retry ---
                        except Exception as e:
                            # Check if it's a DTQ error
                            is_dtq = False
                            try:
                                module = config["module"]
                                if hasattr(module, 'DTQError') and isinstance(e, module.DTQError):
                                    is_dtq = True
                            except:
                                pass

                            error_type = "DTQ decline" if is_dtq else f"Attempt {attempt + 1}"
                            print(f"[ERROR] {state_normalized} {error_type}: {e}")
                            
                            write_progress(f"Row {i}: FAILED - {applicant['first_name']} {applicant['last_name']} ({state_normalized}) - {error_type}")

                            # DTQ errors: Don't retry, just log and continue
                            if is_dtq:
                                total_failed += 1
                                state_stats[state_normalized]["failed"] += 1
                                snap(page, f"row{i}_{state_normalized.lower()}_dtq")
                                
                                out_row = {**row}
                                out_row.update(
                                    {
                                        "row_index": i,
                                        "quote_number": "",
                                        "policy_number": "",
                                        "processed_state": state_normalized,
                                        "status": "error",
                                        "error": str(e),  
                                        "run_at": "'" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    }
                                )
                                writer.writerow(out_row)
                                f_out.flush()
                                
                                # FIX: Don't reset - DTQ handlers already navigate to home!
                                break  

                            # Regular errors: Retry on first attempt
                            elif attempt == 0:
                                print(f"[INFO] Row {i} failed first attempt, resetting context and retrying...")
                                try:
                                    context.close()
                                except Exception:
                                    pass
                                context = browser.new_context(
                                    storage_state=None   # Prevents caching
                                )
                                page = context.new_page()
                                try:
                                    context.clear_cookies()  # Clear cache
                                except:
                                    pass
                                ct.login(page)
                                continue 
                            
                            # Second failure of regular error → log and reset
                            else:
                                total_failed += 1
                                state_stats[state_normalized]["failed"] += 1
                                snap(page, f"row{i}_{state_normalized.lower()}_error")
                                
                                out_row = {**row}
                                out_row.update(
                                    {
                                        "row_index": i,
                                        "quote_number": "",
                                        "policy_number": "",
                                        "processed_state": state_normalized,
                                        "status": "error",
                                        "error": f"{state_normalized}: {str(e)}",
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
                                    context = browser.new_context(
                                        storage_state=None  # Prevents caching
                                    )
                                    page = context.new_page()
                                    try:
                                        context.clear_cookies()  # Clear cache
                                    except:
                                        pass
                                    ct.login(page)
                                break

        finally:
            context.close()
            browser.close()

    # Enhanced reporting
    print("\n" + "=" * 80)
    print("MULTI-STATE PROCESSING COMPLETE")
    print("=" * 80)
    print(f"Total successful policies: {total_successful}")
    print(f"Total failed policies: {total_failed}")
    print(f"Overall success rate: {(total_successful / (total_successful + total_failed)) * 100:.1f}%" if (total_successful + total_failed) > 0 else "0%")
    print("\nSTATE BREAKDOWN:")
    print("-" * 50)
    for state in ["Connecticut", "Massachusetts", "New Hampshire", "New Jersey", "New York", "Pennsylvania"]:
        if state in state_stats:
            stats = state_stats[state]
            total_state = stats["success"] + stats["failed"]
            success_rate = (stats["success"] / total_state * 100) if total_state > 0 else 0
            print(f"{state:<20}: {stats['success']:>3} success, {stats['failed']:>3} failed, {success_rate:>5.1f}% rate")
    
    print(f"\nResults saved to: {out_csv}")
    
    write_progress(f"Processing complete: {total_successful} success, {total_failed} failed")

    # Optional Excel export  
    if out_xlsx:
        try:
            df = pd.read_csv(out_csv)
            df.to_excel(out_xlsx, index=False)
            print(f"Excel export saved to: {out_xlsx}")
        except Exception as e:
            print(f"[WARN] Excel export failed: {e}")

    print("=" * 80)


if __name__ == "__main__":
    in_csv = args.input_file or (sys.argv[1] if len(sys.argv) > 1 else "input_multistate.csv")  
    out_csv = args.output_file or (
        sys.argv[2]
        if len(sys.argv) > 2
        else f"output_multistate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )  
    out_xlsx = sys.argv[3] if len(sys.argv) > 3 else out_csv.replace(".csv", ".xlsx")

    if out_xlsx == "":
        out_xlsx = None

    headless = args.headless or ("--headless" in sys.argv) 

    try:
        main(in_csv, out_csv, out_xlsx, headless, args.quotes_only) 
    except KeyboardInterrupt:
        print("\n\nBatch processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)