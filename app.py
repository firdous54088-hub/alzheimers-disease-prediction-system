# ============================================================
# Alzheimer's Disease Prediction System
# app.py
# ============================================================

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_file
)

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

import numpy as np
import os
import traceback
import datetime

# ============================================================
# PDF Libraries
# ============================================================

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)

# ============================================================
# Flask App
# ============================================================

app = Flask(__name__)

app.config["DEBUG"] = True

# ============================================================
# Global Variables
# ============================================================

latest_report = {}
latest_image_path = ""

# ============================================================
# Upload Folder
# ============================================================

UPLOAD_FOLDER = "static/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ============================================================
# Load AI Model
# ============================================================

try:

    model = load_model("alzheimers_model.keras", compile=False)
    print("Model Loaded Successfully")

except Exception as e:

    print("Error Loading Model")
    print(e)

    model = None

# ============================================================
# Model Classes
# ============================================================

class_labels = [

    "MildDemented",

    "ModerateDemented",

    "NonDemented",

    "VeryMildDemented"

]

# ============================================================
# Home Page
# ============================================================

@app.route("/")
def index():

    return render_template("index.html")


# ============================================================
# Test Route
# ============================================================

@app.route("/test")
def test():

    return jsonify({

        "status": "Application Running",

        "model_loaded": model is not None,

        "upload_folder": UPLOAD_FOLDER,

        "upload_exists": os.path.exists(UPLOAD_FOLDER)

    })
# ============================================================
# Prediction Route
# ============================================================

