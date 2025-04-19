from flask import Flask, request, jsonify, send_from_directory
from model import EvacuationPlanner

app = Flask(__name__)
planner = EvacuationPlanner()

@app.route('/')
def serve_html():
    return send_from_directory('.', 'index.html')

@app.route('/plan', methods=['POST'])
def get_plan():
    data = request.json
    query = data.get('query', '')
    needs = data.get('needs', 'none')
    result = planner.get_evacuation_plan(query, needs)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)