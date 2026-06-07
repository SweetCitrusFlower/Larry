"""Reset the database schema for the backend.

This script drops and recreates all tables using SQLAlchemy `Base.metadata`.
It is robust to being executed from the repository root or from the `backend` folder.

Examples:
  python backend/scripts/reset_db.py
  python backend/scripts/reset_db.py --yes --migrate

Use `--migrate` to run `alembic upgrade head` after recreating tables.
"""

from __future__ import annotations

import os
import sys
import argparse
import subprocess
from pathlib import Path

# Ensure the backend package is importable regardless of working directory
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def main() -> None:
    parser = argparse.ArgumentParser(description="Drop and recreate backend database tables")
    parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")
    parser.add_argument("--migrate", action="store_true", help="Run `alembic upgrade head` after recreate")
    args = parser.parse_args()

    try:
        from app.db.database import engine, Base
        # import models to ensure they are registered with Base
        from app import models  # noqa: F401
    except Exception as exc:
        print("Failed to import backend package. Ensure you're running from the repo root or that `backend` is on PYTHONPATH.")
        print(f"Import error: {exc}")
        sys.exit(1)

    if not args.yes:
        confirm = input("This will DROP and RECREATE all tables in the database. Continue? [y/N]: ")
        if confirm.lower() not in ("y", "yes"):
            print("Aborted by user.")
            return

    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Recreating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Done.")

    if args.migrate:
        print("Running alembic upgrade head...")
        env = os.environ.copy()
        # Ensure Alembic can import the backend package
        env_pythonpath = env.get("PYTHONPATH", "")
        if str(BACKEND_DIR) not in env_pythonpath.split(os.pathsep):
            env["PYTHONPATH"] = str(BACKEND_DIR) + (os.pathsep + env_pythonpath if env_pythonpath else "")
        try:
            subprocess.run(["alembic", "upgrade", "head"], cwd=str(BACKEND_DIR), check=True, env=env)
            print("Alembic upgrade completed.")
        except subprocess.CalledProcessError as e:
            print("Alembic upgrade failed:", e)


if __name__ == "__main__":
    main()
