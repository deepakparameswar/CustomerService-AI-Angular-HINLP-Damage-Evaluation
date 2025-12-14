# tools/image_analyzer.py
import os
from ultralytics import YOLO
import cv2
import urllib.request
from agentapp.llm_utils import callGroq

# Load YOLO model once globally
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "best.pt")
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
    print(f"images: >>>>>>>>> {images}")
    session_id = session_id or "session-less"
    results = []
    matchMetrix = None
    for img_path in images:
        print(f"img_path: >>>>>>>> ",img_path)
        if not os.path.exists(img_path):
            results.append({"image": img_path, "error": "file not found"})
            continue

        output_path, damage_info = detect_and_estimate(img_path)

        # Load SOP
        sop_path = os.path.join(os.path.dirname(__file__), "sop", "damage_inference.json")
        damage_sop = {}
        if os.path.exists(sop_path):
            import json
            with open(sop_path, "r") as f:
                damage_sop = json.load(f)

        if not damage_info:
            damage_summary = "No visible damage detected."
        else:
            damage_summary_lines = []
            for d in damage_info:
                label = d['label'].lower()
                
                # Look up probable damages in SOP
                probable_damages = damage_sop.get(label, [])
                
                # Fallback: check for keywords if exact match not found
                if not probable_damages:
                    for key in ["dent", "scratch", "crack", "broken glass", "missing part"]:
                        if key in label:
                            probable_damages.extend(damage_sop.get(key, []))
                    
                    # Remove duplicates if any
                    probable_damages = list(set(probable_damages))
                print(f"probable_damages for '{label}': >>>>>>>> ", probable_damages)
                probable_info = ""
                if probable_damages:
                    probable_info = f"\n  -> Probable Hidden/Associated Damages: {', '.join(probable_damages)}"
                
                # Add probable damages to the structured output
                d['probable_damages'] = probable_damages

                print(f"probable_info: >>>>>>>> ", probable_info)

                damage_summary_lines.append(f"- {d['label']} ({d['severity']}, Confidence: {d['confidence']:.2f}){probable_info}")
            damage_summary = "\n".join(damage_summary_lines)

        print(f"\n[Visual Evidence Detected]:\n{damage_summary}")

        # 2. Reasoning Step: Ask Llama 3.1
        system_prompt = (
            "You are an AI insurance adjuster. Your job is to compare the visual evidence "
            "from a car accident photo with the driver's claim description.\n"
            "Analyze if the detected damage supports the claim.\n"
            "Be objective and concise. Start with 'MATCH', 'MISMATCH', or 'INCONCLUSIVE'."
        )

        user_content = (
            f"Claim Description: \"{description}\"\n\n"
            f"Visual Evidence from Image Analysis:\n{damage_summary}\n\n"
            "Does the evidence support the claim? Explain your reasoning."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        try:
            print("\n[Consulting Llama 3.1]...")
            matchMetrix = callGroq(messages)

            print(f"\n analyze_image [LLM Response]:\n{matchMetrix.content}")

        except Exception as e:
            return f"Error calling LLM: {e}"
        # end

        results.append({
            "image": img_path,
            "annotated_output": output_path,
            "damages": damage_info,
            "notes": description,
            "matchMetrix": matchMetrix.content
        })

    return {"session_id": session_id, "analysis": results}
