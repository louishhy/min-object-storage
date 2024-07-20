"""
Blueprints for testing purposes and not related to core functionalities.
"""

from flask import Blueprint, request, jsonify
import time

test_bp = Blueprint("test_bp", __name__)

@test_bp.route("/sleep_test", methods=['GET'])
def sleep_test():
    delay = int(request.args.get('delay', 10))
    # Sim a long handling query
    time.sleep(delay)
    return jsonify(
        {"message": f"Sleeping test completed, delay: {delay}s"}
    )
