from air_ground_collaboration.uav_path_planning import IUAVPathPlanning

class GridPathPlanning(IUAVPathPlanning):

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
        mission_section.append([-50, -50, 2])
        return mission_section

    def define_mission(self):
        mission_sublist = []

        mission_sublist += self.generate_mission_section(-50, -50, -17, 2)
        mission_sublist += self.generate_mission_section(0, -50, -17, 2)
        mission_sublist += self.generate_mission_section(-50, -17, 17, 2)
        mission_sublist += self.generate_mission_section(0, -17, 17, 2)
        mission_sublist += self.generate_mission_section(-50, 17, 50, 2)
        mission_sublist += self.generate_mission_section(0, 17, 50, 2)

        return [mission_sublist]