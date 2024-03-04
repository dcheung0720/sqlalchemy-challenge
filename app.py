# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime as dt

#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect the tables
Base = automap_base()
Base.prepare(autoload_with = engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def Home():
    return "<p>Welcome!</p> The available routes are: \
            <ol>\
                <li>/api/v1.0/precipitation</li>\
                <li>/api/v1.0/stations</li>\
                <li>/api/v1.0/tobs</li>\
                <li>/api/v1.0/&lt;start&gt;</li>\
                <li>/api/v1.0/&lt;start&gt;/&lt;end&gt;</li>\
            </ol>"

@app.route("/api/v1.0/precipitation")
def Precipitation():
    last_entry = session.query(measurement.date).order_by(measurement.date.desc()).first()
    year_before_last_entry = dt.datetime.strptime(last_entry[0], "%Y-%m-%d") - dt.timedelta(days = 366) 
    precip_data_query = session.query(measurement.date, measurement.prcp).filter(measurement.date >= year_before_last_entry).all()

    precip_data = {}
    for row in precip_data_query:
        precip_data[row[0]] = row[1]

    return jsonify(precip_data)

if __name__ == "__main__":
    app.run(debug = True)