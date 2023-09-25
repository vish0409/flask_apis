from flask import Flask, request, jsonify
import json
import psycopg2
import pandas as pd
from sqlalchemy import create_engine

# Getting Data from a postgres DB
dbname="postgres"
user="postgres"
password="Vishnu123"
host="localhost"
port=5432
connection = psycopg2.connect(
    dbname=dbname,
    user=user,
    password=password,
    host=host,
    port=port
)
print("Connected")
cursor=connection.cursor()
cursor.execute("SELECT * FROM incident_data")
rows=cursor.fetchall()
columns=[col[0] for col in cursor.description]

df=pd.DataFrame(rows,columns=columns)
dict1=df.to_dict(orient="records")
dict1

cursor.close()
connection.close()

# Making the flask app
def flask_app():
    app = Flask(__name__)

    @app.route("/")
    def hello():
        return jsonify({"message":"Hello World, This is my API"})

# GET requests endpoint
    @app.route("/get_data")
    def get_incident():
        incident_id=request.args.get("incident_id")
        incident_catgeory=request.args.get("incident_category")

        if incident_id:
            for incident in dict1:
                if incident["incident_id"]==int(incident_id):
                    return jsonify(incident),200
            return jsonify({"message": "Incident id not found"}), 404
        elif incident_catgeory:
            matching_incidents=[incident for incident in dict1 if incident["incident_category"]==str(incident_catgeory)]
            if matching_incidents:
                return jsonify(matching_incidents),200
            else:
                return jsonify({"message": "Incident category not found"}), 404
        else:
            return jsonify(dict1),200

    # POST requests endpoint  
    @app.route("/input-data", methods=['POST'])
    def input_incident():
        if request.method == "POST":
            try:
                data = request.get_json()
                if data is None:
                    return jsonify({"error": "Invalid JSON data"}), 400

                # Print the received data for debugging
                print("Received data:", data)
                df=pd.DataFrame(data)
                engine = create_engine("postgresql://postgres:Vishnu123@localhost/postgres")
                with engine.connect() as conn:
                    df.to_sql('incident_data', if_exists="append", index=False, con=conn)
                    conn.commit()
                conn.close()

            except Exception as e:
                return jsonify({"error": str(e)}), 500

            return "Your input has been added to the database", 201


            
    return app

if __name__ == "__main__":
    app = flask_app()
    app.run(debug=True)
