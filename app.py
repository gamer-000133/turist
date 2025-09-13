from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from models import db, Tourist, Location, Alert, Incident, Group, GroupMember
import qrcode
import io
import base64
import random
import string
from datetime import datetime
from functools import wraps

app = Flask(__name__)
import os
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///tourist.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def generate_tourist_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def generate_group_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def generate_qr_code(data):
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode()
    except Exception as e:
        print(f"QR Code generation error: {e}")
        return None

def police_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'police_logged_in' not in session:
            return redirect(url_for('police_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tourist')
def tourist_portal():
    return render_template('tourist.html')

@app.route('/register', methods=['POST'])
def register_tourist():
    data = request.get_json()
    tourist_id = generate_tourist_id()
    
    tourist = Tourist(
        name=data['name'],
        email=data['email'],
        phone=data['phone'],
        tourist_id=tourist_id
    )
    
    db.session.add(tourist)
    db.session.commit()
    
    qr_data = f"Tourist ID: {tourist_id}\nName: {data['name']}\nPhone: {data['phone']}"
    qr_code = generate_qr_code(qr_data)
    
    if qr_code is None:
        return jsonify({
            'success': True,
            'tourist_id': tourist_id,
            'qr_code': None,
            'message': 'Tourist registered but QR code generation failed'
        })
    
    return jsonify({
        'success': True,
        'tourist_id': tourist_id,
        'qr_code': qr_code
    })

@app.route('/login', methods=['POST'])
def login_tourist():
    data = request.get_json()
    tourist = Tourist.query.filter_by(tourist_id=data['tourist_id']).first()
    
    if tourist:
        session['tourist_id'] = tourist.tourist_id
        return jsonify({'success': True, 'name': tourist.name})
    return jsonify({'success': False, 'message': 'Invalid Tourist ID'})

@app.route('/update_location', methods=['POST'])
def update_location():
    data = request.get_json()
    location = Location(
        tourist_id=data['tourist_id'],
        latitude=data['latitude'],
        longitude=data['longitude']
    )
    db.session.add(location)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/panic_alert', methods=['POST'])
def panic_alert():
    data = request.get_json()
    
    # Get tourist name for better alert message
    tourist = Tourist.query.filter_by(tourist_id=data['tourist_id']).first()
    tourist_name = tourist.name if tourist else data['tourist_id']
    
    # Main alert for police - always create this
    alert = Alert(
        tourist_id=data['tourist_id'],
        alert_type='panic',
        message=f"🆘 EMERGENCY: {tourist_name} ({data['tourist_id']}) pressed panic button!",
        latitude=data.get('latitude'),
        longitude=data.get('longitude')
    )
    db.session.add(alert)
    
    # Create confirmation alert for sender
    sender_alert = Alert(
        tourist_id=data['tourist_id'],
        alert_type='user_alert',
        message=f"✓ Your emergency alert has been sent to police! Help is on the way.",
        latitude=data.get('latitude'),
        longitude=data.get('longitude')
    )
    db.session.add(sender_alert)
    
    # Send alert to group members if in group
    sender_group = GroupMember.query.filter_by(tourist_id=data['tourist_id']).first()
    group_message = ""
    if sender_group:
        group_members = GroupMember.query.filter_by(group_id=sender_group.group_id).all()
        for member in group_members:
            if member.tourist_id != data['tourist_id']:  # Don't alert the sender
                user_alert = Alert(
                    tourist_id=member.tourist_id,
                    alert_type='user_alert',
                    message=f"🚨 GROUP EMERGENCY: {tourist_name} needs help! Location: {data.get('latitude', 'Unknown')}, {data.get('longitude', 'Unknown')}",
                    latitude=data.get('latitude'),
                    longitude=data.get('longitude')
                )
                db.session.add(user_alert)
        group_message = " and group members"
    
    db.session.commit()
    return jsonify({'success': True, 'message': f'Emergency alert sent to police{group_message}!'})

@app.route('/police_login')
def police_login():
    return render_template('police_login.html')

@app.route('/police_auth', methods=['POST'])
def police_auth():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username == 'admin' and password == '12345':
        session['police_logged_in'] = True
        session['police_username'] = username
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid credentials!', 'error')
        return redirect(url_for('police_login'))

@app.route('/police_logout')
def police_logout():
    session.pop('police_logged_in', None)
    session.pop('police_username', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
@police_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/alerts_monitor')
@police_required
def alerts_monitor():
    return render_template('alerts_monitor.html')

@app.route('/api/tourists')
@police_required
def get_tourists():
    tourists = Tourist.query.all()
    return jsonify([{
        'id': t.id,
        'name': t.name,
        'tourist_id': t.tourist_id,
        'phone': t.phone,
        'created_at': t.created_at.strftime('%Y-%m-%d %H:%M')
    } for t in tourists])

@app.route('/api/locations')
@police_required
def get_locations():
    locations = Location.query.all()
    return jsonify([{
        'tourist_id': l.tourist_id,
        'latitude': l.latitude,
        'longitude': l.longitude,
        'timestamp': l.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for l in locations])

@app.route('/api/user_alerts/<tourist_id>')
def get_user_alerts(tourist_id):
    from datetime import timezone, timedelta
    
    alerts = Alert.query.filter_by(tourist_id=tourist_id, resolved=False).filter(
        Alert.alert_type.in_(['user_alert'])
    ).order_by(Alert.timestamp.desc()).limit(10).all()
    
    # Indian timezone (UTC+5:30)
    indian_tz = timezone(timedelta(hours=5, minutes=30))
    
    return jsonify([{
        'id': a.id,
        'alert_type': a.alert_type,
        'message': a.message,
        'latitude': a.latitude,
        'longitude': a.longitude,
        'timestamp': a.timestamp.replace(tzinfo=timezone.utc).astimezone(indian_tz).strftime('%H:%M:%S')
    } for a in alerts])

@app.route('/api/alerts')
@police_required
def get_alerts():
    # Police see panic alerts and group emergency alerts
    alerts = Alert.query.filter_by(resolved=False).filter(
        Alert.alert_type.in_(['panic'])
    ).order_by(Alert.timestamp.desc()).all()
    alert_data = []
    
    for a in alerts:
        # Get tourist details for each alert
        tourist = Tourist.query.filter_by(tourist_id=a.tourist_id).first()
        tourist_name = tourist.name if tourist else 'Unknown'
        tourist_phone = tourist.phone if tourist else 'N/A'
        
        # Indian timezone (UTC+5:30)
        from datetime import timezone, timedelta
        indian_tz = timezone(timedelta(hours=5, minutes=30))
        indian_time = a.timestamp.replace(tzinfo=timezone.utc).astimezone(indian_tz)
        
        alert_data.append({
            'id': a.id,
            'tourist_id': a.tourist_id,
            'tourist_name': tourist_name,
            'tourist_phone': tourist_phone,
            'alert_type': a.alert_type,
            'message': a.message,
            'latitude': a.latitude,
            'longitude': a.longitude,
            'timestamp': indian_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify(alert_data)

@app.route('/api/resolve_alert/<int:alert_id>', methods=['POST'])
@police_required
def resolve_alert(alert_id):
    alert = db.session.get(Alert, alert_id)
    if alert:
        alert.resolved = True
        
        # Also resolve related user alerts for the same incident
        related_alerts = Alert.query.filter_by(
            alert_type='user_alert',
            latitude=alert.latitude,
            longitude=alert.longitude,
            resolved=False
        ).all()
        
        for related_alert in related_alerts:
            if alert.tourist_id in related_alert.message:
                related_alert.resolved = True
        
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/create_incident', methods=['POST'])
@police_required
def create_incident():
    data = request.get_json()
    efir_number = f"FIR{random.randint(100000, 999999)}"
    
    incident = Incident(
        tourist_id=data['tourist_id'],
        incident_type=data['incident_type'],
        description=data['description'],
        efir_number=efir_number
    )
    db.session.add(incident)
    db.session.commit()
    
    return jsonify({'success': True, 'efir_number': efir_number})

@app.route('/api/incidents')
@police_required
def get_incidents():
    incidents = Incident.query.order_by(Incident.timestamp.desc()).all()
    return jsonify([{
        'id': i.id,
        'efir_number': i.efir_number,
        'tourist_id': i.tourist_id,
        'incident_type': i.incident_type,
        'description': i.description,
        'timestamp': i.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for i in incidents])

@app.route('/api/tourist_details/<tourist_id>')
@police_required
def get_tourist_details(tourist_id):
    tourist = Tourist.query.filter_by(tourist_id=tourist_id).first()
    if not tourist:
        return jsonify({'error': 'Tourist not found'}), 404
    
    # Get latest location
    latest_location = Location.query.filter_by(tourist_id=tourist_id).order_by(Location.timestamp.desc()).first()
    
    return jsonify({
        'tourist_id': tourist.tourist_id,
        'name': tourist.name,
        'email': tourist.email,
        'phone': tourist.phone,
        'created_at': tourist.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'latest_location': {
            'latitude': latest_location.latitude if latest_location else None,
            'longitude': latest_location.longitude if latest_location else None,
            'timestamp': latest_location.timestamp.strftime('%Y-%m-%d %H:%M:%S') if latest_location else None
        }
    })

# Group Management Routes
@app.route('/create_group', methods=['POST'])
def create_group():
    data = request.get_json()
    
    # Check if user is already in a group
    existing_membership = GroupMember.query.filter_by(tourist_id=data['tourist_id']).first()
    if existing_membership:
        return jsonify({'success': False, 'message': 'You must leave your current group first'})
    
    group_code = generate_group_code()
    
    group = Group(
        name=data['name'],
        group_code=group_code,
        created_by=data['tourist_id']
    )
    db.session.add(group)
    db.session.flush()
    
    # Add creator as first member
    member = GroupMember(
        group_id=group.id,
        tourist_id=data['tourist_id']
    )
    db.session.add(member)
    db.session.commit()
    
    return jsonify({'success': True, 'group_code': group_code})

@app.route('/join_group', methods=['POST'])
def join_group():
    data = request.get_json()
    group = Group.query.filter_by(group_code=data['group_code']).first()
    
    if not group:
        return jsonify({'success': False, 'message': 'Invalid group code'})
    
    # Check if already in any group
    existing_membership = GroupMember.query.filter_by(tourist_id=data['tourist_id']).first()
    if existing_membership:
        return jsonify({'success': False, 'message': 'You must leave your current group first'})
    
    # Add to new group
    member = GroupMember(
        group_id=group.id,
        tourist_id=data['tourist_id']
    )
    db.session.add(member)
    db.session.commit()
    
    return jsonify({'success': True, 'group_name': group.name})

@app.route('/api/group_locations/<tourist_id>')
def get_group_locations(tourist_id):
    # Get user's group first
    user_group = GroupMember.query.filter_by(tourist_id=tourist_id).first()
    if not user_group:
        return jsonify([])
    
    # Get all group members
    group_members = GroupMember.query.filter_by(group_id=user_group.group_id).all()
    locations = []
    
    for member in group_members:
        tourist = Tourist.query.filter_by(tourist_id=member.tourist_id).first()
        latest_location = Location.query.filter_by(tourist_id=member.tourist_id).order_by(Location.timestamp.desc()).first()
        
        if tourist and latest_location:
            locations.append({
                'tourist_id': member.tourist_id,
                'name': tourist.name,
                'latitude': latest_location.latitude,
                'longitude': latest_location.longitude,
                'timestamp': latest_location.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'is_group_member': True
            })
    
    return jsonify(locations)

@app.route('/api/my_group/<tourist_id>')
def get_my_group(tourist_id):
    group_member = GroupMember.query.filter_by(tourist_id=tourist_id).first()
    if not group_member:
        return jsonify({'has_group': False})
    
    group = db.session.get(Group, group_member.group_id)
    members = GroupMember.query.filter_by(group_id=group.id).all()
    
    member_list = []
    for member in members:
        tourist = Tourist.query.filter_by(tourist_id=member.tourist_id).first()
        if tourist:
            member_list.append({
                'tourist_id': member.tourist_id,
                'name': tourist.name,
                'joined_at': member.joined_at.strftime('%Y-%m-%d %H:%M')
            })
    
    return jsonify({
        'has_group': True,
        'group_name': group.name,
        'group_code': group.group_code,
        'members': member_list
    })

@app.route('/leave_group', methods=['POST'])
def leave_group():
    data = request.get_json()
    member = GroupMember.query.filter_by(tourist_id=data['tourist_id']).first()
    
    if member:
        db.session.delete(member)
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Not in any group'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)