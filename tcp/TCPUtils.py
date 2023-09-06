from socketserver import ThreadingMixIn, TCPServer, BaseRequestHandler
from typing import Callable, Optional

from loggingUtils import getLogger

class AsyncTCPServer:
    @staticmethod
    def run(host: str, port: int, cb: Callable[[str, str], Optional[bytes]]):
        factory = AsyncTCPServer.ThreadedTCPRequestHandlerFactory(cb)

        with AsyncTCPServer.ThreadedTCPServer((host, port), factory.start) as server:
            server.serve_forever()

    class ThreadedTCPServer(ThreadingMixIn, TCPServer):
        pass

    class ThreadedTCPRequestHandler(BaseRequestHandler):
        def __init__(self, request, client_address, server, callback: Callable[[str, str], Optional[bytes]]):
            self.logger = getLogger("Singularr.TCPServer")
            self.cb = callback
            super().__init__(request, client_address, server)

        def setup(self):
            self.logger.info(f"Connected to client with ip {self.client_address[0]}")

        def handle(self):
            data = str(self.request.recv(1024), 'ascii')
            self.logger.info(f"Got {data} to client with ip {self.client_address[0]}")
            to_send = self.cb(self.client_address[0], data)
            if not to_send is None:
                self.request.sendall(to_send)

        def finish(self):
            self.logger.info(f"Disconnected from client with ip {self.client_address[0]}")

    class ThreadedTCPRequestHandlerFactory:
        def __init__(self, callback: Callable[[str, str], Optional[bytes]]):
            self.callback = callback

        def start(self, request, client_address, server):
            return AsyncTCPServer.ThreadedTCPRequestHandler(request, client_address, server, self.callback)