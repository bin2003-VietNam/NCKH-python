from ultralytics import YOLO

model_path = r"C:\Users\nguye\PycharmProjects\PythonProject\Weight-yolo11s\best.pt"
image_path = r"C:\Users\nguye\PycharmProjects\PythonProject\Test_resource\image\Bien-cam-di-nguoc-chieu-p_102-2.jpg"


model = YOLO(model_path)
# lưu ảnh có vẽ box vào thư mục mặc định runs/detect/predict...
results = model.predict(source=image_path, save=True, conf=0.25)