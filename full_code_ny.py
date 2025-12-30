import re, time, os
from datetime import datetime
from dotenv import load_dotenv
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


BASE_URL = os.getenv("PR_BASE_URL", "https://agentweb1mod.plymouthrock.com")
LOGIN_URL = f"{BASE_URL}/aiui/login"
HOME_URL = f"{BASE_URL}/aiui/home"
# NY patterns for quote (NYHQ) and policy (NYH) numbers
QUOTE_REGEX = re.compile(r"\bNYHQ\w+\b", re.I)
NY_POLICY_REGEX = re.compile(r"\bNYH\w+\b", re.I)


class DTQError(Exception):
    """Raised when a DTQ popup or decline condition occurs"""
    pass


# ---------- tiny utils ----------
def log(msg):
    print(f"[STEP] {msg}")


def safe_action(action, description):
    try:
        action()
        log(f"Success: {description}")
    except Exception as e:
        log(f"[ERROR] Failed: {description} | {e}")
        raise


def wait_for_nonempty_text(scope, selector, timeout_ms=20000):
    deadline = time.time() + timeout_ms / 1000.0
    loc = scope.locator(selector).first
    try:
        loc.wait_for(state="visible", timeout=timeout_ms)
    except Exception:
        return None
    while time.time() < deadline:
        try:
            txt = loc.inner_text().strip()
            if txt:
                return txt
        except Exception:
            pass
        time.sleep(0.2)
    return None


def wait_for_text_change(scope, selector, old_value, timeout_ms=10000):
    """Wait for the selector text to change from old_value; return new text or None."""
    deadline = time.time() + timeout_ms / 1000.0
    loc = scope.locator(selector).first
    while time.time() < deadline:
        try:
            txt = loc.inner_text().strip()
            if txt and txt != old_value:
                return txt
        except Exception:
            pass
        time.sleep(0.2)
    return None


def normalize_state(s):
    m = {
        "NY": "New York",
        "NJ": "New Jersey",
        "NH": "New Hampshire",
        "MA": "Massachusetts",
        "CT": "Connecticut",
        "PA": "Pennsylvania",
    }
    s = (s or "").strip()
    return m.get(s.upper(), s or "New York")


def normalize_dob(dob_str: str) -> str:
    try:
        dt = datetime.strptime(dob_str.strip(), "%m/%d/%Y")
        return dt.strftime("%m/%d/%Y")
    except Exception:
        return dob_str.strip()


def dismiss_backdrop(page, timeout=4000): 
    try:
        backdrop = page.locator("div.modal-backdrop.in")
        if backdrop.count() > 0:
            log("Backdrop detected, waiting for it to disappear")
            backdrop.wait_for(state="detached", timeout=timeout)
    except Exception:
        pass


# ---------- login ----------
def login(page):
    load_dotenv(override=True)
    
    user = os.getenv("PR_USERNAME") or ""
    pw = os.getenv("PR_PASSWORD") or ""
    if not user or not pw:
        raise RuntimeError("Missing PR_USERNAME/PR_PASSWORD (set in .env)")

    print(f"[DEBUG] Logging in with username: {user}")
    print(f"[DEBUG] Password starts with: {pw[:4]}...")
    
    log("Login")
    safe_action(lambda: page.goto(LOGIN_URL), "Go to login page")
    safe_action(
        lambda: page.get_by_role("textbox", name="Username").fill(user), "Fill username"
    )
    safe_action(
        lambda: page.get_by_role("textbox", name="Password").fill(pw), "Fill password"
    )
    safe_action(
        lambda: page.get_by_role("button", name="Login").click(), "Submit login"
    )
    page.get_by_role("button", name="New Quote").wait_for(timeout=25000)


