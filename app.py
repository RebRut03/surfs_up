import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

app = Flask(__name__)

@app.route("/")

def welcome():
    return(
    '''
    Welcome to the Climate Analysis API!
    Available Routes:
    /api/v1.0/precipitation
    /api/v1.0/stations
    /api/v1.0/tobs
    /api/v1.0/temp/start/end
    ''')

@app.route("/api/v1.0/precipitation")
def precipitation():
   prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
   precipitation = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= prev_year).all()
   precip = {date: prcp for date, prcp in precipitation}
   return jsonify(precip)

# return a list of all the stations by defining the route 
# & route name
@app.route("/api/v1.0/stations")
# create function called stations
def stations():
    #create a query that will allow us to get 
    # all of the stations in our database
    results = session.query(Station.station).all()
    # start by unraveling results into a one-dimensional array
    # convert unraveled array results into a list using list func
    stations = list(np.ravel(results))
    # jsonify the list
    return jsonify(stations=stations)

# temp observations route defined
@app.route("/api/v1.0/tobs")
# create function called temp_monthly()
def temp_monthly():
    # calculate the date one year ago 
    # from the last date in the database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # query the primary station for all the temperature 
    # observations from the previous year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
    # unravel the results into a one-dimensional array
    # and convert that array into a list
    temps = list(np.ravel(results))
    # jsonify our temps list
    return jsonify(temps=temps)

# Create route to report on min, average, and maximum temps
# different than others need start & ending date
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
# create a function called stats() with start & end parameter
def stats(start=None, end=None):
    # create a query to select the min, average, and max temps 
    # from our SQLite db. Start by creating a list called sel
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    # to determine starting & ending date, add  if-not statement 
    # query database using the list that we just made. 
    #asterisk is used to indicate multiple results for our query: 
    # minimum, average, and maximum temperatures
    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
        # unravel the results into a one-dimensional array 
        # and convert them to a list.
        temps = list(np.ravel(results))
        # jsonify our results and return them.
        return jsonify(temps=temps)
    
    # calculate the temperature minimum, average, and maximum 
    # with the start and end dates. 
    # use the sel list, which is the data points we need to collect
    # create our next query, which will get our statistics data.
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)