import json


def load_config() -> dict:
    with open("config.json", "r") as f:
        return json.load(f)
    
def load_twitch_config() -> dict:
    return load_config()["twitch"]

def load_spotify_config() -> dict:
    return load_config()["spotify"]

def push_config(config: dict) -> None:
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)