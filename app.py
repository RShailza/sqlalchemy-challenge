import numpy as np
import re
import datetime as dt

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

#f"/api/v1.0/start<br/>"
#f"/api/v1.0/start/end"

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

    return jsonify(precipitation_date)


#Return a JSON list of stations from the dataset
@app.route("/api/v1.0/stations")
def stations():
    # Create session (link) from Python to the DB
    session2 = Session(engine)

    # Query Stations
    results2 = session2.query(Station.name).all()

    # Convert list of tuples into normal list
    station_details = list(np.ravel(results2))

    return jsonify(station_details) 

#Query the dates and temperature observations of the most 
#active station for the last year of data.

@app.route("/api/v1.0/tobs")
def tobs():
    
    #create a session
    session3 = Session(engine)
    
    # Query measurement for latest datre 
    last_date = session3.query(Measurement.date).order_by(Measurement.date.desc()).first()

    last_12mnth = (dt.datetime.strptime(last_date[0], '%Y-%m-%d') -dt.timedelta(days=365)).date()
    print(last_12mnth)
    
    tobs_results = session3.query(Measurement.date, Measurement.tobs).\
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


# Return a JSON list of the minimum temperature, the average temperature, and 
# the max temperature for a given start or start-end range.


# When given the start only, calculate TMIN, TAVG, and TMAX for all dates
# greater than and equal to the start date.


# When given the start and the end date, calculate the 
# TMIN, TAVG, and TMAX for dates between the start and end date inclusiv

# first_date = session3.query(Measurement.date).order_by((Measurement.date)).limit(1).all()
# print(first_date[0])

# last_date = session3.query(Measurement.date).order_by(Measurement.date.desc()).first()


# @app.route("/api/v1.0/<start>")
# @app.route("/api/v1.0/<start>/<end>")

# def start_date(start=None, end=None):
#     print(start, "is here")
    
#     #convert the tsring from user to date
#     start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
#     end_date= dt.datetime.strptime(end, '%Y-%m-%d').date()
    
# #     last_date_dd = (dt.datetime.strptime(last_date[0], '%Y-%m-%d')).date() 
# #     first_date_dd = (dt.datetime.strptime(first_date[0], '%Y-%m-%d')).date()
    
#     #if fgiven start_date greater than last or lesser than first available date in dataset, print the following 
#     if start_date > last_date_dd or start_date < first_date_dd:
#         return(f"Select date range between {first_date[0]} and {last_date[0]}")
#     else:
#         start_min_max_temp = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),\
#             func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
#         start_date_data = list(np.ravel(start_min_max_temp))
#         return jsonify(start_date_data)

@app.route("/api/v1.0/<start>") 
def start_only(start):

    # Create session (link) from Python to the DB
    session = Session(engine)

    # Date Range (only for help to user in case date gets entered wrong)
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date_str = str(last_date)
    last_date_str = re.sub("'|,", "",last_date_str)
    print (last_date_str)

    initial_date = session.query(Measurement.date).first()
    initial_date_str = str(initial_date)
    initial_date_str = re.sub("'|,", "",initial_date_str)
    print (initial_date_str)


    # Check for valid entry of start date
    valid_entry = session.query(exists().where(Measurement.date == start)).scalar()

    if valid_entry:

        results = (session.query(func.min(Measurement.tobs)
                     ,func.avg(Measurement.tobs)
                     ,func.max(Measurement.tobs))
                          .filter(Measurement.date >= start).all())

        tmin =results[0][0]
        tavg ='{0:.4}'.format(results[0][1])
        tmax =results[0][2]

        result_printout =( ['Input Start Date: ' + start,
                            'Lowest Temperature: '  + str(tmin) + ' F',
                            'Average Temperature: ' + str(tavg) + ' F',
                            'Highest Temperature: ' + str(tmax) + ' F'])
        return jsonify(result_printout)

    return jsonify({"error": f"Input Date {start} not valid. Date Range is {initial_date_str} to {last_date_str}"}), 404


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    # Create session (link) from Python to the DB
    session = Session(engine)

    # Date Range (only for help to user in case date gets entered wrong)
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date_str = str(last_date)
    last_date_str = re.sub("'|,", "",last_date_str)
    print (last_date_str)

    initial_date = session.query(Measurement.date).first()
    initial_date_str = str(initial_date)
    initial_date_str = re.sub("'|,", "",initial_date_str)
    print (initial_date_str)

    # Check for valid entry of start date
    valid_entry_start = session.query(exists().where(Measurement.date == start)).scalar()

    # Check for valid entry of end date
    valid_entry_end = session.query(exists().where(Measurement.date == end)).scalar()

    if valid_entry_start and valid_entry_end:

        results = (session.query(func.min(Measurement.tobs)
                     ,func.avg(Measurement.tobs)
                     ,func.max(Measurement.tobs))
                          .filter(Measurement.date >= start)
                          .filter(Measurement.date <= end).all())

        tmin =results[0][0]
        tavg ='{0:.4}'.format(results[0][1])
        tmax =results[0][2]

        result_printout =( ['Input Start Date: ' + start,
                            'Input End Date: ' + end,
                            'Lowest Temperature: '  + str(tmin) + ' F',
                            'Average Temperature: ' + str(tavg) + ' F',
                            'Highest Temperature: ' + str(tmax) + ' F'])
        return jsonify(result_printout)

    if not valid_entry_start and not valid_entry_end:
        return jsonify({"error": f"Input Start {start} and End Date {end} not valid. Date Range is {initial_date_str} to {last_date_str}"}), 404

    if not valid_entry_start:
        return jsonify({"error": f"Input Start Date {start} not valid. Date Range is {initial_date_str} to {last_date_str}"}), 404

    if not valid_entry_end:
        return jsonify({"error": f"Input End Date {end} not valid. Date Range is {initial_date_str} to {last_date_str}"}), 404


if __name__ == "__main__":
    app.run(debug=True) 
    
    


                                  