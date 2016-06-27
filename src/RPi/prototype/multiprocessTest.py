import multiprocessing as mp
import time


class ProperlySuicidalClass(mp.Process):
    def __init__(self, recv_pipe):
        mp.Process.__init__(self)
        self.recv = recv_pipe
        self.end_the_party_event = mp.Event()
        self.end_the_party_event.clear()

    def run(self):
        while not self.end_the_party_event.is_set():
            self._do_sth()
            time.sleep(0.01)
        print("Suicide exit")

    def _do_sth(self):
        data = self.recv.poll()
        if data:
            print("\nSuicidal process: {}".format(self.recv.recv()))

    def kill(self):
        self.end_the_party_event.set()


def second_func(pipe_data):
    while True:
        time.sleep(0.01)
        if pipe_data:
            print("\nSecond process: {}".format(pipe_data.recv()))


def get_text(pipe):
    in_data = ""
    while in_data != 'q':
        in_data = input("Enter data: ")
        pipe.send(in_data)


def main_version1():
    recv, echo = mp.Pipe()
    process = mp.Process(target=second_func, args=(recv,))
    process.start()
    get_text(echo)
    process.join()


def main_version2():
    recv, echo = mp.Pipe()
    process = ProperlySuicidalClass(recv_pipe=recv)
    process.start()
    get_text(echo)
    process.kill()
    process.join()
    print("Main exit")


if __name__ == "__main__":
    main_version2()
