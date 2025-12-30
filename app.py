

# # app.py 
# import streamlit as st
# import subprocess
# import pandas as pd
# import os
# import time
# from datetime import datetime
# from pathlib import Path
# import sys

# st.set_page_config(
#     page_title="Plymouth Rock Automation",
#     page_icon="🪨",
#     layout="wide"
# )

# # Initialize session state
# if 'process' not in st.session_state:
#     st.session_state.process = None
# if 'running' not in st.session_state:
#     st.session_state.running = False

# st.title("Plymouth Rock Quote Automation")

# # Add logo if available
# if Path("plymouth_rock_logo.png").exists():
#     st.image("plymouth_rock_logo.png", width=300)
    
# st.markdown("---")

# # ========== SIMPLIFIED CREDENTIALS MANAGEMENT ==========

# def manage_credentials():
#     """Simple credentials management in Streamlit sidebar"""
#     st.sidebar.markdown("---")
#     st.sidebar.subheader("🔐 Plymouth Rock Login")
    
#     # Check if .env file exists
#     env_path = Path(".env")
    
#     # Read current credentials from .env if they exist
#     current_username = ""
#     current_password = ""
    
#     if env_path.exists():
#         try:
#             from dotenv import dotenv_values
#             env_vars = dotenv_values(".env")
#             current_username = env_vars.get("PR_USERNAME", "")
#             current_password = env_vars.get("PR_PASSWORD", "")
#         except:
#             pass
    
#     # Show credential status
#     if current_username:
#         st.sidebar.success(f"Logged in as: **{current_username}**")
#     else:
#         st.sidebar.warning("No credentials saved")
    
#     # Expander for updating credentials
#     with st.sidebar.expander("🔧 Update Credentials", expanded=not current_username):
#         with st.form("credentials_form"):
#             st.markdown("**Enter Plymouth Rock credentials:**")
            
#             new_username = st.text_input(
#                 "Agent Username",
#                 value=current_username,
#                 help="Your Plymouth Rock AgentWeb username"
#             )
            
#             new_password = st.text_input(
#                 "Agent Password",
#                 type="password",
#                 help="Your Plymouth Rock AgentWeb password"
#             )
            
#             # FIXED: Only Save button
#             save_button = st.form_submit_button("Save Credentials", use_container_width=True, type="primary")
            
#             if save_button:
#                 if new_username and new_password:
#                     # Update .env file
#                     try:
#                         # Read existing .env content (preserve other variables)
#                         existing_lines = []
#                         if env_path.exists():
#                             with open(env_path, 'r') as f:
#                                 existing_lines = [line for line in f.readlines() 
#                                                 if not line.startswith('PR_USERNAME=') 
#                                                 and not line.startswith('PR_PASSWORD=')]
                        
#                         # Write updated credentials
#                         with open(env_path, 'w') as f:
#                             # Write other existing env vars first
#                             for line in existing_lines:
#                                 f.write(line)
#                             # Write credentials
#                             f.write(f"PR_USERNAME={new_username}\n")
#                             f.write(f"PR_PASSWORD={new_password}\n")
                        
#                         st.success(f"Credentials saved for **{new_username}**!")
#                         st.balloons()
#                         time.sleep(1)
#                         st.rerun()
#                     except Exception as e:
#                         st.error(f"Error saving credentials: {e}")
#                 else:
#                     st.warning("Please enter both username and password")

# # ========== END CREDENTIALS MANAGEMENT ==========


# # ========== AGENCY CONFIGURATION MANAGEMENT ==========
# def manage_agency_config():
#     """Agency configuration management in Streamlit sidebar"""
#     st.sidebar.markdown("---")
#     st.sidebar.subheader("🏢 Agency Configuration")
    
#     env_path = Path(".env")
    
#     # Read current configs from .env if they exist
#     current_configs = {}
#     if env_path.exists():
#         try:
#             from dotenv import dotenv_values
#             env_vars = dotenv_values(".env")
            
#             for state_abbr in ["CT", "MA", "NH", "NJ", "NY", "PA"]:
#                 current_configs[state_abbr] = {
#                     "branch": env_vars.get(f"PR_{state_abbr}_BRANCH", ""),
#                     "agency": env_vars.get(f"PR_{state_abbr}_AGENCY", ""),
#                     "producer": env_vars.get(f"PR_{state_abbr}_PRODUCER", "")
#                 }
#         except:
#             pass
    
#     # Show summary
#     configured_count = sum(1 for cfg in current_configs.values() if cfg.get("branch") or cfg.get("agency"))
#     if configured_count > 0:
#         st.sidebar.info(f"Configured: {configured_count}/6 states")
#     else:
#         st.sidebar.warning("No custom configs - using defaults")
    
#     # Connecticut
#     with st.sidebar.expander("Connecticut (CT)"):
#         with st.form("ct_agency_form"):
#             ct_branch = st.text_input("Branch Name", value=current_configs.get("CT", {}).get("branch", ""), placeholder="BHIC0035 | New England", key="ct_branch")
#             ct_agency = st.text_input("Agency Name", value=current_configs.get("CT", {}).get("agency", ""), placeholder="Columbia", key="ct_agency")
#             ct_producer = st.text_input("Producer Name", value=current_configs.get("CT", {}).get("producer", ""), placeholder="Columbia Insurance Agency", key="ct_producer")
            
#             if st.form_submit_button("Save CT", use_container_width=True):
#                 try:
#                     existing_lines = []
#                     if env_path.exists():
#                         with open(env_path, 'r') as f:
#                             existing_lines = [line for line in f.readlines() 
#                                             if not line.startswith('PR_CT_')]
                    
#                     with open(env_path, 'w') as f:
#                         for line in existing_lines:
#                             f.write(line)
#                         if ct_branch:
#                             f.write(f"PR_CT_BRANCH={ct_branch}\n")
#                         if ct_agency:
#                             f.write(f"PR_CT_AGENCY={ct_agency}\n")
#                         if ct_producer:
#                             f.write(f"PR_CT_PRODUCER={ct_producer}\n")
                    
#                     st.success("CT saved!")
#                     time.sleep(1)
#                     st.rerun()
#                 except Exception as e:
#                     st.error(f"Error: {e}")
    
#     # Massachusetts
#     with st.sidebar.expander("Massachusetts (MA)"):
#         with st.form("ma_agency_form"):
#             ma_branch = st.text_input("Branch Name", value=current_configs.get("MA", {}).get("branch", ""), placeholder="BHIC0035 | New England", key="ma_branch")
#             ma_agency = st.text_input("Agency Name", value=current_configs.get("MA", {}).get("agency", ""), placeholder="Columbia Insurance Agency", key="ma_agency")
#             ma_producer = st.text_input("Producer Name", value=current_configs.get("MA", {}).get("producer", ""), placeholder="Columbia Insurance Agency, Inc. - 0001001", key="ma_producer")
            
#             if st.form_submit_button("Save MA", use_container_width=True):
#                 try:
#                     existing_lines = []
#                     if env_path.exists():
#                         with open(env_path, 'r') as f:
#                             existing_lines = [line for line in f.readlines() 
#                                             if not line.startswith('PR_MA_')]
                    
#                     with open(env_path, 'w') as f:
#                         for line in existing_lines:
#                             f.write(line)
#                         if ma_branch:
#                             f.write(f"PR_MA_BRANCH={ma_branch}\n")
#                         if ma_agency:
#                             f.write(f"PR_MA_AGENCY={ma_agency}\n")
#                         if ma_producer:
#                             f.write(f"PR_MA_PRODUCER={ma_producer}\n")
                    
#                     st.success("MA saved!")
#                     time.sleep(1)
#                     st.rerun()
#                 except Exception as e:
#                     st.error(f"Error: {e}")
    
#     # New Hampshire
#     with st.sidebar.expander("New Hampshire (NH)"):
#         with st.form("nh_agency_form"):
#             nh_branch = st.text_input("Branch Name", value=current_configs.get("NH", {}).get("branch", ""), placeholder="BHIC0035 | New England", key="nh_branch")
#             nh_agency = st.text_input("Agency Name", value=current_configs.get("NH", {}).get("agency", ""), placeholder="Columbia Insurance Agency", key="nh_agency")
#             nh_producer = st.text_input("Producer Name", value=current_configs.get("NH", {}).get("producer", ""), placeholder="Columbia Insurance Agency", key="nh_producer")
            
#             if st.form_submit_button("Save NH", use_container_width=True):
#                 try:
#                     existing_lines = []
#                     if env_path.exists():
#                         with open(env_path, 'r') as f:
#                             existing_lines = [line for line in f.readlines() 
#                                             if not line.startswith('PR_NH_')]
                    
#                     with open(env_path, 'w') as f:
#                         for line in existing_lines:
#                             f.write(line)
#                         if nh_branch:
#                             f.write(f"PR_NH_BRANCH={nh_branch}\n")
#                         if nh_agency:
#                             f.write(f"PR_NH_AGENCY={nh_agency}\n")
#                         if nh_producer:
#                             f.write(f"PR_NH_PRODUCER={nh_producer}\n")
                    
#                     st.success("NH saved!")
#                     time.sleep(1)
#                     st.rerun()
#                 except Exception as e:
#                     st.error(f"Error: {e}")
    
#     # New Jersey
#     with st.sidebar.expander("New Jersey (NJ)"):
#         with st.form("nj_agency_form"):
#             nj_branch = st.text_input("Branch Name", value=current_configs.get("NJ", {}).get("branch", ""), placeholder="Palisades", key="nj_branch")
#             nj_agency = st.text_input("Agency Name", value=current_configs.get("NJ", {}).get("agency", ""), placeholder="A & L Insurance Agency, LLC", key="nj_agency")
#             nj_producer = st.text_input("Producer Name", value=current_configs.get("NJ", {}).get("producer", ""), placeholder="A & L Insurance Agency, LLC", key="nj_producer")
            
