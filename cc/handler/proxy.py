
import zmq

from cc.handler import CCHandler
from cc.message import CCMessage
from cc.stream import CCStream

__all__ = ['ProxyHandler']

CC_HANDLER = 'ProxyHandler'

#
# message proxy
#

class ProxyHandler(CCHandler):
    """Simply proxies further"""
    def __init__(self, hname, hcf, ccscript):
        super(ProxyHandler, self).__init__(hname, hcf, ccscript)

        s = self.make_socket()
        s.setsockopt(zmq.LINGER, 500)
        self.stream = CCStream(s, ccscript.ioloop)
        self.stream.on_recv(self.on_recv)

        self.launch_workers()

        self.stat_increase = ccscript.stat_increase

    def launch_workers(self):
        pass

    def make_socket(self):
        zurl = self.cf.get('remote-cc')
        s = self.zctx.socket(zmq.XREQ)
        s.setsockopt(zmq.LINGER, 500)
        s.connect(zurl)
        return s

    def on_recv(self, zmsg):
        """Got message from remote CC, send to client."""
        try:
            self.log.debug('ProxyHandler.handler.on_recv')
            cmsg = CCMessage(zmsg)
            self.stat_increase('count')
            self.stat_increase('bytes', cmsg.get_size())
            self.cclocal.send_multipart(zmsg)
        except:
            self.log.exception('ProxyHandler.on_recv crashed, dropping msg')

    def handle_msg(self, cmsg):
        """Got message from client, send to remote CC"""
        self.stream.send_cmsg(cmsg)
