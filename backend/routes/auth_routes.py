from flask import Blueprint, jsonify, request

auth_bp = Blueprint('auth', __name__)

# TODO: Implement auth routes
@auth_bp.route('/', methods=['GET'])
def index():
    return jsonify({'module': 'auth', 'status': 'ready'})