#             if st.form_submit_button("Save NJ", use_container_width=True):
#                 try:
#                     existing_lines = []
#                     if env_path.exists():
#                         with open(env_path, 'r') as f:
#                             existing_lines = [line for line in f.readlines() 
#                                             if not line.startswith('PR_NJ_')]
                    
#                     with open(env_path, 'w') as f:
#                         for line in existing_lines:
#                             f.write(line)
#                         if nj_branch:
#                             f.write(f"PR_NJ_BRANCH={nj_branch}\n")
#                         if nj_agency:
#                             f.write(f"PR_NJ_AGENCY={nj_agency}\n")
#                         if nj_producer:
#                             f.write(f"PR_NJ_PRODUCER={nj_producer}\n")
                    
#                     st.success("NJ saved!")
#                     time.sleep(1)
#                     st.rerun()
#                 except Exception as e:
#                     st.error(f"Error: {e}")
    
#     # New York
#     with st.sidebar.expander("New York (NY)"):
#         with st.form("ny_agency_form"):
#             ny_branch = st.text_input("Branch Name", value=current_configs.get("NY", {}).get("branch", ""), placeholder="Palisades", key="ny_branch")
#             ny_agency = st.text_input("Agency Name", value=current_configs.get("NY", {}).get("agency", ""), placeholder="A.H. Meyers and Company", key="ny_agency")
#             ny_producer = st.text_input("Producer Name", value=current_configs.get("NY", {}).get("producer", ""), placeholder="A.H. Meyers and Company", key="ny_producer")
            
#             if st.form_submit_button("Save NY", use_container_width=True):
#                 try:
#                     existing_lines = []
#                     if env_path.exists():
#                         with open(env_path, 'r') as f:
#                             existing_lines = [line for line in f.readlines() 
#                                             if not line.startswith('PR_NY_')]
                    
#                     with open(env_path, 'w') as f:
#                         for line in existing_lines:
#                             f.write(line)
#                         if ny_branch:
#                             f.write(f"PR_NY_BRANCH={ny_branch}\n")
#                         if ny_agency:
#                             f.write(f"PR_NY_AGENCY={ny_agency}\n")
#                         if ny_producer:
#                             f.write(f"PR_NY_PRODUCER={ny_producer}\n")
                    
#                     st.success("NY saved!")
#                     time.sleep(1)
#                     st.rerun()
#                 except Exception as e:
#                     st.error(f"Error: {e}")
    
#     # Pennsylvania
#     with st.sidebar.expander("Pennsylvania (PA)"):
#         with st.form("pa_agency_form"):
#             pa_branch = st.text_input("Branch Name", value=current_configs.get("PA", {}).get("branch", ""), placeholder="Palisades", key="pa_branch")
#             pa_agency = st.text_input("Agency Name", value=current_configs.get("PA", {}).get("agency", ""), placeholder="A.H. Meyers and Company", key="pa_agency")
#             pa_producer = st.text_input("Producer Name", value=current_configs.get("PA", {}).get("producer", ""), placeholder="A.H. Meyers and Company", key="pa_producer")
            
#             if st.form_submit_button("Save PA", use_container_width=True):
#                 try:
#                     existing_lines = []
#                     if env_path.exists():
#                         with open(env_path, 'r') as f:
#                             existing_lines = [line for line in f.readlines() 
#                                             if not line.startswith('PR_PA_')]
                    
#                     with open(env_path, 'w') as f:
#                         for line in existing_lines:
#                             f.write(line)
#                         if pa_branch:
#                             f.write(f"PR_PA_BRANCH={pa_branch}\n")
#                         if pa_agency:
#                             f.write(f"PR_PA_AGENCY={pa_agency}\n")
#                         if pa_producer:
#                             f.write(f"PR_PA_PRODUCER={pa_producer}\n")
                    
#                     st.success("PA saved!")
#                     time.sleep(1)
#                     st.rerun()
#                 except Exception as e:
#                     st.error(f"Error: {e}")


# # ========== END AGENCY CONFIGURATION ==========
# # Create temp folder for Streamlit runs
# TEMP_DIR = Path("streamlit_temp")
# TEMP_DIR.mkdir(exist_ok=True)

# # Auto-cleanup old temp files (keep last 20 runs)
# try:
#     temp_files = sorted(TEMP_DIR.glob("output_*.csv"), key=lambda x: x.stat().st_mtime, reverse=True)
#     for i, temp_file in enumerate(temp_files):
#         if i >= 20:
#             try:
#                 input_file = temp_file.parent / temp_file.name.replace("output_", "input_")
#                 if input_file.exists():
#                     input_file.unlink()
#                 temp_file.unlink()
#             except:
#                 pass
# except:
#     pass

# # NEW: MODE SELECTION WITH 4TH HELP OPTION
# st.header("Select Processing Mode")
# mode = st.radio(
#     "How do you want to process quotes?",
#     [
#         "Multi-State (All states in one file)",
#         "Single State (One state at a time)",
#         "Multiple States (Separate files for each state)",
#         "Help & Documentation"
#     ],
#     horizontal=True
# )

# st.markdown("---")

# # State batch file mapping
# STATE_BATCH_FILES = {
#     "Connecticut (CT)": "batch_full_ct.py",
#     "Massachusetts (MA)": "batch_full_ma.py",
#     "New Hampshire (NH)": "batch_full_nh.py",
#     "New Jersey (NJ)": "batch_full_nj.py",
#     "New York (NY)": "batch_full_ny.py",
#     "Pennsylvania (PA)": "batch_full_pa.py",
# }

# # ========== OPTIMIZED RUN AUTOMATION FUNCTION ==========
# def run_automation(state_name, batch_file, input_file, output_file, df, headless, base_url):
#     # Progress checklist
#     progress_container = st.container()
#     with progress_container:
#         st.markdown(f"### Progress for {state_name}")
        
#         checklist = {
#             "setup": st.empty(),
#             "login": st.empty(),
#             "processing": st.empty(),
#             "complete": st.empty()
#         }
        
#         checklist["setup"].markdown("**Setup** - Preparing files...")
        
#     # Scrollable logs
#     with st.expander("View Terminal Logs", expanded=False):
#         log_output = st.empty()
    
#     # Progress bar
#     progress_bar = st.progress(0)
#     progress_text = st.empty()
    
#     # OPTIMIZED: Non-buffered subprocess
#     env = os.environ.copy()
#     env['PYTHONIOENCODING'] = 'utf-8'
#     env['PYTHONUNBUFFERED'] = '1'
#     env['PR_BASE_URL'] = base_url
    
#     cmd = [sys.executable, "-u", batch_file, input_file, output_file]
#     if headless:
#         cmd.append("--headless")
#     if quotes_only:
#         cmd.append("--quotes-only")
    
#     process = subprocess.Popen(
#         cmd,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.STDOUT,
#         text=True,
#         bufsize=1,
#         encoding='utf-8',
#         errors='replace',
#         cwd=os.getcwd(),
#         env=env,
#         universal_newlines=True
#     )
    
#     st.session_state.process = process
    
#     # Track progress
#     output_lines = []
#     current_row = 0
#     total_rows = len(df)
#     last_update_time = time.time()
#     start_time = time.time()
#     max_time_per_record = 600
    
#     try:
#         # OPTIMIZED: Less frequent updates
#         while True:
#             line = process.stdout.readline()
#             if not line and process.poll() is not None:
#                 break
            
#             if line:
#                 line = line.rstrip()
#                 output_lines.append(line)
                
#                 # Update every 2 seconds OR every 15 lines
#                 current_time = time.time()
#                 if current_time - last_update_time > 2.0 or len(output_lines) % 15 == 0:
#                     # FIXED: text_area with unique key
#                     log_output.text_area(
#                         "Terminal Output",
#                         '\n'.join(output_lines[-50:]),
#                         height=400,
#                         key=f"log_{len(output_lines)}"
#                     )
#                     last_update_time = current_time
                
#                 # Immediate checklist updates
#                 if "Login successful" in line:
#                     checklist["setup"].markdown("**Setup** - Files ready")
#                     checklist["login"].markdown("**Login** - Logged into Plymouth Rock")
                
#                 # Real-time row tracking
#                 if "===== ROW" in line:
#                     try:
#                         current_row = int(line.split("ROW")[1].split("=====")[0].strip())
#                         progress = current_row / total_rows
#                         progress_bar.progress(progress)
#                         progress_text.text(f"Processing row {current_row} of {total_rows}")
#                         checklist["processing"].markdown(f"**Processing** - Row {current_row} of {total_rows}")
#                     except:
#                         pass
                
#                 # Success feedback
#                 if "[SUCCESS]" in line or "Quote Number:" in line or "quote_number" in line.lower():
#                     try:
#                         if "Quote" in line or "quote" in line:
#                             st.success(f"Row {current_row}: Quote generated")
#                     except:
#                         pass
                
#                 # Error feedback
#                 if "[ERROR]" in line:
#                     if "DTQ" in line or "decline" in line.lower() or "CRN" in line:
#                         st.warning(f"Row {current_row}: Declined by system")
#                     elif "Attempt 2" in line or "failed" in line.lower():
#                         st.error(f"Row {current_row}: Failed")
            
#             # Timeout check
#             if time.time() - start_time > (max_time_per_record * total_rows):
#                 st.error("Process timeout - killing automation")
#                 process.kill()
#                 break
    
#     except Exception as e:
#         st.error(f"Error during processing: {e}")
    
#     # Wait for completion
#     return_code = process.wait()
#     st.session_state.process = None
#     st.session_state.running = False
    
