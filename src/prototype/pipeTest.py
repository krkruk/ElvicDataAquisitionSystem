import multiprocessing as mp
import time


class PipeTest(mp.Process):
    def __init__(self):
        super(PipeTest, self).__init__()
        self.send, self.recv = mp.Pipe()
        self.kill_process = mp.Event()
        self.kill_process.clear()

    def run(self):
        try:
            while not self.kill_process.is_set():
                print(self.recv.recv(), "in process!!!")
        except KeyboardInterrupt:
            pass

    def send_msg(self, msg):
        self.send.send(msg)

    def kill(self):
        self.kill_process.set()

if __name__ == "__main__":
    data = "Hello world!"

    p = PipeTest()
    p.daemon = True
    p.start()

    for i in range(5):
        p.send_msg(data)
        time.sleep(0.5)

    p.kill()
    print("EXIT")
