import sleekxmpp
import multiprocessing as mp


class Sender(sleekxmpp.ClientXMPP):
    def __init__(self, jid, pwd, pipe_recv, send_to_addr):
        super(Sender, self).__init__(jid=jid, password=pwd)
        self.add_event_handler("session_start", self.start_session)
        self.register_plugin("xep_0030")
        self.register_plugin("xep_0199")
        self.pipe_recv = pipe_recv
        self.send_to = send_to_addr

    def start_session(self, event):
        self.send_presence()
        self.get_roster()
        self._start_thread("chat_send", self.chat_send)

    def chat_send(self):
        while True:
            try:
                data = self.pipe_recv.recv()
            except KeyboardInterrupt:
                break
            self.send_message(mto=self.send_to,
                              mbody=data,
                              mtype="chat")


class MultiprocessingSender(mp.Process):
    def __init__(self, jid, pwd, send_to_addr):
        super(MultiprocessingSender, self).__init__()
        self.pipe_send, self.pipe_recv = mp.Pipe()
        self.sender = Sender(jid, pwd, self.pipe_recv, send_to_addr)
        self.daemon = True

    def run(self):
        if self.sender.connect():
            self.sender.process(block=True)
        else:
            print("Could not connect to the network.")

    def send_msg(self, msg=""):
        if msg:
            self.pipe_send.send(msg)
