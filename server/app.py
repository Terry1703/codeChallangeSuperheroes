from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

app = Flask(__name__)

# Set up the database URI
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

@app.route('/')
def index():
    return '<h1>Code Challenge</h1>'

# Hero Resource
class HeroResource(Resource):
    def get(self):
        heroes = Hero.query.all()
        return jsonify([hero.to_dict() for hero in heroes]), 200

    def post(self):
        data = request.get_json()
        new_hero = Hero(name=data['name'], super_name=data['super_name'])
        db.session.add(new_hero)
        db.session.commit()
        return jsonify(new_hero.to_dict()), 201

class HeroDetailResource(Resource):
    def get(self, id):
        hero = Hero.query.get(id)
        if hero:
            return jsonify(hero.to_dict()), 200
        return jsonify({"error": "Hero not found"}), 404

# Power Resource
class PowerResource(Resource):
    def get(self):
        powers = Power.query.all()
        return jsonify([power.to_dict() for power in powers]), 200

class PowerDetailResource(Resource):
    def get(self, id):
        power = Power.query.get(id)
        if power:
            return jsonify(power.to_dict()), 200
        return jsonify({"error": "Power not found"}), 404

    def patch(self, id):
        power = Power.query.get(id)
        if not power:
            return jsonify({"error": "Power not found"}), 404

        data = request.get_json()
        if 'description' in data:
            try:
                power.description = data['description']
                db.session.commit()
                return jsonify(power.to_dict()), 200
            except ValueError as e:
                return jsonify({"errors": [str(e)]}), 400

        return jsonify({"error": "No valid fields to update"}), 400

# HeroPower Resource
class HeroPowerResource(Resource):
    def post(self):
        data = request.get_json()
        hero_power = HeroPower(
            strength=data['strength'],
            hero_id=data['hero_id'],
            power_id=data['power_id']
        )

        try:
            db.session.add(hero_power)
            db.session.commit()
            return jsonify(hero_power.to_dict()), 201
        except ValueError as e:
            return jsonify({"errors": [str(e)]}), 400

# Register Resources with Flask-RESTful
api.add_resource(HeroResource, '/heroes')
api.add_resource(HeroDetailResource, '/heroes/<int:id>')
api.add_resource(PowerResource, '/powers')
api.add_resource(PowerDetailResource, '/powers/<int:id>')
api.add_resource(HeroPowerResource, '/hero_powers')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
