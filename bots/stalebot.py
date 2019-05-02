from pprint import pprint
import asyncio
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from toolz import itertoolz
from models.mongo.issues import MongoIssueActionStatus, MongoIssueAction, MongoIssue, MongoIssueClosed
from models.mongo.user import MongoUserAuthStatus
from api import GitHubAPI
from typing import List


class StaleBot:


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

    async def run(self):
        await self._schedule(self._mark_stale_issues, time=10)
        await self._schedule(self._close_stale_issues, time=10)

    async def _schedule(self, func, *, time = 60):
        try:
            await func()
        except BaseException as err:
            print(err)
        finally:
            await asyncio.sleep(time)
            asyncio.create_task(self._schedule(func, time=time))

    async def _get_old_issues_with_status(self, status: MongoIssueActionStatus) -> List:
        utcnow = datetime.utcnow()
        cursor = self._colls.issues.find(
            {
                "action.status": status,
                "action.date": {"$lte": utcnow}
            }
        )

        return await cursor.to_list(None)

    async def _map_installation_with_token(self, issues):
        ids = list({issue["installation_id"] for issue in issues})
        cursor = self._colls.installations.find(
            filter={"_id": {"$in": ids}}
        )

        mapping = {x["_id"] : x["token"] for x in await cursor.to_list(None)}
        return mapping

    async def _mark_stale_issues(self):
        print("[ENTER] _mark_stale_issues")
        utcnow = datetime.utcnow()
        cursor = self._colls.issues.find(
            {
                "action.status": MongoIssueActionStatus.mark_stale,
                "action.date": {"$lte": utcnow}
            }
        )

        stale_issues = await cursor.to_list(None)
        # Break as soon as possible if no stale issues
        if not stale_issues:
            return None

        install_ids = list({issue["installation_id"] for issue in stale_issues})

        cursor = self._colls.installations.find(
            filter={"_id": {"$in": install_ids}}
        )

        mapping = { item["_id"] : item["token"] for item in await cursor.to_list(None)}

        for issue in stale_issues:
            token = mapping[issue["installation_id"]]
            kwargs = {
                "owner": issue["owner"],
                "repo": issue["repo"],
                "issue": issue["issue"]
            }

            context = GitHubAPI(token).add_labels_to_issue(labels="stale", **kwargs)
            async with context as resp:
                if resp.status in [200, 201]:
                    new_date = issue["action"]["date"] + timedelta(minutes=1)
                    new_action = MongoIssueAction(
                        status=MongoIssueActionStatus.close_issue,
                        date=new_date
                    ).dict(skip_defaults=True)
                    issue_id = issue["_id"]

                    result = await self._colls.issues.update_one(
                        filter={"_id": issue_id},
                        update={"$set": {"action": new_action}}
                    )
                    print(f"[...] _mark_stale_issues: updated issue [{issue_id}] with action: [{new_action}]")
                    if result.acknowledged == True:
                        pass
                elif resp.status == 404:
                    print(f"!!!!!!!! CHECK THAT PATH !!!!!!!!!!")
                    new_action = dict(MongoIssueClosed())
                    result = await self._colls.issues.update_one(
                        filter={"_id": issue["_id"]},
                        update={"$set": {"action": new_action}}
                    )

                    if result.acknowledged == True:
                        print(f"Successfully closed issue: [{pprint(issue)}]")
                    # Issue was deleted manually by someone
        print("[EXIT] _mark_stale_issues")

    async def _close_stale_issues(self):
        print("[ENTER] _close_stale_issues")
        issues = await self._get_old_issues_with_status(MongoIssueActionStatus.close_issue)
        if not issues:
            return None

        tokens = await self._map_installation_with_token(issues)
        for issue in issues:
            token = tokens[issue["installation_id"]]
            kwargs = {
                "owner": issue["owner"],
                "repo": issue["repo"],
                "issue": issue["issue"]
            }

            gh = GitHubAPI(token)
            async with gh.close_issue(**kwargs) as resp:
                if resp.status in [200, 201]:
                    async with gh.remove_label_from_issue(label="stale", **kwargs) as resp:
                        if resp.status in [200, 404]:
                            new_action = dict(MongoIssueClosed())
                            issue_id = issue["_id"]
                            result = await self._colls.issues.update_one(
                                filter={"_id": issue_id},
                                update={"$set": {"action": new_action}}
                            )
                            print(f"[...] _close_stale_issues: updated issue [{issue_id}] with action: [{new_action}]")

                            if result.acknowledged == True:
                                pass
        print("[EXIT] _close_stale_issues")
