import os

from ultralytics import YOLO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(BASE_DIR, "DL_Model", "best.pt")
model = YOLO(model=model_path)

def predict_waste(path):
    predict = model.predict(path,conf=0.25)
    waste_classes = {
    "E-waste", "Metal-waste", "bottles", "cardboard",
    "cups", "organic-waste", "other-trash",
    "paper", "plastic-waste", "trash"
    }

    detected = False
    count = 0
    pred_labels = set()
    for r in predict:
        for cls in r.boxes.cls:
            label = r.names[int(cls)]
            if label in waste_classes:
                print(label)
                if label == "other-trash":
                    count = count + 4
                count = count+1
                pred_labels.add(label)
    print(count)

    if count<3:
        return {"detect_res": 0
        }
    else: 
        return {"detect_res": 1}
