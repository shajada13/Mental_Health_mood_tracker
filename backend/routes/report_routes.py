from flask import Blueprint, jsonify, request

report_bp = Blueprint('report', __name__)

# TODO: Implement report routes
@report_bp.route('/', methods=['GET'])
def index():
    return jsonify({'module': 'report', 'status': 'ready'})
