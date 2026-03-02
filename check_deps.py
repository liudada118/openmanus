#!/usr/bin/env python3
"""
check_deps.py - 检查并安装 OpenManus 所需的所有依赖

使用方法:
    python check_deps.py

功能:
    1. 检查 Python 版本
    2. 检查并安装后端依赖 (OpenManus-GUI)
    3. 检查 Node.js 和 pnpm
    4. 检查并安装前端依赖 (web-ui)
"""

import os
import sys
import subprocess
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_cmd(cmd, cwd=None, check=False):
    """Run a command and return (success, output)"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            cwd=cwd, timeout=120
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

def check_python():
    print("=" * 50)
    print("[1/4] Checking Python...")
    version = sys.version
    print(f"  Python version: {version}")
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 10):
        print("  [WARN] Python 3.10+ recommended")
        return False
    print("  [OK]")
    return True

def check_backend_deps():
    print()
    print("=" * 50)
    print("[2/4] Checking backend dependencies...")

    gui_dir = os.path.join(BASE_DIR, "OpenManus-GUI")
    req_file = os.path.join(gui_dir, "requirements.txt")

    if not os.path.exists(gui_dir):
        print("  [SKIP] OpenManus-GUI directory not found")
        print("  Run: git clone https://github.com/manusAI/OpenManus-GUI.git")
        return False

    if not os.path.exists(req_file):
        print("  [SKIP] requirements.txt not found")
        return False

    # Check key packages
    key_packages = ["fastapi", "uvicorn", "pydantic", "httpx"]
    missing = []
    for pkg in key_packages:
        ok, _ = run_cmd(f'python -c "import {pkg}"')
        if not ok:
            missing.append(pkg)

    if missing:
        print(f"  Missing packages: {', '.join(missing)}")
        print(f"  Installing from requirements.txt...")
        ok, output = run_cmd(f"pip install -r requirements.txt", cwd=gui_dir)
        if ok:
            print("  [OK] Dependencies installed")
        else:
            print(f"  [ERROR] Installation failed")
            print(f"  Try manually: cd {gui_dir} && pip install -r requirements.txt")
            return False
    else:
        print("  [OK] All key packages found")

    return True

def check_node():
    print()
    print("=" * 50)
    print("[3/4] Checking Node.js and pnpm...")

    node_path = shutil.which("node")
    if not node_path:
        print("  [ERROR] Node.js not found!")
        print("  Download from: https://nodejs.org/")
        return False

    ok, output = run_cmd("node --version")
    print(f"  Node.js: {output.strip()}")

    pnpm_path = shutil.which("pnpm")
    if not pnpm_path:
        print("  [WARN] pnpm not found, installing...")
        ok, _ = run_cmd("npm install -g pnpm")
        if not ok:
            print("  [ERROR] Failed to install pnpm")
            return False

    ok, output = run_cmd("pnpm --version")
    print(f"  pnpm: {output.strip()}")
    print("  [OK]")
    return True

def check_frontend_deps():
    print()
    print("=" * 50)
    print("[4/4] Checking frontend dependencies...")

    ui_dir = os.path.join(BASE_DIR, "web-ui")
    if not os.path.exists(ui_dir):
        print("  [SKIP] web-ui directory not found")
        return False

    node_modules = os.path.join(ui_dir, "node_modules")
    if not os.path.exists(node_modules):
        print("  Installing frontend dependencies...")
        ok, output = run_cmd("pnpm install", cwd=ui_dir)
        if ok:
            print("  [OK] Dependencies installed")
        else:
            print("  [ERROR] Installation failed")
            print(f"  Try manually: cd {ui_dir} && pnpm install")
            return False
    else:
        print("  [OK] node_modules exists")

    return True

def main():
    print("========================================")
    print("  OpenManus Dependency Checker")
    print("========================================")
    print()

    results = []
    results.append(("Python", check_python()))
    results.append(("Backend deps", check_backend_deps()))
    results.append(("Node.js/pnpm", check_node()))
    results.append(("Frontend deps", check_frontend_deps()))

    print()
    print("=" * 50)
    print("Summary:")
    all_ok = True
    for name, ok in results:
        status = "OK" if ok else "NEEDS ATTENTION"
        print(f"  {name}: [{status}]")
        if not ok:
            all_ok = False

    print()
    if all_ok:
        print("All checks passed! You can now run: 启动全部.bat")
    else:
        print("Some checks failed. Please fix the issues above.")

if __name__ == "__main__":
    main()
