import os
import yaml


def loadyaml(configfile):
    with open(configfile, encoding='utf-8') as fl:
        ymlstring = fl.read()
    return yaml.load(ymlstring)


def update_config(configfile, config):
    with open(configfile, "w") as fl:
        yaml.dump(config, fl, default_flow_style=False)


def load_config():
    configfile = os.path.expanduser("~/.gitlab_cli.yml")
    if os.path.exists(configfile):
        config = loadyaml(configfile)
    else:
        print("Config file not found. A new one will be created")
        config = loadyaml("./gitlab_cli/config.yml")
        config["client"] = {
            "server": input("Gitlab server: "),
            "token": input("Token: "),
            "api_version": "4",
            "default_project": input("Default project id: "),
        }
        update_config(configfile, config)
    return config


config = load_config()
