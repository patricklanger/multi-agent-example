import time
import asyncio
import requests
import random
import json
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, FSMBehaviour, State
from spade.message import Message
from spade.template import Template

STATE_ONE = "STATE_ONE"
STATE_TWO = "STATE_TWO"
STATE_THREE = "STATE_THREE"

SPEED = 20  # ms / step


def calc_distance(start, goal):
    x_dist = start["x"] - goal["x"] if start["x"] > goal["x"] else goal["x"] - start["x"]
    y_dist = start["y"] - goal["y"] if start["y"] > goal["y"] else goal["y"] - start["y"]
    return x_dist + y_dist


class AntState(State):
    async def run(self):
        pass

    def send_move_request(self, move_to):
        try:
            res = requests.get(f"http://127.0.0.1:5000/move?name={self.agent.name}&direction={move_to}")
            if int(res.status_code) == 200:
                res = json.loads(res.text)
                if res["moved"]:
                    self.agent.position["x"] = res["position"][0]
                    self.agent.position["y"] = res["position"][1]
                    if res["found_food"]:
                        self.agent.carry_food = True
                        self.agent.good_food_place = {"x": res["position"][0], "y": res["position"][1]}
                        print(f"{self.agent.name} found food {self.agent.carry_food}")
                    if res["delivered_food"]:
                        self.agent.carry_food = False
                else:
                    n, e, s, w = ("north", "east", "south", "west")
                    self.agent.actions = random.choice([[n, e], [e, s], [s, w], [w, n]])
        except Exception as e:
            print(e)

    def decide_next_move(self, goal):
        print(f"{self.agent.name} has a goal {goal}")
        pos = self.agent.position
        if pos["x"] > goal["x"]:
            move_to = "west"
        elif pos["x"] < goal["x"]:
            move_to = "east"
        elif pos["y"] < goal["y"]:
            move_to = "south"
        else:
            move_to = "north"
        return move_to


class AntBehaviour(FSMBehaviour):
    async def on_start(self):
        print(f"FSM starting at initial state {self.current_state}")
        n, e, s, w = ("north", "east", "south", "west")
        self.agent.actions = random.choice([[n, e], [e, s], [s, w], [w, n]])


class BeBorn(State):
    async def run(self):
        res = requests.get(f"http://127.0.0.1:5000/create_ant?name={self.agent.name}")
        position = json.loads(res.text)["position"]
        self.agent.position = {"x": position[0], "y": position[1]}
        self.agent.home = {"x": position[0], "y": position[1]}
        self.agent.good_food_place = False
        self.agent.carry_food = False

        await asyncio.sleep(0.1)
        self.set_next_state(STATE_TWO)


class Searching(AntState):
    async def run(self):
        await asyncio.sleep(SPEED)
        if self.agent.good_food_place:
            move_to = self.decide_next_move(self.agent.good_food_place)
        else:
            move_to = random.choice(self.agent.actions)
        self.send_move_request(move_to)
        if self.agent.carry_food:
            self.set_next_state(STATE_THREE)
            return
        self.set_next_state(STATE_TWO)


class CarryHome(AntState):
    async def run(self):
        await asyncio.sleep(SPEED)
        move_to = self.decide_next_move(self.agent.home)
        self.send_move_request(move_to)
        if not self.agent.carry_food:
            self.set_next_state(STATE_TWO)
            print(f"{self.agent.name} food delivered")
            return
        self.set_next_state(STATE_THREE)


class AntAgent(Agent):
    async def setup(self):
        fsm = AntBehaviour()
        fsm.add_state(name=STATE_ONE, state=BeBorn(), initial=True)
        fsm.add_state(name=STATE_TWO, state=Searching())
        fsm.add_state(name=STATE_THREE, state=CarryHome())
        fsm.add_transition(source=STATE_ONE, dest=STATE_TWO)
        fsm.add_transition(source=STATE_TWO, dest=STATE_TWO)
        fsm.add_transition(source=STATE_TWO, dest=STATE_THREE)
        fsm.add_transition(source=STATE_THREE, dest=STATE_TWO)
        fsm.add_transition(source=STATE_THREE, dest=STATE_THREE)
        self.add_behaviour(fsm)


