#!/usr/bin/env python3
"""
fix_cors.py - 自动为 OpenManus-GUI 的 api_server.py 添加 CORS 支持

使用方法:
    python fix_cors.py

功能:
    1. 自动检测 api_server.py 是否已有 CORS 配置
    2. 如果没有，自动添加 FastAPI CORS 中间件
    3. 备份原始文件为 api_server.py.bak
"""

import os
import sys
import shutil

# 自动检测路径
POSSIBLE_PATHS = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "OpenManus-GUI", "api_server.py"),
    r"E:\openmanus\OpenManus-GUI\api_server.py",
    r"E:\OpenManus\OpenManus-GUI\api_server.py",
]

def find_api_server():
    for p in POSSIBLE_PATHS:
        if os.path.exists(p):
            return p
    return None

def main():
    api_path = find_api_server()
    if not api_path:
        print("[ERROR] Could not find api_server.py")
        print("Searched paths:")
        for p in POSSIBLE_PATHS:
            print(f"  - {p}")
        sys.exit(1)

    print(f"[INFO] Found api_server.py at: {api_path}")

    with open(api_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 检查是否已有 CORS 配置
    if "CORSMiddleware" in content:
        print("[OK] CORS middleware already configured. No changes needed.")
        return

    # 备份
    backup_path = api_path + ".bak"
    shutil.copy2(api_path, backup_path)
    print(f"[INFO] Backup saved to: {backup_path}")

    # 添加 CORS 导入和中间件
    cors_import = "from fastapi.middleware.cors import CORSMiddleware\n"
    cors_middleware = """
# === CORS Support (added by fix_cors.py) ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# === End CORS ===
"""

    # 策略1: 在 from fastapi 导入行后添加 CORS 导入
    if "from fastapi import" in content:
        content = content.replace(
            "from fastapi import",
            f"{cors_import}from fastapi import",
            1
        )
    elif "import fastapi" in content:
        content = content.replace(
            "import fastapi",
            f"import fastapi\n{cors_import}",
            1
        )
    else:
        # 在文件开头添加
        content = cors_import + content

    # 策略: 在 app = FastAPI(...) 之后添加中间件
    # 寻找 app = FastAPI 的位置
    import re
    # 匹配 app = FastAPI(...) 可能跨多行
    pattern = r'(app\s*=\s*FastAPI\([^)]*\))'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        insert_pos = match.end()
        content = content[:insert_pos] + "\n" + cors_middleware + content[insert_pos:]
    else:
        # 如果找不到 app = FastAPI，尝试在所有 import 之后添加
        lines = content.split("\n")
        last_import = 0
        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                last_import = i
        lines.insert(last_import + 1, cors_middleware)
        content = "\n".join(lines)

    with open(api_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("[OK] CORS middleware added successfully!")
    print()
    print("Changes made:")
    print("  1. Added 'from fastapi.middleware.cors import CORSMiddleware'")
    print("  2. Added app.add_middleware(CORSMiddleware, ...) after app creation")
    print()
    print("To undo: copy api_server.py.bak back to api_server.py")

if __name__ == "__main__":
    main()
