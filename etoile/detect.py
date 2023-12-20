import cv2
import time
import uuid
from enum import Enum

class State(Enum):
    ENTER = 0
    IN_TRANSIT = 1
    EXIT = 2

    def __str__(self):
        return self.name
    
    @classmethod
    def parse(cls, s):
        return cls[s.upper()]

class Figure:
    def __init__(self, x, y, w, h):
        self.id = uuid.uuid4()
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.midpoint = (x + w // 2, y + h // 2)
        self.state = State.ENTER
        self.prev_state = None

    def update(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.midpoint = (x + w // 2, y + h // 2)

    def change_state(self, state):
        self.prev_state = self.state
        self.state = state


class FigureDetector:
    """
    FigureDetector detects figures from a stream of video frames.
    """

    def __init__(self, stream, show=False):
        self.stream = stream
        self.show = show
        if self.show:
            cv2.namedWindow('FigureDetector')
    
    def preprocess(self, frame):
        frame = cv2.resize(frame, (640, 480))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.GaussianBlur(frame, (5, 5), 0)
        return frame
    
    def detect_rects(self, prev, frame):
        min_area = 1000
        max_area = 10**6

        # Difference between the previous frame and the current frame.
        #print(prev.shape, frame.shape)
        #print(prev.dtype, frame.dtype)
        cv2.accumulateWeighted(frame, prev, 0.5)
        delta = cv2.absdiff(frame, cv2.convertScaleAbs(prev))
        thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]

        # Dilate the thresholded image to fill in holes, then find contours on thresholded image.
        thresh = cv2.dilate(thresh, None, iterations=2)
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        figures = []
        for c in contours:
            # Filter by size
            area = cv2.contourArea(c)
            if area < min_area or area > max_area:
                continue

            # Compute the bounding box for the contour
            x, y, w, h = cv2.boundingRect(c)
            figures.append((x, y, w, h))
        return prev, figures

    def detect(self):
        """
        Return an iterator of detected figures.
        """

        avg = None
        on_screen = []
        while True:
            frame = self.stream.read()
            if frame is None:
                break

            # Preprocess the video frame, applying transformations to make it easier to detect figures.
            frame = self.preprocess(frame)

            # Detect the figures in the frame
            seen = set()
            if avg is not None:
                avg, rects = self.detect_rects(avg, frame)
                for r in rects:
                    x, y, w, h = r
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    midpoint = (x + w // 2, y + h // 2)

                    # Check if the figure is already on screen
                    found = False
                    for i, s in enumerate(on_screen):
                        dist = ((midpoint[0] - s.midpoint[0])**2 + (midpoint[1] - s.midpoint[1])**2)**0.5
                        if dist < 100:
                            on_screen[i].update(x, y, w, h)
                            on_screen[i].change_state(State.IN_TRANSIT)
                            seen.add(s.id)
                            found = True
                            break

                    if not found:
                        on_screen.append(Figure(x, y, w, h))
                        seen.add(on_screen[-1].id)
            else:
                avg = frame.copy().astype('float')
                continue

            # Update the state of the figures
            for f in on_screen:
                if f.id not in seen:
                    f.change_state(State.EXIT)

            # Return figures that changed state
            yield [f for f in on_screen if f.prev_state is None or f.state != f.prev_state]

            # Remove figures that have exited the screen
            on_screen = [f for f in on_screen if f.state != State.EXIT]

            if self.show:
                cv2.imshow('FigureDetector', frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    fname = str(time.time()) + '.png'
                    cv2.imwrite(fname, frame)