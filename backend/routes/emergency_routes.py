from flask import Blueprint, jsonify, request

emergency_bp = Blueprint('emergency', __name__)

# TODO: Implement emergency routes
@emergency_bp.route('/', methods=['GET'])
def index():
    return jsonify({'module': 'emergency', 'status': 'ready'})
