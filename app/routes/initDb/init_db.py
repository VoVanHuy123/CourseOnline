from flask import Blueprint, jsonify, request
from app.extensions import db

init_bp = Blueprint("init_db",__name__,url_prefix="/init_dbs")
@init_bp.route('/', methods=['GET'])
def init_db():
    try:
        db.create_all()
        return jsonify({'message': 'Database tables created successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
def init_register_docs(docs):
    docs.register(init_db, blueprint='init_db')