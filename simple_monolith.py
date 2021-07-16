from turtle import Screen, Turtle
from ant_agent import AntAgent
import time
from flask import Flask, render_template, request, Response
import random
import json
from world import World

AGENT_A_USERNAME = "agent-a"
AGENT_A_PASSWORD = "agent-a1234"
XMPP_SERVER = "192.168.178.22"

world = World(100, 70, 5, 14)

if __name__ == "__main__":

    ant = AntAgent(f"{AGENT_A_USERNAME}@{XMPP_SERVER}", AGENT_A_PASSWORD)
    future = ant.start()
    future.result()
    # future = ant.web.start(hostname="127.0.0.1", port="10000")
    # future.result()

    app = Flask(__name__)

    @app.route('/hello')
    def say_hello():
        print("Hello Server")
        return "200"

    @app.route("/move")
    def ant_moves():
        x = int(request.args.get("x"))
        y = int(request.args.get("y"))
        old_x = int(request.args.get("old_x"))
        old_y = int(request.args.get("old_y"))
        try:
            world.world_with_ants[x][y] = world.ant_field
        except IndexError:
            return Response(status=400)
        world.world_with_ants[old_x][old_y] = world.world_without_ants[old_x][old_y]
        return world.world_without_ants[x][y], 200

    @app.route('/world')
    def return_world():
        return json.dumps(world.world_with_ants)

    @app.route('/')
    def show_view():
        return render_template("view.html")

    app.run()

    while ant.is_alive():
        try:
            time.sleep(1)
            print("pow")
        except KeyboardInterrupt:
            ant.stop()
            break
    print("Ants finished")

