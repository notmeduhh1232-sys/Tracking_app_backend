"""
Helper script to update MongoDB connection string in .env file
"""

import os

print("=" * 60)
print("MONGODB CONNECTION STRING UPDATER")
print("=" * 60)

print("\n📋 This script will help you update your MongoDB connection string")
print("\n🔗 Your connection string should look like:")
print("   mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/vehicle_tracking")

print("\n" + "=" * 60)

connection_string = input("\n📝 Paste your MongoDB Atlas connection string here:\n> ").strip()

if not connection_string:
    print("\n❌ No connection string provided. Exiting.")
    exit(1)

if not connection_string.startswith("mongodb"):
    print("\n❌ Invalid connection string. Should start with 'mongodb://' or 'mongodb+srv://'")
    exit(1)

# Ensure it ends with database name
if "vehicle_tracking" not in connection_string:
    if "?" in connection_string:
        # Insert database name before query params
        connection_string = connection_string.replace("/?", "/vehicle_tracking?")
    else:
        # Add database name at the end
        connection_string += "/vehicle_tracking"
    print(f"\n✅ Added database name: /vehicle_tracking")

# Read current .env
env_path = ".env"
if not os.path.exists(env_path):
    print(f"\n❌ .env file not found at {env_path}")
    exit(1)

with open(env_path, 'r') as f:
    lines = f.readlines()

# Update MONGODB_URL line
updated = False
new_lines = []
for line in lines:
    if line.startswith("MONGODB_URL="):
        new_lines.append(f"MONGODB_URL={connection_string}\n")
        updated = True
    else:
        new_lines.append(line)

if not updated:
    print("\n❌ MONGODB_URL not found in .env file")
    exit(1)

# Write back
with open(env_path, 'w') as f:
    f.writelines(new_lines)

print("\n✅ Updated backend/.env with new MongoDB connection string")

# Hide password in output
display_string = connection_string
if "@" in display_string:
    parts = display_string.split("@")
    user_pass = parts[0].split("://")[1]
    if ":" in user_pass:
        username = user_pass.split(":")[0]
        display_string = display_string.replace(user_pass, f"{username}:****")

print(f"\n📝 Connection string: {display_string}")

print("\n" + "=" * 60)
print("🧪 Testing connection...")
print("=" * 60)

# Test connection
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def test_connection():
    try:
        client = AsyncIOMotorClient(connection_string)
        await client.admin.command('ping')
        print("\n✅ SUCCESS! MongoDB connection works!")
        print("\n🚀 Next steps:")
        print("   1. Run: python main.py")
        print("   2. Run: python tmp_rovodev_test_backend.py")
        client.close()
        return True
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("\n📋 Please check:")
        print("   1. Connection string is correct")
        print("   2. Password is correct (URL-encoded if special chars)")
        print("   3. IP whitelist includes 0.0.0.0/0 in Atlas Network Access")
        print("   4. Database user exists in Atlas Database Access")
        print("   5. Wait 2-3 minutes after creating user/whitelist")
        return False

asyncio.run(test_connection())
