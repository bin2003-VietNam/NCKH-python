from ultralytics import YOLO
import cv2
import numpy as np

model = YOLO(r"C:\Users\nguye\PycharmProjects\PythonProject\Weight-yolo11s\best.pt")
cap = cv2.VideoCapture(r"C:\Users\nguye\PycharmProjects\PythonProject\Test_resource\video\Untitled video - Made with Clipchamp.mp4")

if not cap.isOpened():
    print("Không mở được video!")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, stream=True)

    for r in results:
        for box in r.boxes:
            # Lấy confidence
            conf = float(box.conf[0])
            if conf < 0.3:  # loại box rác
                continue

            # Lấy toạ độ
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

            # Nếu box to hơn 90% frame → bỏ luôn (lỗi model)
            h, w = frame.shape[:2]
            if (x2 - x1) * (y2 - y1) > 0.9 * w * h:
                continue

            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])

            cls = int(box.cls[0])
            label = f"{model.names[cls]} {conf:.2f}"

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.imshow("YOLO", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
