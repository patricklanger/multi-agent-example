import time
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
import requests
import random


class AntAgent(Agent):
    class SearchBehav(CyclicBehaviour):
        async def run(self):
            # print(f"{self.agent.jid} is searching for food...")
            time.sleep(0.2)
            move_to = random.choice(self.actions)
            old_x, old_y = self.agent.position.values()
            if move_to == "north":
                x = old_x
                y = old_y + 1
            elif move_to == "east":
                x = old_x + 1
                y = old_y
            elif move_to == "south":
                x = old_x
                y = old_y - 1
            elif move_to == "west":
                x = old_x - 1
                y = old_y
            try:
                res = requests.get(f"http://127.0.0.1:5000/move?x={x}&y={y}&old_x={old_x}&old_y={old_y}")
                if int(res.status_code) == 200:
                    self.agent.position["x"] = x
                    self.agent.position["y"] = y
                else:
                    dirs = ["north", "east", "south", "west"]
                    dirs.remove(move_to)
                    self.actions = dirs
                    print(move_to)
                    print(self.actions)
            except Exception as e:
                print(e)
                # stop agent from behaviour
            # await self.agent.stop()

        async def on_start(self):
            self.actions = random.sample(["north", "east", "south", "west"], 3)

    class MyBehav2(CyclicBehaviour):
        async def run(self):
            print("Hello Behav2")
            time.sleep(1)
            # stop agent from behaviour
            # await self.agent.stop()

    async def setup(self):
        print("AntAgent started")
        self.position = {
            "x": 35,
            "y": 50
        }
        s = self.SearchBehav()
        self.add_behaviour(s)
        self.web.start(hostname="127.0.0.1", port=10000)
        print(self.web.server, self.web.port)


