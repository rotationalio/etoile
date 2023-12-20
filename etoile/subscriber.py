import json
import time
from datetime import datetime
import pandas as pd
from pyensign.ensign import Ensign
from pyensign.utils.pbtime import to_datetime

from etoile.detect import State

class TrafficSubscriber:
    """
    Subscribe to traffic updates and return aggregated data.
    """

    def __init__(self, topic="figure-updates-json", cred_path=""):
        self.ensign = Ensign(cred_path=cred_path)
        self.topic = topic
        self.vehicles = {}
        self.start = time.time()
        self.total_vehicles = 0

    async def updates(self):
        """
        Subscribe to traffic updates, yield aggregated data.
        """

        async for event in self.ensign.subscribe(self.topic):
            updates = json.loads(event.data)
            for update in updates:
                self.update_vehicle(update["id"], State.parse(update["state"]))
            yield self.vehicle_rate()

    async def daily_counts(self):
        """
        Return daily vehicle counts.
        """

        days = {}
        query = "SELECT * FROM " + self.topic
        cursor = await self.ensign.query(query)
        ids = set()
        async for event in cursor:
            now = to_datetime(event.created)
            day = now.strftime("%Y-%m-%d")
            updates = json.loads(event.data)
            for update in updates:
                if update["id"] not in ids:
                    ids.add(update["id"])
                    if day not in days:
                        days[day] = 0
                    days[day] += 1
        d = [[k, v] for k, v in days.items()]
        d.sort(key=lambda x: x[0])
        return d

    def update_vehicle(self, id, state):
        if state == State.EXIT:
            if id in self.vehicles:
                del self.vehicles[id]
            return
        elif state == State.ENTER:
            self.total_vehicles += 1
        self.vehicles[id] = state

    def vehicle_rate(self):
        now = datetime.now()
        rate = (self.total_vehicles / (now.timestamp() - self.start)) / 60
        return now, rate