#     # FIXED: Show final logs with unique key
#     log_output.text_area(
#         "Complete Terminal Output",
#         '\n'.join(output_lines[-50:]),
#         height=400,
#         key=f"complete_{len(output_lines)}"
#     )
    
#     # Update final status
#     progress_bar.progress(1.0)
#     checklist["processing"].markdown(f"**Processing** - Completed {total_rows} rows")
    
#     # Show results
#     if return_code == 0 and os.path.exists(output_file):
#         checklist["complete"].markdown("**Complete** - Results ready!")
        
#         results_df = pd.read_csv(output_file)
        
#         st.markdown("---")
#         st.subheader("Results Summary")
        
#         col1, col2, col3, col4 = st.columns(4)
#         total = len(results_df)
#         success = len(results_df[results_df['status'] == 'ok'])
#         failed = total - success
        
#         col1.metric("Total", total)
#         col2.metric("Success", success, delta=f"{(success/total*100):.0f}%")
#         col3.metric("Failed", failed)
#         col4.metric("Success Rate", f"{(success/total*100):.0f}%")
        
#         st.dataframe(results_df, use_container_width=True)
        
#         col1, col2 = st.columns(2)
#         with col1:
#             st.download_button(
#                 "Download Results",
#                 data=results_df.to_csv(index=False),
#                 file_name=f"plymouth_rock_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
#                 mime="text/csv",
#                 use_container_width=True,
#                 key=f"dl_{output_file}"
#             )
#         with col2:
#             if st.button("Save to Main Folder", use_container_width=True, key=f"sv_{output_file}"):
#                 saved_file = f"saved_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
#                 results_df.to_csv(saved_file, index=False)
#                 st.success(f"Saved as {saved_file}")
        
#         return {"success": success, "failed": failed, "output": output_file}
#     else:
#         checklist["complete"].markdown("**Complete** - Processing failed")
#         st.error(f"Processing failed (return code: {return_code})")
        
#         # FIXED: Error logs with unique key
#         with st.expander("Error Details", expanded=True):
#             st.text_area(
#                 "Error Log",
#                 '\n'.join(output_lines[-50:]),
#                 height=400,
#                 key=f"error_{len(output_lines)}"
#             )
        
#         return {"success": 0, "failed": total_rows, "output": None}

# # ========== END OPTIMIZED RUN AUTOMATION ==========

# # NEW: HELP & DOCUMENTATION MODE
# if "Help" in mode:
#     st.subheader("Complete User Guide")
    
#     st.markdown("---")
    
#     # Getting Started Section
#     st.header("Getting Started")
    
#     st.markdown("""
#     **Step 1: Setup Credentials**
    
#     Navigate to the sidebar and click on "Update Credentials". Enter your Plymouth Rock AgentWeb username and password, then click "Save Credentials". Your credentials will be securely stored in a .env file.
    
#     **Step 2: Prepare Your CSV File**
    
#     Create a CSV file with the required columns listed below. Ensure your data is clean and properly formatted.
    
#     **Step 3: Select Processing Mode**
    
#     Choose one of the three processing modes based on your needs (described in detail below).
    
#     **Step 4: Upload and Process**
    
#     Upload your CSV file(s), enable headless mode if desired, and click "START PROCESSING". Monitor the real-time progress on screen.
#     """)
    
#     st.markdown("---")
    
#     # CSV Format Guide
#     st.header("CSV Format Requirements")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.subheader("Required Columns")
#         st.markdown("""
#         - **first_name** - Applicant's first name
#         - **last_name** - Applicant's last name  
#         - **dob** - Date of birth in MM/DD/YYYY format
#         - **address** - Complete street address with city and state
#         - **state** - Two-letter state code (CT, MA, NH, NJ, NY, PA) - Required for Multi-State mode only
#         """)
    
#     with col2:
#         st.subheader("Optional Columns")
#         st.markdown("""
#         - **phone** - Phone number (defaults to 555-555-5555 if not provided)
#         - **effective_date** - Policy effective date in MM/DD/YYYY format (defaults to today if not provided)
#         - **line_of_business** - Policy type: HO3 (Homeowners), HO4 (Renters), HO6 (Condo-Owners)
#         """)
    
#     st.subheader("Example CSV Format")
#     st.code("""first_name,last_name,dob,address,state,line_of_business
# John,Smith,01/15/1980,123 Main St Boston MA 02101,MA,HO3
# Jane,Doe,05/22/1975,456 Oak Ave Hartford CT 06101,CT,HO4
# Robert,Johnson,03/10/1985,789 Pine Rd Trenton NJ 08601,NJ,HO6""", language=None)
    
#     st.markdown("---")
    
#     # Processing Modes
#     st.header("Processing Modes Explained")
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         st.subheader("Multi-State")
#         st.markdown("""
#         **When to use:**
        
#         When you have applicants from multiple states in a single batch.
        
#         **How it works:**
        
#         Upload ONE CSV file that includes a 'state' column. The system automatically routes each applicant to the correct state processor.
        
#         **Best for:**
        
#         Mixed batches with applicants from different states combined in one file.
#         """)
    
#     with col2:
#         st.subheader("Single State")
#         st.markdown("""
#         **When to use:**
        
#         When all applicants are from the same state.
        
#         **How it works:**
        
#         Select the state from the dropdown, then upload a CSV file without a 'state' column. All records will be processed for that state.
        
#         **Best for:**
        
#         State-specific batches or when you want explicit control over which state to process.
#         """)
    
#     with col3:
#         st.subheader("Multiple States")
#         st.markdown("""
#         **When to use:**
        
#         When you have large batches already organized by state.
        
#         **How it works:**
        
#         Select 2-6 states, then upload a separate CSV file for each state. The system processes each state sequentially.
        
#         **Best for:**
        
#         Large batches where you've already separated applicants by state into different files.
#         """)
    
#     st.markdown("---")
    
#     # Understanding Results
#     st.header("Understanding Results")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.subheader("Status Codes")
#         st.markdown("""
#         **ok** - Quote and policy generated successfully. Both quote number and policy number will be populated.
        
#         **dtq_error** - Declined to quote. The applicant did not qualify due to credit, risk, or underwriting factors. This is a normal business outcome.
        
#         **error** - Technical processing error. The automation encountered an issue. Check the error_message column for details.
#         """)
    
#     with col2:
#         st.subheader("Output Columns")
#         st.markdown("""
#         The output CSV will contain all your input columns plus:
        
#         - **quote_number** - Generated quote number (e.g., MAHQ...)
#         - **policy_number** - Generated policy number (e.g., MAH...)
#         - **status** - Processing status (ok, dtq_error, or error)
#         - **error_message** - Error details if status is not 'ok'
#         """)
    
#     st.markdown("---")
    
#     # Troubleshooting
#     st.header("Troubleshooting Guide")
    
#     st.subheader("Login Failed or Missing Credentials")
#     st.markdown("""
#     - Verify credentials are saved correctly in the sidebar
#     - Confirm your username and password with IT support
#     - Ensure the .env file exists in the application folder
#     - Try logging into Plymouth Rock AgentWeb manually to verify credentials work
#     """)
    
#     st.subheader("DTQ or Decline Errors")
#     st.markdown("""
#     - This is normal business behavior - some applicants do not qualify for quotes
#     - Declined applicants typically have credit issues, claims history, or risk factors
#     - Verify the applicant data (address, DOB) is correct - data errors can cause declines
#     - Check with underwriting if you believe an applicant should have qualified
#     """)
    
#     st.subheader("Processing Stuck or Frozen")
#     st.markdown("""
#     - Click the "Reset App" button in the sidebar Controls section
#     - Check your internet connection
#     - Verify the Plymouth Rock AgentWeb site is accessible
#     - Try reducing your batch size to fewer records
#     """)
    
#     st.subheader("Page Not Responding")
#     st.markdown("""
#     - Close other browser tabs to free up memory
#     - Reduce your CSV file size to under 50 records
#     - Enable headless mode for better performance
#     - Restart your browser if issues persist
#     """)
    
#     st.subheader("Wrong Agency or Producer Selected")
#     st.markdown("""
#     - This is a known timing issue with dropdown loading
#     - The quotes and policies generated are still valid
#     - Agency and producer information can be corrected manually in Plymouth Rock AgentWeb
#     - Contact the BA team if this occurs frequently
#     """)
    
#     st.markdown("---")
    
#     # Performance Tips
#     st.header("Performance & Best Practices")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.subheader("Batch Size Recommendations")
#         st.markdown("""
#         **Recommended batch size:** 10-25 records
        
#         **Maximum batch size:** 50 records
        
#         **For larger volumes:** Split into multiple CSV files and process separately. This prevents browser memory issues and provides better error recovery.
#         """)
        
#         st.subheader("Timing Expectations")
#         st.markdown("""
#         **Average processing time:** 45-60 seconds per record
        
#         **10 records:** Approximately 8-10 minutes  
#         **25 records:** Approximately 20-25 minutes  
#         **50 records:** Approximately 40-50 minutes
        
#         Processing time varies based on system load and network speed.
#         """)
    
#     with col2:
#         st.subheader("Best Practices")
#         st.markdown("""
#         **Run during off-peak hours** - Early morning (8am-10am) or mid-afternoon (2pm-4pm) typically have better system performance.
        
#         **Use headless mode** - Enables faster processing by running browser in background without UI rendering.
        
#         **Keep browser tab active** - Do not switch away from the tab or minimize the browser during processing.
        
#         **Avoid refreshing** - Do not refresh the page or click the back button while processing is in progress.
        
#         **Stable internet connection** - Ensure you have a reliable internet connection throughout the batch processing.
#         """)
    
#     st.markdown("---")
    
