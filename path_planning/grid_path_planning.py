from path_planning.uav_path_planning_interface import IUAVPathPlanning

class GridPathPlanning(IUAVPathPlanning):

    def __init__(self, size, uav_num):
        self.size = size
        self.step = 0.02 * self.size
        self.uav_num = uav_num

    def generate_mission_section(self, start_x, start_y, end_y, step):
        mission_section = []
        mission_section.append([start_x, start_y, 2])
        x = start_x
        y = start_y
        limit_y = end_y

        for i in range(50):
            if i % 2 == 0:
                x += step
            else:
                if y == start_y:
                    y = limit_y
                else:
                    y = start_y
            mission_section.append([x, y, 2])
        mission_section.append([-1 * self.size//2, -1 * self.size//2, 2])
        return mission_section
    '''
    def define_mission2(self):
        mission_sublist = []

        mission_sublist += self.generate_mission_section(-50, -50, -17, 2)
        mission_sublist += self.generate_mission_section(0, -50, -17, 2)
        mission_sublist += self.generate_mission_section(-50, -17, 17, 2)
        mission_sublist += self.generate_mission_section(0, -17, 17, 2)
        mission_sublist += self.generate_mission_section(-50, 17, 50, 2)
        mission_sublist += self.generate_mission_section(0, 17, 50, 2)

        return [mission_sublist]
    '''
    
    def define_mission(self):
        total_mission = []
        mission_sublist = []
        mission_sublist2 = []
        mission_sublist3 = []

        if self.uav_num == 1:
            mission_sublist += self.generate_mission_section(-1 * self.size//2, -1 * self.size//2, -1* (self.size//6 + 1), self.step)
            mission_sublist += self.generate_mission_section(0, -1 * self.size//2, -1* (self.size//6 + 1), self.step)
            mission_sublist += self.generate_mission_section(-1 * self.size//2, -1* (self.size//6 + 1), self.size//6 + 1, self.step)
            mission_sublist += self.generate_mission_section(0, -1* (self.size//6 + 1), self.size//6 + 1, self.step)
            mission_sublist += self.generate_mission_section(-1 * self.size//2, self.size//6 + 1, self.size//2, self.step)
            mission_sublist += self.generate_mission_section(0, self.size//6 + 1, self.size//2, self.step)
            total_mission.append([mission_sublist])
        elif self.uav_num == 2:
            mission_sublist += self.generate_mission_section(-1 * self.size//2, -1 * self.size//2, -1* (self.size//6 + 1), 2)
            mission_sublist2 += self.generate_mission_section(0, -1 * self.size//2, -1* (self.size//6 + 1), 2)
            mission_sublist += self.generate_mission_section(-1 * self.size//2, -1* (self.size//6 + 1), self.size//6 + 1, 2)
            mission_sublist2 += self.generate_mission_section(0, -1* (self.size//6 + 1), self.size//6 + 1, 2)
            mission_sublist += self.generate_mission_section(-1 * self.size//2, self.size//6 + 1, self.size//2, 2)
            mission_sublist2 += self.generate_mission_section(0, self.size//6 + 1, self.size//2, 2)
            total_mission.append([mission_sublist])
            total_mission.append([mission_sublist2])
        elif self.uav_num == 3:
            mission_sublist += self.generate_mission_section(-1 * self.size//2, -1 * self.size//2, -1* (self.size//6 + 1), 2)
            mission_sublist += self.generate_mission_section(0, -1 * self.size//2, -1* (self.size//6 + 1), 2)
            mission_sublist2 += self.generate_mission_section(-1 * self.size//2, -1* (self.size//6 + 1), self.size//6 + 1, 2)
            mission_sublist2 += self.generate_mission_section(0, -1* (self.size//6 + 1), self.size//6 + 1, 2)
            mission_sublist3 += self.generate_mission_section(-1 * self.size//2, self.size//6 + 1, self.size//2, 2)
            mission_sublist3 += self.generate_mission_section(0, self.size//6 + 1, self.size//2, 2)
            total_mission.append([mission_sublist])
            total_mission.append([mission_sublist2])
            total_mission.append([mission_sublist3])

        return total_mission