import sqlite3
from datetime import datetime, timedelta
import time
import random

class AIAnomalyDetector:
    def __init__(self, db_path='tourist.db'):
        self.db_path = db_path
    
    def get_db_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def detect_inactivity(self):
        """Detect tourists inactive for more than 15 minutes"""
        conn = self.get_db_connection()
        
        # Get latest location for each tourist
        query = """
        SELECT l.tourist_id, MAX(l.timestamp) as last_seen
        FROM location l
        GROUP BY l.tourist_id
        HAVING datetime(last_seen) < datetime('now', '-15 minutes')
        """
        
        inactive_tourists = conn.execute(query).fetchall()
        
        for tourist in inactive_tourists:
            # Check if alert already exists
            existing_alert = conn.execute(
                "SELECT id FROM alert WHERE tourist_id = ? AND alert_type = 'inactivity' AND resolved = 0",
                (tourist['tourist_id'],)
            ).fetchone()
            
            if not existing_alert:
                conn.execute(
                    "INSERT INTO alert (tourist_id, alert_type, message) VALUES (?, ?, ?)",
                    (tourist['tourist_id'], 'inactivity', f"Tourist {tourist['tourist_id']} inactive for >15 minutes")
                )
                print(f"🚨 INACTIVITY ALERT: Tourist {tourist['tourist_id']} inactive since {tourist['last_seen']}")
        
        conn.commit()
        conn.close()
    
    def detect_route_deviation(self):
        """Simulate route deviation detection"""
        conn = self.get_db_connection()
        
        # Get recent locations
        query = """
        SELECT tourist_id, latitude, longitude, timestamp
        FROM location
        WHERE datetime(timestamp) > datetime('now', '-1 hour')
        ORDER BY tourist_id, timestamp DESC
        """
        
        locations = conn.execute(query).fetchall()
        
        # Group by tourist
        tourist_locations = {}
        for loc in locations:
            if loc['tourist_id'] not in tourist_locations:
                tourist_locations[loc['tourist_id']] = []
            tourist_locations[loc['tourist_id']].append(loc)
        
        for tourist_id, locs in tourist_locations.items():
            if len(locs) >= 3:
                # Simple deviation detection: if tourist moves >5km from starting point
                start_lat, start_lng = locs[-1]['latitude'], locs[-1]['longitude']
                current_lat, current_lng = locs[0]['latitude'], locs[0]['longitude']
                
                # Rough distance calculation (not precise, for demo)
                distance = ((current_lat - start_lat) ** 2 + (current_lng - start_lng) ** 2) ** 0.5
                
                if distance > 0.05:  # Roughly 5km
                    existing_alert = conn.execute(
                        "SELECT id FROM alert WHERE tourist_id = ? AND alert_type = 'deviation' AND resolved = 0",
                        (tourist_id,)
                    ).fetchone()
                    
                    if not existing_alert:
                        conn.execute(
                            "INSERT INTO alert (tourist_id, alert_type, message, latitude, longitude) VALUES (?, ?, ?, ?, ?)",
                            (tourist_id, 'deviation', f"Tourist {tourist_id} deviated from expected route", current_lat, current_lng)
                        )
                        print(f"🚨 ROUTE DEVIATION: Tourist {tourist_id} moved significantly from starting point")
        
        conn.commit()
        conn.close()
    
    def simulate_random_alerts(self):
        """Generate random alerts for demonstration"""
        conn = self.get_db_connection()
        
        # Get active tourists
        tourists = conn.execute("SELECT tourist_id FROM tourist").fetchall()
        
        if tourists and random.random() < 0.3:  # 30% chance
            tourist = random.choice(tourists)
            alert_types = ['suspicious_activity', 'geo_fence_breach', 'speed_anomaly']
            alert_type = random.choice(alert_types)
            
            conn.execute(
                "INSERT INTO alert (tourist_id, alert_type, message) VALUES (?, ?, ?)",
                (tourist['tourist_id'], alert_type, f"AI detected {alert_type.replace('_', ' ')} for tourist {tourist['tourist_id']}")
            )
            print(f"🤖 AI ALERT: {alert_type} detected for tourist {tourist['tourist_id']}")
        
        conn.commit()
        conn.close()
    
    def run_monitoring(self):
        """Main monitoring loop"""
        print("🤖 AI Anomaly Detection Engine Started")
        print("Monitoring for inactivity, route deviations, and other anomalies...")
        
        while True:
            try:
                self.detect_inactivity()
                self.detect_route_deviation()
                self.simulate_random_alerts()
                
                print(f"✅ Monitoring cycle completed at {datetime.now().strftime('%H:%M:%S')}")
                time.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                print("\n🛑 AI Engine stopped by user")
                break
            except Exception as e:
                print(f"❌ Error in AI engine: {e}")
                time.sleep(30)

if __name__ == "__main__":
    detector = AIAnomalyDetector()
    detector.run_monitoring()