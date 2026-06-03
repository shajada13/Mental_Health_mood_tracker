from flask import Blueprint, jsonify, request

ai_bp = Blueprint('ai', __name__)

# TODO: Implement ai routes
@ai_bp.route('/', methods=['GET'])
def index():
    return jsonify({'module': 'ai', 'status': 'ready'})
