#!/usr/bin/env python3
"""
OpenStack Dashboard Launcher
"""

import os
import sys
from dotenv import load_dotenv

def check_environment():
    """Check if required environment variables are set"""
    load_dotenv()
    
    required_vars = [
        "OPENSTACK_AUTH_URL",
        "OPENSTACK_PROJECT_NAME",
        "OPENSTACK_USERNAME",
        "OPENSTACK_PASSWORD"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease create a .env file based on env_example.txt")
        return False
    
    return True

def main():
    """Main launcher function"""
    print("🚀 OpenStack Dashboard Launcher")
    print("=" * 40)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    print("✅ Environment variables loaded successfully")
    print("🚀 Starting OpenStack Dashboard...")
    
    try:
        # Import and run the Flask app
        from backend.app import app, socketio
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
