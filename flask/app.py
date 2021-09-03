import numpy as np
import re
import datetime as dt
import json
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.sql import exists  

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""

    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end (enter as YYYY-MM-DD/YYYY-MM-DD)"

    )

#Convert the query results to a dictionary using date as the key and prcp as the value.
@app.route("/api/v1.0/precipitation") 
def precipitation():
    # Create session (link) from Python to the DB
    session = Session(engine)

    # Query Measurement
    results = (session.query(Measurement.date, Measurement.prcp)
                      .order_by(Measurement.date))
    
    # Create a dictionary
    precipitation_date = []
    for each_row in results:
        dt_dict = {}
        dt_dict["date"] = each_row.date
        dt_dict["prcp"] = each_row.prcp
        precipitation_date.append(dt_dict)
        

    return "hello"
    #return json.dumps(precipitation_date)

#     return jsonify(precipitation_date)

#Return a JSON list of stations from the dataset
@app.route("/api/v1.0/stations")
def stations():
    # Create session (link) from Python to the DB
    session2 = Session(engine)

    # Query Stations
    results2 = session2.query(Station.name).all()

    # Convert list of tuples into normal list
    station_details = list(np.ravel(results))

    return jsonify(station_details) 

#Query the dates and temperature observations of the most 
#active station for the last year of data.

@app.route("/api/v1.0/tobs")
def tobs():
    
    #create a session
    Session3 = Session(engine)
    
    # Query measurement for latest datre 
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    last_12mnth = (dt.datetime.strptime(last_date[0][0], '%Y-%m-%d') - dt.timedelta(days=365)).date()
    print(last_12mnth)
    
    tobs_results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= last_12mnth).order_by(Measurement.date).all()
    
    # Create a list of dicts with `date` and `tobs` as the keys and values
    tobs_totals = []
    for result in tobs_results:
        row = {}
        row["date"] = result[0]
        row["tobs"] = result[1]
        tobs_totals.append(row)
        
    #Return a JSON list of Temperature Observations (tobs) for the previous year.
    return jsonify(tobs_totals)

if __name__ == "__main__":
    app.run(debug=True)                                     
                                  