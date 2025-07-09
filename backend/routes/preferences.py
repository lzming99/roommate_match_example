from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from utils import now_utc

preferences_bp = Blueprint('preferences', __name__)

def _clean_dict(d):
    """ remove value == None """
    if not isinstance(d, dict):
        return d
    return {k: _clean_dict(v) for k, v in d.items() if v is not None}

@preferences_bp.route('/', methods=['GET'])
@jwt_required()
def get_preferences():
    """Get current user's roommate preferences"""
    user_id = ObjectId(get_jwt_identity())
    
    preferences = current_app.db.preferences.find_one({'user_id': user_id})
    if preferences:
        preferences['_id'] = str(preferences['_id'])
        preferences['user_id'] = str(preferences['user_id'])
    
    return jsonify(preferences or {}), 200

@preferences_bp.route('/', methods=['POST', 'PUT'])
@jwt_required()
def save_preferences():
    user_id = ObjectId(get_jwt_identity())
    data = request.get_json() or {}

    preferences_doc = { # allow none, clean up later, _id for internal ref. 
        'user_id': user_id,
        'updated_at': now_utc(),

        # 1. USER INFO
        'personal_profile': {
            'age': data.get('age'),
            'gender': data.get('gender'),
            'occupation': data.get('occupation'),
            'lifestyle': {
                'smoking': data.get('smoking'),
                'drinking': data.get('drinking'),
                'partying': data.get('partying'),
                'schedule': data.get('schedule'),
                'partner_stay_over': data.get('partner_stay_over'),
            }
        },

        # 2. USER EXPT HOUSE
        'housing_preferences': {
            'locations': data.get('locations'),
            'is_flexible_locations': data.get('is_flexible_locations', False),
            'budget': data.get('budget'),
            'is_flexible_budget': data.get('is_flexible_budget', False),
            'lease_term': {
                'start': data.get('lease_start'),
                'end': data.get('lease_end'),
            },
            'is_flexible_lease_term': data.get('is_flexible_lease_term', False),
            'room_choice': data.get('room_choice'),
            'is_flexible_room_choice': data.get('is_flexible_room_choice', False),
        },

        # 3. USER EXPT ROOMMATE
        'roommate_preferences': {
            'age_range': {
                'min': data.get('pref_age_min'),
                'max': data.get('pref_age_max'),
                'is_flexible': data.get('is_flexible_age_range', False)
            },
            
            'gender': data.get('pref_gender'),
            'lifestyle': {
                'pets_ok': data.get('pets_ok'),
                'smoking_ok': data.get('pref_smoking_ok'),
                'drinking_ok': data.get('pref_drinking_ok'),
                'partying_ok': data.get('pref_partying_ok'),
                'noise_level': data.get('pref_noise_level'),
                'quiet_hours': data.get('pref_quiet_hours'),
                'is_flexible_quiet_hours': data.get('is_flexible_quiet_hours', False),
            }
        }
    }

    clean_doc = _clean_dict(preferences_doc) # 去除 None，避免覆盖已有值
    set_doc = {k: v for k, v in clean_doc.items() if k != 'user_id'} # Remove user_id from $set，prevent conflict with $setOnInsert

    current_app.db.preferences.update_one( # Upsert
        {'user_id': user_id},
        {'$set': set_doc, '$setOnInsert': {'user_id': user_id}},
        upsert=True
    )

    current_app.db.users.update_one( # db 更新 user 表
        {'_id': user_id},
        {'$set': {'profile_complete': True, 'updated_at': now_utc()}}
    )

    saved = current_app.db.preferences.find_one({'user_id': user_id}, {'_id': 0, 'user_id': 0}) # 读出含_id最新文档

    return jsonify({
        'message': 'Preferences saved successfully',
        'preferences': saved
    }), 200