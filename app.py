from flask import Flask, render_template, request
import os
import pdfplumber
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from Skills.skills import SKILLS
import google.generativeai as genai

genai.configure(api_key="AQ.Ab8RN6KH898wzpP-LYusB25MOKN6HihycgUWjXjUrmHmKXSUFg")
model = genai.GenerativeModel("gemini-2.0-flash-exp")

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        return render_template("upload.html")

    return render_template("login.html")


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        return render_template("login.html")

    return render_template("register.html")


# ---------------- UPLOAD ----------------

@app.route("/upload")
def upload():
    return render_template("upload.html")


# ---------------- ANALYZE ----------------

@app.route("/analyze", methods=["POST"])
def analyze():

    file = request.files["resume"]

    if file.filename == "":
        return "Please select a resume."

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    # Read Resume PDF
    resume_text = ""

    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                resume_text += text + "\n"

    # Job Description
    job_description = request.form["job_description"]

    resume_lower = resume_text.lower()
    job_lower = job_description.lower()# Find required skills from Job Description
    skills = []

    for skill in SKILLS:
        if skill.lower() in job_lower:
            skills.append(skill)

    found_skills = []
    missing_skills = []

    # Match resume skills
    for skill in skills:
        if skill.lower() in resume_lower:
            found_skills.append(skill)
        else:
            missing_skills.append(skill)

    # ATS Score based on matched skills
    if len(skills) > 0:
        ats_score = round((len(found_skills) / len(skills)) * 100, 2)
    else:
        ats_score = 0

    # Progress Bar Color
    if ats_score >= 80:
        color = "success"
    elif ats_score >= 60:
        color = "warning"
    else:
        color = "danger"

    # AI Suggestions
    suggestions = []

    if len(missing_skills) > 0:
        for skill in missing_skills:
            suggestions.append(f"Add {skill} to your resume if you have experience.")

    if ats_score >= 80:
        suggestions.append("Excellent! Your resume is ATS Friendly.")
    elif ats_score >= 60:
        suggestions.append("Good Resume. Add the missing skills to improve your ATS score.")
    else:
        suggestions.append("Resume needs improvement. Add more relevant skills and projects.")
        response = model.generate_content(f"Provide feedback on how to improve a resume with an ATS score of {ats_score}%.")
        suggestions.extend([suggestion for suggestion in response.candidates[0].content.parts if suggestion])
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>ATS Result</title>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet">
</head>

<body class="bg-light">

<div class="container mt-5">

<div class="card shadow p-5">

<h1 class="text-center text-success">
🤖 AI Resume Analysis
</h1>

<hr>

<h3 class="mb-3">
ATS Score : {ats_score}%
</h3>

<div class="progress mb-4" style="height:35px;">
    <div class="progress-bar bg-{color}"
         role="progressbar"
         style="width:{ats_score}%">
        {ats_score}%
    </div>
</div>

<h4 class="text-primary">✅ Skills Found</h4>

<ul>
{"".join(f"<li>{skill}</li>" for skill in found_skills) if found_skills else "<li>No matching skills found.</li>"}
</ul>

<h4 class="text-danger mt-4">❌ Missing Skills</h4>

<ul>
{"".join(f"<li>{skill}</li>" for skill in missing_skills) if missing_skills else "<li>No missing skills.</li>"}
</ul>

<h4 class="text-success mt-4">💡 AI Suggestions</h4>

<ul>
{"".join(f"<li>{item}</li>" for item in suggestions)}
</ul>

<a href="/upload" class="btn btn-primary mt-3">
Analyze Another Resume
</a>

</div>

</div>

</body>
</html>
"""


if __name__ == "__main__":
    app.run(debug=True)