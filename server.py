import http.server
import socketserver

PORT = 8000

Handler = http.server.ThreadingHTTPServer

with socketserver.TCPServer(("", PORT), Handler) as server:
    print("serving at port ", PORT)
    server.serve_forever()