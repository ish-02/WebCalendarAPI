from flask import Flask, abort, request, jsonify
import sys
from flask_restful import Api, Resource, reqparse, inputs
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, DATE
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///event.db'
post_parser = reqparse.RequestParser()
get_parser = reqparse.RequestParser()

post_parser.add_argument(
    'date',
    type=inputs.date,
    help="The event date with the correct format is required! The correct format is YYYY-MM-DD!",
    required=True
)
post_parser.add_argument(
    'event',
    type=str,
    help="The event name is required!",
    required=True
)

get_parser.add_argument(
    'time_start',
    type=str,
    required=False
)
get_parser.add_argument(
    'time_end',
    type=str,
    required=False
)

Base = declarative_base()


class Event(Base):
    __tablename__ = 'Events'
    id = Column(Integer, primary_key=True)
    event = Column(String, nullable=False)
    date = Column(DATE, nullable=False)


engine = create_engine("sqlite:///event.db", connect_args={"check_same_thread": False})
Event.__table__.create(bind=engine, checkfirst=True)
Session = sessionmaker(bind=engine)
Session.configure(bind=engine)
db = Session()


class HelloWorldResource(Resource):
    @staticmethod
    def get():
        return jsonify({"message": "Hello from the RESt API!"})


class EventsToday(Resource):
    @staticmethod
    def get():
        query = db.query(Event).filter(Event.date == datetime.today().date()).all()
        return jsonify([{"id": key.id, "event": key.event, "date": str(key.date)} for key in query])


class Events(Resource):
    @staticmethod
    def get():
        get_args = get_parser.parse_args()
        time_start, time_end = get_args.time_start, get_args.time_end
        if time_start and time_end is not None:
            start_time = datetime.strptime(time_start, "%Y-%m-%d")
            end_time = datetime.strptime(time_end, "%Y-%m-%d")
            event_in_range = db.query(Event).filter(Event.date <= end_time, Event.date >= start_time).all()
            return jsonify([{"id": key.id, "event": key.event, "date": str(key.date)} for key in event_in_range])
        query = db.query(Event).all()
        return jsonify([{"id": key.id, "event": key.event, "date": str(key.date)} for key in query])

    @staticmethod
    def post():
        args = post_parser.parse_args()
        try:
            db.add(Event(event=args.event, date=args.date))
            db.commit()
        except SQLAlchemyError:
            return abort(404, "SQLAlchemyError")
        else:
            return jsonify({
                "message": "The event has been added!",
                "event": args.event,
                "date": str(args.date.strftime("%Y-%m-%d"))
            })


class EventByID(Resource):
    @staticmethod
    def get(event_id):
        event = db.query(Event).filter(Event.id == int(event_id)).first()
        if event is None:
            return abort(404, "The event doesn't exist!")
        return jsonify({"id": event.id, "event": event.event, "date": str(event.date)})

    @staticmethod
    def delete(event_id):
        event = db.query(Event).filter(Event.id == int(event_id)).first()
        if event is None:
            return abort(404, "The event doesn't exist!")
        try:
            db.query(Event).filter(Event.id == event.id).delete()
            db.commit()
        except SQLAlchemyError:
            db.rollback()
        else:
            return jsonify({"message": "The event has been deleted!"})


api.add_resource(HelloWorldResource, '/hello')
api.add_resource(EventsToday, '/event/today')
api.add_resource(Events, '/event')
api.add_resource(EventByID, '/event/<int:event_id>')

# do not change the way you run the program
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port, debug=True)
    else:
        app.run(debug=True)
