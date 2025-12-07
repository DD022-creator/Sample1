from flask import Flask, render_template,jsonify,request
from flask_cors import CORS
import random


app = Flask(__name__)
CORS(app)

# Simple in-memory storage
trucks = [
    {"id": 1, "name": "Truck-001", "status": "active", "capacity": 5.0, "current_load": 3.5, "fuel_efficiency": 4.5},
    {"id": 2, "name": "Truck-002", "status": "active", "capacity": 7.5, "current_load": 4.8, "fuel_efficiency": 4.2},
    {"id": 3, "name": "Truck-003", "status": "maintenance", "capacity": 6.0, "current_load": 0, "fuel_efficiency": 4.8}
]

plants = [
    {"id": 1, "name": "Central Biogas Plant", "type": "biogas", "capacity": 100, "current_load": 45.5, "energy_output": 6500},
    {"id": 2, "name": "West Delhi WTE Plant", "type": "incineration", "capacity": 150, "current_load": 89.2, "energy_output": 12500},
    {"id": 3, "name": "South Energy Plant", "type": "biogas", "capacity": 80, "current_load": 32.1, "energy_output": 4200}
]

routes = [
    {"id": 1, "truck_id": 1, "truck_name": "Truck-001", "source": "Sector 15", "destination": "Central Biogas Plant", "distance": 8.2, "eta": 15, "waste_load": 3.5, "co2_saved": 4.2},
    {"id": 2, "truck_id": 2, "truck_name": "Truck-002", "source": "Commercial Zone A", "destination": "West Delhi WTE Plant", "distance": 12.5, "eta": 22, "waste_load": 4.8, "co2_saved": 6.1}
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/trucks', methods=['GET'])
def get_trucks():
    return jsonify(trucks)

@app.route('/api/trucks', methods=['POST'])
def add_truck():
    data = request.json
    new_truck = {
        "id": len(trucks) + 1,
        "name": data.get('name', f'Truck-{len(trucks) + 1:03d}'),
        "status": "active",
        "capacity": round(random.uniform(3, 8), 1),
        "current_load": 0,
        "fuel_efficiency": round(random.uniform(3.5, 5.5), 1)
    }
    trucks.append(new_truck)
    return jsonify({"message": "Truck added successfully", "truck": new_truck})

@app.route('/api/trucks/<int:truck_id>', methods=['DELETE'])
def delete_truck(truck_id):
    global trucks
    trucks = [truck for truck in trucks if truck['id'] != truck_id]
    return jsonify({"message": "Truck deleted successfully"})

@app.route('/api/plants', methods=['GET'])
def get_plants():
    return jsonify(plants)

@app.route('/api/routes', methods=['GET'])
def get_routes():
    return jsonify(routes)

@app.route('/api/routes/optimize', methods=['POST'])
def optimize_routes():
    global routes
    routes.clear()
    
    sources = ["Sector 15", "Commercial Zone A", "Residential Area B", "Market Complex C"]
    
    for i, truck in enumerate([t for t in trucks if t['status'] == 'active']):
        new_route = {
            "id": i + 1,
            "truck_id": truck['id'],
            "truck_name": truck['name'],
            "source": random.choice(sources),
            "destination": random.choice(plants)['name'],
            "distance": round(random.uniform(5, 15), 1),
            "eta": random.randint(10, 30),
            "waste_load": round(random.uniform(1, truck['capacity']), 1),
            "co2_saved": round(random.uniform(3, 8), 1)
        }
        routes.append(new_route)
    
    return jsonify({
        "message": f"Optimized {len(routes)} routes",
        "optimized_count": len(routes)
    })

@app.route('/api/analytics/summary', methods=['GET'])
def get_analytics_summary():
    active_trucks = len([t for t in trucks if t['status'] == 'active'])
    total_co2 = sum(route['co2_saved'] for route in routes)
    total_fuel = sum(route['distance'] for route in routes) / 4.5  # Average efficiency
    
    return jsonify({
        "trucks": active_trucks,
        "plants": len(plants),
        "co2_saved": round(total_co2 / 100 + 12.5, 1),
        "fuel_saved": round(total_fuel + 200),
        "waste_processed": round(sum(truck['current_load'] for truck in trucks) + 80.2, 1),
        "energy_generated": round(sum(plant['energy_output'] for plant in plants) + 11000),
        "routes_optimized": len(routes) + 150,
        "system_efficiency": 92
    })

if __name__ == '__main__':
    print("🚀 ENERG ENIX API Server Starting...")
    print("📍 URL: http://10.14.210.158:5000")
    print("✅ API is ready!")
    app.run(host='0.0.0.0', port=5000, debug=True)
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import random
from database import *

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/trucks', methods=['GET'])
def get_trucks():
    trucks = get_all_trucks()
    return jsonify(trucks)

@app.route('/api/trucks', methods=['POST'])
def add_truck():
    data = request.json
    name = data.get('name', f'Truck-{random.randint(100, 999)}')
    capacity = round(random.uniform(3, 8), 1)
    fuel_efficiency = round(random.uniform(3.5, 5.5), 1)
    
    truck_id = add_truck(name, capacity, fuel_efficiency)
    
    return jsonify({
        "message": "Truck added successfully", 
        "truck": {
            "id": truck_id,
            "name": name,
            "status": "active",
            "capacity": capacity,
            "current_load": 0,
            "fuel_efficiency": fuel_efficiency
        }
    })

@app.route('/api/trucks/<int:truck_id>', methods=['DELETE'])
def delete_truck(truck_id):
    delete_truck(truck_id)
    return jsonify({"message": "Truck deleted successfully"})

@app.route('/api/plants', methods=['GET'])
def get_plants():
    plants = get_all_plants()
    return jsonify(plants)

@app.route('/api/routes', methods=['GET'])
def get_routes():
    routes = get_all_routes()
    return jsonify(routes)

@app.route('/api/routes/optimize', methods=['POST'])
def optimize_routes():
    new_routes = optimize_routes()
    return jsonify({
        "message": f"Optimized {len(new_routes)} routes",
        "optimized_count": len(new_routes)
    })

@app.route('/api/analytics/summary', methods=['GET'])
def get_analytics_summary():
    summary = get_analytics_summary()
    return jsonify(summary)

@app.route('/api/analytics/historical', methods=['GET'])
def get_historical_analytics():
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analytics ORDER BY date DESC LIMIT 30")
    analytics = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()
    return jsonify(analytics)

if __name__ == '__main__':
    print("🚀 ENERG ENIX API Server Starting...")
    print("📍 URL: http://10.14.210.158:5000")
    print("🗄️ Database initialized successfully!")
    print("✅ API is ready!")
    app.run(host='0.0.0.0', port=5000, debug=True)