@app.route("/predict", methods=["POST"])
def predict():

    global latest_report
    global latest_image_path

    try:

        print("Prediction Request Received")

        # --------------------------------------------------
        # Check Model
        # --------------------------------------------------

        if model is None:
            return jsonify({"error": "Model not loaded"}), 500

        # --------------------------------------------------
        # Check Uploaded MRI Image
        # --------------------------------------------------

        if "image" not in request.files:
            return jsonify({"error": "No MRI image uploaded"}), 400

        img = request.files["image"]

        if img.filename == "":
            return jsonify({"error": "Please select an MRI image"}), 400

        # --------------------------------------------------
        # Patient Details
        # --------------------------------------------------

        patient_name = request.form.get("patientName", "Not Provided")
        patient_age = request.form.get("patientAge", "Not Provided")
        patient_gender = request.form.get("patientGender", "Not Provided")

        # --------------------------------------------------
        # Save MRI Image
        # --------------------------------------------------

        filename = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{img.filename}"

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        img.save(filepath)

        latest_image_path = filepath

        print("MRI Image Saved:", filepath)

        # --------------------------------------------------
        # Image Preprocessing
        # --------------------------------------------------

        img_data = image.load_img(
            filepath,
            target_size=(128, 128)
        )

        img_array = image.img_to_array(img_data)

        img_array = np.expand_dims(img_array, axis=0)

        img_array = img_array / 255.0

        print("Image Preprocessed Successfully")

        # --------------------------------------------------
        # AI Prediction
        # --------------------------------------------------

        prediction = model.predict(img_array)[0]

        predicted_index = np.argmax(prediction)

        predicted_class = class_labels[predicted_index]

        confidence = float(prediction[predicted_index])

        print("Prediction:", predicted_class)
        print("Confidence:", confidence)

        # --------------------------------------------------
        # Probability Distribution
        # --------------------------------------------------

        all_predictions = {}

        for i, label in enumerate(class_labels):

            all_predictions[label] = round(
                float(prediction[i]),
                4
            )

        # --------------------------------------------------
        # Risk Level
        # --------------------------------------------------

        if predicted_class == "NonDemented":

            risk = "Low Risk"

        elif predicted_class == "VeryMildDemented":

            risk = "Early Stage"

        elif predicted_class == "MildDemented":

            risk = "Medium Risk"

        elif predicted_class == "ModerateDemented":

            risk = "High Risk"

        else:

            risk = "Unknown"

        # --------------------------------------------------
        # Recommendation
        # --------------------------------------------------

        if predicted_class == "NonDemented":

            recommendation = (
                "No signs of Alzheimer's disease were detected. "
                "Maintain a healthy lifestyle and attend regular medical check-ups."
            )

        elif predicted_class == "VeryMildDemented":

            recommendation = (
                "Early-stage Alzheimer's indicators were detected. "
                "Consult a neurologist and undergo cognitive assessment (MMSE/MoCA)."
            )

        elif predicted_class == "MildDemented":

            recommendation = (
                "Mild Alzheimer's disease detected. "
                "Neurological consultation and cognitive therapy are recommended."
            )

        elif predicted_class == "ModerateDemented":

            recommendation = (
                "Moderate Alzheimer's disease detected. "
                "Immediate specialist consultation and continuous medical supervision are advised."
            )

        else:

            recommendation = (
                "Please consult a qualified neurologist."
            )
                    # --------------------------------------------------
        # AI Analysis
        # --------------------------------------------------

        if predicted_class == "NonDemented":

            analysis = """
Prediction : Non Demented

Interpretation :
No significant signs of Alzheimer's disease were detected in the uploaded MRI scan.

Recommendation :
• Continue a healthy lifestyle.
• Regular medical check-ups are recommended.
• Consult a neurologist if symptoms appear.
"""

        elif predicted_class == "VeryMildDemented":

            analysis = """
Prediction : Very Mild Demented

Interpretation :
The MRI scan shows early structural changes that may indicate the beginning stage of Alzheimer's disease.

Recommendation :
• Consult a neurologist for further evaluation.
• Perform cognitive assessment (MMSE/MoCA).
• Schedule regular follow-up examinations.
"""

        elif predicted_class == "MildDemented":

            analysis = """
Prediction : Mild Demented

Interpretation :
The MRI scan indicates mild Alzheimer's disease with noticeable brain changes.

Recommendation :
• Immediate neurological consultation.
• Cognitive therapy may be beneficial.
• Regular MRI monitoring is recommended.
"""

        elif predicted_class == "ModerateDemented":

            analysis = """
Prediction : Moderate Demented

Interpretation :
The MRI scan indicates advanced Alzheimer's disease.

Recommendation :
• Immediate specialist consultation.
• Continuous medical supervision.
• Caregiver support is strongly recommended.
"""

        else:

            analysis = """
Prediction could not be determined.

Please upload a valid MRI image.
"""

        # --------------------------------------------------
        # Save Latest Report
        # --------------------------------------------------

        latest_report = {

            "patient_name": patient_name,

            "patient_age": patient_age,

            "patient_gender": patient_gender,

            "prediction": predicted_class.replace(
                "VeryMildDemented", "Very Mild Demented"
            ).replace(
                "ModerateDemented", "Moderate Demented"
            ).replace(
                "MildDemented", "Mild Demented"
            ).replace(
                "NonDemented", "Non Demented"
            ),

            "confidence": confidence * 100,

            "risk": risk,

            "analysis": analysis,

            "recommendation": recommendation,

            "date": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }

        print("Report Saved Successfully")

        # --------------------------------------------------
        # Return JSON Response
        # --------------------------------------------------

        return jsonify({

            "prediction": predicted_class,

            "confidence": confidence,

            "risk": risk,

            "analysis": analysis,

            "recommendation": recommendation,

            "all_predictions": all_predictions

        })

    except Exception as e:

        print(traceback.format_exc())

        return jsonify({

            "error": str(e)

        }), 500
    # ============================================================
# Download PDF Report
# ============================================================