# ---------- new quote ----------
def create_new_quote(page, state="New York", effective_date="", line_of_business="HO3"):
    """Create new quote with optional effective date"""
    state_full = normalize_state(state)
    log("Start New Quote")
    dismiss_backdrop(page)
    safe_action(
        lambda: page.get_by_role("button", name="New Quote").click(), "Click New Quote"
    )
    safe_action(
        lambda: page.get_by_role("cell", name="Personal Auto").locator("a").click(),
        "Click Personal Auto",
    )
    safe_action(
        lambda: page.locator("#lobNQ_chosen").get_by_text("Home").click(),
        "Set LOB = Home",
    )

    safe_action(
        lambda: page.get_by_role("cell", name="--Select--").locator("a").click(),
        "Expand state list",
    )
    container = page.locator("#stateNQ_chosen")
    try:
        container.locator("input").fill(state_full)
    except Exception:
        pass
    container.get_by_text(state_full, exact=False).click()
    
    log(f"Selecting line of business: {line_of_business}")
    try:
        if line_of_business == "HO4":
            page.locator("span").filter(has_text="Renters").get_by_role("radio").check()
            log("Selected Renters (HO4)")
        elif line_of_business == "HO6":
            page.locator("span").filter(has_text="Condo-Owners").get_by_role("radio").check()
            log("Selected Condo-Owners (HO6)")
        else:  # HO3 or blank - default
            page.locator("span").filter(has_text="Homeowners").get_by_role("radio").check()
            log("Selected Homeowners (HO3)")
    except Exception as e:
        log(f"[WARN] Could not select line of business radio button: {e}")
        log("Continuing with default (Homeowners)")
    
    if effective_date:
        try:
            safe_action(
                lambda: page.locator("#policyEffectiveDateNQ").fill(effective_date),
                f"Fill effective date: {effective_date}"
            )
        except Exception as e:
            log(f"[INFO] Could not fill effective date: {e}")


# ---------- applicant ----------
def fill_applicant_info(page, applicant):
    log("Fill applicant info")
    page.evaluate("document.body.style.zoom='0.7'")
    safe_action(
        lambda: page.locator("#firstNameNewCo").fill(applicant["first_name"]),
        "Fill first name",
    )
    safe_action(
        lambda: page.locator("#lastNameNewCo").fill(applicant["last_name"]),
        "Fill last name",
    )
    safe_action(
        lambda: page.get_by_role("textbox", name="mm/dd/yyyy").fill(
            normalize_dob(applicant["dob"])
        ),
        "Fill DOB",
    )

    bare_address = applicant["address"].replace(",", "").strip()
    log(f"[DEBUG] Address: {bare_address}")
    
    addr_box = page.get_by_placeholder("Enter street, city, state and")
    
    safe_action(lambda: addr_box.click(), "Click address box")
    safe_action(lambda: addr_box.fill(bare_address), "Fill address")
    safe_action(lambda: addr_box.click(), "Click again (1)")
    safe_action(lambda: addr_box.click(), "Click again (2)")
    safe_action(lambda: addr_box.press("ControlOrMeta+a"), "Select all")
    safe_action(lambda: addr_box.fill(bare_address), "Refill address")
    
    log("[DEBUG] Waiting for dropdown...")
    time.sleep(2)
    
    try:
        log("[DEBUG] Using keyboard to select address...")
        safe_action(lambda: addr_box.press("ArrowDown"), "Press Arrow Down")
        time.sleep(0.3)
        safe_action(lambda: addr_box.press("Enter"), "Press Enter")
        log("✓ Selected address from dropdown")
        
        time.sleep(0.5)
        final = addr_box.input_value()
        log(f"[DEBUG] Final: {final[:80]}")
        
    except Exception as e:
        log(f"[WARN] Dropdown failed: {e}")
        addr_box.press("Enter")


