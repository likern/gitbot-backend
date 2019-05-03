from enum import Enum
from typing import Any, Optional, Union, List
from pydantic import BaseModel, validator
from datetime import datetime


class IssueAction(str, Enum):
    opened = 'opened'
    edited = 'edited'
    deleted = 'deleted'
    transferred = 'transferred'
    pinned = 'pinned'
    unpinned = 'unpinned'
    closed = 'closed'
    reopened = 'reopened'
    assigned = 'assigned'
    unassigned = 'unassigned'
    labeled = 'labeled'
    unlabeled = 'unlabeled'
    milestoned = 'milestoned'
    demilestoned = 'demilestoned'

class IssueUser(BaseModel):
    login: str
    id: int
    node_id: str
    avatar_url: str
    gravatar_id: str
    url: str
    html_url: str
    followers_url: str
    following_url: str
    gists_url: str
    starred_url: str
    subscriptions_url: str
    organizations_url: str
    repos_url: str
    events_url: str
    received_events_url: str
    type: str
    site_admin: bool

class IssueSender(IssueUser):
    pass

class IssueRepositoryOwner(IssueUser):
    pass

class IssueRepository(BaseModel):
    id: int
    node_id: str
    name: str
    full_name: str
    owner: IssueRepositoryOwner
    private: bool
    html_url: str
    description: Optional[str]
    fork: bool
    url: str
    forks_url: str
    keys_url: str
    collaborators_url: str
    teams_url: str
    hooks_url: str
    issue_events_url: str
    events_url: str
    assignees_url: str
    branches_url: str
    tags_url: str
    blobs_url: str
    git_tags_url: str
    git_refs_url: str
    trees_url: str
    statuses_url: str
    languages_url: str
    stargazers_url: str
    contributors_url: str
    subscribers_url: str
    subscription_url: str
    commits_url: str
    git_commits_url: str
    comments_url: str
    issue_comment_url: str
    contents_url: str
    compare_url: str
    merges_url: str
    archive_url: str
    downloads_url: str
    issues_url: str
    pulls_url: str
    milestones_url: str
    notifications_url: str
    labels_url: str
    releases_url: str
    deployments_url: str
    created_at: datetime
    updated_at: datetime
    pushed_at: datetime
    git_url: str
    ssh_url: str
    clone_url: str
    svn_url: str
    homepage: Optional[str]
    size: int
    stargazers_count: int
    watchers_count: int
    language: Optional[str]
    has_issues: bool
    has_projects: bool
    has_downloads: bool
    has_wiki: bool
    has_pages: bool
    forks_count: int
    mirror_url: Optional[str]
    archived: bool
    open_issues_count: int
    license: Optional[str]
    forks: int
    open_issues: int
    watchers: int
    default_branch: str

class IssuePayload(BaseModel):
    id: int
    title: str
    body: str
    state: str
    locked: bool
    labels: List[str]
    milestone: Optional[Any]
    created_at: str
    updated_at: str
    closed_at: Optional[str]
    comments: int
    assignee: Optional[Any]
    assignees: Optional[List[str]]
    number: int
    user: IssueUser
    author_association: str
    url: str
    comments_url: str
    events_url: str
    html_url: str
    labels_url: str
    repository_url: str
    node_id: str
    

class IssueInstallation(BaseModel):
    id: int
    node_id: str

class IssueChangesTitle(BaseModel):
    previous: str

    class Config:
        fields = {
            'previous': 'from'
        }

class IssueChangesBody(BaseModel):
    previous: str

    class Config:
        fields = {
            'previous': 'from'
        }

class IssueChanges(BaseModel):
    title: IssueChangesTitle
    body: IssueChangesBody

class IssueEvent(BaseModel):
    action: IssueAction
    issue: IssuePayload
    assignee: Optional[Any]
    label: Optional[Any]
    repository: IssueRepository
    sender: IssueSender
    installation: IssueInstallation

class IssueOpened(IssueEvent):
    @validator('action')
    def check_type(cls, value):
        if value != IssueAction.opened:
            raise ValueError('Not IssueOpened')
        return value

class IssueEdited(IssueEvent):
    changes: IssueChanges

    @validator('action')
    def check_type(cls, value):
        if value != IssueAction.edited:
            raise ValueError('Not IssueEdited')
        return value

class IssueClosed(IssueEvent):
    changes: Any

    @validator('action')
    def check_type(cls, value):
        if value != IssueAction.closed:
            raise ValueError('Not IssueClosed')
        return value

