$(document).ready(function() {

    // ===============================
    // Symptom & Allergy Lists
    // ===============================

    const symptomsList = [
        "fever","cough","body_aches","chills","fatigue","headache",
        "sore_throat","runny_nose","sneezing","nasal_congestion",
        "sinus_pressure","facial_pain","shortness_of_breath","wheezing",
        "chest_tightness","chest_pain","abdominal_pain","diarrhea",
        "vomiting","nausea","burning_urination","frequent_urination",
        "itching","skin_rash","joint_pain","back_pain","weight_loss",
        "weight_gain","excessive_thirst","blurred_vision",
        "slow_healing_wounds","dizziness","night_sweats",
        "loss_of_appetite","yellowish_skin","dark_urine",
        "palpitations","anxiety","depression","heartburn",
        "regurgitation","bloating","constipation","bone_pain",
        "hair_loss","irregular_periods","pelvic_pain",
        "swelling","leg_pain","phlegm","malaise"
    ];

    const allergyList = [
        "dust","pollen","peanuts","seafood","milk",
        "eggs","pet_dander","latex","insect_stings",
        "medicine_allergy"
    ];

    // ===============================
    // Populate Dropdowns
    // ===============================

    symptomsList.forEach(symptom => {
        $('#symptoms').append(
            `<option value="${symptom}">${symptom.replace(/_/g, " ")}</option>`
        );
    });

    allergyList.forEach(allergy => {
        $('#allergy').append(
            `<option value="${allergy}">${allergy.replace(/_/g, " ")}</option>`
        );
    });

    // ===============================
    // Enable Select2
    // ===============================

    $('#symptoms').select2({
        placeholder: "Search and select symptoms",
        allowClear: false,
        closeOnSelect: false
    });

    $('#allergy').select2({
        placeholder: "Search and select allergies",
        allowClear: false,
        closeOnSelect: false
    });

    // ===============================
    // Form Submit Logic
    // ===============================

    const form = document.getElementById("symptomForm");
    const result = document.getElementById("result");
    const spinner = document.getElementById("loadingSpinner");

    form.addEventListener("submit", function(e) {
        e.preventDefault();

        const age = document.getElementById("age").value;
        const selectedSymptoms = $('#symptoms').val();
        const selectedAllergies = $('#allergy').val();

        if (!age) {
            alert("Please enter age.");
            return;
        }

        if (!selectedSymptoms || selectedSymptoms.length === 0) {
            alert("Please select at least one symptom.");
            return;
        }

        result.style.display = "none";
        spinner.style.display = "block";

        fetch("http://127.0.0.1:5000/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                age: age,
                symptoms: selectedSymptoms
            })
        })
        .then(response => response.json())
        .then(data => {

            spinner.style.display = "none";
            result.style.display = "block";
            result.innerHTML = "";

            // ============================================
            // SHOW EMERGENCY BANNER ONLY IF TOP IS SERIOUS
            // ============================================

            if (data.length > 0 && data[0].serious === true) {
                result.innerHTML += `
                    <div class="emergency-banner">
                        ⚠ URGENT: Immediate Medical Consultation Recommended
                    </div>
                `;
            }

            // ============================================
            // DISPLAY DISEASE CARDS
            // ============================================

            data.forEach((item, index) => {

                const isSerious = item.serious === true;

                let confidenceClass = "";

if (item.confidence >= 70) {
    confidenceClass = "confidence-high";
} else if (item.confidence >= 40) {
    confidenceClass = "confidence-medium";
} else {
    confidenceClass = "confidence-low";
}

                result.innerHTML += `
                    <div class="disease-card 
                        ${index === 0 ? 'top-match' : ''} 
                        ${isSerious ? 'serious-case' : ''}">
                        
                      <div class="disease-title">
    ${isSerious ? "🏥 " : ""}
    ${item.disease} 
    ${index === 0 ? "(Top Match)" : ""}
</div>

                        ${
                            isSerious
                            ? `<div class="serious-warning">
                                ⚠ This condition may require immediate attention.
                               </div>`
                            : ""
                        }

                        <div><strong>Age:</strong> ${age}</div>
                        <div><strong>Symptoms:</strong> 
                            ${selectedSymptoms.join(", ").replace(/_/g, " ")}
                        </div>
                        <div><strong>Allergies:</strong> 
                            ${selectedAllergies 
                                ? selectedAllergies.join(", ").replace(/_/g, " ") 
                                : "None"}
                        </div>

                        <div><strong>Recommended Medicine:</strong> 
    ${item.medicines}
</div>

                        <div>Confidence: ${item.confidence}%</div>
                        <div class="probability-bar">
                            <div class="probability-fill ${confidenceClass}" 
     style="width:${item.confidence}%">
</div>
                        </div>
                    </div>
                `;
            });

          result.innerHTML += `
    <div class="disclaimer">
        <strong>Medical Disclaimer:</strong>
        This AI-based prediction system is for informational purposes only.
        It does not replace professional medical advice, diagnosis, or treatment.
        Always consult a qualified healthcare provider for proper medical evaluation.
    </div>
`;  

        })


        .catch(error => {
            spinner.style.display = "none";
            alert("Error connecting to backend.");
            console.error(error);
        });
    });

});