#Matt Bennett
#CNE 350 5/26/2023
#Host a web server that can query and update an SQL database.
#Resources used:
# Drew heavily from https://github.com/ellisju37073/States/blob/main/states/rest_web/rest_web.py - Thanks, Justin!
# https://www.tutorialspoint.com/flask/flask_http_methods.htm

from flask import Flask, render_template, request
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.sql import text

#Establish connection to the WAMP SQL DB and upload .csv file
hostname = "127.0.0.1"
uname = "root"
pwd = ""
dbname = "zipcodes"
engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
tables = pd.read_csv(r"C:\Users\mwben\Documents\zip_code_database.csv", dtype={"Population": int})
tables.rename(columns={"zip": "zip_code"}, inplace=True)
tables.rename(columns={"Population": "population"}, inplace=True)
tables.to_sql('zipcodes', con=engine, if_exists='replace', index=False)

#Establishing Flask
app = Flask(__name__)
app.debug = True

#Setting home.html as homepage
@app.route('/')
def zipcodes_dash():
    return render_template('home.html')

#Using GET for /search argument
@app.route('/search', methods=['GET'])
def search():
    zip_code = request.args.get('zipCode')

    data = get_zip_results(zip_code)
    population = data.population if data is not None else None

    return render_template('search.html', zipCode=zip_code, population=population)

#Queries the DB using input from zipCode
def get_zip_results(zip_code):
    connection = engine.connect()
    query = text("SELECT * FROM zipcodes WHERE zip_code = :zip_code")
    result = connection.execute(query, {"zip_code": zip_code}).fetchone()
    connection.close()
    return result

#Updates DB if zip and pop are valid arguments. Sends to fail if not
@app.route('/update', methods=['POST'])
def update():
    zip_code = request.form['zipCode']
    population = request.form['population']

    if zip_code.isdigit() and population.isdigit():
        zip_code = int(zip_code)
        population = int(population)
        if 0 <= zip_code <= 99999 and population >= 0:
            connection = engine.connect()
            query = text("UPDATE zipcodes SET population = :population WHERE zip_code = :zip_code")
            connection.execute(query, {"zip_code": zip_code, "population": population})
            connection.close()
            return render_template('update_success.html')
    return render_template('update_fail.html')

#Run Flask
if __name__ == '__main__':
    app.run()
