import argparse
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import os

def verify_claim_clip(image_path, claim_description):
    """
    Verifies if the claim description matches the visual evidence in the image using CLIP.
    """
    print(f"--- Verifying Claim with CLIP ---")
    print(f"Image: {image_path}")
    print(f"Claim: {claim_description}")

    if not os.path.exists(image_path):
        return f"Error: Image file not found at {image_path}"

    try:
        # Load model and processor
        model_id = "openai/clip-vit-base-patch32"
        print(f"Loading CLIP model: {model_id}...")
        model = CLIPModel.from_pretrained(model_id)
        processor = CLIPProcessor.from_pretrained(model_id)

        image = Image.open(image_path)

        # Prepare inputs
        # We will compare the claim against a few contrasting statements to see which one fits best,
        # or just check the score of the claim directly?
        # CLIP works best with a set of candidate labels.
        # Let's try to frame it as a binary classification: "The claim is true" vs "The claim is false"
        # Or better: "A photo of [claim]" vs "A photo of something else"
        
        # Actually, let's just use the claim and a generic negative prompt.
        # Or maybe just the claim and see the raw score? Raw scores are not normalized.
        # Standard CLIP usage is zero-shot classification.
        
        candidate_labels = [
            f"a photo of {claim_description}",
            "a photo of an undamaged car",
            "a photo of a car with different damage",
            "a photo of a random scene"
        ]
        
        inputs = processor(text=candidate_labels, images=image, return_tensors="pt", padding=True)

        outputs = model(**inputs)
        logits_per_image = outputs.logits_per_image  # this is the image-text similarity score
        probs = logits_per_image.softmax(dim=1)  # we can take the softmax to get the label probabilities

        print("\n[CLIP Analysis]:")
        for i, label in enumerate(candidate_labels):
            print(f"{label}: {probs[0][i].item():.4f}")

        # Determine the best match
        best_match_idx = probs.argmax().item()
        best_match_label = candidate_labels[best_match_idx]
        confidence = probs[0][best_match_idx].item()

        result = f"Best match: '{best_match_label}' with confidence {confidence:.2f}"
        print(f"result >>>>>>>>>>>>>>>> {result}")        
        # Simple logic: if the first label (the claim) is the highest or has a high enough score
        if best_match_idx == 0:
             return f"MATCH: The image seems to support the claim. ({result})"
        else:
             return f"MISMATCH: The image might not support the claim. ({result})"

    except Exception as e:
        return f"Error during CLIP verification: {e}"
