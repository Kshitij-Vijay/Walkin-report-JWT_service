import subprocess
import time

while True:
    print("Starting FastAPI server...")
    
    process = subprocess.Popen(
        ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
    )

    process.wait()

    print("Server crashed. Restarting in 3 seconds...")
    time.sleep(3)