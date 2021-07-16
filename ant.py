class Ant:
    def __init__(self, position):
        self.xcor, self.ycor = position
        self.xcor_home, self.ycor_home = position
        self.color = "#284E78"

    def carry_mode(self):
        self.color = "#3E215D"

    def search_mode(self):
        self.color = "#284E78"
