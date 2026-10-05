"""Loopback-only static preview; no dependencies, external APIs or secrets."""
import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import time
from urllib.parse import unquote, urlsplit

ROOT=Path(__file__).resolve().parents[1]


class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(ROOT),**kwargs)

    def public_path(self):
        if any(part.startswith('.') for part in unquote(urlsplit(self.path).path).split('/') if part):
            self.send_error(404)
            return False
        return True

    def do_GET(self):
        if self.public_path():super().do_GET()

    def do_HEAD(self):
        if self.public_path():super().do_HEAD()

    def end_headers(self):
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','no-referrer')
        self.send_header('X-Frame-Options','DENY')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; object-src 'none'; base-uri 'self'; form-action 'none'; frame-ancestors 'none'")
        super().end_headers()

    def log_message(self,*args):
        pass


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=4174)
    parser.add_argument('--stop',action='store_true')
    args=parser.parse_args()
    stage=ROOT/'.local-preview';stage.mkdir(exist_ok=True)
    stop=stage/f'{args.port}.stop'
    if args.stop:
        stop.touch();print('Requested shutdown of this portfolio preview.');return
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    stop.unlink(missing_ok=True)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    print(f'Portfolio preview: http://127.0.0.1:{args.port}/',flush=True)
    try:
        while not stop.exists():time.sleep(.25)
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown();server.server_close();thread.join(timeout=3)


if __name__=='__main__':main()
