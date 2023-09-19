from . import db
from datetime import datetime
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()



# User-ChatRoom association table
user_chatroom = db.Table('user_chatroom',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('chatroom_id', db.Integer, db.ForeignKey('chat_room.id'))
)


# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(55))
    last_name = db.Column(db.String(55))
    message = db.relationship('Message', backref='user')

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
    
    def is_active(self):
        
        return True 
    
    def get_id(self):
        # Return the unique identifier for the user, typically the 'id' field
        return str(self.id)
    

# ChatRoom model
class ChatRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    users = db.relationship('User', secondary='user_chatroom', backref='chat_rooms')
    message = db.relationship('Message', backref='chat_room')
  
  
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    room_id = db.Column(db.Integer, db.ForeignKey('chat_room.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
