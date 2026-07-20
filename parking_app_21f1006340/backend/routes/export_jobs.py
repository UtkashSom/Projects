from flask import Blueprint, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from celery.result import AsyncResult
from celery_worker import celery

export_bp = Blueprint("export", __name__)

@export_bp.route("/user/history/export", methods=["POST"])
@jwt_required()
def export_user_history():
    claims = get_jwt()
    if claims.get("is_admin"):
        return jsonify({"msg": "Access denied, users only"}), 403
    user_id = int(get_jwt_identity())
    task = celery.send_task("tasks.export_user_history_csv", args=[user_id])
    return jsonify({"task_id": task.id})

@export_bp.route("/admin/reservations/export", methods=["POST"])
@jwt_required()
def export_all_reservations():
    claims = get_jwt()
    if not claims.get("is_admin"):
        return jsonify({"msg": "Access denied, admins only"}), 403
    task = celery.send_task("tasks.export_all_reservations_csv")
    return jsonify({"task_id": task.id})

@export_bp.route("/export/status/<task_id>", methods=["GET"])
@jwt_required()
def export_status(task_id):
    result = AsyncResult(task_id, app=celery)
    state = result.state
    if state in {"PENDING", "STARTED", "RETRY"}:
        return jsonify({"state": state, "ready": False})
    if state == "SUCCESS":
        return jsonify({"state": state, "ready": True})
    return jsonify({"state": state, "ready": False, "error": str(result.info)}), 500

@export_bp.route("/export/result/<task_id>", methods=["GET"])
@jwt_required()
def export_result(task_id):
    result = AsyncResult(task_id, app=celery)
    if not result.ready():
        return jsonify({"state": result.state, "ready": False}), 202
    data = result.get() or ""
    headers = {
        "Content-Disposition": f"attachment; filename=export_{task_id}.csv"
    }
    return Response(data, mimetype="text/csv", headers=headers)
