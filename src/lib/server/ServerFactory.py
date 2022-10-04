from .constants import TCP_PROTOCOL, SAW_PROTOCOL, GBN_PROTOCOL
from .TCPServer import TCPServer
from .SAWServer import SAWServer
from .GBNServer import GBNServer
from lib.server.logger import log_tcp, log_saw, log_gbn
from .exceptions.ProtocolNotSupportedException import ProtocolNotSupportedException


class ServerFactory:

    def __init__(self, host, port, storage):
        self.servers = {
            TCP_PROTOCOL: TCPServer(host, port, storage),
            SAW_PROTOCOL: SAWServer(host, port, storage),
            GBN_PROTOCOL: GBNServer(host, port, storage)
        }

        self.loggers = {
            TCP_PROTOCOL: log_tcp,
            SAW_PROTOCOL: log_saw,
            GBN_PROTOCOL: log_gbn
        }


    def _is_supported_protocol(self, protocol):
        return protocol.lower() in self.servers


    def _verify_supported_protocol(self, protocol):
        if not self._is_supported_protocol(protocol):
            raise ProtocolNotSupportedException(f"Protocol {protocol} not supported")
        
    def get_server(self, protocol):
        self._verify_supported_protocol(protocol)
        return self.servers[protocol.lower()]


    def get_logger(self, protocol):
        self._verify_supported_protocol(protocol)
        return self.loggers[protocol.lower()]

        