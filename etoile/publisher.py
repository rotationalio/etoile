import cv2
import json

from pyensign.ensign import Ensign
from pyensign.events import Event

from etoile.stream import VideoStream
from etoile.detect import FigureDetector

class TrafficPublisher():
    """
    Publish traffic updates to an Ensign topic.
    """

    def __init__(self, topic="figure-updates-json", frames_topic="detection-frames", cred_path="", src="", show=False):
        self.ensign = Ensign(cred_path=cred_path)
        self.topic = topic
        self.frames_topic = frames_topic
        self.show = show
        self.detector = FigureDetector(VideoStream(src), show=self.show)

    async def run(self):
        """
        Publish traffic updates as they are detected.
        """

        for figures, frame in self.detector.detect():
            if figures:
                event = self.figures_to_event(figures)
                await self.ensign.publish(self.topic, event)
            if frame is not None:
                event = self.frame_to_event(frame)
                await self.ensign.publish(self.frames_topic, event)

    def frame_to_event(self, frame):
        """
        Convert an OpenCV frame into an Ensign event.
        """

        data = cv2.imencode(".jpg", frame)[1].tobytes()
        return Event(data, mimetype="application/octet-stream", schema_name="video-frame", schema_version="0.1.0", meta={"encoding": "jpeg"})

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