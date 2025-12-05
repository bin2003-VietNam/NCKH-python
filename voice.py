import cv2
import time
import threading
import queue
import io
import pygame
from gtts import gTTS
from ultralytics import YOLO

model_path = r"C:\Users\nguye\PycharmProjects\PythonProject\Weight-yolo11s\best.pt"
video_path = r"C:\Users\nguye\PycharmProjects\PythonProject\Test_resource\video\test_1.mp4"
conf_threshold = 0.4
cooldown_duration = 5.0
frame_threshold = 15    # 1 khoảng 15 Frame
required_count = 5      # đếm số lượng/ tần xuất xuất hiện liên tục của nhãn biển báo
traffic_sign_ref = {
    'ben_xe_buyt': 'biển bến xe buýt',
    'cam_di_nguoc_chieu': 'biển cấm đi ngược chiều',
    'cam_do_xe': 'biển cấm đỗ xe',
    'cam_dung_cam_do_xe': 'biển cấm dừng và cấm đỗ xe',
    'cam_queo_phai': 'biển cấm quẹo phải',
    'cam_queo_trai': 'biển cấm quẹo trái',
    'cam_xe_container': 'biển cấm xe container',
    'cam_xe_o_to': 'biển cấm xe ô tô',
    'cam_xe_tai': 'biển cấm xe tải',
    'di_cham': 'biển đi chậm',
    'duong_nguoi_di_bo_cat_ngang': 'biển đường người đi bộ cắt ngang',
    'giao_nhau_voi_duong_khong_uu_tien': 'biển giao nhau với đường không ưu tiên',
    'huong_phai_di_vong_chuong_ngai_vat': 'biển hướng phải đi vòng chướng ngại vật',
    'toc_do_toi_da_50kmh': 'biển tốc độ tối đa năm mươi ki lô mét một giờ',
    'toc_do_toi_da_60kmh': 'biển tốc độ tối đa sáu mươi ki lô mét một giờ',
    'tre_em': 'biển báo trẻ em'
}
pygame.mixer.init()
speech_queue = queue.Queue()
model = YOLO(model_path)
last_alert_time = {}
detection_history = {}

def audio_worker():
    while True:
        text = speech_queue.get()
        if text is None:
            break

        try:
            clean_text = text.replace("_", " ")
            tts = gTTS(text=clean_text, lang='vi')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            # Phát âm thanh
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()

            pygame.mixer.music.load(fp)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

        except Exception as e:
            print(f"Lỗi âm thanh: {e}")
        finally:
            speech_queue.task_done()


t = threading.Thread(target=audio_worker, daemon=True)
t.start()


def process_frame(frame):
    results = model(frame, conf=conf_threshold, verbose=False)
    current_time = time.time()

    for result in results:
        boxes = result.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls_id = int(box.cls[0])
            class_name = model.names[cls_id]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, class_name, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            history = detection_history.setdefault(class_name, [])
            history.append(current_time)
            if len(history) > frame_threshold:
                history.pop(0)
            if len(history) < required_count:
                continue
            last_time = last_alert_time.get(class_name, 0)
            if current_time - last_time < cooldown_duration:
                continue
            readable_text = traffic_sign_ref[class_name]
            print(readable_text)

            speech_queue.put(readable_text)

            last_alert_time[class_name] = current_time

    return frame



# --- 3. CHƯƠNG TRÌNH CHÍNH ---
print("Đang khởi động Video...")
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(f"Không thể mở video tại: {video_path}")
    exit()

