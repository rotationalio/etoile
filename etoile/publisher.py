import json

from pyensign.ensign import Ensign
from pyensign.events import Event

from etoile.stream import VideoStream
from etoile.detect import FigureDetector

class TrafficPublisher():
    """
    Publish traffic updates to an Ensign topic.
    """

    def __init__(self, topic="figure-updates-json", cred_path="", src="", show=False):
        self.ensign = Ensign(cred_path=cred_path)
        self.topic = topic
        self.show = show
        self.detector = FigureDetector(VideoStream(src), show=self.show)

    async def run(self):
        """
        Publish traffic updates as they are detected.
        """

        for figures in self.detector.detect():
            if figures:
                event = self.figures_to_event(figures)
                await self.ensign.publish(self.topic, event)

    def figures_to_event(self, figures):
        """
        Convert figures into Ensign events.
        """

        updates = []
        for figure in figures:
            u = {
                "id": str(figure.id),
                "state": str(figure.state),
            }
            updates.append(u)

        return Event(json.dumps(updates).encode("utf-8"), schema_name="traffic-update", schema_version="0.1.0")