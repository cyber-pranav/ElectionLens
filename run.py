"""
ElectionLens — Single entry point.
Starts the FastAPI backend and Streamlit frontend.
"""

import subprocess
import sys
import os
import time
import signal

from dotenv import load_dotenv

load_dotenv()


def main():
    project_root = os.path.dirname(os.path.abspath(__file__))
    port = os.getenv("PORT", "8000")
    frontend_port = os.getenv("FRONTEND_PORT", "8501")

    print("=" * 60)
    print("🗳️  ElectionLens — Election Data Intelligence System")
    print("=" * 60)
    print(f"  API Server   → http://localhost:{port}")
    print(f"  Frontend     → http://localhost:{frontend_port}")
    print(f"  Health Check → http://localhost:{port}/health")
    print("=" * 60)
    print()

    # Start FastAPI in background
    api_process = subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn",
            "api.main:app",
            "--host", "0.0.0.0",
            "--port", port,
            "--reload",
        ],
        cwd=project_root,
    )

    # Give API a moment to start
    time.sleep(3)

    # Start Streamlit (foreground — blocks until user exits)
    try:
        subprocess.run(
            [
                sys.executable, "-m", "streamlit", "run",
                os.path.join("frontend", "app.py"),
                "--server.port", frontend_port,
                "--server.address", "0.0.0.0",
                "--browser.gatherUsageStats", "false",
            ],
            cwd=project_root,
        )
    except KeyboardInterrupt:
        print("\n🛑 Shutting down ElectionLens...")
    finally:
        api_process.terminate()
        api_process.wait(timeout=5)
        print("✅ ElectionLens stopped.")


if __name__ == "__main__":
    main()
