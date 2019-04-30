import asyncio
from datetime import datetime
from itertools import groupby
from models.mongo.issues import MongoIssueActionStatus
from models.mongo.user import MongoUserAuthStatus


class StaleBot:
    urls = {
        "set_label": "/repos/{owner}/{repo}/issues/{issue}/labels"
    }

    def __init__(self, collections, http_client):
        self._colls = collections
        self._http_client = http_client

    async def map_user_with_token(user_ids):
        documents = self._colls.users.find(
            filter={"auth.status": MongoUserAuthStatus.success},
            projection=["auth.token", "auth.github.user_id"]
        )

        user_to_token = {}
        for user_id in user_ids:
            for document in documents:
                if user_id == document["auth.github.user_id"]:
                    user_to_token[user_id] = document["auth.token"]
            if user_id not in user_to_token:
                raise ValueError(f"Can't find token for user_id [{user_id}]")
        return user_to_token

    async def set_label(self, *, label, owner, repo, issue):
        endpoint = urls["set_label"].format(owner=owner, repo=repo, issue=issue)
        payload = { "labels": [f"{label}"] }

        async with self._http_client.post(endpoint, json=payload) as resp:
            print(resp.status)
            print(resp.json())

    async def schedule_issue_become_stale(self):
        pass

    async def mark_stale_issues(self):
        print("[STALEBOT] MARK STALE ISSUES")
        utcnow = datetime.utcnow()
        cursor = self._colls.issues.find(
            {
                "action.status": MongoIssueActionStatus.mark_stale,
                "action.date": {"$lte": utcnow}
            }
        )
        
        stale_issues = await cursor.to_list(None)
        install_ids = [stale_issue["installation_id"] for stale_issue in stale_issues]
        # groups = groupby(stale_issues, key=lambda issue: return issue["installation_id"])

        cursor = self._colls.installations.find(
            filter={"_id": {"$in": install_ids}}
        )

        installs = await cursor.to_list(None)
        install_to_token = dict(installs)

        for install_id in install_ids:
            # FIXME

        for key, group in groupby(stale_issues, key=lambda x: return )
        
        print(stale_issues)
        # [issue["issue_id"] for issue in stale_issue]
        # for issue in  :
        #     print(f"STALE ISSUE: [{issue}]")
        await asyncio.sleep(10)
        asyncio.create_task(self.mark_stale_issues())

    async def close_stale_issues(self):
        print("[STALEBOT] CLOSE STALE ISSUES")
        utcnow = datetime.utcnow()
        result = self._colls.issues.find(
            {
                "action.status": MongoIssueActionStatus.close_issue,
                "action.date": {"$lte": utcnow}
            }
        )
        await asyncio.sleep(10)
        asyncio.create_task(self.close_stale_issues())
