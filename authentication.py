
import os
import json





class Authentication:

    JSON_PATH = "netatmo_app.json"
    TOKEN_FILE_PATH = ".netatmo_token"
    def __init__(self):
        print("authentication help going")

    def netatmo_json_exists(self):
        # Does this return false if the file doesn't exist?
        return os.path.isfile(self.JSON_PATH)

    def token_file_exists(self):
        return os.path.isfile(self.TOKEN_FILE_PATH)

    def create_netatmo_json(self, client_id, client_secret):
        mydict = {
            "name": "Station & Temperature download",
            "redirect_uri": "http://127.0.0.1:5000/auth-callback",
            "client_id": f"{client_id}",
            "client_secret": f"{client_secret}"
        }
        json_str = json.dumps(mydict, indent=4)
        with open('netatmo_app.json', 'x') as f:
            f.write(json_str)
        return True



