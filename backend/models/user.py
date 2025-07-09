from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
import re
from utils import now_utc

class User:
    def __init__(self, db):
        self.collection = db.users
        
    def create(self, email, password, name):
        """Create a new user with hashed password"""
        # Validate email
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError("Invalid email format")
        
        # Check if user exists
        if self.collection.find_one({'email': email.lower()}):
            raise ValueError("User already exists")
        
        user_doc = {
            'email': email.lower(),
            'password_hash': generate_password_hash(password),
            'name': name,
            'created_at': now_utc,
            'updated_at': now_utc,
            'profile_complete': False,
            'active': True
        }
        
        result = self.collection.insert_one(user_doc)
        user_doc['_id'] = result.inserted_id
        return user_doc
    
    def authenticate(self, email, password):
        """Authenticate user and return user doc if valid"""
        user = self.collection.find_one({'email': email.lower()})
        if user and check_password_hash(user['password_hash'], password):
            return user
        return None
    
    def get_by_id(self, user_id):
        """Get user by ObjectId"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        return self.collection.find_one({'_id': user_id})
    
    def get_by_email(self, email):
        """Get user by email"""
        return self.collection.find_one({'email': email.lower()})