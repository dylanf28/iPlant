import os
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web

class WebpageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("javascript_websocket.html")


class ChangesHandler(tornado.websocket.WebSocketHandler):

    connected_clients = set()

    def check_origin(self, origin):
        return True

    def open(self):
        ChangesHandler.connected_clients.add(self)

    def on_close(self):
        ChangesHandler.connected_clients.remove(self)

    @classmethod
    def send_updates(cls, message):
        for connected_client in cls.connected_clients:
            connected_client.write_message(message)

class SendHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

    def post(self):
        message = self.get_argument(name = "fname")
        ChangesHandler.send_updates(message)

def main():

    app = tornado.web.Application(
        [(r"/socket", ChangesHandler), (r"/", WebpageHandler),(r"/send_data", SendHandler)]
    )

    app.listen(8888)

    loop = tornado.ioloop.IOLoop.current()
    try:
        loop.start()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()