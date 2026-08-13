// ----------------------------
// Ask AI
// ----------------------------

async function askAI() {

    const question = document.getElementById("question").value.trim();

    if (question === "") {
        alert("Please enter a question.");
        return;
    }

    document.getElementById("loading").style.display = "block";
    document.getElementById("response").innerHTML = "";

    try {

       const response = await fetch(" https://aistudymate-qxq9.onrender.com/chat", {

    method: "POST",

    headers: {
        "Content-Type": "application/json"
    },

    body: JSON.stringify({
        question: question
    })

});

const data = await response.json();

const responseDiv = document.getElementById("response");

responseDiv.innerHTML = "";

const text = data.answer;

let i = 0;

const speed = 20;

const interval = setInterval(() => {

    responseDiv.innerHTML = marked.parse(text.substring(0, i));

    i++;

    if(i > text.length){

        clearInterval(interval);

    }

}, speed);

    } catch (error) {

        document.getElementById("response").innerHTML =
            "<p style='color:red;'>❌ Unable to connect to the AI server.</p>";

        console.error(error);

    } finally {

        document.getElementById("loading").style.display = "none";

    }

}

// ----------------------------
// Upload PDF
// ----------------------------

async function uploadPDF() {

    const file = document.getElementById("pdfFile").files[0];

    if (!file) {
        alert("Please select a PDF.");
        return;
    }

    const formData = new FormData();

    formData.append("file", file);

    document.getElementById("loading").style.display = "block";

    try {

        const response = await fetch("https://aistudymate-qxq9.onrender.com/upload", {

            method: "POST",

            body: formData

        });

        const data = await response.json();

        alert(data.message);

    } catch (error) {

        alert("Error uploading PDF.");

        console.error(error);

    } finally {

        document.getElementById("loading").style.display = "none";

    }

}

// ----------------------------
// Summary
// ----------------------------

async function getSummary() {

    document.getElementById("loading").style.display = "block";

    try {

        const response = await fetch("https://aistudymate-qxq9.onrender.com/summary");

        const data = await response.json();

        document.getElementById("response").innerHTML =
            marked.parse(data.summary);

    } catch (error) {

        alert("Unable to generate summary.");

    } finally {

        document.getElementById("loading").style.display = "none";

    }

}

// ----------------------------
// MCQs
// ----------------------------

async function generateMCQ() {

    document.getElementById("loading").style.display = "block";

    try {

        const response = await fetch("https://aistudymate-qxq9.onrender.com/mcq");

        const data = await response.json();

        document.getElementById("response").innerHTML =
            marked.parse(data.mcq);

    } catch (error) {

        alert("Unable to generate MCQs.");

    } finally {

        document.getElementById("loading").style.display = "none";

    }

}

// ----------------------------
// Flashcards
// ----------------------------

async function generateFlashcards() {

    document.getElementById("loading").style.display = "block";

    try {

        const response = await fetch("https://aistudymate-qxq9.onrender.com/flashcards");

        const data = await response.json();

        document.getElementById("response").innerHTML =
            marked.parse(data.flashcards);

    } catch (error) {

        alert("Unable to generate flashcards.");

    } finally {

        document.getElementById("loading").style.display = "none";

    }

}

// ----------------------------
// Copy Answer
// ----------------------------

function copyAnswer() {

    const text = document.getElementById("response").innerText;

    if (text.trim() === "") {

        alert("Nothing to copy.");

        return;

    }

    navigator.clipboard.writeText(text);

    alert("✅ Answer copied successfully!");

}

// ----------------------------
// Download Notes
// ----------------------------

async function downloadNotes() {
    const notes = document.getElementById("response").innerText;

    if (notes.trim() === "") {
        alert("Nothing to download.");
        return;
    }

    document.getElementById("loading").style.display = "block";

    try {
        const response = await fetch(
            "https://aistudymate-qxq9.onrender.com/download",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    question: notes
                })
            }
        );

        if (!response.ok) {
            throw new Error("PDF generation failed");
        }

        const blob = await response.blob();

        const url = window.URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = "AI_StudyMate_Notes.pdf";

        document.body.appendChild(a);
        a.click();

        a.remove();
        window.URL.revokeObjectURL(url);

    } catch (error) {
        console.error(error);
        alert("Unable to create PDF.");
    } finally {
        document.getElementById("loading").style.display = "none";
    }
}
// ----------------------------
// Quiz Generator
// ----------------------------

async function generateQuiz() {

    document.getElementById("loading").style.display = "block";

    document.getElementById("quizOutput").innerHTML = "";

    try {

        const response = await fetch("https://aistudymate-qxq9.onrender.com/quiz");

        const data = await response.json();

        document.getElementById("quizOutput").innerHTML =
            marked.parse(data.quiz);

    } catch (error) {

        document.getElementById("quizOutput").innerHTML =
            "<p style='color:red;'>❌ Unable to generate quiz.</p>";

        console.error(error);

    } finally {

        document.getElementById("loading").style.display = "none";

    }

}

// ----------------------------
// Dark Mode
// ----------------------------

function toggleTheme() {

    document.body.classList.toggle("dark-mode");

    const btn = document.getElementById("themeToggle");

    if(document.body.classList.contains("dark-mode")){

        localStorage.setItem("theme","dark");
        btn.innerHTML="☀ Light Mode";

    }else{

        localStorage.setItem("theme","light");
        btn.innerHTML="🌙 Dark Mode";

    }

}

window.onload = function(){

    const theme = localStorage.getItem("theme");

    if(theme==="dark"){

        document.body.classList.add("dark-mode");

        document.getElementById("themeToggle").innerHTML="☀ Light Mode";

    }

}

document
.getElementById("pdfFile")
.addEventListener("change",function(){

    if(this.files.length>0){

        document.getElementById("fileName").innerHTML=
        this.files[0].name;

    }else{

        document.getElementById("fileName").innerHTML=
        "No file selected";

    }

});

function downloadPDF() {
    try {
        const { jsPDF } = window.jspdf;

        const pdf = new jsPDF();

        pdf.setFontSize(18);
        pdf.text("AI StudyMate - Study Notes", 20, 20);

        pdf.setFontSize(11);

        const responseElement = document.getElementById("response");

        if (!responseElement || !responseElement.innerText.trim()) {
            alert("Please generate some notes or an AI response first.");
            return;
        }

        const text = responseElement.innerText;

        const lines = pdf.splitTextToSize(text, 170);

        let y = 35;

        lines.forEach((line) => {
            if (y > 280) {
                pdf.addPage();
                y = 20;
            }

            pdf.text(line, 20, y);
            y += 7;
        });

        pdf.save("AI_StudyMate_Notes.pdf");

    } catch (error) {
        console.error("PDF Error:", error);
        alert("Unable to create PDF. Please try again.");
    }
}