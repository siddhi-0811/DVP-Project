import os
import json
import random
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, send_file
from dotenv import load_dotenv
from database import init_db, get_db, DB_KIND
from services import (
    get_destinations, get_destination, get_dashboard_stats, get_analytics,
    recommend_destinations, build_itinerary, save_trip, get_favorites,
    toggle_favorite, save_quiz_result, get_trip_history, get_saved_trip, 
    update_trip, delete_trip
)
from exports import make_csv, make_pdf

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-this-development-secret")
init_db()

def visitor_id():
    if "visitor_id" not in session:
        session["visitor_id"] = str(uuid.uuid4())
    return session["visitor_id"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/destinations")
def destinations_page():
    return render_template("destinations.html")

@app.route("/planner")
def planner_page():
    return render_template("planner.html")

@app.route("/analytics")
def analytics_page():
    return render_template("analytics.html")

@app.route("/quiz")
def quiz_page():
    return render_template("quiz.html")

@app.route("/favorites")
def favorites_page():
    return render_template("favorites.html")

@app.route("/history")
def history_page():
    return render_template("history.html")

@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "database": DB_KIND})

@app.route("/api/dashboard")
def dashboard():
    return jsonify(get_dashboard_stats())

@app.route("/api/destinations")
def api_destinations():
    filters = {
        "q": request.args.get("q", "").strip(),
        "state": request.args.get("state", "").strip(),
        "type": request.args.get("type", "").strip(),
        "min_rating": request.args.get("min_rating", "").strip(),
        "max_fee": request.args.get("max_fee", "").strip(),
        "sort": request.args.get("sort", "rating").strip()
    }
    return jsonify(get_destinations(filters))

@app.route("/api/destinations/<int:destination_id>")
def api_destination(destination_id):
    item = get_destination(destination_id)
    if not item:
        return jsonify({"error": "Destination not found"}), 404
    return jsonify(item)

@app.route("/api/filters")
def filters():
    rows = get_destinations({})
    states = sorted({r["state"] for r in rows if r.get("state")})
    types = sorted({r["type"] for r in rows if r.get("type")})
    return jsonify({"states": states, "types": types})

@app.route("/api/recommendations")
def recommendations():
    prefs = {
        "type": request.args.get("type", ""),
        "budget": request.args.get("budget", "500"),
        "hours": request.args.get("hours", "6"),
        "rating": request.args.get("rating", "4.0"),
        "state": request.args.get("state", "")
    }
    return jsonify(recommend_destinations(prefs))

@app.route("/api/plan", methods=["POST"])
def create_plan():
    data = request.get_json(silent=True) or {}
    result = build_itinerary(data)
    if not result["items"]:
        return jsonify(result), 400
    plan_id = save_trip(visitor_id(), data, result)
    result["plan_id"] = plan_id
    session["latest_plan"] = result
    return jsonify(result)

@app.route("/api/favorites")
def favorites():
    return jsonify(get_favorites(visitor_id()))

@app.route("/api/favorites/<int:destination_id>", methods=["POST", "DELETE"])
def favorite_action(destination_id):
    if request.method == "DELETE":
        toggle_favorite(visitor_id(), destination_id, remove=True)
        return jsonify({"saved": False})
    saved = toggle_favorite(visitor_id(), destination_id)
    return jsonify({"saved": saved})

@app.route("/api/trip-history")
def trip_history():
    return jsonify(get_trip_history(visitor_id()))

@app.route("/api/trip-history/<int:trip_id>")
def saved_trip_details(trip_id):
    trip = get_saved_trip(visitor_id(), trip_id)

    if not trip:
        return jsonify({"error": "Trip not found"}), 404

    return jsonify(trip)


@app.route("/api/trip-history/<int:trip_id>", methods=["PUT"])
def update_saved_trip(trip_id):
    data = request.get_json(silent=True) or {}

    try:
        updated = update_trip(visitor_id(), trip_id, data)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    if not updated:
        return jsonify({"error": "Trip not found"}), 404

    return jsonify({"success": True, "message": "Itinerary updated successfully"})


@app.route("/api/trip-history/<int:trip_id>", methods=["DELETE"])
def delete_saved_trip(trip_id):
    deleted = delete_trip(visitor_id(), trip_id)

    if not deleted:
        return jsonify({"error": "Trip not found"}), 404

    return jsonify({
        "success": True,
        "message": "Itinerary deleted successfully"
    })


@app.route("/api/quiz/questions")
def quiz_questions():
    rows = get_destinations({})
    random.shuffle(rows)
    questions = []
    for item in rows[:8]:
        distractors = [x for x in rows if x["id"] != item["id"] and x.get("city")]
        options = [item["name"]]
        seen = {item["name"]}
        for other in distractors:
            if other["name"] not in seen:
                options.append(other["name"])
                seen.add(other["name"])
            if len(options) == 4:
                break
        random.shuffle(options)
        questions.append({
            "id": item["id"],
            "question": f"Which attraction is located in {item.get('city') or 'this destination'}?",
            "hint": f"Category: {item.get('type') or 'Tourist attraction'}",
            "options": options,
            "answer": item["name"],
            "fact": f"{item['name']} is listed in {item.get('city') or 'India'}."
        })
    return jsonify(questions)

@app.route("/api/quiz/submit", methods=["POST"])
def quiz_submit():
    data = request.get_json(silent=True) or {}
    score = max(0, int(data.get("score", 0)))
    total = max(0, int(data.get("total", 0)))
    save_quiz_result(visitor_id(), score, total)
    return jsonify({"saved": True, "score": score, "total": total})

@app.route("/api/analytics")
def analytics():
    return jsonify(get_analytics())

@app.route("/api/export/destinations.csv")
def export_destinations():
    rows = get_destinations({
        "q": request.args.get("q", ""),
        "state": request.args.get("state", ""),
        "type": request.args.get("type", ""),
        "min_rating": request.args.get("min_rating", ""),
        "max_fee": request.args.get("max_fee", ""),
        "sort": request.args.get("sort", "rating")
    })
    path = make_csv(rows)
    return send_file(path, as_attachment=True, download_name="explore_india_destinations.csv")

@app.route("/api/export/plan/<int:plan_id>.pdf")
def export_plan(plan_id):
    # The latest generated plan is kept in the user's session for convenient export.
    plan = session.get("latest_plan")
    if not plan or plan.get("plan_id") != plan_id:
        return jsonify({"error": "Plan not found in this browser session. Generate the plan again."}), 404
    path = make_pdf(plan)
    return send_file(path, as_attachment=True, download_name="explore_india_trip_plan.pdf")

@app.after_request
def remember_latest_plan(response):
    return response

if __name__ == "__main__":
    app.run(debug=True)
