from datetime import datetime

def _upgrade_session(session):
    session['time'] = (int(session['endTimeMillis']) - int(session['startTimeMillis'])) / 1000 / 60 / 60
    session['start_time'] = int(int(session['startTimeMillis']) / 1000)
    session['end_time'] = int(int(session['endTimeMillis']) / 1000)
    session['data_start'] = datetime.fromtimestamp(session['start_time'])
    session['data_end'] = datetime.fromtimestamp(session['end_time'])
    return session

def _minimal_session(session):
    del session['id']
    del session['name']
    del session['description']
    del session['startTimeMillis']
    del session['endTimeMillis']
    del session['modifiedTimeMillis']
    del session['application']
    return session

def _upgrade_point(point):
    point['start_time'] = int(int(point['startTimeNanos']) / 1000 / 1000 / 1000)
    point['end_time'] = int(int(point['endTimeNanos']) / 1000 / 1000 / 1000)
    point['time'] = int((point['end_time'] - point['start_time']) / 60)
    point['data_start'] = datetime.fromtimestamp(point['start_time'])
    point['data_end'] = datetime.fromtimestamp(point['end_time'])
    return point

def _minimal_point(point):
    del point['startTimeNanos']
    del point['endTimeNanos']
    if 'modifiedTimeMillis' in point:
        del point['modifiedTimeMillis']
    del point['dataTypeName']
    if 'originDataSourceId' in point:
        del point['originDataSourceId']
    return point

def _upgrade_point_dataSourse(point):
    point['time'] = int(int(point['startTimeNanos']) / 1000 / 1000 / 1000)
    point['data'] = datetime.fromtimestamp(point['time'])
    return point

def _minimal_point_dataSourse(point):

    del point['startTimeNanos']
    del point['endTimeNanos']
    del point['modifiedTimeMillis']
    del point['dataTypeName']
    if 'originDataSourceId' in point:
        del point['originDataSourceId']
    return point