print("Nhấn 'q' để thoát")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Hết video hoặc lỗi đọc frame.")
        break

    # Gọi hàm xử lý và nhận lại frame đã vẽ
    processed_frame = process_frame(frame)

    # Hiển thị
    cv2.imshow('Traffic Sign Detection', processed_frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

# Dọn dẹp
cap.release()
cv2.destroyAllWindows()




















# from ultralytics import YOLO
# import cv2
# import pyttsx3
# from collections import deque
# import time
# import threading
#
#
# class TrafficSignDetector:
#     def __init__(self, model_path):
#         # Load YOLO model
#         self.model = YOLO(model_path)
#
#         # Khởi tạo text-to-speech engine
#         self.engine = pyttsx3.init()
#         self.engine.setProperty('rate', 150)  # Tốc độ đọc
#         self.engine.setProperty('volume', 5.0)  # Âm lượng
#
#         # Dictionary ánh xạ tên class sang câu đọc
#         self.sign_messages = {
#             'ben_xe_buyt': 'biển bến xe buýt',
#             'cam_di_nguoc_chieu': 'biển cấm đi ngược chiều',
#             'cam_do_xe': 'biển cấm đỗ xe',
#             'cam_dung_cam_do_xe': 'biển cấm dừng và cấm đỗ xe',
#             'cam_queo_phai': 'biển cấm quẹo phải',
#             'cam_queo_trai': 'biển cấm quẹo trái',
#             'cam_xe_container': 'biển cấm xe container',
#             'cam_xe_o_to': 'biển cấm xe ô tô',
#             'cam_xe_tai': 'biển cấm xe tải',
#             'di_cham': 'biển đi chậm',
#             'duong_nguoi_di_bo_cat_ngang': 'biển đường người đi bộ cắt ngang',
#             'giao_nhau_voi_duong_khong_uu_tien': 'biển giao nhau với đường không ưu tiên',
#             'huong_phai_di_vong_chuong_ngai_vat': 'biển hướng phải đi vòng chướng ngại vật',
#             'toc_do_toi_da_50kmh': 'biển tốc độ tối đa năm mươi ki lô mét một giờ',
#             'toc_do_toi_da_60kmh': 'biển tốc độ tối đa sáu mươi ki lô mét một giờ',
#             'tre_em': 'biển báo trẻ em'
#         }
#
#         # Queue để quản lý các biển báo cần đọc
#         self.announcement_queue = deque()
#         self.last_announced = {}  # Lưu thời gian đọc gần nhất
#         self.cooldown_time = 3.0  # Tăng lên 3s để tránh spam âm thanh liên tục gây khó chịu
#
#         # Thread state
#         self.is_running = True
#
#         # Thread để xử lý đọc âm thanh
#         self.speaker_thread = threading.Thread(target=self._process_announcements, daemon=True).start()
#
#     def _process_announcements(self):
#         """Xử lý queue đọc âm thanh luân phiên"""
#         while self.is_running:
#             if self.announcement_queue:
#                 message = self.announcement_queue.popleft()
#                 try:
#                     engine = pyttsx3.init()
#                     engine.setProperty('rate', 150)
#                     engine.setProperty('volume', 1.0)
#                     print(f"Đang đọc: {message}")
#                     engine.say(message)
#                     # runAndWait là lệnh chặn (blocking), nó sẽ chờ đọc xong mới chạy tiếp
#                     engine.runAndWait()
#                     engine.stop()
#                     del engine
#                 except Exception as e:
#                     print(f"Lỗi âm thanh: {e}")
#             else:
#                 time.sleep(0.1)
#
#     def _should_announce(self, class_name):
#         """Kiểm tra xem có nên đọc biển báo này không"""
#         current_time = time.time()
#         if class_name in self.last_announced:
#             if current_time - self.last_announced[class_name] < self.cooldown_time:
#                 return False
#         return True
#
#     def detect_and_announce(self, frame):
#         """Phát hiện biển báo và thêm vào queue để đọc"""
#         results = self.model(frame, conf=0.5, verbose=False)
#
#         announced_signs = set()
#
#         for result in results:
#             boxes = result.boxes
#             for box in boxes:
#                 class_id = int(box.cls[0])
#                 class_name = self.model.names[class_id]
#                 confidence = float(box.conf[0])
#
#                 # Vẽ bounding box
#                 x1, y1, x2, y2 = map(int, box.xyxy[0])
#                 cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
#
#                 # Hiển thị label
#                 label = f'{class_name} {confidence:.2f}'
#                 cv2.putText(frame, label, (x1, y1 - 10),
#                             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
#
#                 # Logic thêm vào hàng đợi đọc
#                 if class_name in self.sign_messages:
#                     if self._should_announce(class_name):
#                         message = self.sign_messages[class_name]
#                         self.announcement_queue.append(message)
#                         self.last_announced[class_name] = time.time()
#
#         return frame
#
#     def run_webcam(self):
#         """Chạy detection từ webcam"""
#         cap = cv2.VideoCapture(0)
#
#         print("Nhấn 'q' để thoát")
#         print("Đang chạy detection...")
#
#         while True:
#             ret, frame = cap.read()
#             if not ret:
#                 break
#
#             # Detection và announce
#             frame = self.detect_and_announce(frame)
#
#             # Hiển thị frame
#             cv2.imshow('Traffic Sign Detection', frame)
#
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break
#
#         cap.release()
#         cv2.destroyAllWindows()
#
#     def run_video(self, video_path):
#         """Chạy detection từ video file"""
#         cap = cv2.VideoCapture(video_path)
#
#         print("Nhấn 'q' để thoát")
#         print("Đang chạy detection...")
#
#         while True:
#             ret, frame = cap.read()
#             if not ret:
#                 break
#
#             frame = self.detect_and_announce(frame)
#             cv2.imshow('Traffic Sign Detection', frame)
#
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break
#
#         cap.release()
#         cv2.destroyAllWindows()
#
#
# # Sử dụng
# if __name__ == "__main__":
#     # Đường dẫn đến model đã train
#     MODEL_PATH = r"C:\Users\nguye\PycharmProjects\PythonProject\Weight-yolo11s\best.pt"  # Thay bằng đường dẫn model của bạn
#     VIDEO_PATH = r"C:\Users\nguye\Downloads\Untitled video - Made with Clipchamp.mp4"
#     # Khởi tạo detector
#     detector = TrafficSignDetector(MODEL_PATH)
#
#     # Chạy với webcam
#     detector.run_video(VIDEO_PATH)
#
#     # Hoặc chạy với video file
#     # detector.run_video("traffic_video.mp4")