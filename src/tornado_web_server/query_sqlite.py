import sqlite3
import pandas as pd
import json

def _execute(query):
    """
    This function takes in SQLite queries and returns the answer to the user
    """
    dbPath = r'C:\Users\Kangabire\OneDrive - Northwestern University\BS Degree\Senior\Spring\EE 327\iPlant\src\tornado_web_server\database\sensor_reading_database.db'
    connection = sqlite3.connect(dbPath)
    cursorobj = connection.cursor()
    try:
        cursorobj.execute(query)
        result = cursorobj.fetchall()
        connection.commit()
    except Exception:
        raise
    connection.close()
    return result

supported_measurements = [
    "ds", 
    "light_intensity",    
    "temperature",                
    "humidity",                
    "soil_moisture",                 
    "ts"
    ]

def _processresponse(rows):
        data = pd.DataFrame(rows,columns=supported_measurements)
        message = {}
        message["light_intensity"] = data[["ds","light_intensity"]].to_json(orient="values")
        message["temperature"] = data[["ds","temperature"]].to_json(orient="values")
        message["humidity"] = data[["ds","humidity"]].to_json(orient="values")
        message["soil_moisture"] = data[["ds","soil_moisture"]].to_json(orient="values")
        
        return json.dumps(message)

if __name__ == "__main__":
    table_name = "sensor_readings_test4"
    query = ''' select 
                        ds,
                        light_intensity, 
                        temperature, 
                        humidity, 
                        soil_moisture, 
                        ts 
                    from %s limit 5
                '''%table_name

    rows =_execute(query) 
    print(type(_processresponse(rows)))
    