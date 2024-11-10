from path_planning.uav_path_planning_interface import IUAVPathPlanning

class ZigZagPathPlanning(IUAVPathPlanning):

    def generate_mission_section(self, start_x, start_y, end_x, end_y, step, substep):
        mission_section = []
        x = start_x
        y = start_y
        limit_y = start_y - substep
        limit_x = start_x

        mission_section.append([start_x, start_y, 2])
        
        for i in range(18):
            if i % 2 == 0:
                if x < end_x:
                    x += step
                mission_section.append([x, limit_y, 2])
            else:
                if y <= end_y:
                    y += step
                else:
                    limit_x += 10
                mission_section.append([limit_x, y, 2])

        mission_section.append([end_x, end_y, 2])
        mission_section.append([-50, -50, 2])

        return mission_section

    def define_mission(self):
        mission_sublist = []
        
        # Generate mission sections
        mission_sublist += self.generate_mission_section(-50, -50, 0, -17, 7, 4)
        mission_sublist += self.generate_mission_section(0, -50, 50, -17, 7, 4)
        mission_sublist += self.generate_mission_section(-50, -17, 0, 17, 7, 4)
        mission_sublist += self.generate_mission_section(0, -17, 50, 17, 7, 4)
        mission_sublist += self.generate_mission_section(-50, 17, 0, 50, 7, 4)
        mission_sublist += self.generate_mission_section(0, 17, 50, 50, 7, 4)
        
        return [mission_sublist]