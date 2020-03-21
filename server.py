import http.server
import app

class BuildRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        kwargs['directory'] = './build'
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        # Rebuild every time a request is made
        app.build()
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

def main():
    server_address = ('', 8000)
    server = http.server.HTTPServer(server_address, BuildRequestHandler)
    print('Start http server on http://0.0.0.0:8000')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()

if __name__ == '__main__':
    main()
