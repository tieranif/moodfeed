"""
MoodFeed — Step 1: Standalone real-time expression detector

Run this alone, before building anything else. It opens your webcam,
detects your face, classifies your expression, and shows it live.
This proves the core mechanic works before you wire it into an app.

SETUP:
    python3 -m pip install fer opencv-python tensorflow

    (fer bundles a pretrained CNN — no training needed to get started.
    tensorflow is a heavy install; give it a few minutes the first time.)

RUN:
    python3 detector.py

    Press 'q' to quit.
"""

try:
    import cv2
    try:
        from fer import FER
    except ImportError:  # fer 25.x exposes the class under fer.fer
        from fer.fer import FER
except ModuleNotFoundError as exc:
    import traceback
    traceback.print_exception(exc)
    raise SystemExit(
        "Missing required dependencies. Install them with:\n"
        "  python3 -m pip install fer opencv-python tensorflow"
    ) from exc

import time

# mtcnn=True uses a more accurate (but slower) face detector.
# Set to False for faster/cheaper detection once you're just testing logic.
detector = None


def get_detector(mtcnn: bool = True):
    """Return a singleton FER detector, creating it on first call.

    This avoids heavy TensorFlow model initialization at import time.
    """
    global detector
    if detector is None:
        detector = FER(mtcnn=mtcnn)
    return detector

EXPRESSIONS = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]

def dominant_expression(emotions: dict) -> tuple[str, float]:
    """Return (label, confidence) for the top-scoring expression."""
    label = max(emotions, key=emotions.get)
    return label, emotions[label]


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam. Check camera permissions.")

    print("MoodFeed detector running. Press 'q' to quit.")

    last_log = 0
    LOG_INTERVAL = 2  # seconds between console logs, keeps output readable

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # use lazy detector for standalone run too
        det = get_detector()
        results = det.detect_emotions(frame)

        for face in results:
            (x, y, w, h) = face["box"]
            label, confidence = dominant_expression(face["emotions"])

            # Draw box + label on the video feed
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 200, 0), 2)
            cv2.putText(
                frame,
                f"{label} ({confidence:.2f})",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 200, 0),
                2,
            )

            now = time.time()
            if now - last_log > LOG_INTERVAL:
                print(f"Detected: {label} ({confidence:.2f})")
                last_log = now

        cv2.imshow("MoodFeed — Expression Detector (press q to quit)", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()