from flask import Flask, request, jsonify, send_from_directory
from model import EvacuationPlanner

planner = EvacuationPlanner()

app = Flask(__name__)

@app.route('/')
def serve_html():
    return send_from_directory('.', 'index.html')

@app.route('/plan', methods=['POST'])
def get_plan():
    data = request.json
    query = data.get('query', '')
    needs = data.get('needs', 'none')
    plan = planner.get_evacuation_plan(query, needs)
    return jsonify({'plan': plan})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)