# ---------- branch, agency, and producer (NY specific) ----------
def select_branch_and_agency(
    page,
    branch_filter="Palisades",
    branch_name="Palisades",
    agency_filter="A.H. Meyers",
    agency_name="A.H. Meyers and Company",
    producer_filter=None,
    producer_name=None,
):
    log("Select branch, agency, and producer")

    # --- Branch ---
    br_row = page.get_by_role("row", name=re.compile(r"^Branch", re.I))
    br_row.locator(".chosen-container a").click()
    try:
        br_row.locator(".chosen-container input").fill(branch_filter)
    except Exception:
        pass

    # Select branch
    page.locator(".chosen-drop .chosen-results li").filter(
        has_text=re.compile(re.escape(branch_filter), re.I)
    ).first.click()
    log(f"Branch selected: {branch_name}")

    # Wait for dropdowns to refresh
    time.sleep(1)

    # --- Agency (using working reference pattern) ---
    try:
        # Wait for agency dropdown to populate
        page.wait_for_function(
            """() => {
                const el = document.querySelector('#agencyNewCo');
                return el && el.options && el.options.length > 1;
            }""",
            timeout=10000,
        )

        # Click the agency dropdown using --Select-- cell
        page.get_by_role("cell", name="--Select--").locator("a").first.click()
        log("Clicked agency dropdown")
        time.sleep(0.5)

        # Try to select by text from chosen dropdown using agency_name parameter
        agency_search = agency_filter if agency_filter else "A.H. Meyers"
        log(f"Searching for agency: {agency_search}")
        
        try:
            agency_option = (
                page.locator("#agencyNewCo_chosen")
                .get_by_text(re.compile(re.escape(agency_search), re.I))
                .first
            )
            agency_option.click()
            log(f"Agency selected: {agency_name}")
        except:
            # Fallback: type and select first result
            try:
                search_box = page.locator("#agencyNewCo_chosen input[type='text']")
                search_box.fill(agency_search)
                time.sleep(0.5)
                
                page.locator(
                    "#agencyNewCo_chosen .chosen-results li.active-result"
                ).first.click()
                log("Agency selected via search")
            except:
                # Last resort: JavaScript
                page.evaluate(
                    """(agencySearch) => {
                        const el = document.querySelector('#agencyNewCo');
                        if (el && el.options.length > 1) {
                            for (let i = 0; i < el.options.length; i++) {
                                if (el.options[i].text.includes('A.H. Meyers') || 
                                    el.options[i].text.includes('Meyers')) {
                                    el.selectedIndex = i;
                                    el.dispatchEvent(new Event('change', {bubbles:true}));
                                    if (window.jQuery) {
                                        $(el).trigger('chosen:updated');
                                    }
                                    return;
                                }
                            }
                            el.selectedIndex = 1;
                            el.dispatchEvent(new Event('change', {bubbles:true}));
                        }
                    }""",
                    agency_search
                )
                log("Agency selected via JavaScript")

    except Exception as e:
        log(f"[ERROR] Agency selection failed: {e}")
        raise

    # Wait for producer dropdown to appear
    time.sleep(1)

    # --- Producer (using working reference pattern) ---
    try:
        # Find remaining --Select-- cells for producer
        select_cells = page.get_by_role("cell", name="--Select--").all()
        if len(select_cells) > 0:
            select_cells[0].locator("a").click()
            log("Clicked producer dropdown")
            time.sleep(0.5)

            # Try to select producer
            producer_search = producer_filter if producer_filter else "A.H. Meyers"
            log(f"Searching for producer: {producer_search}")
            
            try:
                producer_option = (
                    page.locator("#producerNewCo_chosen")
                    .get_by_text(re.compile(re.escape(producer_search), re.I))
                    .first
                )
                producer_option.click()
                log(f"Producer selected: {producer_name if producer_name else producer_search}")
            except:
                # Try partial match
                try:
                    first_word = producer_search.split()[0]
                    producer_option = (
                        page.locator("#producerNewCo_chosen")
                        .get_by_text(re.compile(re.escape(first_word), re.I))
                        .first
                    )
                    producer_option.click()
                    log(f"Producer selected via partial match: {first_word}")
                except:
                    try:
                        search_box = page.locator(
                            "#producerNewCo_chosen input[type='text']"
                        )
                        search_box.fill(producer_search)
                        time.sleep(0.5)
                        page.locator(
                            "#producerNewCo_chosen .chosen-results li.active-result"
                        ).first.click()
                        log("Producer selected via search")
                    except:
                        page.evaluate(
                            """(producerSearch) => {
                                const el = document.querySelector('#producerNewCo');
                                if (el && el.options.length > 1) {
                                    for (let i = 0; i < el.options.length; i++) {
                                        if (el.options[i].text.includes('A.H. Meyers') || 
                                            el.options[i].text.includes('3018200')) {
                                            el.selectedIndex = i;
                                            el.dispatchEvent(new Event('change', {bubbles:true}));
                                            if (window.jQuery) {
                                                $(el).trigger('chosen:updated');
                                            }
                                            return;
                                        }
                                    }
                                    el.selectedIndex = 1;
                                    el.dispatchEvent(new Event('change', {bubbles:true}));
                                }
                            }""",
                            producer_search
                        )
                        log("Producer selected via JavaScript")
        else:
            log("[WARN] No producer dropdown found")

    except Exception as e:
        log(f"[WARN] Producer selection failed: {e}")


