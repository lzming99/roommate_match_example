from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from bson import ObjectId
import re

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
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc),
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
    
    def update_profile(self, user_id, profile_data):
        """Update user profile information"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        # Validate NYC area (simplified - you can enhance with proper geocoding)
        allowed_states = ['NY', 'NJ']
        if profile_data.get('state') not in allowed_states:
            raise ValueError("Service area limited to NYC and New Jersey")
        
        update_data = {
            'updated_at': datetime.utcnow(),
            'profile_complete': True,
            'profile': {
                'age': profile_data.get('age'),
                'gender': profile_data.get('gender'),
                'occupation': profile_data.get('occupation'),
                'bio': profile_data.get('bio', ''),
                'budget_min': profile_data.get('budget_min'),
                'budget_max': profile_data.get('budget_max'),
                'move_in_date': profile_data.get('move_in_date'),
                'location': {
                    'city': profile_data.get('city'),
                    'state': profile_data.get('state'),
                    'neighborhoods': profile_data.get('neighborhoods', []),
                    'max_commute_mins': profile_data.get('max_commute_mins', 45)
                },
                'lifestyle': {
                    'smoking': profile_data.get('smoking', False),
                    'pets': profile_data.get('pets', 'none'),  # none, cat, dog, other
                    'cleanliness': profile_data.get('cleanliness', 'moderate'),  # messy, moderate, neat
                    'schedule': profile_data.get('schedule', 'regular'),  # early_bird, night_owl, regular
                    'guests': profile_data.get('guests', 'occasional'),  # never, occasional, frequent
                    'noise_level': profile_data.get('noise_level', 'moderate')  # quiet, moderate, social
                },
                'tags': profile_data.get('tags', [])  # interests/hobbies
            }
        }
        
        result = self.collection.update_one(
            {'_id': user_id},
            {'$set': update_data}
        )
        
        return result.modified_count > 0
    
    def get_public_profile(self, user_id):
        """Get user profile without sensitive data"""
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        return {
            '_id': str(user['_id']),
            'name': user['name'],
            'created_at': user['created_at'],
            'profile': user.get('profile', {}),
            'profile_complete': user.get('profile_complete', False)
        }