#     # File Management
#     st.header("File Management")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.subheader("Temp Folder System")
#         st.markdown("""
#         The application automatically saves all processing runs to a temporary folder (`streamlit_temp/`).
        
#         **Auto-cleanup:** Only the last 20 runs are kept. Older runs are automatically deleted to save disk space.
        
#         **Location:** All temporary files are stored in `streamlit_temp/` in the application directory.
#         """)
    
#     with col2:
#         st.subheader("Saving Files")
#         st.markdown("""
#         **Download Button:** Downloads the results CSV to your browser's Downloads folder. These files are separate from the temp folder.
        
#         **Save to Main Folder:** Permanently saves the file to the main application directory with a `saved_` prefix. These files are never auto-deleted.
        
#         **Previous Runs:** Access any of your last 20 runs or any permanently saved files from the Previous Runs section.
#         """)
    
#     st.markdown("---")
    
#     # Advanced Features
#     st.header("Advanced Features")
    
#     st.subheader("Custom Effective Date")
#     st.markdown("""
#     Add an `effective_date` column to your CSV file with dates in MM/DD/YYYY format. This allows you to specify when the policy should take effect. If not provided, the system defaults to today's date.
#     """)
    
#     st.subheader("Custom Phone Numbers")
#     st.markdown("""
#     Add a `phone` column to your CSV file. Accepted formats include XXX-XXX-XXXX or XXXXXXXXXX. If not provided, the system uses a default value of 555-555-5555.
#     """)
    
#     st.subheader("Line of Business")
#     st.markdown("""
#     Add a `line_of_business` column to specify policy type:
#     - **HO3** - Homeowners (default if not specified)
#     - **HO4** - Renters
#     - **HO6** - Condo-Owners
#     """)
    
#     st.subheader("Reset App Function")
#     st.markdown("""
#     The Reset App button (located in sidebar Controls) immediately stops any running processes, clears all session data, and resets the application to its initial state. Use this if the page becomes unresponsive or you need to cancel processing.
#     """)
    
#     st.markdown("---")
    
#     # Support
#     st.header("Support & Contact")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.markdown("""
#         **Technical Support**
        
#         For technical issues, questions, or assistance:
        
#         **Email:** sganesh@plymouthrock.com  
#         **Team:** Business Analyst (BA) Team
        
#         **Response Time:** Typically within 1 business day
#         """)
    
#     with col2:
#         st.markdown("""
#         **Application Information**
        
#         **Version:** 2.0  
#         **Last Updated:** December 2025  
#         **Maintained by:** IT Co-op Team
        
#         **Supported States:** CT, MA, NH, NJ, NY, PA
#         """)

# # MULTI-STATE MODE
# elif "Multi-State" in mode:
#     st.subheader("Multi-State Processing")
#     st.info("Upload ONE CSV with a 'state' column (CT, MA, NH, NJ, NY, PA)")
    
#     uploaded_file = st.file_uploader("Upload CSV", type=['csv'], key="multistate")
    
#     if uploaded_file:
#         df = pd.read_csv(uploaded_file)
        
#         # Validate
#         required = ['first_name', 'last_name', 'dob', 'address', 'state']
#         missing = [col for col in required if col not in df.columns]
        
#         if missing:
#             st.error(f"Missing columns: {', '.join(missing)}")
#         else:
#             # Show breakdown by state
#             col1, col2 = st.columns(2)
#             with col1:
#                 st.metric("Total Records", len(df))
#                 state_counts = df['state'].value_counts()
#                 st.dataframe(state_counts, use_container_width=True)
            
#             with col2:
#                 with st.expander("Preview Data"):
#                     st.dataframe(df.head(10))
            
#             batch_file = "batch_multistate.py"

# # SINGLE STATE MODE
# elif "Single State" in mode:
#     st.subheader("Single State Processing")
    
#     col1, col2 = st.columns(2)
#     with col1:
#         selected_state = st.selectbox("Select State:", list(STATE_BATCH_FILES.keys()))
#     with col2:
#         st.info(f"Will use: `{STATE_BATCH_FILES[selected_state]}`")
    
#     uploaded_file = st.file_uploader(f"Upload CSV for {selected_state}", type=['csv'], key="single")
    
#     if uploaded_file:
#         df = pd.read_csv(uploaded_file)
        
#         required = ['first_name', 'last_name', 'dob', 'address']
#         missing = [col for col in required if col not in df.columns]
        
#         if missing:
#             st.error(f"Missing columns: {', '.join(missing)}")
#         else:
#             col1, col2 = st.columns(2)
#             with col1:
#                 st.metric("Total Records", len(df))
#             with col2:
#                 with st.expander("Preview Data"):
#                     st.dataframe(df.head(10))
            
#             batch_file = STATE_BATCH_FILES[selected_state]

# # MULTIPLE STATES MODE
# elif "Multiple States" in mode:
#     st.subheader("Multiple States Processing")
#     st.info("Upload separate CSV files for each state you want to process")
    
#     selected_states = st.multiselect(
#         "Select states to process:",
#         list(STATE_BATCH_FILES.keys()),
#         default=[]
#     )
    
#     if selected_states:
#         uploaded_files = {}
#         for state in selected_states:
#             uploaded_files[state] = st.file_uploader(
#                 f"CSV for {state}:",
#                 type=['csv'],
#                 key=f"multi_{state}"
#             )
        
#         # Check if all uploaded
#         all_uploaded = all(uploaded_files.values())
        
#         if all_uploaded:
#             # Calculate total and reset file pointers
#             total_records = 0
#             for file_obj in uploaded_files.values():
#                 total_records += len(pd.read_csv(file_obj))
#                 file_obj.seek(0)
            
#             st.success(f"All {len(selected_states)} files uploaded! Total: {total_records} records")
            
#             # Preview for Multiple States
#             with st.expander("Preview Data"):
#                 for state, file_obj in uploaded_files.items():
#                     st.markdown(f"**{state}:**")
#                     file_obj.seek(0)
#                     preview_df = pd.read_csv(file_obj)
#                     st.dataframe(preview_df.head(5))
#                     file_obj.seek(0)
            
#             batch_file = "multiple"

# # PROCESSING SECTION
# if ('uploaded_file' in locals() and uploaded_file and 'batch_file' in locals()) or ('batch_file' in locals() and batch_file == "multiple"):
#     st.markdown("---")
    
#     # Row 1 - Model Selection
#     server_url = st.selectbox(
#         "🌐 Select Plymouth Rock Model:",
#         [
#             "Model 1 (agentweb1mod)",
#             "Model 2 (agentweb2mod)",
#             "Model 3 (agentweb3mod)"
#         ],
#         index=0
#     )
    
#     # Map selection to base URL
#     url_mapping = {
#         "Model 1 (agentweb1mod)": "https://agentweb1mod.plymouthrock.com",
#         "Model 2 (agentweb2mod)": "https://agentweb2mod.plymouthrock.com",
#         "Model 3 (agentweb3mod)": "https://agentweb3mod.plymouthrock.com"
#     }
#     base_url = url_mapping[server_url]
    
#     st.markdown("---")
    
#     # Row 2 - Processing Options
#     col1, col2 = st.columns(2)
#     with col1:
#         headless = st.checkbox("⚡ Headless mode (run in background)", value=True)
#     with col2:
#         quotes_only = st.checkbox(
#             "📋 Quote Numbers Only", 
#             value=False,
#             help="Check to get ONLY quote numbers (skip policy issuance)"
#         )
    
#     if quotes_only:
#         st.info("📋 Mode: Quote Numbers Only")
#     else:
#         st.success("📋 Mode: Full Processing (Quote + Policy)")
    
#     # FIXED: Only START button
#     start_btn = st.button(
#         "START PROCESSING", 
#         type="primary", 
#         use_container_width=True, 
#         disabled=st.session_state.running
#     )
    
#     if st.session_state.running:
#         st.info("Processing in progress... Use 'Reset App' in sidebar if needed.")
    
#     if start_btn:
#         st.session_state.running = True
        
#         # Save files to temp folder
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
#         if batch_file == "multiple":
#             # Multiple states - run each separately
#             st.info(f"Processing {len(selected_states)} states sequentially...")
            
#             all_results = []
            
#             for state in selected_states:
#                 state_abbr = state.split("(")[1].split(")")[0]
#                 input_file = str(TEMP_DIR / f"input_{state_abbr}_{timestamp}.csv")
#                 output_file = str(TEMP_DIR / f"output_{state_abbr}_{timestamp}.csv")
                
#                 # Reset and read file
#                 uploaded_files[state].seek(0)
#                 state_df = pd.read_csv(uploaded_files[state])
#                 state_df.to_csv(input_file, index=False)
                
#                 # Process this state
#                 st.subheader(f"Processing {state}")
#                 result = run_automation(state, STATE_BATCH_FILES[state], input_file, output_file, state_df, headless, base_url)
#                 all_results.append(result)
            
#             st.success(f"Completed all {len(selected_states)} states!")
            
#         else:
#             # Single or multi-state file
#             input_file = str(TEMP_DIR / f"input_{timestamp}.csv")
#             output_file = str(TEMP_DIR / f"output_{timestamp}.csv")
            
#             df.to_csv(input_file, index=False)
            
#             state_name = "Multi-State" if batch_file == "batch_multistate.py" else selected_state
#             run_automation(state_name, batch_file, input_file, output_file, df, headless, base_url)
        
#         # Reset running state
#         st.session_state.running = False

# # Previous results section (only show if not in Help mode)
# if "Help" not in mode:
#     st.markdown("---")
#     st.subheader("Previous Runs")

#     # Get files from BOTH temp folder AND main directory
#     all_files = []

