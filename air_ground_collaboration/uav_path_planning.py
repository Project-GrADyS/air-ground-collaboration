from abc import ABC, abstractmethod
from typing import List, Tuple

class IUAVPathPlanning(ABC):

    @abstractmethod
    def define_mission() -> List[List[Tuple]]:
        pass

    def generate_mission_section(self) -> List[Tuple]:
        pass


'''
def grid_mission2():
    mission_sublist = []

    start_x = -50
    start_y = -50
    x = start_x
    y = start_y
    limit_y = -17

    for i in range(50):
        if i % 2 == 0:
            x += 2
        else:
            if y == start_y:
                y = limit_y
            else:
                y = start_y
        mission_sublist.append([x, y, 2])
    mission_sublist.append([-50, -50, 2])
    return [mission_sublist]
'''
'''

def define_mission(type):
    if type == "ZigZag":
        return zigzag_mission()
    elif type == "Grid":
        return grid_mission()
'''
