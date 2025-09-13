#!/usr/bin/env python3
"""
Smart Tourist Safety Monitoring System Setup
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Failed to install packages. Please run: pip install -r requirements.txt")
        return False
    return True

def create_database():
    """Initialize the database"""
    print("🗄️ Creating database...")
    try:
        from app import app, db
        with app.app_context():
            db.create_all()
        print("✅ Database created successfully!")
    except Exception as e:
        print(f"❌ Failed to create database: {e}")
        return False
    return True

def main():
    print("🛡️ Smart Tourist Safety Monitoring System Setup")
    print("=" * 50)
    
    if not install_requirements():
        return
    
    if not create_database():
        return
    
    print("\n🎉 Setup completed successfully!")
    print("\nTo start the application:")
    print("1. Run the Flask app: python app.py")
    print("2. Run the AI engine (in another terminal): python ai_engine.py")
    print("3. Open http://127.0.0.1:5000/ in your browser")
    print("\n📱 Test the system:")
    print("- Register as a tourist and get your QR code")
    print("- Use the panic button to test alerts")
    print("- Check the police dashboard for monitoring")

if __name__ == "__main__":
    main()