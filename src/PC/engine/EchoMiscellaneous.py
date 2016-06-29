import multiprocessing as mp


class EchoMiscellaneous(mp.Process):
    def __init__(self, recv_pipe):
        super(EchoMiscellaneous, self).__init__()
        self.recv_pipe = recv_pipe
        self.daemon = True

    def run(self):
        while self._main(): pass

    def _main(self):
        try:
            data = self.recv_pipe.recv()
        except KeyboardInterrupt:
            return False
        print("DATA RECEIVED:")
        print(data)

        return True
