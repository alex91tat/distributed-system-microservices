import os
import subprocess
import sys
from dotenv import load_dotenv

load_dotenv()

def run_services() -> None:
    print("Starting Distributed System Services...")
    print("API Gateway    -> http://localhost:5000")
    print("Movie Service  -> http://localhost:5001")
    print("Recommendation -> http://localhost:5002")


    env = os.environ.copy()
    processes = []

    try:
        # Start each service as a separate process
        processes.append(subprocess.Popen([
            sys.executable, "-m", "uvicorn",
            "recommendation_service.main:app",
            "--port", "5002",
            "--reload"
        ]))

        processes.append(subprocess.Popen([
            sys.executable, "-m", "uvicorn",
            "movie_service.main:app",
            "--port", "5001",
            "--reload"
        ]))

        processes.append(subprocess.Popen([
            sys.executable, "-m", "uvicorn",
            "gateway.main:app",
            "--port", "5000",
            "--reload"
        ]))

        for process in processes:
            process.wait()

    except KeyboardInterrupt:
        print("\nShutting down all services...")
        for process in processes:
            process.terminate()
        print("All services stopped.")


if __name__ == "__main__":
    run_services()