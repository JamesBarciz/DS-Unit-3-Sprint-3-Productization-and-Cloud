"""OpenAQ Air Quality Dashboard with Flask."""
from flask import Flask, render_template
import openaq
from flask_sqlalchemy import SQLAlchemy

APP = Flask(__name__)

APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(APP)

class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return f'{self.datetime}: {self.value}'

# def getUTCValues(list):
#     res = []
#     for i in list:
#         res.append((i['date']['utc'], i['value']))
#     return str(res)

def get_records(list):
    for i in list:
        DB.session.add(Record(
            datetime=i['date']['utc'],
            value=i['value']
        ))

@APP.route('/')
def root():
    # Moved the required queried data to '/data' route
    return render_template('homepage.html')

@APP.route('/data')
def data():
    """Base view."""
    api = openaq.OpenAQ()
    status, body = api.measurements(city='Los Angeles', parameter='pm25')
    results = body['results']
    get_records(results)

    # I found our you could render HTML within a string/docstring
    # So I looked up how to create a table and then
    # Pass in several parameters to space the values out
    # By 5 pixels
    output = '''
    <table style="border-spacing: 5px;">
     <thead>
      <tr>
       <th style="border: 1px solid #dddddd; text-align: left; padding: 8px;">
        Time
       </th>
       <th style="border: 1px solid #dddddd; text-align: left; padding: 8px;">
        Value
       </th>
      </tr>
     </thead>
    <tbody>
    '''
    # Establishing a condition for the query filter
    condition = (Record.value >= 10)
    # for record in Record.query.all():
    # Using code from challenge.md
    for record in Record.query.filter(condition).all():
        #
        output += f'''
        <tr>
         <td style="border: 1px solid #dddddd; text-align: left; padding: 8px;">
          {record.datetime}
         </td>
         <td style="border: 1px solid #dddddd; text-align: left; padding: 8px;">
          {record.value}
         </td>
        </tr>
        '''
    return output + '</tbody></table>'
    # return getUTCValues(results)

@APP.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    # TODO Get data from OpenAQ, make Record objects with it, and add to db
    DB.session.commit()
    return 'Data refreshed!'
