import json
from database import get_db, DB_KIND

def _dict(row):
    if row is None:
        return None
    return dict(row)

def _all(sql, params=()):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    if DB_KIND == "mysql":
        cols = [c[0] for c in cur.description]
        result = [dict(zip(cols, r)) for r in rows]
    else:
        result = [dict(r) for r in rows]
    cur.close()
    conn.close()
    return result

def _one(sql, params=()):
    rows = _all(sql, params)
    return rows[0] if rows else None

def _number(value, default=0):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (ValueError, TypeError):
        return default

def _normalize(row):
    if not row:
        return None
    return {
        "id": int(row["id"]),
        "zone": row.get("zone") or "",
        "state": row.get("state") or "",
        "city": row.get("city") or "",
        "name": row.get("name") or "Unnamed attraction",
        "type": row.get("attraction_type") or "Other",
        "establishment_year": row.get("establishment_year") or "",
        "visit_hours": _number(row.get("visit_hours"), 1),
        "rating": _number(row.get("rating"), 0),
        "entrance_fee": _number(row.get("entrance_fee"), 0),
        "airport_nearby": row.get("airport_nearby") or "Not specified",
        "weekly_off": row.get("weekly_off") or "Not specified",
        "significance": row.get("significance") or "",
        "dslr_allowed": row.get("dslr_allowed") or "Not specified",
        "review_lakhs": _number(row.get("review_lakhs"), 0),
        "best_time": row.get("best_time") or "Not specified"
    }

def get_destinations(filters=None):
    filters = filters or {}
    clauses, params = [], []
    q = filters.get("q", "")
    if q:
        like = f"%{q}%"
        clauses.append("(name LIKE %s OR city LIKE %s OR state LIKE %s OR attraction_type LIKE %s)" if DB_KIND == "mysql" else "(name LIKE ? OR city LIKE ? OR state LIKE ? OR attraction_type LIKE ?)")
        params.extend([like] * 4)
    for key, col in [("state", "state"), ("type", "attraction_type")]:
        val = filters.get(key, "")
        if val:
            clauses.append(f"{col} = {'%s' if DB_KIND == 'mysql' else '?'}")
            params.append(val)
    min_rating = filters.get("min_rating", "")
    if min_rating != "":
        clauses.append(f"rating >= {'%s' if DB_KIND == 'mysql' else '?'}")
        params.append(_number(min_rating))
    max_fee = filters.get("max_fee", "")
    if max_fee != "":
        clauses.append(f"entrance_fee <= {'%s' if DB_KIND == 'mysql' else '?'}")
        params.append(_number(max_fee, 1000000))
    sort_map = {
        "rating": "rating DESC, review_lakhs DESC",
        "fee": "entrance_fee ASC",
        "name": "name ASC",
        "duration": "visit_hours ASC",
        "reviews": "review_lakhs DESC"
    }
    order = sort_map.get(filters.get("sort"), sort_map["rating"])
    sql = "SELECT * FROM destinations"
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY " + order
    return [_normalize(r) for r in _all(sql, params)]

def get_destination(destination_id):
    row = _one("SELECT * FROM destinations WHERE id = " + ("%s" if DB_KIND == "mysql" else "?"), (destination_id,))
    return _normalize(row)

def get_dashboard_stats():
    row = _one("""SELECT COUNT(*) AS total, COUNT(DISTINCT state) AS states,
        COUNT(DISTINCT attraction_type) AS types, AVG(rating) AS avg_rating,
        AVG(entrance_fee) AS avg_fee FROM destinations""") or {}
    top = get_destinations({"sort": "rating"})[:5]
    return {
        "total": int(row.get("total") or 0),
        "states": int(row.get("states") or 0),
        "types": int(row.get("types") or 0),
        "avg_rating": round(_number(row.get("avg_rating")), 2),
        "avg_fee": round(_number(row.get("avg_fee")), 2),
        "top_destinations": top
    }

def get_analytics():
    by_state = _all("""SELECT state AS label, COUNT(*) AS count, AVG(rating) AS rating,
        AVG(entrance_fee) AS fee FROM destinations WHERE state IS NOT NULL
        GROUP BY state ORDER BY count DESC LIMIT 12""")
    by_type = _all("""SELECT attraction_type AS label, COUNT(*) AS count FROM destinations
        WHERE attraction_type IS NOT NULL GROUP BY attraction_type ORDER BY count DESC LIMIT 12""")
    fee_rating = _all("""SELECT * FROM destinations
        WHERE rating IS NOT NULL ORDER BY review_lakhs DESC LIMIT 60""")
    top_reviewed = get_destinations({"sort": "reviews"})[:8]
    return {
        "by_state": [{"label": r.get("label") or "Unknown", "count": int(r.get("count") or 0),
                      "rating": round(_number(r.get("rating")), 2), "fee": round(_number(r.get("fee")), 2)} for r in by_state],
        "by_type": [{"label": r.get("label") or "Other", "count": int(r.get("count") or 0)} for r in by_type],
        "fee_rating": [{"name": r["name"], "rating": r["rating"], "fee": r["entrance_fee"],
                        "reviews": r["review_lakhs"]} for r in [_normalize(x) for x in fee_rating]],
        "top_reviewed": top_reviewed
    }

