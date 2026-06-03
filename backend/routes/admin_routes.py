from flask import Blueprint, jsonify, request

admin_bp = Blueprint('admin', __name__)

# TODO: Implement admin routes
@admin_bp.route('/', methods=['GET'])
def index():
    return jsonify({'module': 'admin', 'status': 'ready'})
