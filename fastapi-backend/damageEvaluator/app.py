import streamlit as st
import os
from image_analyzer import analyze_image

# App title
st.set_page_config(page_title="Damage Detection using YOLO", layout="wide")
st.title("🧠 Vehicle Damage Detection & Severity Estimation")
st.write("Upload one or more images to detect and estimate damage severity using your YOLO model.")

# Sidebar for description and session ID
st.sidebar.header("📝 Analysis Info")
session_id = st.sidebar.text_input("Session ID", value="session_001")
description = st.sidebar.text_area("Description / Notes", value="Automated inspection analysis")

# File uploader
uploaded_files = st.file_uploader(
    "Upload images for damage detection",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if uploaded_files:
    image_paths = []
    os.makedirs("uploads", exist_ok=True)
    
    # Save uploaded files locally
    for uploaded_file in uploaded_files:
        img_path = os.path.join("uploads", uploaded_file.name)
        with open(img_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        image_paths.append(img_path)
    
    st.info(f"🖼️ {len(image_paths)} image(s) uploaded successfully.")
    
    if st.button("🔍 Run YOLO Analysis"):
        with st.spinner("Running YOLO model... please wait ⏳"):
            result = analyze_image(session_id=session_id, images=image_paths, description=description)

        st.success("✅ Analysis completed successfully!")

        # Display results
        for item in result["analysis"]:
            col1, col2 = st.columns([1, 1])
            with col1:
                st.image(item["image"], caption="Original Image", use_container_width=True)
            with col2:
                if "annotated_output" in item and os.path.exists(item["annotated_output"]):
                    st.image(item["annotated_output"], caption="Detected Damages", use_container_width=True)
                else:
                    st.error(f"❌ Could not process {item['image']}")
            
            st.write("### 🧾 Damage Details")
            if "damages" in item and item["damages"]:
                for dmg in item["damages"]:
                    st.write(f"- **Label:** {dmg['label']} | **Severity:** {dmg['severity']} | **Confidence:** {dmg['confidence']}")
            else:
                st.warning("No damages detected.")

            st.divider()
else:
    st.info("👆 Upload images from the sidebar to start analysis.")
