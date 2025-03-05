from flask import Flask, request, jsonify
from model import EvacuationPlanner

app = Flask(__name__)
planner = EvacuationPlanner()

@app.route('/plan', methods=['POST'])
def get_plan():
    data = request.json
    plan = planner.get_evacuation_plan(data['query'], data['user_needs'])
    return jsonify({'plan': plan})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)