from . import socketio
from flask import Blueprint,request,jsonify,session
from flask_login import login_user,login_required,logout_user,current_user
from .models import User,ChatRoom,Message
from . import db
import re
from flask_socketio import emit,join_room,disconnect,rooms

# from flask_bcrypt import Bcrypt

views=Blueprint('views',__name__)



@views.route('/register', methods=['POST'])
def register():
    if request.method =='POST':
        try:
            # Get JSON data from the request
            data = request.get_json()
            if not data:
                return jsonify(message='No JSON data provided in the request'), 400
            # Extract user input data
            email = data.get('email')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            password = data.get('password')
            confirm_password = data.get('confirm_password')
            # Validate input data
            if not (email and first_name and last_name and password and confirm_password):
                return jsonify(message='All fields are required'), 400

            # Check if the email already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return jsonify(message='Email already exists'), 400

            # Additional input data validation
            # Validate email using regex
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                return jsonify(message='Invalid email address'), 400

            # Validate first name using regex
            if not re.match(r'^[A-Za-z]+$', first_name):
                return jsonify(message='First name must contain only alphabetic characters'), 400

            # Validate last name using regex
            if not re.match(r'^[A-Za-z]+$', last_name):
                return jsonify(message='Last name must contain only alphabetic characters'), 400

            if password != confirm_password:
                return jsonify(message='Passwords do not match'), 400
            if len(password) < 7:
                return jsonify(message='Password must be at least 7 characters long'), 400

            # Hash the password before storing it
           
            # Create a new user
            new_user = User(email=email, first_name=first_name, last_name=last_name)
            new_user.set_password(password)

            # Add the user to the database
            db.session.add(new_user)
            db.session.commit()
            return jsonify(message='Registration successful'), 200
        except Exception as e:
            return jsonify(message='Failed to process the request: {}'.format(str(e))), 500
    return jsonify(message='Mthod no allowed: {}'.format(str(e))), 405
    

@views.route('/login',methods=['POST'])
def login():
    if request.method == "POST":
        try:
            # Get JSON data from the request
            data = request.get_json()
            if not data:
                return jsonify(message='No JSON data provided in the request'), 400
            # Extract user input data
            email = data.get('email')
            password = data.get('password')
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                login_user(user, remember=True)
                
                

                # Query chat rooms where the current user is a member
                # chatrooms = ChatRoom.query.filter(ChatRoom.users.contains(current_user)).all()
                # # Extract chat room names
                # chatroom_names = [f"{room.name}_{room.id}" for room in chatrooms]
                # u_session_id = session.get('_id')
                # # Emit the "loggedin" event with chatroom_names and user session ID
                # socketio.emit("loggedin", {'channel_names': chatroom_names, 'user_session_id': u_session_id})
                return jsonify(message='Login successfully'), 200
            else:
                return jsonify(message='Invalid credentials'), 401
        except Exception as e:
            return jsonify(message='Failed to process the request: {}'.format(str(e))), 500

    return jsonify(message='Only post method is allowed'), 400


@views.route('/logout', methods=['POST'])
def logout():
    try:
        logout_user()
        return jsonify(message="Logged out successfully"), 200
    except Exception as e:
        return jsonify(message=f"Error: {str(e)}"), 500 



@login_required 
@views.route('/chat/room/create', methods=['POST'])
def create_chatroom():
    usr=getattr(current_user, 'id', None)
    if usr!=None:
        try:
            data = request.get_json()
            chatroom_name = data.get('name') 
            # Check if chatroom name is empty
            if not chatroom_name:
                return jsonify(message='Chatroom name cannot be empty'), 400
            # Create the chatroom and add the currently logged-in user
            chatroom = ChatRoom(name=chatroom_name)
            chatroom.users.append(current_user)
            db.session.add(chatroom)
            db.session.commit()
            # socketio.emit('new_chatroom', {'name': chatroom.name, 'id': chatroom.id}, namespace='/chat')
            return jsonify(message='Chatroom created successfully'), 201
        except Exception as e:
            db.session.rollback()
            return jsonify(message=f"Error creating chatroom {e}"), 500
    else:
        return jsonify(message="Unauthorized"), 401




@login_required  
@views.route('/chat/room/<int:chat_id>/join', methods=['POST'])
def join_chat(chat_id):
    chat_room = ChatRoom.query.get(chat_id)
    usr=getattr(current_user, 'id', None)
    if usr!=None:
        if chat_room:
            user = current_user  
            if user not in chat_room.users:  # Check if the user is not already in the chat room
                chat_room.users.append(user)
                db.session.commit()  # Make sure to commit the changes to the database
                return jsonify(message="You have joined the room successfully"), 200
            else:
                return jsonify(message="You are already in this room"), 400
        else:
            return jsonify(message="Room not found"),404
    else:
        return jsonify(message="Unauthorized"), 401

    
