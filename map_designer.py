import pygame
import json
import os


class Helper:
    @staticmethod
    def get_distance(pos1, pos2):
        return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5

    @staticmethod
    def intersection_point_circle(pos1, pos2, radius):
        return Helper.get_distance(pos1, pos2) <= radius


class Line:
    def __init__(self, pos1, pos2):
        self.pos1 = pos1
        self.pos2 = pos2


class Designer:
    VERSION = 1

    def __init__(self):
        self.size = (1920, 1080)
        self.auto_end_dist = 10
        self.screen = pygame.display.set_mode(self.size)

        self.last_point = None
        self.branch_start = None
        self.enable = False

        self.lines = []
        self.draw()

    def start(self):
        if self.enable:
            raise Exception("Already running")
        
        self.enable = True
        self.loop()

    def stop(self):
        self.enable = False

    def click(self, pos):
        if not self.last_point:
            self.branch_start = pos
            self.last_point = pos
        
        else:
            if self.branch_start and Helper.intersection_point_circle(pos, self.branch_start, self.auto_end_dist):
                self.lines.append(Line(self.last_point, self.branch_start))
                self.reset_selection()

            else:
                self.lines.append(Line(self.last_point, pos))
                self.last_point = pos

        self.draw()

    def reset_selection(self):
        self.last_point = None
        self.branch_start = None
        self.draw()

    def event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.enable = False
    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.click(event.pos)
                
                elif event.button == 3:
                    self.reset_selection()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.save()

                elif event.key == pygame.K_l and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.load()

                elif event.key == pygame.K_SPACE:
                    self.clear()

    def normalize_pos(self, pos):
        return pos[0] / self.size[0], pos[1] / self.size[1]

    def scale_up(self, pos):
        return pos[0] * self.size[0], pos[1] * self.size[1]

    def save(self, file_path="map.json"):
        result = {
            "v": self.VERSION,
            "lines": [[self.normalize_pos(line.pos1), self.normalize_pos(line.pos2)] for line in self.lines]
        }

        result_json = json.dumps(result)

        try:
            with open(file_path, "w") as file:
                file.write(result_json)

            print("saved")

        except PermissionError:
            print("No access, not saved")

    def load(self, file_path="map.json"):
        if not (os.path.exists(file_path) and os.path.isfile(file_path)):
            print("Path not exists or path is not a file")
            return

        with open(file_path, "r") as file:
            map_json = file.read()

        map_dict = json.loads(map_json)

        if map_dict["v"] != self.VERSION:
            print("Incorrect map version")
            return

        self.lines = [Line(self.scale_up(line[0]), self.scale_up(line[1])) for line in map_dict["lines"]]
        self.reset_selection()

    def clear(self):
        self.lines = []
        self.draw()

    def draw(self):
        self.screen.fill((255, 255, 255))

        for line in self.lines:
            pygame.draw.aaline(self.screen, (0, 0, 0), line.pos1, line.pos2)
        
        if self.last_point:
            pygame.draw.circle(self.screen, (255, 0, 255), self.last_point, 3)

        if self.branch_start:
            pygame.draw.circle(self.screen, (0, 255, 0), self.branch_start, self.auto_end_dist)

        pygame.display.update()

    def loop(self):
        while self.enable:
            self.event()
            

if __name__ == "__main__":
    des = Designer()
    des.start()
