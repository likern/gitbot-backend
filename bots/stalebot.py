import asyncio
from datetime import datetime
from models.mongo.issues import MongoIssueActionStatus


class StaleBot:
    def __init__(self, collection):
        self._collection = collection

    async def mark_stale_issues(self):
        utcnow = datetime.utcnow()
        cursor = self._collection.find(
            {
                "action.status": MongoIssueActionStatus.mark_stale,
                "action.date": {"$lte": utcnow}
            }
        )
        for issue in await cursor.to_list(100):
            pass
        await asyncio.sleep(60)
        asyncio.create_task(self.mark_stale_issues())

    async def close_stale_issues(self):
        utcnow = datetime.utcnow()
        result = self._collection.find(
            {
                "action.status": MongoIssueActionStatus.close_issue,
                "action.date": {"$lte": utcnow}
            }
        )
        await asyncio.sleep(60)
        asyncio.create_task(self.close_stale_issues())
