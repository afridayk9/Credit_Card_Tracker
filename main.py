import os
import logging
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'CC_Debt_Strategy.db')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
engine = create_engine('sqlite:///' + db_path, echo=True, connect_args={'timeout': 10})
Session = sessionmaker(bind=engine)

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column('id', db.Integer, primary_key=True)
    user_name = db.Column('user_name', db.String, unique=True, nullable=False)
    credit_cards = db.relationship('CreditCard', backref='user')

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
    with session_scope() as session:
        session.add(user)
        session.flush()  
        user_id = user.id   
    return {'id': user_id}, 201     

@app.route('/users/<user_name>', methods=['GET'])
def get_user(user_name):
    with session_scope() as session:
        user = session.query(User).filter_by(user_name=user_name).first()
        if user is None:
            return {"error": "User not found"}, 404
        user_dict = {'id': user.id, 'user_name': user.user_name}
    return user_dict, 200


@app.route('/users/<username>', methods=['PUT'])
def update_user(username):
    new_username = request.json.get('user_name')
    if not new_username:
        return {"error": "New username not provided"}, 400

    with session_scope() as session:
        user = session.query(User).filter_by(user_name=username).first()
        if user is None:
            return {"error": "User not found"}, 404

        user.user_name = new_username
        logging.info(f"Updated username to {new_username}")

    return {}, 204

@app.route('/users/<username>', methods=['DELETE'])
def delete_user(username):
    with session_scope() as session:
        user = session.query(User).filter_by(user_name=username).first()
        if user is None:
            return {"error": "User not found"}, 404
        session.delete(user)
    return {}, 204


@app.route('/credit_cards', methods=['POST'])
def create_credit_card():
    username = request.json.get('username')
    with session_scope() as session:
        user = session.query(User).filter_by(user_name=username).first()
        if user is None:
            return {"error": "User not found"}, 404

        card_name = request.json.get('card_name')
        card_limit = request.json.get('card_limit')
        credit_card = CreditCard(user_id=user.id, card_name=card_name, card_limit=card_limit)
        session.add(credit_card)
        session.flush()  # This is necessary to generate the ID for the new credit card
        credit_card_id = credit_card.id  # Store the ID in a variable
    return {'id': credit_card_id}, 201  # Return the variable

@app.route('/users/<user_name>/credit_cards', methods=['GET'])
def get_credit_cards(user_name):
    with session_scope() as session:
        user = session.query(User).filter_by(user_name=user_name).first()
        if user is None:
            return {"error": "User not found"}, 404
        cards = session.query(CreditCard).filter_by(user_id=user.id).all()
        cards_dict = [{'id': card.id, 'card_name': card.card_name, 'card_limit': card.card_limit} for card in cards]
    return {'credit_cards': cards_dict}, 200


@app.route('/users/<username>/credit_cards/<int:card_id>', methods=['PUT'])
def update_credit_card(username, card_id):
    with session_scope() as session:
        user = session.query(User).filter_by(user_name=username).first()
        if user is None:
            return {"error": "User not found"}, 404

        credit_card = session.query(CreditCard).get(card_id)
        if credit_card is None or credit_card.user_id != user.id:
            return {"error": "Credit card not found"}, 404

        credit_card.card_name = request.json.get('card_name')
        credit_card.card_limit = request.json.get('card_limit')
        session.flush()  
    return {}, 204

@app.route('/users/<username>/credit_cards/<int:card_id>', methods=['DELETE'])
def delete_credit_card(username, card_id):
    with session_scope() as session:
        user = session.query(User).filter_by(user_name=username).first()
        if user is None:
            return {"error": "User not found"}, 404

        credit_card = session.query(CreditCard).get(card_id)
        if credit_card is None or credit_card.user_id != user.id:
            return {"error": "Credit card not found"}, 404

        session.delete(credit_card)
    return {}, 204

@app.route('/users/<username>/credit_cards', methods=['DELETE'])
def delete_user_credit_cards(username):
    with session_scope() as session:
        user = session.query(User).filter_by(user_name=username).first()
        if user is None:
            return {"error": "User not found"}, 404

        cards = session.query(CreditCard).filter_by(user_id=user.id).all()
        for card in cards:
            session.delete(card)
    return {}, 204


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