@app.route("/download_report")
def download_report():

    global latest_report
    global latest_image_path

    if not latest_report:
        return "No report available."

    pdf_name = f"Alzheimer_Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    doc = SimpleDocTemplate(
        pdf_name,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    story = []

    # =====================================================
    # Custom Styles
    # =====================================================

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=22,
        textColor=colors.darkblue,
        spaceAfter=20
    )

    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        textColor=colors.darkblue,
        spaceAfter=10
    )

    # =====================================================
    # Title
    # =====================================================

    story.append(
        Paragraph(
            "AI Powered Alzheimer's Disease Prediction Report",
            title_style
        )
    )

    story.append(Spacer(1, 15))

    # =====================================================
    # Patient Information Table
    # =====================================================

    patient_data = [

        ["Patient Name", latest_report["patient_name"]],

        ["Age", latest_report["patient_age"]],

        ["Gender", latest_report["patient_gender"]],

        ["Date", latest_report["date"]],

        ["Prediction", latest_report["prediction"]],

        ["Confidence",
         f"{latest_report['confidence']:.2f}%"],

        ["Risk Level", latest_report["risk"]]

    ]

    table = Table(
        patient_data,
        colWidths=[2.2*inch, 3.5*inch]
    )

    table.setStyle(TableStyle([

        ("BACKGROUND",(0,0),(0,-1),colors.darkblue),

        ("TEXTCOLOR",(0,0),(0,-1),colors.white),

        ("BACKGROUND",(1,0),(1,-1),colors.whitesmoke),

        ("GRID",(0,0),(-1,-1),1,colors.grey),

        ("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),

        ("BOTTOMPADDING",(0,0),(-1,-1),8),

        ("TOPPADDING",(0,0),(-1,-1),8),

        ("VALIGN",(0,0),(-1,-1),"MIDDLE")

    ]))

    story.append(table)

    story.append(Spacer(1,20))

    # =====================================================
    # MRI Image
    # =====================================================

    if os.path.exists(latest_image_path):

        story.append(
            Paragraph(
                "Uploaded MRI Scan",
                heading_style
            )
        )

        img = Image(
            latest_image_path,
            width=4*inch,
            height=4*inch
        )

        story.append(img)

        story.append(Spacer(1,20))

    # =====================================================
    # AI Analysis
    # =====================================================

    story.append(
        Paragraph(
            "AI Analysis",
            heading_style
        )
    )

    story.append(

        Paragraph(

            latest_report["analysis"].replace(
                "\n",
                "<br/>"
            ),

            styles["BodyText"]

        )

    )

    story.append(Spacer(1,15))

    # =====================================================
    # Recommendation
    # =====================================================

    story.append(

        Paragraph(

            "Medical Recommendation",

            heading_style

        )

    )

    story.append(

        Paragraph(

            latest_report["recommendation"],

            styles["BodyText"]

        )

    )

    story.append(Spacer(1,15))

    # =====================================================
    # Disclaimer
    # =====================================================

    story.append(

        Paragraph(

            "Disclaimer",

            heading_style

        )

    )

    story.append(

        Paragraph(

            "This report is generated using an Artificial Intelligence model for educational and research purposes only. "
            "It is not intended to replace professional medical diagnosis. "
            "Always consult a qualified neurologist or healthcare professional.",

            styles["BodyText"]

        )

    )

    story.append(Spacer(1,25))

    # =====================================================
    # Footer
    # =====================================================

    footer = ParagraphStyle(

        "Footer",

        alignment=TA_CENTER,

        textColor=colors.grey,

        fontSize=9

    )

    story.append(

        Paragraph(

            "Generated by Alzheimer's Disease Prediction System | AI + TensorFlow + Flask",

            footer

        )

    )

    # =====================================================
    # Create PDF
    # =====================================================

    doc.build(story)

    return send_file(

        pdf_name,

        as_attachment=True

    )
# ============================================================
# Run Flask Application
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print(" Alzheimer's Disease Prediction System")
    print("=" * 60)
    print(" Flask Server Started Successfully")
    print(" Open your browser and visit:")
    print(" http://127.0.0.1:5000")
    print("=" * 60)

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
    
