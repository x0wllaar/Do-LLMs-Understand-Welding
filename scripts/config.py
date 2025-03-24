import json5

with open("./config.jsonc", "rt", encoding="utf-8") as config_file:
    CONFIG = json5.load(config_file)

with open("./secrets.jsonc", "rt", encoding="utf-8") as secrets_file:
    CONFIG["secrets"] = json5.load(secrets_file)["secrets"]
