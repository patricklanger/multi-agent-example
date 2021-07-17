import json
from flask import Flask, render_template, request, Response
from gevent.pywsgi import WSGIServer
from ant_agent import AntAgent
from world import World

world = World(world_width=70, world_height=25, number_of_leftover_food=10, size_of_leftover_food=5)

user_letters = ["a", "b", "c", "d", "e", "f", "g", "h"]
XMPP_SERVER = "192.168.178.22"
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

    @app.route("/get_friends")
    def return_agent_addresses():
        addresses = [f"{agent.name}@{XMPP_SERVER}" for agent in agents.values()]
        return json.dumps(addresses), 200

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