def recommend_destinations(prefs):
    rows = get_destinations({})
    budget = max(0, _number(prefs.get("budget"), 500))
    hours = max(0.5, _number(prefs.get("hours"), 6))
    min_rating = _number(prefs.get("rating"), 4.0)
    wanted_type = prefs.get("type", "").strip().lower()
    wanted_state = prefs.get("state", "").strip().lower()
    scored = []
    for item in rows:
        fee = item["entrance_fee"]
        duration = item["visit_hours"]
        if fee > budget or duration > hours or item["rating"] < min_rating:
            continue
        score = item["rating"] * 20
        score += 12 if fee <= budget * 0.25 else 7 if fee <= budget * 0.5 else 2
        score += 8 if duration <= hours * 0.35 else 4
        if wanted_type and wanted_type in item["type"].lower():
            score += 18
        if wanted_state and wanted_state == item["state"].lower():
            score += 12
        score += min(item["review_lakhs"], 5) * 1.2
        item["recommendation_score"] = round(score, 1)
        reasons = []
        if item["rating"] >= 4.5: reasons.append("high visitor rating")
        if fee <= budget * 0.25: reasons.append("budget-friendly")
        if duration <= hours * 0.5: reasons.append("fits your available time")
        if wanted_type and wanted_type in item["type"].lower(): reasons.append("matches your preferred category")
        item["recommendation_reason"] = ", ".join(reasons[:3]) or "matches your selected limits"
        scored.append(item)
    scored.sort(key=lambda x: x["recommendation_score"], reverse=True)
    return scored[:12]

def build_itinerary(data):
    budget = max(0, _number(data.get("budget"), 1000))
    hours = max(0.5, _number(data.get("hours"), 6))
    state = (data.get("state") or "").strip()
    wanted_type = (data.get("type") or "").strip()
    minimum_rating = _number(data.get("rating"), 4.0)
    candidates = get_destinations({"state": state, "type": wanted_type, "min_rating": minimum_rating, "sort": "rating"})
    candidates.sort(key=lambda x: (x["rating"] * 10 - x["entrance_fee"] / max(budget, 1) * 10, -x["visit_hours"]), reverse=True)
    chosen, fee_sum, hour_sum = [], 0, 0
    for item in candidates:
        fee, duration = item["entrance_fee"], max(item["visit_hours"], 0.25)
        if fee_sum + fee <= budget and hour_sum + duration <= hours:
            chosen.append(item)
            fee_sum += fee
            hour_sum += duration
        if len(chosen) >= int(_number(data.get("count"), 6)):
            break
    return {
        "items": chosen,
        "budget": budget,
        "hours_available": hours,
        "total_fee": round(fee_sum, 2),
        "total_hours": round(hour_sum, 2),
        "remaining_budget": round(budget - fee_sum, 2),
        "remaining_hours": round(hours - hour_sum, 2),
        "message": "Plan created using entrance fees and visit durations in the dataset. Travel, food and accommodation are not included."
    }

def save_trip(visitor, data, result):
    conn = get_db()
    cur = conn.cursor()
    items_json = json.dumps(result["items"])
    title = data.get("title") or "My India trip"
    if DB_KIND == "mysql":
        cur.execute("INSERT INTO trip_plans(visitor_id,title,budget,hours_available,total_fee,total_hours,items_json) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                    (visitor, title, result["budget"], result["hours_available"], result["total_fee"], result["total_hours"], items_json))
    else:
        cur.execute("INSERT INTO trip_plans(visitor_id,title,budget,hours_available,total_fee,total_hours,items_json) VALUES(?,?,?,?,?,?,?)",
                    (visitor, title, result["budget"], result["hours_available"], result["total_fee"], result["total_hours"], items_json))
    plan_id = cur.lastrowid
    conn.commit()
    cur.close()
    conn.close()
    return plan_id

def get_favorites(visitor):
    sql = """SELECT d.* FROM destinations d JOIN favorites f ON f.destination_id=d.id
             WHERE f.visitor_id = """ + ("%s" if DB_KIND == "mysql" else "?") + " ORDER BY f.created_at DESC"
    return [_normalize(r) for r in _all(sql, (visitor,))]

def toggle_favorite(visitor, destination_id, remove=False):
    conn = get_db()
    cur = conn.cursor()
    ph = "%s" if DB_KIND == "mysql" else "?"
    cur.execute("SELECT destination_id FROM favorites WHERE visitor_id=" + ph + " AND destination_id=" + ph,
                (visitor, destination_id))
    exists = cur.fetchone()
    if remove and exists:
        cur.execute("DELETE FROM favorites WHERE visitor_id=" + ph + " AND destination_id=" + ph, (visitor, destination_id))
        saved = False
    elif exists:
        cur.execute("DELETE FROM favorites WHERE visitor_id=" + ph + " AND destination_id=" + ph, (visitor, destination_id))
        saved = False
    else:
        cur.execute("INSERT INTO favorites(visitor_id,destination_id) VALUES(" + ph + "," + ph + ")", (visitor, destination_id))
        saved = True
    conn.commit()
    cur.close()
    conn.close()
    return saved

def save_quiz_result(visitor, score, total):
    conn = get_db()
    cur = conn.cursor()
    ph = "%s" if DB_KIND == "mysql" else "?"
    cur.execute("INSERT INTO quiz_results(visitor_id,score,total) VALUES(" + ph + "," + ph + "," + ph + ")", (visitor, score, total))
    conn.commit()
    cur.close()
    conn.close()

def get_trip_history(visitor):
    ph = "%s" if DB_KIND == "mysql" else "?"
    return _all("SELECT id,title,budget,hours_available,total_fee,total_hours,created_at FROM trip_plans WHERE visitor_id=" + ph + " ORDER BY id DESC LIMIT 10", (visitor,))
