import json


class GitHubError(Exception):
    """General exception for GitHub"""

    def __init__(self, message, payload=None):
        self.message = message
        self.payload = payload

    def __str__(self):
        if self.payload:
            json_string = json.dumps(self.payload, indent=2, sort_keys=True)
            return f"{self.message}\nPayload:\n{json_string}"
        else:
            return f"{self.message}"


class NoHandlerError(GitHubError):
    pass


class MultipleHandlerError(GitHubError):
    pass
