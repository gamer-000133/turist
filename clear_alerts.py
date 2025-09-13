#!/usr/bin/env python3
"""
Clear all alerts from database
"""

from app import app
from models import db, Alert

def clear_all_alerts():
    """Delete all alerts from database"""
    with app.app_context():
        try:
            # Delete all alerts
            Alert.query.delete()
            db.session.commit()
            print("All alerts cleared successfully!")
            
        except Exception as e:
            print(f"Error clearing alerts: {e}")

if __name__ == '__main__':
    clear_all_alerts()