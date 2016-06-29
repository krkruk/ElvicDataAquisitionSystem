import multiprocessing as mp
import sleekxmpp
import time


class XmppReceiverClient(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password, pipe_pass_data):
        self.pipe_pass_data = pipe_pass_data
        super(XmppReceiverClient, self).__init__(jid=jid, password=password)
        self.add_event_handler("session_start", self.start_session)
        self.add_event_handler("message", self.message)
        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0004')  # Data Forms
        self.register_plugin('xep_0060')  # PubSub
        self.register_plugin('xep_0199')  # XMPP Ping
        print("In init")

    def start_session(self, event):
        print("XMPP session started")
        self.send_presence()
        self.get_roster()

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            try:
                self.pipe_pass_data.send(msg["body"])
            except KeyboardInterrupt:
                pass


class XmppDataReceiver(mp.Process):
    def __init__(self, jid, password, pipe_pass_data):
        super(XmppDataReceiver, self).__init__()
        self.daemon = True
        self.send_pipe = pipe_pass_data
        self.kill_process = mp.Event()
        self.kill_process.clear()
        self.xmpp = XmppReceiverClient(jid, password, self.send_pipe)

    def run(self):
        print("In xmpp run")
        if self.xmpp.connect():
            self.xmpp.process(block=True)
        else:
            print("Unable to connect.")
        print("Exited:", self.pid)

    def kill(self):
        self.kill_process.set()

if __name__ == "__main__":
    send, recv = mp.Pipe()
    p = XmppDataReceiver("elvic02@jappix.com", "elvic", recv)
    p.start()

    try:
        print(recv.recv())
    except KeyboardInterrupt:
        pass

    p.kill()
