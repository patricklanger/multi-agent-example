import requests
import random
import json
import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, FSMBehaviour, State
from spade.message import Message

STATE_TWO = "STATE_TWO"
STATE_THREE = "STATE_THREE"

SPEED = 0.1  # s / step


def choose_random_directions():
    """
    :return: Returns two random directions as list
    """
    n, e, s, w = ("north", "east", "south", "west")
    return random.choice([[n, e], [e, s], [s, w], [w, n]])


def decide_next_move(goal, pos):
    """
    For a given pos and a goal, the function calculates the best next move.
    :param goal: (x, y)
    :param pos: (x, y)
    :return: north, east, south or west as string
    """
    x_dir = pos[0] - goal[0]  # 0 -> x, 1 -> y
    y_dir = pos[1] - goal[1]
    if abs(x_dir) > abs(y_dir):
        return "west" if x_dir > 0 else "east"
    else:
        return "north" if y_dir > 0 else "south"


def calc_distance(start, goal):
    x_dist = abs(start[0] - goal[0])  # 0 -> x, 1 -> y
    y_dist = abs(start[1] - goal[1])
    return x_dist + y_dist


class AntState(State):
    async def run(self):
        pass

    def send_move_request(self, move_to):
        try:
            res = requests.get(f"http://127.0.0.1:5000/move/{self.agent.name}/{move_to}")
            res = json.loads(res.text)
            if res["moved"]:
                self.agent.position = (res["position"][0], res["position"][1])
                if res["found_food"]:
                    self.agent.carry_food = True
                    self.agent.good_food_place = (res["position"][0], res["position"][1])
                if res["delivered_food"]:
                    self.agent.carry_food = False
            else:
                self.agent.actions = choose_random_directions()
        except Exception as e:
            print(e)

    async def inform_friends(self):
        try:
            res = requests.get(f"http://127.0.0.1:5000/get_friends")
            res = [friend for friend in json.loads(res.text) if self.agent.name not in friend]
            for friend in res:
                msg = Message(to=friend)     # Instantiate the message
                msg.body = json.dumps(self.agent.position)  # Set the message content
                await self.send(msg)
        except Exception as e:
            print(e)

    def decide_next_move(self, goal):
        pos = self.agent.position
        if pos[0] > goal[0]:
            move_to = "west"
        elif pos[0] < goal[0]:
            move_to = "east"
        elif pos[1] < goal[1]:
            move_to = "south"
        else:
            move_to = "north"
        return move_to


class AntBehaviour(FSMBehaviour):
    async def on_start(self):
        res = requests.get(f"http://127.0.0.1:5000/create_ant/{self.agent.name}")
        position = json.loads(res.text)["position"]
        self.agent.position = (position[0], position[1])
        self.agent.home = (position[0], position[1])
        self.agent.good_food_place = (99999, 99999)
        self.agent.carry_food = False
        self.agent.actions = choose_random_directions()


class Searching(AntState):
    async def run(self):
        #  print("SEARCHING", self.agent.name, self.agent.position, self.agent.good_food_place)
        await asyncio.sleep(SPEED)
        if calc_distance(self.agent.position, self.agent.good_food_place) < 30:
            move_to = decide_next_move(self.agent.good_food_place, self.agent.position)
        else:
            move_to = random.choice(self.agent.actions)
        self.send_move_request(move_to)
        if calc_distance(self.agent.position, self.agent.good_food_place) == 0:
            self.agent.good_food_place = (99999, 99999)
        if self.agent.carry_food:
            self.set_next_state(STATE_THREE)
            await self.inform_friends()
        else:
            self.set_next_state(STATE_TWO)


class CarryHome(AntState):
    async def run(self):
        #  print("CARRYING", self.agent.name, self.agent.position, self.agent.good_food_place)
        await asyncio.sleep(SPEED)
        move_to = decide_next_move(self.agent.home, self.agent.position)
        self.send_move_request(move_to)
        if self.agent.carry_food:
            self.set_next_state(STATE_THREE)
        else:
            self.set_next_state(STATE_TWO)


class ReceiveMsg(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            #  print(f"{self.agent.name} Hey I got a msg: {msg.body}")
            body = json.loads(msg.body)
            acceptable_distance = 30
            distance_to_new_food_source = calc_distance(self.agent.position, body)
            if distance_to_new_food_source < calc_distance(self.agent.position, self.agent.good_food_place) \
                    and distance_to_new_food_source <= acceptable_distance:
                self.agent.good_food_place = body


class AntAgent(Agent):
    async def setup(self):
        print(f"{self.name} started")

        # self.web.start(hostname="127.0.0.1", port=10000)
        # print(self.web.server, self.web.port)

        fsm = AntBehaviour()
        fsm.add_state(name=STATE_TWO, state=Searching(), initial=True)
        fsm.add_state(name=STATE_THREE, state=CarryHome())
        fsm.add_transition(source=STATE_TWO, dest=STATE_TWO)
        fsm.add_transition(source=STATE_TWO, dest=STATE_THREE)
        fsm.add_transition(source=STATE_THREE, dest=STATE_TWO)
        fsm.add_transition(source=STATE_THREE, dest=STATE_THREE)
        self.add_behaviour(fsm)

        cycl = ReceiveMsg()
        self.add_behaviour(cycl)


