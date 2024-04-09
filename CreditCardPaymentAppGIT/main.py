from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
'''''
pip install Flask flask_sqlalchemy sqlalchemy
'''''
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///CC_Debt_Strategy.db'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
engine = create_engine('sqlite:///:memory:', echo=True)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column('id', db.Integer, primary_key=True)
    user_name = db.Column('user_name', db.String, unique=True, nullable=False)
    
class CreditCard(db.Model):
    __tablename__ = 'credit_cards'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    card_name = db.Column(db.String(80), nullable=False)
    card_limit = db.Column(db.Float, nullable=False)
    

@app.route('/users', methods=['POST'])
def create_user():
    user_name = request.json.get('user_name')
    user = User(user_name=user_name)
    db.session.add(user)
    db.session.commit()
    return {'id': user.id}, 201

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return {"error": "User not found"}, 404
    return {'user_name': user.user_name}, 200

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return {"error": "User not found"}, 404
    user.user_name = request.json.get('user_name')
    db.session.commit()
    return {}, 204

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return {"error": "User not found"}, 404
    db.session.delete(user)
    db.session.commit()
    return {}, 204
#---------------------------------------------------------    
@app.route('/credit_cards', methods=['POST'])
def create_credit_card():
    user_id = request.json.get('user_id')
    card_name = request.json.get('card_name')
    card_limit = request.json.get('card_limit')
    credit_card = CreditCard(user_id=user_id, card_name=card_name, card_limit=card_limit)
    db.session.add(credit_card)
    db.session.commit()
    return {'id': credit_card.id}, 201

#INSERT INTO "credit_card" ("user_id", "card_name", "card_limit")
#SELECT 1, 'Tony Lowes', 30000.0
#FROM "users"
#WHERE "user_name" = 'AFRIDAY';

@app.route('/users/<int:user_id>/credit_cards', methods=['GET'])
def get_credit_cards(user_id):
    credit_cards = CreditCard.query.filter_by(user_id=user_id).all()
    if credit_cards is None:
        return {"error": "No credit cards found for this user"}, 404
    return {
        'credit_cards': [
            {
                'card_name': card.card_name,
                'card_limit': card.card_limit,
                'thirty_percent_limit' : card.card_limit * 0.3,
                'ten_percent_limit' : card.card_limit * 0.1,
            } for card in credit_cards
        ]
    }, 200

@app.route('/credit_cards/<int:card_id>', methods=['PUT'])
def update_credit_card(card_id):
    credit_card = CreditCard.query.get(card_id)
    if credit_card is None:
        return {"error": "Credit card not found"}, 404
    credit_card.user_id = request.json.get('user_id')
    credit_card.card_name = request.json.get('card_name')
    credit_card.card_limit = request.json.get('card_limit')
    db.session.commit()
    return {}, 204

@app.route('/credit_cards/<int:card_id>', methods=['DELETE'])
def delete_credit_card(card_id):
    credit_card = CreditCard.query.get(card_id)
    if credit_card is None:
        return {"error": "Credit card not found"}, 404
    db.session.delete(credit_card)
    db.session.commit()
    return {}, 204
    

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)