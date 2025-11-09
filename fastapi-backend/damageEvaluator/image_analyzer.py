# tools/image_analyzer.py
import os
from ultralytics import YOLO
import cv2

# Load YOLO model once globally
MODEL_PATH = "models/best.pt"
model = YOLO(MODEL_PATH)

# Ensure output folder exists
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def detect_and_estimate(img_path: str):
    """
    Detect damages and estimate severity using YOLO.
    Returns (annotated_image_path, damage_info).
    """
    results = model.predict(img_path, conf=0.3)

    damage_info = []
    for r in results:
        for box in r.boxes:
            conf = float(box.conf[0])
            area = (box.xyxy[0][2] - box.xyxy[0][0]) * (box.xyxy[0][3] - box.xyxy[0][1])

            # Simple severity estimation
            if area < 5000:
                severity = "Minor"
            elif area < 15000:
                severity = "Moderate"
            else:
                severity = "Severe"

            label = r.names[int(box.cls[0])]

            damage_info.append({
                "label": label,
                "severity": severity,
                "confidence": round(conf, 3)
            })

    # Save annotated image
    annotated_img = results[0].plot()
    output_path = os.path.join(OUTPUT_DIR, os.path.basename(img_path))
    cv2.imwrite(output_path, annotated_img)

    return output_path, damage_info


def analyze_image(session_id: str, images: list, description: str):
    """
    Runs YOLO detection on multiple images.
    Returns structured JSON with paths + detected damages.
    """
    session_id = session_id or "session-less"
    results = []
    for img_path in images:
        if not os.path.exists(img_path):
            results.append({"image": img_path, "error": "file not found"})
            continue

        output_path, damage_info = detect_and_estimate(img_path)
        results.append({
            "image": img_path,
            "annotated_output": output_path,
            "damages": damage_info,
            "notes": description
        })

    return {"session_id": session_id, "analysis": results}
