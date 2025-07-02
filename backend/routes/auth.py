from flask import Blueprint, request, jsonify, current_app # 导入 Flask 中的核心组件 
from flask_jwt_extended import create_access_token
from models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['email', 'password', 'name']
        for field in required:
            value = data.get(field)
            if not value or (isinstance(value, str) and not value.strip()):  # 检查值是否为空或仅为空白字符
                return jsonify({'error': f'{field} is required and cannot be empty'}), 400
            
        # Password strength check
        if len(data['password']) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        
        # Create user
        user_model = User(current_app.db)
        user = user_model.create(
            email=data['email'],
            password=data['password'],
            name=data['name']
        )
        
        # Generate JWT token
        access_token = create_access_token(
            identity=str(user['_id']),
            additional_claims={'email': user['email']}
        )
        
        return jsonify({
            'message': 'User created successfully',
            'access_token': access_token,
            'user': {
                'id': str(user['_id']),
                'email': user['email'],
                'name': user['name'],
                'profile_complete': user['profile_complete']
            }
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Registration failed'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        # Authenticate user
        user_model = User(current_app.db)
        user = user_model.authenticate(data['email'], data['password'])
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate JWT token
        access_token = create_access_token(
            identity=str(user['_id']),
            additional_claims={'email': user['email']}
        )
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': {
                'id': str(user['_id']),
                'email': user['email'],
                'name': user['name'],
                'profile_complete': user.get('profile_complete', False)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Login failed'}), 500