#     # Get temp files
#     try:
#         temp_files = list(TEMP_DIR.glob("output_*.csv"))
#         all_files.extend([(f, "Temp") for f in temp_files])
#     except:
#         pass

#     # Get ALL output files from main directory
#     try:
#         main_files = [Path(f) for f in os.listdir('.') if (f.startswith(('saved_', 'output_')) and f.endswith('.csv'))]
#         all_files.extend([(f, "Main") for f in main_files])
#     except:
#         pass

#     # Sort by modification time
#     all_files.sort(key=lambda x: x[0].stat().st_mtime, reverse=True)

#     # Show counts
#     temp_count = sum(1 for _, tag in all_files if tag == "Temp")
#     main_count = sum(1 for _, tag in all_files if tag == "Main")
#     st.caption(f"Temp folder: {temp_count} runs | Main folder: {main_count} files")

#     if all_files:
#         # Format for display
#         file_labels = [f"{f.name} ({f.stat().st_size / 1024:.1f} KB) [{tag}]" for f, tag in all_files]
        
#         selected_idx = st.selectbox("Select run:", range(len(all_files)), format_func=lambda i: file_labels[i])
#         selected_file, file_tag = all_files[selected_idx]
        
#         if st.button("Load Selected Run"):
#             prev_df = pd.read_csv(selected_file)
            
#             col1, col2, col3 = st.columns(3)
#             success = len(prev_df[prev_df['status'] == 'ok'])
#             failed = len(prev_df[prev_df['status'] != 'ok'])
            
#             col1.metric("Total", len(prev_df))
#             col2.metric("Success", success)
#             col3.metric("Failed", failed)
            
#             st.dataframe(prev_df, use_container_width=True)
            
#             # Download options
#             col1, col2 = st.columns(2)
#             with col1:
#                 st.download_button(
#                     "Download",
#                     data=prev_df.to_csv(index=False),
#                     file_name=f"plymouth_rock_{selected_file.stem}.csv",
#                     mime="text/csv",
#                     use_container_width=True,
#                     key=f"dl_prev_{selected_file.stem}"
#                 )
#             with col2:
#                 if file_tag == "Temp":
#                     if st.button("Save to Main Folder", use_container_width=True, key=f"sv_prev_{selected_file.stem}"):
#                         saved_name = f"saved_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
#                         prev_df.to_csv(saved_name, index=False)
#                         st.success(f"Saved as {saved_name}")
#                         st.rerun()
#     else:
#         st.info("No previous runs found")

# # ========== SIDEBAR ==========
# with st.sidebar:
#     # Credentials manager
#     manage_credentials()
    
#     # ✅ NEW: Agency Configuration
#     manage_agency_config()
    
#     st.markdown("---")
#     st.header("Quick Guide")
    
#     st.markdown("""
#     ### Multi-State
#     - One CSV with 'state' column
#     - Processes all states together
#     - Best for mixed state batches
    
#     ### Single State
#     - One CSV for one state
#     - Choose which state
#     - Best for state-specific batches
    
#     ### Multiple States
#     - Separate CSV for each state
#     - Upload 2-6 files
#     - Processes sequentially
    
#     ---
    
#     ### Timing
#     - ~45-60 seconds per record
#     - Real-time progress tracking
#     - Headless mode recommended
    
#     ---
    
#     ### File Management
#     - Last 20 runs kept in temp folder
#     - Download → Goes to Downloads
#     - Save → Keeps permanently
#     - Previous Runs → All files
#     """)
    
#     st.markdown("---")
#     st.caption(f"Python: {sys.executable[:40]}...")
    
#     # Show temp folder info
#     try:
#         temp_count = len(list(TEMP_DIR.glob("output_*.csv")))
#         if temp_count > 0:
#             temp_size = sum(f.stat().st_size for f in TEMP_DIR.glob("output_*.csv"))
#             st.caption(f"Temp: {temp_count} files, {temp_size / 1024:.1f} KB")
#     except:
#         pass
    
#     # Reset button
#     st.markdown("---")
#     st.subheader("Controls")
    
#     if st.button("Reset App", use_container_width=True):
#         if st.session_state.process:
#             try:
#                 if sys.platform == "win32":
#                     subprocess.run(['taskkill', '/F', '/T', '/PID', str(st.session_state.process.pid)], 
#                                    capture_output=True, timeout=5)
#                 else:
#                     st.session_state.process.kill()
#             except:
#                 pass
        
#         st.session_state.running = False
#         st.session_state.process = None
#         st.success("App reset!")
#         time.sleep(0.5)
#         st.rerun()
    
#     if st.session_state.running:
#         st.warning("Process is running")


# app.py - Main Streamlit interface for Plymouth Rock Quote Automation
# This app provides a user-friendly way to batch process insurance quotes across 6 states
# Supports 3 modes: Multi-State (mixed CSV), Single State, and Multiple States (separate CSVs)

import streamlit as st
import subprocess
import pandas as pd
import os
import time
from datetime import datetime
from pathlib import Path
import sys

# Configure the Streamlit page with title and icon
st.set_page_config(
    page_title="Plymouth Rock Automation",
    page_icon="🪨",
    layout="wide"
)

# Initialize session state variables to track automation process
# These persist across Streamlit reruns
if 'process' not in st.session_state:
    st.session_state.process = None  # Stores the subprocess object
if 'running' not in st.session_state:
    st.session_state.running = False  # Tracks if automation is currently running

st.title("Plymouth Rock Quote Automation")

# Display Plymouth Rock logo if it exists in the directory
if Path("plymouth_rock_logo.png").exists():
    st.image("plymouth_rock_logo.png", width=300)
    
st.markdown("---")

# ========== CREDENTIALS MANAGEMENT ==========
# This section handles secure storage and retrieval of Plymouth Rock login credentials
# Credentials are stored in a .env file and never displayed in plain text

