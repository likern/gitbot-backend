from pydantic import BaseModel


class Account(BaseModel):
    id: int
    avatar_url: str
    events_url: str,
    followers_url: str
    following_url: str
    gists_url: str
    gravatar_id: str
    html_url: str
    login: str
    node_id: str
    organizations_url: str
    received_events_url: str
    repos_url: str
    site_admin: bool
    starred_url: str
    subscriptions_url: str
    type: str
    url: str
