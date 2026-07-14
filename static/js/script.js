document.addEventListener("DOMContentLoaded", function () {

    const imageInput = document.getElementById("imageInput");
    const preview = document.getElementById("preview");
    const submitBtn = document.getElementById("submitBtn");

    imageInput.addEventListener("change", function () {

        const file = this.files[0];

        if (file) {

            preview.src = URL.createObjectURL(file);

            preview.style.display = "block";

        }

    });

    submitBtn.addEventListener("click", function () {

        const file = imageInput.files[0];

        // Read patient information
        const patientName = document.getElementById("patientName").value;
        const patientAge = document.getElementById("patientAge").value;
        const patientGender = document.getElementById("patientGender").value;

        if (!file) {
            alert("Please upload an MRI image.");
            return;
        }

        if (patientName === "" || patientAge === "" || patientGender === "") {
            alert("Please fill all patient details.");
            return;
        }
        const formData = new FormData();

        formData.append("image", file);
        formData.append("patientName", patientName);
        formData.append("patientAge", patientAge);
        formData.append("patientGender", patientGender);

        submitBtn.disabled = true;

        submitBtn.innerHTML = "Analyzing...";

        fetch("/predict", {

            method: "POST",

            body: formData

        })

        .then(response => {
            if (!response.ok) {
                throw new Error("Server Error");
            }
            return response.json();
        })

        .then(data => {

            submitBtn.disabled = false;
            submitBtn.innerHTML = "Analyze MRI Scan";

            if (data.error) {
                alert(data.error);
                return;
            }

            const confidence = parseFloat(data.confidence) * 100;

            const predictionNames = {
                "NonDemented":"Non Demented",
                "VeryMildDemented":"Very Mild Demented",
                "MildDemented":"Mild Demented",
                "ModerateDemented":"Moderate Demented"
            };

            const displayPrediction = predictionNames[data.prediction] || data.prediction;
            // Prediction
            
            const predictionElement = document.getElementById("predictionName");
            predictionElement.innerText = displayPrediction;

            switch (data.prediction) {
                case "NonDemented":
                    predictionElement.style.color = "#16a34a";
                    break;

                case "VeryMildDemented":
                    predictionElement.style.color = "#eab308";
                    break;

                case "MildDemented":
                    predictionElement.style.color = "#f97316";
                    break;

                case "ModerateDemented":
                    predictionElement.style.color = "#dc2626";
                    break;

                default:
                    predictionElement.style.color = "#2563eb";
            }
            document.getElementById("predictionResult").innerText = displayPrediction;
            // Prediction Stage
            const stageElement = document.getElementById("predictionStage");

            switch (data.prediction) {

                case "NonDemented":
                    stageElement.innerText = "✅ Normal";
                    stageElement.style.color = "#16a34a";
                    break;

                case "VeryMildDemented":
                    stageElement.innerText = "🟡 Stage 1 - Early";
                    stageElement.style.color = "#eab308";
                    break;

                case "MildDemented":
                    stageElement.innerText = "🟠 Stage 2 - Mild";
                    stageElement.style.color = "#f97316";
                    break;

                case "ModerateDemented":
                    stageElement.innerText = "🔴 Stage 3 - Moderate";
                    stageElement.style.color = "#dc2626";
                    break;

                default:
                    stageElement.innerText = "Unknown";
                    stageElement.style.color = "#2563eb";
            }

            document.getElementById("confidenceText").innerText = confidence.toFixed(1) + "%";

            // Confidence Bar
            const bar = document.getElementById("confidenceBar");
            bar.style.width = confidence + "%";
            bar.innerHTML = confidence.toFixed(1) + "%";

            // Change prediction color
            switch (data.prediction) {

                case "NonDemented":
                    bar.style.background = "#16a34a"; // Green
                    break;

                case "VeryMildDemented":
                    bar.style.background = "#eab308"; // Yellow
                    break;

                case "MildDemented":
                    bar.style.background = "#f97316"; // Orange
                    break;

                case "ModerateDemented":
                    bar.style.background = "#dc2626"; // Red
                    break;

                default:
                    bar.style.background = "#2563eb"; // Blue
            }

            // Probability Distribution
            document.getElementById("nonDemValue").innerText =
                (parseFloat(data.all_predictions.NonDemented) * 100).toFixed(1) + "%";

            document.getElementById("veryMildValue").innerText =
                (parseFloat(data.all_predictions.VeryMildDemented) * 100).toFixed(1) + "%";

            document.getElementById("mildValue").innerText =
                (parseFloat(data.all_predictions.MildDemented) * 100).toFixed(1) + "%";

            document.getElementById("moderateValue").innerText =
                (parseFloat(data.all_predictions.ModerateDemented) * 100).toFixed(1) + "%";

            document.getElementById("nonDemBar").style.width =
                (parseFloat(data.all_predictions.NonDemented) * 100) + "%";

            document.getElementById("veryMildBar").style.width =
                (parseFloat(data.all_predictions.VeryMildDemented) * 100) + "%";

            document.getElementById("mildBar").style.width =
                (parseFloat(data.all_predictions.MildDemented) * 100) + "%";

            document.getElementById("moderateBar").style.width =
                (parseFloat(data.all_predictions.ModerateDemented) * 100) + "%";

                document.getElementById("nonDemBar").style.background = "#16a34a";
                document.getElementById("veryMildBar").style.background = "#eab308";
                document.getElementById("mildBar").style.background = "#f97316";
                document.getElementById("moderateBar").style.background = "#dc2626";

            // Image Analysis Card

            const analysisText = data.analysis
                .replace(/VeryMildDemented/g, "Very Mild Demented")
                .replace(/ModerateDemented/g, "Moderate Demented")
                .replace(/MildDemented/g, "Mild Demented")
                .replace(/NonDemented/g, "Non Demented");

            document.getElementById("imagePredictionOutput").innerHTML = `
                <h5>AI Analysis</h5>
                <hr>
                ${analysisText.replace(/\n/g, "<br>")}
            `;

            // Risk Assessment Card
            document.getElementById("riskAssessmentOutput").innerHTML = `
            <h5>Clinical Assessment</h5>
            <hr>

            <b>Risk Level:</b> ${data.risk}<br><br>

            <b>Model Confidence:</b> ${confidence.toFixed(1)}%<br><br>

            <b>Recommendation:</b><br>
            ${data.recommendation}
            `;

            // Update top summary card
            const riskLevel = document.getElementById("riskLevel");

            riskLevel.innerText = data.risk;

            switch (data.risk) {

                case "Low Risk":
                    riskLevel.style.color = "#16a34a";
                    break;

                case "Early Stage":
                    riskLevel.style.color = "#eab308";
                    break;

                case "Medium Risk":
                    riskLevel.style.color = "#f97316";
                    break;

                case "High Risk":
                    riskLevel.style.color = "#dc2626";
                    break;

                default:
                    riskLevel.style.color = "#2563eb";
            }
            // Enable Download PDF button
            document.getElementById("downloadBtn").disabled = false;

        })

        .catch(err => {

            console.log(err);

            alert("Prediction failed: " + err.message);

            submitBtn.disabled = false;
            submitBtn.innerHTML = "Analyze MRI Scan";

        });

    });
        const downloadBtn = document.getElementById("downloadBtn");

        if (downloadBtn) {
            downloadBtn.addEventListener("click", function () {
                window.location.href = "/download_report";
            });
        }
});