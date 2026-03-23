import queue

class Bus:
    def __init__(self):
        self.cmd_queue = queue.Queue()
        self.log_queue = queue.Queue()
        self.connections = []
        self.targets = []

        