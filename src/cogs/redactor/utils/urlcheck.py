class UrlCheck:
    def __init__(self, url: str):
        self.url = url

    def check(self) -> bool:
        if not self.url.startswith("https://cdn.discordapp.com/"):
            return False
        return True
