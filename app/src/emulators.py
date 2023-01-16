import hjson

class TerminalsJsonApi:
    def __init__(self, file):
        with open(file, "r") as fp:
            self.json_content = hjson.load(fp)
    
    @property
    def current(self):
        id_current = self.json_content["current"]
        for terminal in self.json_content["emulators"]:
            if terminal["id"] == id_current:
                return terminal
    @property
    def all(self):
        return self.json_content["emulators"]