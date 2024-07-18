import os
import json


DEFAULT_CONFIG = {
    "mod_folder_path": "~",
    "download_mods": True,
    "delete_mods": True
}


CONFIG_PATH = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "TSMP_Launcher", "config.json")

class config_service():

    def __init__(self):
        pass

    def create_config(self):
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, 'w') as config_file:
            json.dump(DEFAULT_CONFIG, config_file, indent=4)

    def load_config(self):
        if not os.path.exists(CONFIG_PATH):
            self.create_config()
        with open(CONFIG_PATH, 'r') as config_file:
            return json.load(config_file)

    def save_config(self, config):
        with open(CONFIG_PATH, 'w') as config_file:
            json.dump(config, config_file, indent=4)