# ---------- quote and issue with policy number ----------
def quote_and_issue(page, applicant):
    """Complete quote and issue process returning both quote_number and policy_number"""
    log("Quote → bind → issue → scrape quote & policy numbers")

    dismiss_backdrop(page)

    # FIXED: Changed from 1500 to 800
    try:
        prod = page.locator("#producerNewCoLiteral")
        if prod.is_visible(timeout=800):
            safe_action(lambda: prod.click(), "Producer click")
    except Exception:
        pass

    try:
        page.get_by_text("x New Quote").click(timeout=800)
        log("Success: Remove new quote popup if any")
    except Exception:
        pass

    # FIXED: Changed from 15000 to 5000
    quote_btn = page.get_by_role("button", name="Quote", exact=True)
    quote_btn.wait_for(state="visible", timeout=5000)
    safe_action(lambda: quote_btn.click(), "Click Quote")
    
    try:
        knockout_popup = page.locator("#rateErrorForKnockOutProducer")
        knockout_btn = knockout_popup.get_by_text("Ok")
        knockout_btn.wait_for(state="visible", timeout=3000)
        
        log("Producer knockout error popup detected and VISIBLE")
        knockout_btn.click(timeout=2000)
        log("Closed producer knockout popup, navigating to New Quote immediately")
        
        time.sleep(1)
        page.get_by_role("button", name="New Quote").wait_for(state="visible", timeout=5000)
        
        raise DTQError("Producer knockout error - invalid producer/agency selection")
        
    except DTQError:
        raise
    except:
        log("[INFO] No producer knockout popup visible")

    # FIXED: Use .wait_for(state="visible") instead of .count()
    try:
        dtq_popup_main = page.locator("#ratingErrorForDTBClose")
        dtq_popup_main.wait_for(state="visible", timeout=3000)
        
        log("DTQ/DTB error popup detected and VISIBLE on main page")
        dtq_popup_main.click(timeout=2000)
        log("Closed DTQ/DTB popup")
        
        time.sleep(3)
        log("Navigating to New Quote now")
        page.get_by_role("button", name="New Quote").wait_for(state="visible", timeout=5000)
        
        raise DTQError("DTQ/DTB Error popup on main page - applicant not qualified")
        
    except DTQError:
        raise
    except:
        log("[INFO] No DTQ/DTB popup visible on main page")

    # --- Handle modals ---
    for modal_name, locator in [
        ("Select My Entry", "button#selectMine"),
        ("Save and Continue", "button:has-text('Save and Continue')"),
    ]:
        try:
            btn = page.locator(locator)
            btn.wait_for(state="visible", timeout=5000)
            safe_action(lambda: btn.click(), f"Click {modal_name}")
            dismiss_backdrop(page)
            log(f"Handled {modal_name} modal")
        except Exception:
            log(f"[INFO] No {modal_name} modal found")

    # --- Switch into iframe ---
    try:
        iframe = page.locator('iframe[name="main"]').first
        iframe.wait_for(state="attached", timeout=20000)
        frame = iframe.content_frame
        if frame is None:
            raise DTQError("Quote iframe did not load - possible DTQ decline")
    except Exception as e:
        log(f"[ERROR] Could not load iframe: {e}")
        raise DTQError("Quote iframe did not load - possible DTQ decline")

    # FIXED: ADD CRN/FCRA popup handler (from PA)
    try:
        fcra_close_btn = frame.locator("#fcra-dialog-close")
        fcra_close_btn.wait_for(state="visible", timeout=3000)
        
        log("CRN decline popup detected and VISIBLE in iframe")
        fcra_close_btn.click(timeout=2000)
        log("Closed CRN decline popup")
        
        time.sleep(2)
        
        try:
            frame.get_by_role("link", name="Step 2").click(timeout=3000)
            log("Clicked Step 2 link in iframe")
        except:
            log("[INFO] No Step 2 link found, trying direct home navigation")
        
        time.sleep(1)
        try:
            page.locator("#logoSection").get_by_role("button").click(timeout=3000)
            log("Clicked logo button to go home")
        except:
            try:
                page.locator("#logoSection a").first.click(timeout=3000)
                log("Clicked logo link to go home")
            except:
                log("[WARN] Could not click logo, will try goto")
                page.goto(HOME_URL, timeout=10000)
        
        page.get_by_role("button", name="New Quote").wait_for(state="visible", timeout=15000)
        log("Home page ready - New Quote button visible")
        
        raise DTQError("CRN decline - applicant not qualified")
        
    except DTQError:
        raise
    except:
        log("[INFO] No CRN popup visible in iframe")

    # --- Select Good package ---
    try:
        good_package = frame.locator("input.selectPackage[data-package-name='Good']")
        good_package.wait_for(state="visible", timeout=30000)
        safe_action(lambda: good_package.click(), "Select Good package")
    except Exception:
        safe_action(
            lambda: frame.locator(
                "xpath=//div[contains(.,'Good')]//button[contains(.,'Select')]"
            ).first.click(),
            "Select Good package (fallback)",
        )

    # --- Click "Click to Bind" ---
    target = frame if frame else page
    safe_action(
        lambda: target.get_by_role("button", name="Click to Bind").click(),
        "Click Bind button",
    )

    time.sleep(3)

    # --- Scrape QUOTE NUMBER ---
    quote_number = wait_for_nonempty_text(page, "#policy_number", timeout_ms=20000)
    log(f"Quote number scraped: {quote_number}")

    # --- Producer License Number (NY may not need this) ---
    try:
        producer_row = target.get_by_role("row", name=re.compile(r"Producer License Number", re.I))
        if producer_row.count() > 0:
            log("[INFO] Producer License Number field found - selecting first option")
            producer_row.locator("a").click()
            time.sleep(1)
            
            all_options = target.locator(
                "#producerLicenseNumber_chosen .chosen-results li.active-result"
            ).all()
            
            producer_selected = False
            for i, option in enumerate(all_options[:5]):
                try:
                    option_text = option.inner_text().strip()
                    if "select" in option_text.lower() or option_text == "--" or not option_text:
                        continue
                    
                    option.click()
                    log(f"✓ Selected NY producer: {option_text}")
                    producer_selected = True
                    break
                except:
                    continue
            
            if not producer_selected:
                result = target.evaluate("""
                    () => {
                        const select = document.querySelector('#producerLicenseNumber');
                        if (select && select.options.length > 1) {
                            for (let i = 1; i < select.options.length; i++) {
                                const optText = select.options[i].text;
                                if (optText && !optText.toLowerCase().includes('select')) {
                                    select.selectedIndex = i;
                                    select.dispatchEvent(new Event('change', {bubbles: true}));
                                    if (window.jQuery) {
                                        $(select).trigger('chosen:updated');
                                    }
                                    return optText;
                                }
                            }
                        }
                        return null;
                    }
                """)
                if result:
                    log(f"✓ Selected NY producer via JS: {result}")
        else:
            log("[INFO] No Producer License Number field (expected for NY)")
    except Exception as e:
        log(f"[INFO] Producer License Number not found or not required: {e}")

    # --- Continue with phone/payment info ---
    safe_action(
        lambda: target.get_by_role("row", name=re.compile(r"Phone Number", re.I))
        .locator("a")
        .click(),
        "Expand phone type",
    )
    safe_action(
        lambda: target.locator("#phn_num_type_chosen").get_by_text("Home").click(),
        "Select Home phone",
    )

    phone = applicant.get("phone", "555-555-5555")
    safe_action(
        lambda: target.locator("#phoneNumber").fill(phone),
        "Fill phone number",
    )

    safe_action(
        lambda: target.get_by_role("row", name=re.compile(r"Down Payment Method", re.I))
        .locator("a")
        .click(),
        "Expand down payment",
    )
    safe_action(
        lambda: target.locator("#dwnpaymnt_method_cd_chosen")
        .get_by_text(re.compile(r"No Down Payment Required", re.I))
        .click(),
        "Select no down payment",
    )
    safe_action(
        lambda: target.get_by_role(
            "row", name=re.compile(r"Future Payment Method", re.I)
        )
        .locator("a")
        .click(),
        "Expand future payment",
    )
    safe_action(
        lambda: target.locator("#futurepaymnt_method_cd_chosen")
        .get_by_text(re.compile(r"Paper", re.I))
        .click(),
        "Select future payment Paper",
    )
    safe_action(
        lambda: target.locator("#certifyPaymentInd_Check").check(), "Certify payment"
    )

    # --- Click "Click to Issue" ---
    safe_action(
        lambda: target.get_by_role("button", name="Click to Issue").click(),
        "Click to Issue",
    )
    safe_action(
        lambda: target.get_by_role("button", name="Yes").click(), "Confirm issue"
    )

    # Dismiss optional OK modals
    try:
        page.get_by_role("button", name="OK").click(timeout=3000)
        log("Success: Dismiss OK modal")
    except Exception:
        pass

    # Optional policy details
    try:
        safe_action(
            lambda: target.get_by_text("Policy Details Policy Number").click(),
            "View policy details",
        )
        try:
            safe_action(
                lambda: target.get_by_role("button", name="OK").click(),
                "Acknowledge completion",
            )
        except Exception:
            pass
    except Exception:
        pass

    # --- Scrape POLICY NUMBER ---
    policy_number = wait_for_text_change(
        page, "#policy_number", quote_number, timeout_ms=20000
    )
    if not policy_number:
        policy_number = wait_for_nonempty_text(page, "#policy_number", timeout_ms=8000)

    log(f"Policy number scraped: {policy_number}")

    try:
        page.wait_for_load_state("domcontentloaded", timeout=8000)
    except Exception:
        pass

    # --- Navigate back to home page ---
    log("Navigating back to home page for next quote...")
    time.sleep(1)

    # Clear any leftover frame modals
    try:
        if frame:
            try:
                frame.get_by_role("button", name="OK").click(timeout=1200)
                log("Dismissed OK modal in frame")
            except Exception:
                pass
            
            #  Exit confirmation handling
            try:
                exit_btn = frame.get_by_role("button", name="Exit")
                exit_btn.wait_for(state="visible", timeout=3000)
                safe_action(lambda: exit_btn.click(), "Confirm Exit")
                log("Clicked Exit confirmation")
            except:
                log("[INFO] No Exit confirmation needed")
    except Exception:
        pass

    navigated = False

    # Try logo
    try:
        if page.locator("#logoSection button, #logoSection a").count() > 0:
            safe_action(
                lambda: page.locator("#logoSection button, #logoSection a").first.click(
                    timeout=4000
                ),
                "Home via logo",
            )
            navigated = True
    except Exception:
        pass

    # Try 'Home' link
    if not navigated:
        try:
            safe_action(
                lambda: page.get_by_role(
                    "link", name=re.compile(r"\bHome\b", re.I)
                ).click(timeout=3000),
                "Home via top link",
            )
            navigated = True
        except Exception:
            pass

    # Try frame Home link
    if not navigated:
        try:
            if frame:
                safe_action(
                    lambda: frame.get_by_role(
                        "link", name=re.compile(r"\bHome\b", re.I)
                    ).click(timeout=3000),
                    "Home via frame link",
                )
                navigated = True
        except Exception:
            pass

    # Fallback: browser back
    if not navigated:
        try:
            page.go_back()
            time.sleep(2)
            log("Used browser back button as fallback")
            navigated = True
        except:
            log("[WARN] All navigation methods failed")

    # Confirm home ready
    try:
        page.get_by_role("button", name="New Quote").wait_for(
            state="visible", timeout=15000
        )
        log("Home ready (New Quote visible)")
    except Exception:
        log("[WARN] 'New Quote' not confirmed visible; continuing...")

    # Validate we got both numbers
    if not quote_number:
        raise RuntimeError("Could not scrape quote number")
    if not policy_number:
        raise RuntimeError("Could not scrape policy number")

    return quote_number, policy_number


