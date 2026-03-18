#!/usr/bin/env python3
"""
NotebookLM Skill Scripts Package
Provides automatic environment management for all scripts
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def ensure_venv_and_run():
    """
    Ensure virtual environment exists and run the requested script.
    This is called when any script is imported or run directly.
    """
    # Only do this if we're not already in the skill's venv
    skill_dir = Path(__file__).parent.parent
    venv_dir = skill_dir / ".venv"

    # Check if we're in a venv
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )

    # Check if it's OUR venv
    if in_venv:
        venv_path = Path(sys.prefix)
        if venv_path == venv_dir:
            # We're already in the correct venv
            return

    # We need to set up or switch to our venv
    if not venv_dir.exists():
        print("🔧 First-time setup detected...")
        print("   Creating isolated environment for NotebookLM skill via uv...")
        print("   This ensures clean dependency management...")

        uv_cmd = shutil.which("uv")
        if not uv_cmd:
            print("❌ uv is required but not found.")
            print("   Install it from: https://docs.astral.sh/uv/getting-started/installation/")
            sys.exit(1)

        # Sync dependencies using uv (creates .venv and installs from pyproject.toml + uv.lock)
        try:
            subprocess.run(
                [uv_cmd, "sync"],
                cwd=str(skill_dir),
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print("❌ Failed to set up environment using uv.")
            print(f"   Command exited with status {e.returncode}.")
            print(f"   Try running 'uv sync' manually in: {skill_dir}")
            sys.exit(e.returncode or 1)

        # Also install Chrome for Patchright
        print("   Setting up browser automation...")
        if os.name == 'nt':
            python_exe = venv_dir / "Scripts" / "python.exe"
        else:
            python_exe = venv_dir / "bin" / "python"

        try:
            subprocess.run(
                [str(python_exe), "-m", "patchright", "install", "chrome"],
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            print("⚠️  Failed to install Chrome for Patchright. Continuing without browser setup.")
            if e.stdout:
                try:
                    print("   patchright stdout:")
                    print(e.stdout.decode(errors="replace"))
                except AttributeError:
                    print("   patchright stdout:")
                    print(e.stdout)
            if e.stderr:
                try:
                    print("   patchright stderr:")
                    print(e.stderr.decode(errors="replace"))
                except AttributeError:
                    print("   patchright stderr:")
                    print(e.stderr)

        print("✅ Environment ready! All dependencies isolated in .venv/")

    # If we're here and not in the venv, we should recommend using the venv
    if not in_venv:
        print("\n⚠️  Running outside virtual environment")
        print("   Recommended: Use scripts/run.py to ensure clean execution")
        print("   Or activate: source .venv/bin/activate")


# Check environment when module is imported
ensure_venv_and_run()
