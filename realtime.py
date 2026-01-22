from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
import json
from datetime import datetime

class RealTimeManager:
    """Real-time updates manager for SmartTriage AI"""
    
    def __init__(self, socketio):
        self.socketio = socketio
        self.connected_users = {}  # user_id -> session_info
        self.patient_updates = {}  # patient_id -> update_count
        
    def handle_connect(self):
        """Handle new WebSocket connections"""
        user_id = request.sid
        self.connected_users[user_id] = {
            'connected_at': datetime.now().isoformat(),
            'ip_address': request.remote_addr,
            'user_agent': request.user_agent.string
        }
        
        print(f"🔗 User connected: {user_id}")
        emit('connection_status', {
            'status': 'connected',
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        }, room=user_id)
    
    def handle_disconnect(self):
        """Handle WebSocket disconnections"""
        user_id = request.sid
        if user_id in self.connected_users:
            del self.connected_users[user_id]
        
        print(f"🔌 User disconnected: {user_id}")
        emit('connection_status', {
            'status': 'disconnected',
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        }, room=user_id)
    
    def join_role_room(self, data):
        """Join role-specific room for targeted updates"""
        user_id = request.sid
        role = data.get('role', 'nurse')
        
        # Leave existing rooms
        for room_name in ['nurse', 'clinician', 'admin']:
            leave_room(room_name)
        
        # Join new room
        join_room(role)
        
        print(f"👥 User {user_id} joined {role} room")
        emit('room_joined', {
            'role': role,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        }, room=role)
    
    def handle_patient_update(self, data):
        """Handle patient status updates in real-time"""
        user_id = request.sid
        patient_id = data.get('patient_id')
        new_status = data.get('status')
        updated_by = data.get('updated_by', 'anonymous')
        
        # Update patient in database
        try:
            from models import init_models
            from database import db_manager
            
            models = init_models(db_manager.client)
            success = models['patient'].update_status(patient_id, new_status)
            
            if success:
                # Broadcast update to all connected users
                update_data = {
                    'patient_id': patient_id,
                    'new_status': new_status,
                    'updated_by': updated_by,
                    'timestamp': datetime.now().isoformat(),
                    'update_type': 'status_change'
                }
                
                # Send to general room
                emit('patient_update', update_data, broadcast=True)
                
                # Send to specific role rooms
                if new_status in ['in-progress', 'completed']:
                    emit('patient_update', update_data, room='clinician')
                
                if new_status in ['waiting', 'in-progress']:
                    emit('patient_update', update_data, room='nurse')
                
                print(f"🔄 Patient {patient_id} status updated to {new_status}")
                
                # Update analytics
                models['analytics'].record_patient_flow(
                    datetime.now(),
                    None,  # Will be determined from patient record
                    'status_change'
                )
            else:
                emit('error', {
                    'message': f'Failed to update patient {patient_id}',
                    'timestamp': datetime.now().isoformat()
                }, room=user_id)
                
        except Exception as e:
            emit('error', {
                'message': f'Patient update error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }, room=user_id)
    
    def handle_new_patient(self, data):
        """Handle new patient arrivals in real-time"""
        user_id = request.sid
        patient_data = data.get('patient_data')
        
        # Broadcast new patient to all relevant rooms
        patient_broadcast = {
            'patient_id': patient_data.get('patient_id'),
            'name': patient_data.get('name'),
            'age': patient_data.get('age'),
            'severity': patient_data.get('severity'),
            'timestamp': datetime.now().isoformat(),
            'update_type': 'new_patient'
        }
        
        # Send to all rooms
        emit('new_patient', patient_broadcast, broadcast=True)
        emit('new_patient', patient_broadcast, room='nurse')
        emit('new_patient', patient_broadcast, room='clinician')
        
        print(f"🆕 New patient: {patient_data.get('name')} ({patient_data.get('severity')})")
        
        # Update analytics
        try:
            from models import init_models
            from database import db_manager
            
            models = init_models(db_manager.client)
            models['analytics'].record_patient_flow(
                datetime.now(),
                patient_data.get('severity'),
                'arrival'
            )
        except Exception as e:
            print(f"Analytics update error: {e}")
    
    def handle_critical_alert(self, data):
        """Handle critical patient alerts"""
        user_id = request.sid
        patient_id = data.get('patient_id')
        alert_type = data.get('alert_type', 'critical_vitals')
        
        alert_data = {
            'patient_id': patient_id,
            'alert_type': alert_type,
            'message': data.get('message', 'Critical patient requires immediate attention'),
            'severity': 'RED',
            'timestamp': datetime.now().isoformat(),
            'update_type': 'critical_alert'
        }
        
        # High priority broadcast to all rooms
        emit('critical_alert', alert_data, broadcast=True)
        emit('critical_alert', alert_data, room='nurse')
        emit('critical_alert', alert_data, room='clinician')
        emit('critical_alert', alert_data, room='admin')
        
        print(f"🚨 CRITICAL ALERT: Patient {patient_id} - {data.get('message')}")
    
    def handle_system_update(self, data):
        """Handle system-wide updates"""
        update_type = data.get('update_type', 'general')
        message = data.get('message', 'System update')
        
        system_data = {
            'update_type': update_type,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'severity': data.get('severity', 'info')
        }
        
        # Broadcast to all connected users
        emit('system_update', system_data, broadcast=True)
        
        print(f"📢 System update: {message}")
    
    def get_connection_stats(self):
        """Get real-time connection statistics"""
        stats = {
            'connected_users': len(self.connected_users),
            'active_connections': list(self.connected_users.keys()),
            'server_time': datetime.now().isoformat(),
            'uptime': 'Server active'
        }
        
        emit('connection_stats', stats)
        return stats

def initialize_realtime(socketio):
    """Initialize real-time WebSocket functionality"""
    realtime = RealTimeManager(socketio)
    
    # Register WebSocket event handlers
    socketio.on_event('connect', realtime.handle_connect)
    socketio.on_event('disconnect', realtime.handle_disconnect)
    socketio.on_event('join_room', realtime.join_role_room)
    socketio.on_event('patient_update', realtime.handle_patient_update)
    socketio.on_event('new_patient', realtime.handle_new_patient)
    socketio.on_event('critical_alert', realtime.handle_critical_alert)
    socketio.on_event('system_update', realtime.handle_system_update)
    socketio.on_event('get_stats', realtime.get_connection_stats)
    
    return realtime
