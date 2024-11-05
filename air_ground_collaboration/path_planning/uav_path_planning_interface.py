from abc import ABC, abstractmethod
from typing import List, Tuple

class IUAVPathPlanning(ABC):

    @abstractmethod
    def define_mission() -> List[List[Tuple]]:
        pass
    
    @abstractmethod
    def generate_mission_section(self) -> List[Tuple]:
        pass
