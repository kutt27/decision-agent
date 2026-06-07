def get_config():
    config = {}
    try:
        with open(".env") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip("\"'")
                    config[key] = value
    except FileNotFoundError:
        pass
    return config
