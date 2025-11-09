import http.server
import socketserver

PORT = 8000

Handler = http.server.BaseHTTPRequestHandler

def main():
    host = "0.0.0.0"
    with socketserver.TCPServer((host, PORT), Handler) as server:
        print("serving at port ", PORT)
        server.serve_forever()

if __name__ == "__main__":
    main()


