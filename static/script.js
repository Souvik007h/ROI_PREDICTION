let currentStep = 0;

const steps = document.querySelectorAll(".step-box");
const indicators = document.querySelectorAll(".step");

/* STEP CONTROL */
function showStep(index) {
    steps.forEach((step, i) => {
        step.classList.remove("active");
        indicators[i].classList.remove("active", "completed");

        if (i < index) indicators[i].classList.add("completed");
        if (i === index) {
            step.classList.add("active");
            indicators[i].classList.add("active");
            step.scrollIntoView({ behavior: "smooth" });
        }
    });
}

function validateStep(index) {
    const inputs = steps[index].querySelectorAll("input, select");

    for (let input of inputs) {
        if (!input.value) {
            input.style.border = "1px solid red";
            input.focus();
            return false;
        } else {
            input.style.border = "";
        }
    }
    return true;
}

function nextStep() {
    if (!validateStep(currentStep)) return;
    if (currentStep < steps.length - 1) {
        currentStep++;
        showStep(currentStep);
    }
}

function prevStep() {
    if (currentStep > 0) {
        currentStep--;
        showStep(currentStep);
    }
}

/* FORM SUBMIT */
document.getElementById("form").addEventListener("submit", async function(e){
    e.preventDefault();

    if (!validateStep(currentStep)) return;

    const data = {};
    document.querySelectorAll("input, select").forEach(el => {
        data[el.name] = el.value;
    });

    const btn = document.querySelector(".btn.primary");
    btn.innerText = "⏳ Calculating...";
    btn.disabled = true;

    try {
        const res = await fetch("/predict", {
            method: "POST",
            headers: {"Content-Type":"application/json"},
            body: JSON.stringify(data)
        });

        const result = await res.json();

        const box = document.getElementById("result");
        box.classList.remove("hidden");

        if (result.ROI !== undefined) {
            box.innerHTML = `🌟 Estimated ROI: <b>${result.ROI}</b>`;
        } else {
            box.innerHTML = `❌ Error calculating ROI`;
        }

        currentStep = 3;
        showStep(currentStep);

    } catch (err) {
        alert("Server error");
    }

    btn.innerText = "🌱 Calculate ROI";
    btn.disabled = false;
});

/* INIT */
showStep(currentStep);