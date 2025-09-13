#!/usr/bin/env python3
"""
Database update script for Smart Tourist Safety System
Adds group functionality tables
"""

from app import app
from models import db

def update_database():
    """Create new tables for group functionality"""
    with app.app_context():
        try:
            # Create all tables (including new Group and GroupMember tables)
            db.create_all()
            print("Database updated successfully!")
            print("Group and GroupMember tables created")
            print("\nNew features added:")
            print("   - Create tourist groups")
            print("   - Join groups with group codes")
            print("   - View group member locations")
            print("   - Group-wide panic alerts")
            
        except Exception as e:
            print(f"Error updating database: {e}")

if __name__ == '__main__':
    update_database()