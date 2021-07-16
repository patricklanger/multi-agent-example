from ant_agent import AntAgent
import time
from flask import Flask, render_template, request, Response
from gevent.pywsgi import WSGIServer
import json
from world import World

user_letters = ["a", "b", "c", "d", "e", "f", "g", "h"]
AGENT_A_USERNAME = "agent-a"
AGENT_A_PASSWORD = "agent-a1234"
XMPP_SERVER = "192.168.178.22"

world = World(70, 25, 20, 5)
agents = {}


def produce_agent(user_letter):
    agents[user_letter] = AntAgent(f"agent-{user_letter}@{XMPP_SERVER}", f"agent-{user_letter}1234")
    agents[user_letter].start()


if __name__ == "__main__":
    for user in user_letters:
        produce_agent(user)

    app = Flask(__name__)

    @app.route("/create_ant")
    def create_ant():
        return world.create_ant(request.args.get("name")), 200

    @app.route("/move")
    def ant_moves():
        name = request.args.get("name")
        direction = request.args.get("direction")
        try:
            return world.move_ant(name, direction), 200
        except IndexError:
            return Response(status=400)

    @app.route('/world')
    def return_world():
        return json.dumps(world.get_view())

    @app.route('/')
    def show_view():
        return render_template("view.html")

    # slow server
    # app.run()

    # Fast server
    http_server = WSGIServer(('127.0.0.1', 5000), app)
    http_server.serve_forever()

    while True:
        try:
            time.sleep(1)
            print("pow")
        except KeyboardInterrupt:
            [agent.stop() for agent in agents]
            break
    print("Ants finished")

