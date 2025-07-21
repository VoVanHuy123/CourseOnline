from flask import Blueprint, jsonify, request
def get_field(name):
    return request.form.get(name) or request.json.get(name)