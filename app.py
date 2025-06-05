from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/internships", methods=["GET"])
def internships():
    try:
        city = request.args.get("city", "").lower()
        search = request.args.get("search", "intern").lower()

        response = requests.get("https://www.arbeitnow.com/api/job-board-api")
        jobs = response.json().get("data", [])

        search_terms = search.split()
        filtered = [
            {
                    "title": job["title"],
                    "company": job["company_name"],
                    "location": job.get("location", ""),
                    "url": job.get("url", "")
    }
    for job in jobs
    if any(term in job["title"].lower() for term in search_terms)
]

        print(f"✅ Returning {len(filtered)} internships for '{search}'")
        return jsonify(filtered)

    except Exception as e:
        print("❌ Backend error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=10000)
