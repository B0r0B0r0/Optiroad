import math

class Car:
    def __init__(self, center):
        self.center = center
        self.tendency = 'stationary'
        self.disappear_iter = 0
        self.last_center = center
        self.found = False
        self.found_iter = 0

    def update_center(self, center, offset_car):
        if self.found:
            return False
        
        distance = math.sqrt((center[0] - self.center[0]) ** 2 + (center[1] - self.center[1]) ** 2)
        if distance < offset_car:
            self.last_center = self.center
            self.center = center
            self.disappear_iter = 0
            self.found = True
            self.found_iter += 1

            if self.center[1] > self.last_center[1]:
                self.tendency = 'down'
            elif self.center[1] < self.last_center[1]:
                self.tendency = 'up'

            return True

        return False

    def update_iter(self):
        if not self.found:
            self.disappear_iter += 1
        else:
            self.found = False

        if self.disappear_iter > 2 and self.found_iter > 3:
            if self.tendency == 'up':
                return -1
            elif self.tendency == 'down':
                return 1
        return 0