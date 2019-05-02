from functools import partial
from types import MappingProxyType
from typing import Union, Iterable
from aiohttp import ClientSession

from .models import IssueClose

class Headers:
  headers = MappingProxyType({
    "Accept": "application/vnd.github.machine-man-preview+json",
    "Authorization": "token {token}"
  })

  def __new__(cls, token: str):
    headers = cls.headers.copy()
    headers["Authorization"] = headers["Authorization"].format(token=token)
    return MappingProxyType(headers)

class GitHubAPI:
  http_client: ClientSession = None  
  _prefix = "https://api.github.com"
  _urls = MappingProxyType({
    "add_labels_to_issue": "{prefix}/repos/{owner}/{repo}/issues/{issue}/labels",
    "remove_label_from_issue": "{prefix}/repos/{owner}/{repo}/issues/{issue}/labels/{name}",
    "close_issue": "{prefix}/repos/{owner}/{repo}/issues/{issue}"
  })

  def __init__(self, token: str):
    self.token = token
    self.headers = Headers(token)

  def _url(self, key, **kwargs):
    return self._urls[key].format(prefix=self._prefix, **kwargs)

  def add_labels_to_issue(self, *, labels: Union[str, Iterable[str]], owner: str, repo: str, issue: int):
      _labels = []
      if isinstance(labels, str):
        _labels.append(labels)
      elif isinstance(labels, Iterable):
        _labels.extend(labels)
      else:
        raise TypeError(f"label must be of type str or Iterable[str]")

      url = self._url("add_labels_to_issue", owner=owner, repo=repo, issue=issue)
      data = { "labels": _labels }

      return self.http_client.post(url, json=data, headers=self.headers)

  def remove_label_from_issue(self, *, label: str, owner: str, repo: str, issue: int):
      url = self._url("remove_label_from_issue", name=label, owner=owner, repo=repo, issue=issue)
      return self.http_client.delete(url, headers=self.headers)

  def close_issue(self, *, owner: str, repo: str, issue: int):
      url = self._url("close_issue", owner=owner, repo=repo, issue=issue)
      data = IssueClose().dict()

      return self.http_client.post(url, json=data, headers=self.headers)