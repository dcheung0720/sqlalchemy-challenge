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
    # year of the last entry
    last_entry = session.query(measurement.date).order_by(measurement.date.desc()).first()

    # one year before the last entry
    year_before_last_entry = dt.datetime.strptime(last_entry[0], "%Y-%m-%d") - dt.timedelta(days = 366) 

    # all the data within the last year
    precip_data_query = session.query(measurement.date, measurement.prcp).filter(measurement.date >= year_before_last_entry).all()

    # dictionary data
    precip_data = {}
    for row in precip_data_query:
        precip_data[row[0]] = row[1]

    return jsonify(precip_data)

@app.route("/api/v1.0/stations")
def Stations():
    station_data_query = session.query(station).all()
    
    station_data = []

    # go through all stations
    for data in station_data_query:

        # get the data for one particular station
        thisData = {
            "station": data.station,
            "name": data.name,
            "latitude": data.latitude,
            "longitutde": data.longitude,
            "elevation": data.elevation
        }

        # store data into list
        station_data.append(thisData)
    
    return jsonify(station_data)

@app.route("/api/v1.0/tobs")
def Tobs():
    # get the most active
    most_active_station = session.query(measurement.station).group_by(measurement.station).order_by(func.count(measurement.tobs).desc()).first()[0]

    # year of the last entry
    last_entry = session.query(measurement.date).order_by(measurement.date.desc()).first()

    # one year before the last entry
    year_before_last_entry = dt.datetime.strptime(last_entry[0], "%Y-%m-%d") - dt.timedelta(days = 366) 

    # query all dates and temp of the most active station where date>= one year before the last entry.
    dates_temp_query = session.query(measurement.date, measurement.tobs)\
                        .filter(measurement.station == most_active_station)\
                        .filter(measurement.date >= year_before_last_entry)
    
    dates_temp_data = []

    for data in dates_temp_query:
        thisData = {
            "Date": data[0],
            "Temperature": data[1]
        }
        dates_temp_data.append(thisData)

    return jsonify(dates_temp_data)

@app.route("/api/v1.0/start/<start>")
def TemperatureStart(start):

    # processed date time
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    
    # query min, max, and average temperature greater than the starting date
    temperature_query = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs))\
                        .filter(measurement.date >= start_date).first()
    
    thisData = {
        "min": temperature_query[0],
        "max": temperature_query[2],
        "average": temperature_query[1]
    }
    return jsonify(thisData)

@app.route("/api/v1.0/start/<start>/end/<end>")
def TemperatureStartEnd(start, end):

    # processed date time
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end, "%Y-%m-%d")

    # query min, max, and average temperature greater than the starting date
    temperature_query = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs))\
                        .filter(measurement.date >= start_date).filter(measurement.date <= end_date).first()
    thisData = {
        "min": temperature_query[0],
        "max": temperature_query[2],
        "average": temperature_query[1]
    }

    return jsonify(thisData)

if __name__ == "__main__":
    app.run(debug = True)