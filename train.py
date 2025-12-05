from ultralytics import YOLO

# Load a COCO-pretrained YOLO11n model
model = YOLO("yolo11n.pt")
dataPath = "C:\\Users\\nguye\\PycharmProjects\\PythonProject\\data_yolo\\data.yaml"

# Train the model on the COCO8 example dataset for 100 epochs
results = model.train(data=dataPath, epochs=30, imgsz=640, device=0, workers=0 )

# Run inference with the YOLO11n model on the 'bus.jpg' image
#results = model("path/to/bus.jpg")


