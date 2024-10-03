from abc import ABC, abstractmethod


class OrganiseRun(ABC):

    @abstractmethod
    def organise_run(self):
        ...
