import cv2
import os

# Thư mục chứa các video (gồm cả folder con)
video_root = r"D:\\Coding\\NCKH\\Phone Link\\New folder"

# Thư mục lưu frame
output_folder = r"C:\\Users\\nguye\\Downloads\\Frame_day1_ex"
os.makedirs(output_folder, exist_ok=True)

# Thời gian giữa các frame (giây)
interval = 1.5

# Hàm cắt frame từ 1 video
def extract_frames(video_path, output_folder, interval):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        print(f"Lỗi FPS: {video_path}")
        return

    frame_interval = int(fps * interval)

    frame_count = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Nếu là frame tại khoảng thời gian mong muốn → lưu
        if frame_count % frame_interval == 0:
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            save_path = os.path.join(output_folder, f"{video_name}_frame_{saved_count}.jpg")
            cv2.imwrite(save_path, frame)
            saved_count += 1

        frame_count += 1

    cap.release()
    print(f"Đã lưu {saved_count} frame từ video: {video_path}")


# Duyệt tất cả folder con để tìm mp4
for root, dirs, files in os.walk(video_root):
    for file in files:
        if file.lower().endswith(".mp4"):
            video_path = os.path.join(root, file)
            print(f"Đang xử lý: {video_path}")
            extract_frames(video_path, output_folder, interval)

print("✔️ Hoàn thành trích xuất toàn bộ frame!")
