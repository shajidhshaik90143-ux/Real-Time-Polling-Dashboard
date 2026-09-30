
import csv, io, json, secrets
from .database import get_poll, get_results, get_recent_votes

def make_vote_token():
    # Per-session token. For a real public deployment, replace with authenticated user IDs.
    return secrets.token_hex(16)

def export_poll_csv(poll_id):
    poll = get_poll(poll_id)
    results = get_results(poll_id)
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["Poll ID","Question","Option","Votes","Percentage"])
    total = sum(x["votes"] for x in results)
    for r in results:
        writer.writerow([poll_id, poll["question"], r["option"], r["votes"], round(r["votes"]/total*100,2) if total else 0])
    return out.getvalue()

def export_poll_json(poll_id):
    poll = get_poll(poll_id)
    results = get_results(poll_id)
    total = sum(x["votes"] for x in results)
    payload = {
        "poll_id": poll_id,
        "question": poll["question"],
        "created_at": poll["created_at"],
        "total_votes": total,
        "results": [
            {**r, "percentage": round(r["votes"]/total*100,2) if total else 0}
            for r in results
        ]
    }
    return json.dumps(payload, indent=2)
