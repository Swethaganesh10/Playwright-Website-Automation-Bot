FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Copy all state automation files
COPY full_code_ct.py .
COPY full_code_ma.py .
COPY full_code_nh.py .
COPY full_code_nj.py .
COPY full_code_ny.py .
COPY full_code_pa.py .

# Copy batch processing files
COPY batch_full_ct.py .
COPY batch_full_ma.py .
COPY batch_full_nh.py .
COPY batch_full_nj.py .
COPY batch_full_ny.py .
COPY batch_full_pa.py .
COPY batch_multistate.py .

# Copy requirements and env
COPY requirements.txt .
COPY .env .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy Streamlit UI
COPY app.py .

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]