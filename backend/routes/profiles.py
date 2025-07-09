from flask import Blueprint, request, jsonify, current_app # 导入Flask 
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from models.user import User
from datetime import datetime

profiles_bp = Blueprint('profiles', __name__) # 创建 blueprint 

@profiles_bp.route('/me', methods=['GET']) # 获取认证的用户资料并且处理get 请求
@jwt_required()
def get_my_profile():
    """Get current user's profile"""
    user_id = get_jwt_identity() # 提取用户ID
    user_model = User(current_app.db) # 提取用户模型
    
    user = user_model.get_by_id(user_id) # 根据ID从数据库获取用户文档
    if not user: # 如果未找到用户则报错 
        return jsonify({'error': 'User not found'}), 404
    
    # Return profile data
    profile_data = { # 将Object ID 转为string，JSON格式化后返回
        'id': str(user['_id']),
        'email': user['email'],
        'name': user['name'],
        'profile_complete': user.get('profile_complete', False),
        'created_at': user['created_at'],
        'profile': user.get('profile', {})
    }
    
    return jsonify(profile_data), 200

@profiles_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_my_profile():
    """Update current user's profile"""
    user_id = get_jwt_identity()
    user_model = User(current_app.db)
    data = request.get_json()
    
    try:
        # Update profile
        success = user_model.update_profile(user_id, data)
        
        if success:
            # Get updated user data
            updated_user = user_model.get_public_profile(user_id)
            return jsonify({
                'message': 'Profile updated successfully',
                'profile': updated_user
            }), 200
        else:
            return jsonify({'error': 'Failed to update profile'}), 400
            
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Profile update failed'}), 500