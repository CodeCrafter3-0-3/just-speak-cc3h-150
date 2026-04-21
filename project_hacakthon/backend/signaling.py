from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request

socketio = SocketIO()

@socketio.on('join')
def on_join(data):
    room = data['appointment_id']
    join_room(room)
    emit('status', {'msg': request.sid + ' has entered the room.'}, room=room)

@socketio.on('leave')
def on_leave(data):
    room = data['appointment_id']
    leave_room(room)
    emit('status', {'msg': request.sid + ' has left the room.'}, room=room)

@socketio.on('offer')
def handle_offer(data):
    room = data.get('appointment_id')
    # relay offer to others in the room
    emit('offer', data, room=room, include_self=False)

@socketio.on('answer')
def handle_answer(data):
    room = data.get('appointment_id')
    emit('answer', data, room=room, include_self=False)

@socketio.on('ice_candidate')
def handle_ice_candidate(data):
    room = data.get('appointment_id')
    emit('ice_candidate', data, room=room, include_self=False)
