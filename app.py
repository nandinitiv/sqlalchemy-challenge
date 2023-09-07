# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Create engine to hawaii.sqlite.
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model.
Base = automap_base()

# Reflect the tables.
Base.prepare(autoload_with=engine)

# Save references to each table.
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB.
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

session=Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return (
        f"Welcome to the Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"
    )

# /api/v1.0/precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year ago from the last data point in the database. 
    last_date=session.query(func.max(measurement.date)).first()
    last_year=dt.date(2017,8,23)-dt.timedelta(days=365)
    
    # Query to retrieve the precipitation data for the last year.
    precip_data=session.query(measurement.date, measurement.prcp).filter(measurement.date>=last_year).all()
    precip_dict_list = [{"date": date, "prcp": prcp} for date, prcp in precip_data]

    # Return as JSON.
    return jsonify(precip_dict_list)

# /api/v1.0/stations
@app.route("/api/v1.0/stations")
def stations():
    # Query to retrieve a list of station names.
    total_stations = session.query(station.station).all()

    # Convert the query results to a list of dictionaries.
    stations_list = [{"station": station[0]} for station in total_stations]

    return jsonify(stations_list)

# /api/v1.0/tobs
@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date one year ago from the last data point in the database.
    last_date = session.query(func.max(measurement.date)).scalar()
    last_year = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query to retrieve temperature observations for the most active station for the previous year.
    most_active_station = session.query(measurement.station).group_by(measurement.station).\
        order_by(func.count(measurement.station).desc()).first()[0]
    
    temp_obs = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == most_active_station).\
        filter(measurement.date >= last_year).all()
    
    # Convert the query results to a list of dictionaries.
    temp_obs_list = [{"date": date, "tobs": tobs} for date, tobs in temp_obs]

    return jsonify(temp_obs_list)

# /api/v1.0/<start> and /api/v1.0/<start>/<end>
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_stats(start, end=None):
    # Convert start and end date strings to datetime objects.
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    if end:
        end_date = dt.datetime.strptime(end, "%Y-%m-%d")
    else:
        end_date = dt.datetime.now()  # Use current date if end date is not provided.

    # Query to calculate TMIN, TAVG, and TMAX for the specified date range.
    temperature_stats = session.query(
        func.min(measurement.tobs).label("TMIN"),
        func.avg(measurement.tobs).label("TAVG"),
        func.max(measurement.tobs).label("TMAX")
    ).filter(
        measurement.date >= start_date,
        measurement.date <= end_date
    ).all()

    # Convert the query results to a dictionary.
    stats_dict = {
        "TMIN": temperature_stats[0][0],
        "TAVG": temperature_stats[0][1],
        "TMAX": temperature_stats[0][2]
    }

    return jsonify(stats_dict)


if __name__ == '__main__':
    app.run(debug=True)