import tornado.web
import tornado.ioloop

class basicRequestHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello!!!\n")

class staticRequestHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("")

    def post(self):
        print(self.request.body)
        output_file = open("data.txt", 'ab')
        output_file.write(self.request.body)
        output_file.write(b'\n')
        output_file.close()

if __name__ == "__main__":
    app = tornado.web.Application ([
        (r"/",basicRequestHandler),
        (r"/blog", staticRequestHandler)
    ])

    app.listen(8881)
    print("I am listening")
    tornado.ioloop.IOLoop.current().start()