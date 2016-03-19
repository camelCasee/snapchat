import server
import tornado.ioloop

app = server.Application()
app.listen(8888)
tornado.ioloop.IOLoop.instance().start()
