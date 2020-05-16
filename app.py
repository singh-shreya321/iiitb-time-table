from flask import Flask
import json, os, re
import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from search import searchData
import os
import itertools
import requests
import json
import re
import sys
import collections



app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
port = int(os.environ.get("PORT", 5000))

script_dir = os.path.dirname(__file__)
minorFileName = 'minor.json'
minorFileName = os.path.join(script_dir, minorFileName)

profs_dict = {}


DEPT_KEY = 'dept'
WEBSITE_KEY = 'website'
TIMETABLE_KEY = 'timetable'


class CaseInsensitiveDict(dict):
    """Basic case insensitive dict with strings only keys."""

    proxy = {}


    def __init__(self, data):
        self.proxy = dict((k.lower(), k) for k in data)
        for k in data:
            self[k] = data[k]


    def __contains__(self, k):
        return k.lower() in self.proxy


    def __delitem__(self, k):
        key = self.proxy[k.lower()]
        super(CaseInsensitiveDict, self).__delitem__(key)
        del self.proxy[k.lower()]


    def __getitem__(self, k):
        key = self.proxy[k.lower()]
        return super(CaseInsensitiveDict, self).__getitem__(key)


    def get(self, k, default=None):
        return self[k] if k in self else default


    def __setitem__(self, k, v):
        super(CaseInsensitiveDict, self).__setitem__(k, v)
        self.proxy[k.lower()] = k


with open(os.path.join(script_dir, 'data/data.json'), 'r') as f:
    profs_dict = CaseInsensitiveDict(json.load(f))




def get_times(prof_name):
    data = CaseInsensitiveDict(profs_dict)
    result = []

    try:

        result = data[prof_name][TIMETABLE_KEY]

        if result:
            result.sort()
            result = list(result for result, _ in itertools.groupby(result))

    except:

        pass

    return result

def get_table(details):
    tb = {}

    for i in range(5):
        for j in range(9):
            tb.update({'%d%d' % (i, j): []})

    for times, venues in details:
        venues = set(v.strip() for v in venues)

        for time in times:
            tb[time] = venues

    return tb


def get_attr(prof_name, key):
    data = CaseInsensitiveDict(profs_dict)
    result = ""

    try:

        result = data[prof_name][key]

    except:

        pass


@app.route('/')
def home():
	return render_template('home.html')

@app.route('/search/')
def search():
	query = request.args.get('term')
	results = searchData(query)
	return json.dumps( [ course['Name'] for course in results ] )

@app.route('/ajax/', methods=['POST'])
def getCourse():
	query = request.form.get('query')
	results = searchData(query)
	if results:
		return json.dumps( results[0] )
	else:
		return json.dumps( {} )

@app.route('/minor/')
def minor():
	with app.open_resource(minorFileName, 'r') as minorFile:
		data = json.load(minorFile)
	return json.dumps( data )
	app.run(host='0.0.0.0', port=port, debug=True)


with open(os.path.join(script_dir, 'data/data.json')) as f:
    profs = list(set(json.load(f).keys()))
    profs.sort()


def fetch_results(prof):
    tb = [[['Monday']], [['Tuesday']], [['Wednesday']], [['Thursday']], [['Friday']]]
    times = ['', '8 AM', '9 AM', '10 AM', '11 AM', '12 PM', '2 PM', '3 PM', '4 PM', '5 PM']
    slot_data = get_times(prof)
    dept = get_attr(prof, 'dept')
    website = get_attr(prof, 'website')
    print(prof, slot_data, dept, website)

    if len(slot_data) == 0 and len(dept) == 0:
        abort(404)

    data = get_table(slot_data)

    for row in tb:
        for i in range(9):
            row.append([])

    for item in data:
        for venue in data[item]:
            if venue == '0':
                venue = 'In Dept'

            tb[int(item[0])][int(item[1])+1].append(venue)

    return [tb, times, dept, website, prof.title()]

@app.route('/professor', methods=['POST'])
def result():
    prof = request.form['prof']
    tb, times, dept, website, prof = fetch_results(prof)
    print(prof)
    return render_template('main.html', name=prof, website=website, data=tb, times=times, profs=profs, dept=dept, error=False)

@app.route('/professor', methods=['GET'])
def main():
    prof = request.args.get('prof')
    print(prof)
    if prof:
        print("hola")

        tb, times, dept, website, prof = fetch_results(prof)
        return render_template('main.html', name=prof, website=website, data=tb, times=times, profs=profs, dept=dept, error=False)

    else:
        return render_template('main.html', profs=profs) 


if __name__ == '__main__':
	port = int(os.environ.get("PORT", 5000))