@login_required 
@views.route('chat/rooms', methods=['GET'])
def chatrooms():
    chatrooms = ChatRoom.query.all()
    # Using list comprehension to create a list of chat room dictionaries
    chatroom_list = [
        {
            'id': chatroom.id,
            'name': chatroom.name,
            'users': [user.id for user in chatroom.users]  # List of user IDs in the chat room
        }
        for chatroom in chatrooms
    ]
    return jsonify(chatroom_list)


@login_required 
@views.route('chat/rooms/<int:room_id>', methods=['GET'])
def chatroom(room_id):
    chatroom = ChatRoom.query.get_or_404(room_id) 
     # incase messages are required too
    # messages = Message.query.filter_by(room_id=room_id).all()
    
    # Create a dictionary for the chat room
    chatroom_dict = {
        'id': chatroom.id,
        'name': chatroom.name,
        'users': [ {
            'id':user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
        } for user in chatroom.users],     
           
        #       'messages': [{
        #     'id': message.id,
        #     'text': message.text,
        #     'sender_id': message.sender_id,
        #     'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S')
        # } for message in messages]

    }
    return jsonify(chatroom_dict)


@login_required
@views.route('/chat/rooms/<int:room_id>/messages',methods=['GET','POST'])
def message(room_id):
    if request.method == "GET":
                from sqlalchemy import desc
                messages = Message.query.filter_by(room_id=room_id).order_by(desc(Message.created_at)).all()
                messages=[{
                    'id':message.id,
                    'text':message.text,
                    'sender':message.sender_id
                } for message in messages]
                return jsonify(messages)
    if request.method=='POST':
        usr=getattr(current_user, 'id', None)
        if usr!=None:
            try:
                data = request.get_json()
                text = data.get('message_text')
                sender_id = current_user.get_id()
                if not text:
                    return jsonify(message='Message text cannot be empty'), 400
                # Check if the chat room exists and the current user is a member
                chatroom = ChatRoom.query.get_or_404(room_id)
                if current_user not in chatroom.users:
                    return jsonify(message='You are not a member of this chat room'), 403

                # Create a new message
                message = Message(text=text, room_id=room_id, sender_id=sender_id)
                db.session.add(message)
                db.session.commit()

                # Get the IDs of users in the chat room
                chatroom_user_ids = {user.id for user in chatroom.users}

                # get the connected users
                active_users = session.get('active_users', {})

                receivers = {user_id: sid for user_id, sid in active_users.items() if user_id in chatroom_user_ids}
                # Extract the room names from the receivers dictionary
                rooms = [sid for sid in receivers.values()]
                # Broadcast the message to the receivers
                emit('new_message', {'message': message.text}, room=rooms, namespace='/chat')

                return jsonify(message='Message sent successfully'), 200
            except Exception as e:
                return jsonify(message='Failed to send the message: {}'.format(str(e))), 500
        else:
            return jsonify(message="UnAuthorize"),401
        
       

@socketio.on('connect')
def handle_connect():
    # this is for debugging purposes
    # user=User.query.filter_by(email="asif1@gmail.com").first()
    # print(user.email)
    # login_user(user)

    usr=getattr(current_user, 'id', None)
    if usr!=None:
        user_id = current_user.id
        active_users = session.get('active_users', {})
        if user_id not in active_users:
            active_users[user_id] = request.sid
            session['active_users'] = active_users
    else:
        disconnect()

@socketio.on('disconnect')
def handle_disconnect():
    user_id = getattr(current_user, 'id', None)
    if user_id is not None:
        active_users = session.get('active_users', {})
        if user_id in active_users:
            del active_users[user_id]
            session['active_users'] = active_users





       
# @socketio.on('connect')
# def create_rooms(data):
#     # Check if user is authenticated
#     if not current_user.is_authenticated:
#         disconnect()
#         return jsonify({'message': 'Unauthorized'}), 401
#     try:
#         user_session_id = request.sid
#         user_channel_names = data['channel_names']
#         user_channel_names = [channel.strip() for channel in user_channel_names.split(",")]
#         live_rooms = rooms()
#         # Check for new rooms to create
#         for channel_name in user_channel_names:
#             room_name = f'{channel_name}'
#             if channel_name not in live_rooms:
#                 join_room(room_name)
#                 live_rooms.append(room_name)
#         # Join user to rooms    
#         for room_name in user_channel_names:
#             join_room(room_name, sid=user_session_id)
#     except KeyError:
#         return jsonify({'message': 'Missing channel_names in data'}), 400
#     except Exception as e:
#         return jsonify({'message': 'Server error: {}'.format(str(e))}), 500