def quote_only(page, applicant):
    """Get quote number only, skip policy issuance"""
    log("Quote → select Good → scrape quote number (NO policy)")

    dismiss_backdrop(page)

    # Producer click check
    try:
        prod = page.locator("#producerNewCoLiteral")
        if prod.is_visible(timeout=800):
            safe_action(lambda: prod.click(), "Producer click")
    except Exception:
        pass

    # Remove popup check
    try:
        page.get_by_text("x New Quote").click(timeout=800)
        log("Success: Remove new quote popup if any")
    except Exception:
        pass

    # Click Quote
    quote_btn = page.get_by_role("button", name="Quote", exact=True)
    quote_btn.wait_for(state="visible", timeout=5000)
    safe_action(lambda: quote_btn.click(), "Click Quote")

    # Producer knockout popup
    try:
        knockout_popup = page.locator("#rateErrorForKnockOutProducer")
        knockout_btn = knockout_popup.get_by_text("Ok")
        knockout_btn.wait_for(state="visible", timeout=3000)
        
        log("Producer knockout error popup detected and VISIBLE")
        knockout_btn.click(timeout=2000)
        log("Closed producer knockout popup, navigating to New Quote immediately")
        
        time.sleep(1)
        page.get_by_role("button", name="New Quote").wait_for(state="visible", timeout=5000)
        
        raise DTQError("Popup error detected and closed")
        
    except DTQError:
        raise
    except:
        log("[INFO] No producer knockout popup visible")

    # DTQ/DTB popup check
    try:
        dtq_popup_main = page.locator("#ratingErrorForDTBClose")
        dtq_popup_main.wait_for(state="visible", timeout=3000)
        
        log("DTQ/DTB error popup detected and VISIBLE on main page")
        dtq_popup_main.click(timeout=2000)
        log("Closed DTQ/DTB popup, navigating to New Quote immediately")
        
        time.sleep(1)
        page.get_by_role("button", name="New Quote").wait_for(state="visible", timeout=5000)
        
        raise DTQError("DTQ/DTB Error popup on main page - applicant not qualified")
        
    except DTQError:
        raise
    except:
        log("[INFO] No DTQ/DTB popup visible on main page")

    # Handle modals
    for modal_name, locator in [
        ("Select My Entry", "button#selectMine"),
        ("Save and Continue", "button:has-text('Save and Continue')"),
    ]:
        try:
            btn = page.locator(locator)
            btn.wait_for(state="visible", timeout=5000)
            safe_action(lambda: btn.click(), f"Click {modal_name}")
            dismiss_backdrop(page)
            log(f"Handled {modal_name} modal")
        except Exception:
            log(f"[INFO] No {modal_name} modal found")

    # Switch into iframe
    try:
        iframe = page.locator('iframe[name="main"]').first
        iframe.wait_for(state="attached", timeout=20000)
        frame = iframe.content_frame
        if frame is None:
            raise DTQError("Quote iframe did not load - possible DTQ decline")
    except Exception as e:
        log(f"[ERROR] Could not load iframe: {e}")
        raise DTQError("Quote iframe did not load - possible DTQ decline")

    # CRN/FCRA decline popup check in iframe
    try:
        fcra_close_btn = frame.locator("#fcra-dialog-close")
        fcra_close_btn.wait_for(state="visible", timeout=3000)
        
        log("CRN/FCRA decline popup detected and VISIBLE in iframe")
        fcra_close_btn.click(timeout=2000)
        log("Closed CRN decline popup, navigating home immediately")
        
        time.sleep(2)
        page.goto(HOME_URL, timeout=10000)
        page.get_by_role("button", name="New Quote").wait_for(state="visible", timeout=15000)
        
        raise DTQError("CRN decline - applicant not qualified")
        
    except DTQError:
        raise
    except:
        log("[INFO] No CRN/FCRA popup visible in iframe")

    # Select Good package
    try:
        good_package = frame.locator("input.selectPackage[data-package-name='Good']")
        good_package.wait_for(state="visible", timeout=30000)
        safe_action(lambda: good_package.click(), "Select Good package")
    except Exception:
        safe_action(
            lambda: frame.locator(
                "xpath=//div[contains(.,'Good')]//button[contains(.,'Select')]"
            ).first.click(),
            "Select Good package (fallback)",
        )

    log("Waiting for quote number to appear after Good selection...")
    time.sleep(2)

    quote_number = wait_for_nonempty_text(page, "#policy_number", timeout_ms=10000)
    
    if not quote_number:
        # Try searching iframe body
        try:
            txt = frame.inner_text("body")
            log(f"[DEBUG] Searching iframe body for quote number")
        except:
            pass
    
    log(f"Quote number scraped: {quote_number}")

    if not quote_number:
        log("[WARN] Could not scrape quote number after Good selection")

    # Navigate home without issuing policy
    log("Quote-only mode: Navigating home WITHOUT issuing policy...")
    time.sleep(1)

    # Try to navigate via logo
    try:
        logo = page.locator("#logoSection").get_by_role("button")
        logo.wait_for(state="visible", timeout=5000)
        safe_action(lambda: logo.click(), "Click Plymouth Rock logo")
    except:
        # Try home link
        try:
            safe_action(
                lambda: page.get_by_role("link", name=re.compile(r"\bHome\b", re.I)).click(timeout=3000),
                "Home via top link",
            )
        except:
            # Fallback: browser back
            try:
                page.go_back()
                time.sleep(2)
                log("Used browser back button as fallback")
            except:
                log("[WARN] Navigation failed")

    time.sleep(1)
    try:
        exit_btn_main = page.get_by_role("button", name="Exit")
        exit_btn_main.wait_for(state="visible", timeout=3000)
        safe_action(lambda: exit_btn_main.click(), "Confirm Exit on warning popup")
        log("✓ Clicked Exit button on main page")
    except:
        log("[INFO] No Exit popup on main page")

    # Also check iframe for Exit/OK
    try:
        if frame:
            try:
                frame.get_by_role("button", name="OK").click(timeout=1200)
                log("Dismissed OK modal in frame")
            except:
                pass
            try:
                frame.get_by_role("button", name="Exit").click(timeout=1200)
                log("Clicked Exit in frame")
            except:
                pass
    except:
        pass

    # Confirm home ready
    try:
        page.get_by_role("button", name="New Quote").wait_for(state="visible", timeout=15000)
        log("Home ready (New Quote visible)")
    except:
        log("[WARN] 'New Quote' not confirmed visible; continuing...")

    if not quote_number:
        raise RuntimeError("Could not scrape quote number")

    return quote_number, None