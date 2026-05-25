from abc import ABC, abstractmethod

class SimAdapter(ABC):
    @abstractmethod
    def send_command(self, command):
        pass

    @abstractmethod
    def close(self):
        pass