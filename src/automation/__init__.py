class Settings:
    def __init__(self):
        self.options = {}

    def config(self, options: dict):
        self.options.update(options)
        print("[SETTINGS] Updated:", self.options)

settings = Settings()

class Automation:
    def __init__(self):
        self.config = settings.options

    def run(self):
        print("[AUTOMATION] Running automation with:")
        for k, v in self.config.items():
            print(f"  {k}: {v}")
