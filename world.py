import random as r
from ant import Ant


def modify_part_of_world(world, color, center_xcor, center_ycor, size):
    radius = int(size / 2)
    top = int(center_xcor + radius)
    bottom = int(center_xcor - radius)
    left = int(center_ycor - radius)
    right = int(center_ycor + radius)
    for column in range(left, right):
        world[column] = [color if bottom < ind < top else x for ind, x in enumerate(world[column])]
    return world


def distance_to(x_one, y_one, x_two, y_two):
    """
    Calculates the distance from (x_one, y_one) to (x_two, y_two)
    :param x_one:
    :param y_one:
    :param x_two:
    :param y_two:
    :return: the distance
    """
    x_dist = abs(x_one - x_two)
    y_dist = abs(y_one - y_two)
    return x_dist + y_dist


class World:
    def __init__(self, world_width, world_height, number_of_leftover_food, size_of_leftover_food):
        self.width = world_width
        self.height = world_height
        self.center_xcor = int(self.width / 2)
        self.center_ycor = int(self.height / 2)
        self.empty_field = "#5D8233"
        self.ant_field = "#284E78"
        self.loaded_ant_field = "#3E215D"
        self.home_field = "#7F8B52"
        self.food_field = "#ECD662"
        self.ants = {}

        # random_world = [[random.choice([color_food, color_home, color_ant, color_empty]) for i in range(world_length)]
        #                 for j in range(world_height)]

        empty_world = [[self.empty_field for i in range(self.width)] for j in range(self.height)]

        # Create Anthome
        world_with_anthome = modify_part_of_world(world=empty_world,
                                                  color=self.home_field,
                                                  center_xcor=self.center_xcor,
                                                  center_ycor=self.center_ycor,
                                                  size=10)

        # Create Food
        world_with_food = world_with_anthome
        food_radius = int(size_of_leftover_food / 2)
        distance_to_center = food_radius + 10
        distance_to_wall = food_radius + 2
        coordinates = [(x, y) for x in range(self.width) for y in range(self.height)]
        not_possible_coordinates = []
        for (x, y) in coordinates:
            if x < distance_to_wall or x > (self.width - distance_to_wall) or y < distance_to_wall or y > (self.height - distance_to_wall):
                not_possible_coordinates.append((x, y))
            elif x in list(range(self.center_xcor - distance_to_center, self.center_xcor + distance_to_center)) and y in list(range(self.center_ycor - distance_to_center, self.center_ycor + distance_to_center)):
                not_possible_coordinates.append((x, y))
        possible_coordinates = [(x, y) for (x, y) in coordinates if (x, y) not in not_possible_coordinates]
        for i in range(number_of_leftover_food):
            xcor, ycor = r.choice(possible_coordinates)
            try:
                world_with_food = modify_part_of_world(world=world_with_food,
                                                       color=self.food_field,
                                                       center_xcor=xcor,
                                                       center_ycor=ycor,
                                                       size=size_of_leftover_food)
                # print(f"Build food at: {xcor}, {ycor}")
            except IndexError:
                print(f"Cant build food at: {xcor}, {ycor}")

        # World with an anthome and foodplaces is generated
        self.world_without_ants = world_with_food
        self.world_with_ants = [row.copy() for row in world_with_food]  # copy to get a new reference

    def create_ant(self, name):
        self.ants[name] = Ant((self.center_xcor, self.center_ycor))
        answer = {"position": (self.ants[name].xcor, self.ants[name].ycor)}
        return answer

    def get_view(self):
        world_with_ants = [row.copy() for row in self.world_without_ants]
        for ant in self.ants.values():
            world_with_ants[ant.ycor][ant.xcor] = ant.color
        return world_with_ants

    def move_ant(self, name, direction):
        ant = self.ants[name]
        if direction == "north":
            x = ant.xcor
            y = ant.ycor - 1
        elif direction == "east":
            x = ant.xcor + 1
            y = ant.ycor
        elif direction == "south":
            x = ant.xcor
            y = ant.ycor + 1
        elif direction == "west":
            x = ant.xcor - 1
            y = ant.ycor

        answer = {
            "position": (ant.xcor, ant.ycor),
            "moved": False,
            "found_food": False,
            "delivered_food": False
        }
        if 0 >= x or x >= self.width - 1 or 0 >= y or y >= self.height - 1:
            answer["moved"] = False
        elif (ant.xcor, ant.ycor) == (ant.xcor_home, ant.ycor_home):
            ant.search_mode()
            answer["position"] = ant.xcor, ant.ycor = (x, y)
            answer["moved"] = True
            answer["delivered_food"] = True
        elif self.world_without_ants[y][x] == self.food_field:
            ant.carry_mode()
            answer["position"] = ant.xcor, ant.ycor = (x, y)
            answer["moved"] = True
            answer["found_food"] = True
            self.world_without_ants[y][x] = self.empty_field
        else:
            answer["position"] = ant.xcor, ant.ycor = (x, y)
            answer["moved"] = True

        return answer

    def get_reachable_friends(self, name):
        """
        Returns ant names nearby the requesting ant.
        :param name:
        :return: list of ant names
        """
        distance_to_be_reachable = 25
        ant = self.ants[name]
        reachable_friends = [friend for friend in self.ants
                             if 3 < distance_to(self.ants[friend].xcor,
                                                self.ants[friend].ycor,
                                                ant.xcor, ant.ycor) < distance_to_be_reachable]
        return reachable_friends