def manage_credentials():
    """
    Display and manage Plymouth Rock AgentWeb credentials in the sidebar.
    Reads from and writes to .env file for persistent storage.
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("Plymouth Rock Login")
    
    # Check if .env file exists in the application directory
    env_path = Path(".env")
    
    # Try to read existing credentials from .env
    current_username = ""
    current_password = ""
    
    if env_path.exists():
        try:
            from dotenv import dotenv_values
            env_vars = dotenv_values(".env")
            current_username = env_vars.get("PR_USERNAME", "")
            current_password = env_vars.get("PR_PASSWORD", "")
        except:
            pass  # If reading fails, we'll just use empty strings
    
    # Show the user whether credentials are already saved
    if current_username:
        st.sidebar.success(f"Logged in as: **{current_username}**")
    else:
        st.sidebar.warning("No credentials saved")
    
    # Expandable section for updating credentials
    # Collapsed by default if credentials exist, expanded if they don't
    with st.sidebar.expander("Update Credentials", expanded=not current_username):
        with st.form("credentials_form"):
            st.markdown("**Enter Plymouth Rock credentials:**")
            
            # Username input - pre-fill with current value if it exists
            new_username = st.text_input(
                "Agent Username",
                value=current_username,
                help="Your Plymouth Rock AgentWeb username"
            )
            
            # Password input - always blank for security (never show saved password)
            new_password = st.text_input(
                "Agent Password",
                type="password",
                help="Your Plymouth Rock AgentWeb password"
            )
            
            # Single save button to update credentials
            save_button = st.form_submit_button("Save Credentials", use_container_width=True, type="primary")
            
            if save_button:
                # Validate that both fields have values
                if new_username and new_password:
                    try:
                        # Read existing .env content to preserve other variables (like agency configs)
                        existing_lines = []
                        if env_path.exists():
                            with open(env_path, 'r') as f:
                                # Keep all lines except the ones we're about to update
                                existing_lines = [line for line in f.readlines() 
                                                if not line.startswith('PR_USERNAME=') 
                                                and not line.startswith('PR_PASSWORD=')]
                        
                        # Write updated credentials back to .env
                        with open(env_path, 'w') as f:
                            # Write other existing env vars first
                            for line in existing_lines:
                                f.write(line)
                            # Write the new credentials
                            f.write(f"PR_USERNAME={new_username}\n")
                            f.write(f"PR_PASSWORD={new_password}\n")
                        
                        # Show success message and refresh the page
                        st.success(f"Credentials saved for **{new_username}**!")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error saving credentials: {e}")
                else:
                    st.warning("Please enter both username and password")

# ========== END CREDENTIALS MANAGEMENT ==========


# ========== AGENCY CONFIGURATION MANAGEMENT ==========
# This section allows users to customize agency/branch/producer selections for each state
# Different agencies may be used depending on the state being quoted
# If not configured, the automation uses default values from the batch scripts

def manage_agency_config():
    """
    Display and manage state-specific agency configurations in the sidebar.
    Each state can have custom Branch, Agency, and Producer selections.
    Stored in .env file as PR_[STATE]_BRANCH, PR_[STATE]_AGENCY, PR_[STATE]_PRODUCER
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("Agency Configuration")
    
    env_path = Path(".env")
    
    # Read current configs from .env if they exist
    current_configs = {}
    if env_path.exists():
        try:
            from dotenv import dotenv_values
            env_vars = dotenv_values(".env")
            
            # Load configs for all 6 supported states
            for state_abbr in ["CT", "MA", "NH", "NJ", "NY", "PA"]:
                current_configs[state_abbr] = {
                    "branch": env_vars.get(f"PR_{state_abbr}_BRANCH", ""),
                    "agency": env_vars.get(f"PR_{state_abbr}_AGENCY", ""),
                    "producer": env_vars.get(f"PR_{state_abbr}_PRODUCER", "")
                }
        except:
            pass  # If reading fails, configs will just be empty
    
    # Show summary of how many states are configured
    configured_count = sum(1 for cfg in current_configs.values() if cfg.get("branch") or cfg.get("agency"))
    if configured_count > 0:
        st.sidebar.info(f"Configured: {configured_count}/6 states")
    else:
        st.sidebar.warning("No custom configs - using defaults")
    
    # Connecticut configuration
    with st.sidebar.expander("Connecticut (CT)"):
        with st.form("ct_agency_form"):
            ct_branch = st.text_input("Branch Name", value=current_configs.get("CT", {}).get("branch", ""), placeholder="BHIC0035 | New England", key="ct_branch")
            ct_agency = st.text_input("Agency Name", value=current_configs.get("CT", {}).get("agency", ""), placeholder="Columbia", key="ct_agency")
            ct_producer = st.text_input("Producer Name", value=current_configs.get("CT", {}).get("producer", ""), placeholder="Columbia Insurance Agency", key="ct_producer")
            
            if st.form_submit_button("Save CT", use_container_width=True):
                try:
                    # Remove old CT configs while preserving everything else
                    existing_lines = []
                    if env_path.exists():
                        with open(env_path, 'r') as f:
                            existing_lines = [line for line in f.readlines() 
                                            if not line.startswith('PR_CT_')]
                    
                    # Write back with new CT configs
                    with open(env_path, 'w') as f:
                        for line in existing_lines:
                            f.write(line)
                        if ct_branch:
                            f.write(f"PR_CT_BRANCH={ct_branch}\n")
                        if ct_agency:
                            f.write(f"PR_CT_AGENCY={ct_agency}\n")
                        if ct_producer:
                            f.write(f"PR_CT_PRODUCER={ct_producer}\n")
                    
                    st.success("CT saved!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    
    # Massachusetts configuration (same pattern as CT)
    with st.sidebar.expander("Massachusetts (MA)"):
        with st.form("ma_agency_form"):
            ma_branch = st.text_input("Branch Name", value=current_configs.get("MA", {}).get("branch", ""), placeholder="BHIC0035 | New England", key="ma_branch")
            ma_agency = st.text_input("Agency Name", value=current_configs.get("MA", {}).get("agency", ""), placeholder="Columbia Insurance Agency", key="ma_agency")
            ma_producer = st.text_input("Producer Name", value=current_configs.get("MA", {}).get("producer", ""), placeholder="Columbia Insurance Agency, Inc. - 0001001", key="ma_producer")
            
            if st.form_submit_button("Save MA", use_container_width=True):
                try:
                    existing_lines = []
                    if env_path.exists():
                        with open(env_path, 'r') as f:
                            existing_lines = [line for line in f.readlines() 
                                            if not line.startswith('PR_MA_')]
                    
                    with open(env_path, 'w') as f:
                        for line in existing_lines:
                            f.write(line)
                        if ma_branch:
                            f.write(f"PR_MA_BRANCH={ma_branch}\n")
                        if ma_agency:
                            f.write(f"PR_MA_AGENCY={ma_agency}\n")
                        if ma_producer:
                            f.write(f"PR_MA_PRODUCER={ma_producer}\n")
                    
                    st.success("MA saved!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    
    # New Hampshire configuration
    with st.sidebar.expander("New Hampshire (NH)"):
        with st.form("nh_agency_form"):
            nh_branch = st.text_input("Branch Name", value=current_configs.get("NH", {}).get("branch", ""), placeholder="BHIC0035 | New England", key="nh_branch")
            nh_agency = st.text_input("Agency Name", value=current_configs.get("NH", {}).get("agency", ""), placeholder="Columbia Insurance Agency", key="nh_agency")
            nh_producer = st.text_input("Producer Name", value=current_configs.get("NH", {}).get("producer", ""), placeholder="Columbia Insurance Agency", key="nh_producer")
            
            if st.form_submit_button("Save NH", use_container_width=True):
                try:
                    existing_lines = []
                    if env_path.exists():
                        with open(env_path, 'r') as f:
                            existing_lines = [line for line in f.readlines() 
                                            if not line.startswith('PR_NH_')]
                    
                    with open(env_path, 'w') as f:
                        for line in existing_lines:
                            f.write(line)
                        if nh_branch:
                            f.write(f"PR_NH_BRANCH={nh_branch}\n")
                        if nh_agency:
                            f.write(f"PR_NH_AGENCY={nh_agency}\n")
                        if nh_producer:
                            f.write(f"PR_NH_PRODUCER={nh_producer}\n")
                    
                    st.success("NH saved!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    
    # New Jersey configuration
    with st.sidebar.expander("New Jersey (NJ)"):
        with st.form("nj_agency_form"):
            nj_branch = st.text_input("Branch Name", value=current_configs.get("NJ", {}).get("branch", ""), placeholder="Palisades", key="nj_branch")
            nj_agency = st.text_input("Agency Name", value=current_configs.get("NJ", {}).get("agency", ""), placeholder="A & L Insurance Agency, LLC", key="nj_agency")
            nj_producer = st.text_input("Producer Name", value=current_configs.get("NJ", {}).get("producer", ""), placeholder="A & L Insurance Agency, LLC", key="nj_producer")
            
            if st.form_submit_button("Save NJ", use_container_width=True):
                try:
                    existing_lines = []
                    if env_path.exists():
                        with open(env_path, 'r') as f:
                            existing_lines = [line for line in f.readlines() 
                                            if not line.startswith('PR_NJ_')]
                    
                    with open(env_path, 'w') as f:
                        for line in existing_lines:
                            f.write(line)
                        if nj_branch:
                            f.write(f"PR_NJ_BRANCH={nj_branch}\n")
                        if nj_agency:
                            f.write(f"PR_NJ_AGENCY={nj_agency}\n")
                        if nj_producer:
                            f.write(f"PR_NJ_PRODUCER={nj_producer}\n")
                    
                    st.success("NJ saved!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    
    # New York configuration
    with st.sidebar.expander("New York (NY)"):
        with st.form("ny_agency_form"):
            ny_branch = st.text_input("Branch Name", value=current_configs.get("NY", {}).get("branch", ""), placeholder="Palisades", key="ny_branch")
            ny_agency = st.text_input("Agency Name", value=current_configs.get("NY", {}).get("agency", ""), placeholder="A.H. Meyers and Company", key="ny_agency")
            ny_producer = st.text_input("Producer Name", value=current_configs.get("NY", {}).get("producer", ""), placeholder="A.H. Meyers and Company", key="ny_producer")
            
            if st.form_submit_button("Save NY", use_container_width=True):
                try:
                    existing_lines = []
                    if env_path.exists():
                        with open(env_path, 'r') as f:
                            existing_lines = [line for line in f.readlines() 
                                            if not line.startswith('PR_NY_')]
                    
                    with open(env_path, 'w') as f:
                        for line in existing_lines:
                            f.write(line)
                        if ny_branch:
                            f.write(f"PR_NY_BRANCH={ny_branch}\n")
                        if ny_agency:
                            f.write(f"PR_NY_AGENCY={ny_agency}\n")
                        if ny_producer:
                            f.write(f"PR_NY_PRODUCER={ny_producer}\n")
                    
                    st.success("NY saved!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    
    # Pennsylvania configuration
    with st.sidebar.expander("Pennsylvania (PA)"):
        with st.form("pa_agency_form"):
            pa_branch = st.text_input("Branch Name", value=current_configs.get("PA", {}).get("branch", ""), placeholder="Palisades", key="pa_branch")
            pa_agency = st.text_input("Agency Name", value=current_configs.get("PA", {}).get("agency", ""), placeholder="A.H. Meyers and Company", key="pa_agency")
            pa_producer = st.text_input("Producer Name", value=current_configs.get("PA", {}).get("producer", ""), placeholder="A.H. Meyers and Company", key="pa_producer")
            
            if st.form_submit_button("Save PA", use_container_width=True):
                try:
                    existing_lines = []
                    if env_path.exists():
                        with open(env_path, 'r') as f:
                            existing_lines = [line for line in f.readlines() 
                                            if not line.startswith('PR_PA_')]
                    
                    with open(env_path, 'w') as f:
                        for line in existing_lines:
                            f.write(line)
                        if pa_branch:
                            f.write(f"PR_PA_BRANCH={pa_branch}\n")
                        if pa_agency:
                            f.write(f"PR_PA_AGENCY={pa_agency}\n")
                        if pa_producer:
                            f.write(f"PR_PA_PRODUCER={pa_producer}\n")
                    
                    st.success("PA saved!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")


# ========== END AGENCY CONFIGURATION ==========

# Create temporary folder for storing input/output files during Streamlit runs
# This keeps the main directory clean and organized
TEMP_DIR = Path("streamlit_temp")
TEMP_DIR.mkdir(exist_ok=True)

# Auto-cleanup: Keep only the last 20 runs to save disk space
# Older files are automatically deleted on app startup
try:
    temp_files = sorted(TEMP_DIR.glob("output_*.csv"), key=lambda x: x.stat().st_mtime, reverse=True)
    for i, temp_file in enumerate(temp_files):
        if i >= 20:  # Keep only the 20 most recent files
            try:
                # Also delete the corresponding input file
                input_file = temp_file.parent / temp_file.name.replace("output_", "input_")
                if input_file.exists():
                    input_file.unlink()
                temp_file.unlink()
            except:
                pass  # If deletion fails, just continue
except:
    pass  # If cleanup fails, just continue with app startup

# Let users pick how they want to batch their quotes
st.header("Select Processing Mode")
mode = st.radio(
    "How do you want to process quotes?",
    [
        "Multi-State (All states in one file)",
        "Single State (One state at a time)",
        "Multiple States (Separate files for each state)"
    ],
    horizontal=True
)

st.markdown("---")

# Mapping of state names to their corresponding batch processing scripts
# Each state has its own specialized script that handles state-specific logic
STATE_BATCH_FILES = {
    "Connecticut (CT)": "batch_full_ct.py",
    "Massachusetts (MA)": "batch_full_ma.py",
    "New Hampshire (NH)": "batch_full_nh.py",
    "New Jersey (NJ)": "batch_full_nj.py",
    "New York (NY)": "batch_full_ny.py",
    "Pennsylvania (PA)": "batch_full_pa.py",
}

# ========== CORE AUTOMATION RUNNER ==========
# This is the main function that executes the batch processing
# It handles subprocess management, progress tracking, and result display

def run_automation(state_name, batch_file, input_file, output_file, df, headless, base_url):
    """
    Run the automation batch script and display real-time progress.
    
    Args:
        state_name: Display name of the state being processed
        batch_file: Python script to execute (e.g., batch_full_ma.py)
        input_file: Path to input CSV file
        output_file: Path where output CSV will be saved
        df: DataFrame of input data (used for progress tracking)
        headless: Boolean - whether to run browser in headless mode
        base_url: Plymouth Rock model URL to use
    
    Returns:
        Dictionary with success/failed counts and output file path
    """
    
    # Create a container for the progress checklist
    # This shows high-level status: Setup → Login → Processing → Complete
    progress_container = st.container()
    with progress_container:
        st.markdown(f"### Progress for {state_name}")
        
        # Create empty placeholders that we'll update as automation progresses
        checklist = {
            "setup": st.empty(),
            "login": st.empty(),
            "processing": st.empty(),
            "complete": st.empty()
        }
        
        checklist["setup"].markdown("**Setup** - Preparing files...")
    
    # Scrollable terminal logs - collapsed by default to save space
    # Users can expand to see detailed output if needed
    with st.expander("View Terminal Logs", expanded=False):
        log_output = st.empty()
    
    # Progress bar to show visual completion percentage
    progress_bar = st.progress(0)
    progress_text = st.empty()
    
    # Configure subprocess for optimal real-time output
    # PYTHONUNBUFFERED=1 ensures we get output immediately, not batched
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'  # Handle special characters properly
    env['PYTHONUNBUFFERED'] = '1'  # Critical for real-time output
    env['PR_BASE_URL'] = base_url  # Pass the selected Plymouth Rock model URL
    
    # Build the command to execute
    # -u flag makes Python unbuffered (same as PYTHONUNBUFFERED)
    cmd = [sys.executable, "-u", batch_file, input_file, output_file]
    if headless:
        cmd.append("--headless")
    if quotes_only:
        cmd.append("--quotes-only")
    
    # Start the subprocess
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        encoding='utf-8',
        errors='replace',  # Replace any encoding errors instead of crashing
        cwd=os.getcwd(),
        env=env,
        universal_newlines=True
    )
    
    # Store process in session state so we can kill it if user clicks Reset
    st.session_state.process = process
    
    # Initialize tracking variables
    output_lines = []  # Store all output lines for display
    current_row = 0  # Track which row we're currently processing
    total_rows = len(df)
    last_update_time = time.time()  # Throttle UI updates
    start_time = time.time()
    max_time_per_record = 600  # 10 minutes max per record (safety timeout)
    
    try:
        # Main loop: Read output line by line until process completes
        while True:
            line = process.stdout.readline()
            
            # If no more output and process has ended, we're done
            if not line and process.poll() is not None:
                break
            
            if line:
                line = line.rstrip()  # Remove trailing whitespace
                output_lines.append(line)
                
                # Update UI every 2 seconds OR every 15 lines (whichever comes first)
                # This prevents overwhelming the UI with updates
                current_time = time.time()
                if current_time - last_update_time > 2.0 or len(output_lines) % 15 == 0:
                    # Show last 50 lines in the log viewer
                    log_output.text_area(
                        "Terminal Output",
                        '\n'.join(output_lines[-50:]),
                        height=400,
                        key=f"log_{len(output_lines)}"  # Unique key prevents caching issues
                    )
                    last_update_time = current_time
                
                # Update checklist based on specific log messages
                if "Login successful" in line:
                    checklist["setup"].markdown("**Setup** - Files ready")
                    checklist["login"].markdown("**Login** - Logged into Plymouth Rock")
                
                # Track current row number from batch script output
                if "===== ROW" in line:
                    try:
                        current_row = int(line.split("ROW")[1].split("=====")[0].strip())
                        progress = current_row / total_rows
                        progress_bar.progress(progress)
                        progress_text.text(f"Processing row {current_row} of {total_rows}")
                        checklist["processing"].markdown(f"**Processing** - Row {current_row} of {total_rows}")
                    except:
                        pass  # If parsing fails, just skip this update
                
                # Show success messages for completed quotes
                if "[SUCCESS]" in line or "Quote Number:" in line or "quote_number" in line.lower():
                    try:
                        if "Quote" in line or "quote" in line:
                            st.success(f"Row {current_row}: Quote generated")
                    except:
                        pass
                
                # Show appropriate messages for errors and declines
                if "[ERROR]" in line:
                    if "DTQ" in line or "decline" in line.lower() or "CRN" in line:
                        # DTQ = Declined to Quote - this is a normal business outcome
                        st.warning(f"Row {current_row}: Declined by system")
                    elif "Attempt 2" in line or "failed" in line.lower():
                        # Multiple failed attempts indicate a real error
                        st.error(f"Row {current_row}: Failed")
            
            # Safety timeout: If processing takes too long, kill it
            if time.time() - start_time > (max_time_per_record * total_rows):
                st.error("Process timeout - killing automation")
                process.kill()
                break
    
    except Exception as e:
        st.error(f"Error during processing: {e}")
    
    # Wait for process to fully complete and get exit code
    return_code = process.wait()
    st.session_state.process = None
    st.session_state.running = False
    
    # Show final complete logs
    log_output.text_area(
        "Complete Terminal Output",
        '\n'.join(output_lines[-50:]),
        height=400,
        key=f"complete_{len(output_lines)}"
    )
    
    # Update final progress status
    progress_bar.progress(1.0)
    checklist["processing"].markdown(f"**Processing** - Completed {total_rows} rows")
    
    # Display results if processing succeeded
    if return_code == 0 and os.path.exists(output_file):
        checklist["complete"].markdown("**Complete** - Results ready!")
        
        # Load and analyze results
        results_df = pd.read_csv(output_file)
        
        st.markdown("---")
        st.subheader("Results Summary")
        
        # Show key metrics in 4 columns
        col1, col2, col3, col4 = st.columns(4)
        total = len(results_df)
        success = len(results_df[results_df['status'] == 'ok'])
        failed = total - success
        
        col1.metric("Total", total)
        col2.metric("Success", success, delta=f"{(success/total*100):.0f}%")
        col3.metric("Failed", failed)
        col4.metric("Success Rate", f"{(success/total*100):.0f}%")
        
        # Show full results table
        st.dataframe(results_df, use_container_width=True)
        
        # Download and save options
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "Download Results",
                data=results_df.to_csv(index=False),
                file_name=f"plymouth_rock_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
                key=f"dl_{output_file}"
            )
        with col2:
            if st.button("Save to Main Folder", use_container_width=True, key=f"sv_{output_file}"):
                saved_file = f"saved_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                results_df.to_csv(saved_file, index=False)
                st.success(f"Saved as {saved_file}")
        
        return {"success": success, "failed": failed, "output": output_file}
    else:
        # Processing failed
        checklist["complete"].markdown("**Complete** - Processing failed")
        st.error(f"Processing failed (return code: {return_code})")
        
        # Show error details
        with st.expander("Error Details", expanded=True):
            st.text_area(
                "Error Log",
                '\n'.join(output_lines[-50:]),
                height=400,
                key=f"error_{len(output_lines)}"
            )
        
        return {"success": 0, "failed": total_rows, "output": None}

# ========== END AUTOMATION RUNNER ==========


# MULTI-STATE MODE - Process one CSV with multiple states mixed together
if "Multi-State" in mode:
    st.subheader("Multi-State Processing")
    st.info("Upload ONE CSV with a 'state' column (CT, MA, NH, NJ, NY, PA)")
    
    uploaded_file = st.file_uploader("Upload CSV", type=['csv'], key="multistate")
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        
        # Validate that all required columns exist
        required = ['first_name', 'last_name', 'dob', 'address', 'state']
        missing = [col for col in required if col not in df.columns]
        
        if missing:
            st.error(f"Missing columns: {', '.join(missing)}")
        else:
            # Show breakdown by state
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Records", len(df))
                state_counts = df['state'].value_counts()
                st.dataframe(state_counts, use_container_width=True)
            
            with col2:
                with st.expander("Preview Data"):
                    st.dataframe(df.head(10))
            
            # Use the multi-state batch script
            batch_file = "batch_multistate.py"

# SINGLE STATE MODE - Process one CSV for a specific state
elif "Single State" in mode:
    st.subheader("Single State Processing")
    
    col1, col2 = st.columns(2)
    with col1:
        selected_state = st.selectbox("Select State:", list(STATE_BATCH_FILES.keys()))
    with col2:
        st.info(f"Will use: `{STATE_BATCH_FILES[selected_state]}`")
    
    uploaded_file = st.file_uploader(f"Upload CSV for {selected_state}", type=['csv'], key="single")
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        
        # Validate required columns (no 'state' column needed for single state)
        required = ['first_name', 'last_name', 'dob', 'address']
        missing = [col for col in required if col not in df.columns]
        
        if missing:
            st.error(f"Missing columns: {', '.join(missing)}")
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Records", len(df))
            with col2:
                with st.expander("Preview Data"):
                    st.dataframe(df.head(10))
            
            # Use the specific state's batch script
            batch_file = STATE_BATCH_FILES[selected_state]

# MULTIPLE STATES MODE - Process separate CSVs for each selected state
elif "Multiple States" in mode:
    st.subheader("Multiple States Processing")
    st.info("Upload separate CSV files for each state you want to process")
    
    # Let user select which states they want to process
    selected_states = st.multiselect(
        "Select states to process:",
        list(STATE_BATCH_FILES.keys()),
        default=[]
    )
    
    if selected_states:
        # Create file uploaders for each selected state
        uploaded_files = {}
        for state in selected_states:
            uploaded_files[state] = st.file_uploader(
                f"CSV for {state}:",
                type=['csv'],
                key=f"multi_{state}"
            )
        
        # Check if all files have been uploaded
        all_uploaded = all(uploaded_files.values())
        
        if all_uploaded:
            # Calculate total records across all files
            total_records = 0
            for file_obj in uploaded_files.values():
                total_records += len(pd.read_csv(file_obj))
                file_obj.seek(0)  # Reset file pointer after reading
            
            st.success(f"All {len(selected_states)} files uploaded! Total: {total_records} records")
            
            # Preview data from all files
            with st.expander("Preview Data"):
                for state, file_obj in uploaded_files.items():
                    st.markdown(f"**{state}:**")
                    file_obj.seek(0)
                    preview_df = pd.read_csv(file_obj)
                    st.dataframe(preview_df.head(5))
                    file_obj.seek(0)  # Reset again for processing
            
            # Special marker to indicate multiple file processing
            batch_file = "multiple"

# PROCESSING SECTION - This appears after file upload is complete
if ('uploaded_file' in locals() and uploaded_file and 'batch_file' in locals()) or ('batch_file' in locals() and batch_file == "multiple"):
    st.markdown("---")
    
    # Row 1 - Let user select which Plymouth Rock model to use
    server_url = st.selectbox(
        "🌐 Select Plymouth Rock Model:",
        [
            "Model 1 (agentweb1mod)",
            "Model 2 (agentweb2mod)",
            "Model 3 (agentweb3mod)"
        ],
        index=0
    )
    
    # Map friendly name to actual URL
    url_mapping = {
        "Model 1 (agentweb1mod)": "https://agentweb1mod.plymouthrock.com",
        "Model 2 (agentweb2mod)": "https://agentweb2mod.plymouthrock.com",
        "Model 3 (agentweb3mod)": "https://agentweb3mod.plymouthrock.com"
    }
    base_url = url_mapping[server_url]
    
    st.markdown("---")
    
    # Row 2 - Processing options
    col1, col2 = st.columns(2)
    with col1:
        headless = st.checkbox("⚡ Headless mode (run in background)", value=True)
    with col2:
        quotes_only = st.checkbox(
            "📋 Quote Numbers Only", 
            value=False,
            help="Check to get ONLY quote numbers (skip policy issuance)"
        )
    
    # Show which mode is active
    if quotes_only:
        st.info(" Mode: Quote Numbers Only")
    else:
        st.success(" Mode: Full Processing (Quote + Policy)")
    
    # Single START button - disabled while processing
    start_btn = st.button(
        "START PROCESSING", 
        type="primary", 
        use_container_width=True, 
        disabled=st.session_state.running
    )
    
    # Show status message if already running
    if st.session_state.running:
        st.info("Processing in progress... Use 'Reset App' in sidebar if needed.")
    
    # Execute when START is clicked
    if start_btn:
        st.session_state.running = True
        
        # Generate timestamp for unique file naming
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if batch_file == "multiple":
            # Multiple states mode - process each state sequentially
            st.info(f"Processing {len(selected_states)} states sequentially...")
            
            all_results = []
            
            for state in selected_states:
                # Extract state abbreviation from full name
                state_abbr = state.split("(")[1].split(")")[0]
                input_file = str(TEMP_DIR / f"input_{state_abbr}_{timestamp}.csv")
                output_file = str(TEMP_DIR / f"output_{state_abbr}_{timestamp}.csv")
                
                # Reset and read the uploaded file for this state
                uploaded_files[state].seek(0)
                state_df = pd.read_csv(uploaded_files[state])
                state_df.to_csv(input_file, index=False)
                
                # Process this state
                st.subheader(f"Processing {state}")
                result = run_automation(state, STATE_BATCH_FILES[state], input_file, output_file, state_df, headless, base_url)
                all_results.append(result)
            
            st.success(f"Completed all {len(selected_states)} states!")
            
        else:
            # Single file mode (either multi-state or single state)
            input_file = str(TEMP_DIR / f"input_{timestamp}.csv")
            output_file = str(TEMP_DIR / f"output_{timestamp}.csv")
            
            # Save uploaded file to temp directory
            df.to_csv(input_file, index=False)
            
            # Determine display name
            state_name = "Multi-State" if batch_file == "batch_multistate.py" else selected_state
            run_automation(state_name, batch_file, input_file, output_file, df, headless, base_url)
        
        # Reset running state when complete
        st.session_state.running = False

# Previous results section - always show this
st.markdown("---")
st.subheader("Previous Runs")

# Get files from BOTH temp folder AND main directory
all_files = []

# Get temp files
try:
    temp_files = list(TEMP_DIR.glob("output_*.csv"))
    all_files.extend([(f, "Temp") for f in temp_files])
except:
    pass

# Get ALL output files from main directory (both saved_ and output_ prefixes)
try:
    main_files = [Path(f) for f in os.listdir('.') if (f.startswith(('saved_', 'output_')) and f.endswith('.csv'))]
    all_files.extend([(f, "Main") for f in main_files])
except:
    pass

# Sort by modification time (newest first)
all_files.sort(key=lambda x: x[0].stat().st_mtime, reverse=True)

# Show summary counts
temp_count = sum(1 for _, tag in all_files if tag == "Temp")
main_count = sum(1 for _, tag in all_files if tag == "Main")
st.caption(f"Temp folder: {temp_count} runs | Main folder: {main_count} files")

if all_files:
    # Format file names for display with size and location
    file_labels = [f"{f.name} ({f.stat().st_size / 1024:.1f} KB) [{tag}]" for f, tag in all_files]
    
    # Dropdown to select which previous run to view
    selected_idx = st.selectbox("Select run:", range(len(all_files)), format_func=lambda i: file_labels[i])
    selected_file, file_tag = all_files[selected_idx]
    
    # Load and display selected run
    if st.button("Load Selected Run"):
        prev_df = pd.read_csv(selected_file)
        
        # Calculate success/failure metrics
        col1, col2, col3 = st.columns(3)
        success = len(prev_df[prev_df['status'] == 'ok'])
        failed = len(prev_df[prev_df['status'] != 'ok'])
        
        col1.metric("Total", len(prev_df))
        col2.metric("Success", success)
        col3.metric("Failed", failed)
        
        # Show full data
        st.dataframe(prev_df, use_container_width=True)
        
        # Download and save options
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "Download",
                data=prev_df.to_csv(index=False),
                file_name=f"plymouth_rock_{selected_file.stem}.csv",
                mime="text/csv",
                use_container_width=True,
                key=f"dl_prev_{selected_file.stem}"
            )
        with col2:
            # Only show "Save to Main" for temp files (main files are already saved)
            if file_tag == "Temp":
                if st.button("Save to Main Folder", use_container_width=True, key=f"sv_prev_{selected_file.stem}"):
                    saved_name = f"saved_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    prev_df.to_csv(saved_name, index=False)
                    st.success(f"Saved as {saved_name}")
                    st.rerun()
else:
    st.info("No previous runs found")

# ========== SIDEBAR ==========
with st.sidebar:
    # Call the credentials manager function
    manage_credentials()
    
    # Call the agency configuration manager function
    manage_agency_config()
    
    st.markdown("---")
    st.header("Quick Guide")
    
    # Quick reference guide for users
    st.markdown("""
    ### Multi-State
    - One CSV with 'state' column
    - Processes all states together
    - Best for mixed state batches
    
    ### Single State
    - One CSV for one state
    - Choose which state
    - Best for state-specific batches
    
    ### Multiple States
    - Separate CSV for each state
    - Upload 2-6 files
    - Processes sequentially
    
    ---
    
    ### Timing
    - ~45-60 seconds per record
    - Real-time progress tracking
    - Headless mode recommended
    
    ---
    
    ### File Management
    - Last 20 runs kept in temp folder
    - Download → Goes to Downloads
    - Save → Keeps permanently
    - Previous Runs → All files
    """)
    
    st.markdown("---")
    st.caption(f"Python: {sys.executable[:40]}...")
    
    # Show temp folder statistics
    try:
        temp_count = len(list(TEMP_DIR.glob("output_*.csv")))
        if temp_count > 0:
            temp_size = sum(f.stat().st_size for f in TEMP_DIR.glob("output_*.csv"))
            st.caption(f"Temp: {temp_count} files, {temp_size / 1024:.1f} KB")
    except:
        pass
    
    # Reset button - kills any running processes and clears session state
    st.markdown("---")
    st.subheader("Controls")
    
    if st.button("Reset App", use_container_width=True):
        # Try to kill running process if it exists
        if st.session_state.process:
            try:
                if sys.platform == "win32":
                    # Windows requires taskkill command
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(st.session_state.process.pid)], 
                                   capture_output=True, timeout=5)
                else:
                    # Unix/Mac can use kill directly
                    st.session_state.process.kill()
            except:
                pass  # If killing fails, just continue
        
        # Reset session state
        st.session_state.running = False
        st.session_state.process = None
        st.success("App reset!")
        time.sleep(0.5)
        st.rerun()
    
    # Show warning if process is running
    if st.session_state.running:
        st.warning("Process is running")