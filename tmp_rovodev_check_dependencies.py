"""
Check if all backend dependencies are installed
"""

import sys

print("=" * 60)
print("BACKEND DEPENDENCY CHECK")
print("=" * 60)

dependencies = [
    ("fastapi", "FastAPI framework"),
    ("uvicorn", "ASGI server"),
    ("motor", "Async MongoDB driver"),
    ("redis", "Redis client"),
    ("pydantic", "Data validation"),
    ("python-dotenv", "Environment variables"),
    ("httpx", "HTTP client"),
    ("numpy", "Numerical computing"),
    ("scipy", "Scientific computing"),
]

missing = []
installed = []

for module_name, description in dependencies:
    try:
        __import__(module_name.replace("-", "_"))
        print(f"✅ {module_name:20} - {description}")
        installed.append(module_name)
    except ImportError:
        print(f"❌ {module_name:20} - {description} (MISSING)")
        missing.append(module_name)

print("\n" + "=" * 60)
print(f"Installed: {len(installed)}/{len(dependencies)}")
print(f"Missing: {len(missing)}/{len(dependencies)}")
print("=" * 60)

if missing:
    print("\n⚠️  Missing dependencies detected!")
    print("\nTo install missing dependencies:")
    print("  cd backend")
    print("  pip install -r requirements.txt")
    sys.exit(1)
else:
    print("\n✅ All dependencies are installed!")
    print("\n📋 Next steps:")
    print("  1. Ensure MongoDB is running (localhost:27017)")
    print("  2. Ensure Redis is running (localhost:6379) - optional")
    print("  3. Start backend: python main.py")
    print("  4. Run tests: python tmp_rovodev_test_backend.py")
    sys.exit(0)
