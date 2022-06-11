import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.websocket
from query_sqlite import _execute
from extract_ESP32_data import extract_ESP32_data
import pandas as pd
from datetime import date, datetime
import json
import os

table_name = "sensor_readings_test21"
supported_measurements = [
    "ds", 
    "light_intensity",    
    "temperature",                
    "humidity",                
    "soil_moisture",                 
    "ts"
    ]

class WebSocketHandler(tornado.websocket.WebSocketHandler):

    connected_clients = set()

    def check_origin(self, origin):
        return True

    def open(self):
        WebSocketHandler.connected_clients.add(self)

    def on_close(self):
        WebSocketHandler.connected_clients.remove(self)

    @classmethod
    def send_updates(cls, message):
        for connected_client in cls.connected_clients:
            connected_client.write_message(message)


class AddSensorReading(tornado.web.RequestHandler):
    def get(self):
        self.render("static/sensor_readings.html")

        query = ''' select 
                        ds,
                        light_intensity, 
                        temperature, 
                        humidity, 
                        soil_moisture, 
                        ts 
                    from %s limit 5
                '''%table_name

        rows = _execute(query)
        WebSocketHandler.send_updates(self._processresponse(rows))

    def post(self):
        
        ESP32_raw_data = self.request.body # the data is send by the ESP32 as a byte representation of a dictionary
        ESP32_data = extract_ESP32_data(ESP32_raw_data) # the data is returned as a dictionary

        # creating a table if it does not already exist
        create_table_query = '''CREATE TABLE IF NOT EXISTS '%s'
            (
                ds TEXT, 
                light_intensity REAL, 
                temperature REAL, 
                humidity REAL, 
                soil_moisture REAL, 
                ts TEXT
            )'''%table_name;
        _execute(create_table_query)
        
        # inserting the new data in the database
        today = date.today()
        now = datetime.now()
        insert_query = ''' insert into '%s' 
            (
                ds, 
                light_intensity, 
                temperature, 
                humidity, 
                soil_moisture, 
                ts
            ) 
            values 
            ('%s', %f,%f,%f,%f,'%s') 
            ''' %(
                table_name,
                today.strftime("%m/%d/%y"),
                ESP32_data["light_intensity"], 
                ESP32_data["temperature"],
                ESP32_data["humidity"],
                ESP32_data["soil_moisture"],
                now.strftime("%H:%M:%S")
            );
        
        _execute(insert_query)
        

        # send the new data to all the clients
        query = ''' select 
                        ds,
                        light_intensity, 
                        temperature, 
                        humidity, 
                        soil_moisture, 
                        ts 
                    from %s
                '''%table_name

        rows = _execute(query)
        WebSocketHandler.send_updates(self._processresponse(rows))

    def _processresponse(self,rows):
        data = pd.DataFrame(rows,columns=supported_measurements)

        """
        message = {}
        message["light_intensity"] = data[["ds","light_intensity"]].values.tolist()
        message["temperature"] = data[["ds","temperature"]].values.tolist()
        message["humidity"] = data[["ds","humidity"]].values.tolist()
        message["soil_moisture"] = data[["ds","soil_moisture"]].values.tolist()
        
        return json.dumps(message)

        """
        return data.to_html()

class AboutPage(tornado.web.RequestHandler):
    def get(self):
        self.render("static/neat_webpage.html")   


class ShowSensorReading(tornado.web.RequestHandler):
    def get(self):
        self.render("static/sensor_readings.html")   

class TestShowSensorReading(tornado.web.RequestHandler):
    def get(self):
        self.render("static/index.html") 

application = tornado.web.Application(
    [
    (r"/about",AboutPage),
    (r"/show_sensor_reading", ShowSensorReading),
    (r"/add_sensor_reading" ,AddSensorReading),
    (r"/socket", WebSocketHandler),
    (r"/test_webdesign", TestShowSensorReading),
    ],
    debug=True,
    static_path=os.path.join(os.path.dirname(__file__),'static')
    )

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()