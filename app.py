# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    html = (
            f"<h1>Module 10 Challenge: Climate Application</h1>"
            f"<h2>Available Routes:</h2>"
            f"<table>"
            f"<tr><th>Links</th></tr>"
            f"<tr><td><a href=/api/v1.0/precipitation>/api/v1.0/precipitation</td></tr>"
            f"<tr><td><a href=/api/v1.0/stations>/api/v1.0/stations</td></tr>"
            f"<tr><td><a href=/api/v1.0/tobs>/api/v1.0/tobs</td></tr>"
            f"<tr><td><a href=/api/v1.0/<start>>/api/v1.0/<start></td></tr>"
            f"<tr><td><a href=/api/v1.0/<start>/<end>>/api/v1.0/<start>/<end></td></tr>"
            f"</table>"
           )
    
    return html

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    start_date = '2016-08-23'
    results = session.query(Measurement.date, Measurement.prcp).\
                filter(Measurement.date >= start_date)

    session.close()
    
    prcp_list = []
    
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict['date'] = date
        prcp_dict['prcp'] = prcp
        prcp_list.append(prcp_dict)    

    return jsonify(prcp_list)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()
    
    # flatten array
    station_list = list(np.ravel(results))
    
    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    start_date = '2016-08-23'
    station_id = 'USC00519281'
    
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.station == station_id).all()
    
    session.close()
    
    tobs_list = []
    tobs_dict = {}
    for date, tobs in results:
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs
    tobs_list.append(tobs_dict)
    
    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start, end=None):
    
    session = Session(engine)
    
    select_list = [func.min(Measurement.prcp), 
                   func.avg(Measurement.prcp),
                   func.max(Measurement.prcp)]
    
    if (end == None):
        results = session.query(*select_list).\
            filter(Measurement.date >= start).all()
            
    else:
        results = session.query(*select_list).\
            filter(Measurement.date.between(start, end)).all()
    
    session.close()
    
    # Flatten array to normal list
    temp_results = list(np.ravel(results))
    
    return jsonify(temp_results)

if __name__ == "__main__":
    app.run(debug=True)