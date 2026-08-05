from flask import Flask, render_template, request
import os
import pdfplumber
from Skills.skills import SKILLS, JOB_SKILLS

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
        return "Please Select Resume"

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    resume_text = ""

    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text()

            if text:
                resume_text += text + "\n"

    resume_lower = resume_text.lower()

    job_description = request.form["job_description"]
    job_lower = job_description.lower()
    # ---------------- FIND REQUIRED SKILLS ----------------

    required_skills = []

    for job_role, skills in JOB_SKILLS.items():
        if job_role.lower() in job_lower:
            required_skills = skills
            break

    if not required_skills:
        for skill in SKILLS:
            if skill.lower() in job_lower:
                required_skills.append(skill)


    # ---------------- FIND FOUND & MISSING SKILLS ----------------

    found_skills = []
    missing_skills = []

    for skill in required_skills:

        if skill.lower() in resume_lower:
            found_skills.append(skill)

        else:
            missing_skills.append(skill)


    # ---------------- ATS SCORE ----------------

    if len(required_skills) > 0:

        ats_score = round(
            (len(found_skills) / len(required_skills)) * 100,
            2
        )

    else:

        ats_score = 0


    # ---------------- COLOR ----------------

    if ats_score >= 80:
        color = "success"

    elif ats_score >= 60:
        color = "warning"

    else:
        color = "danger"


    # ---------------- SUGGESTIONS ----------------

    suggestions = []

    if ats_score >= 80:

        suggestions.append(
            "Excellent! Your resume matches this job role very well."
        )

    elif ats_score >= 60:

        suggestions.append(
            "Good Resume. Add the missing skills to improve your ATS Score."
        )

    else:

        suggestions.append(
            "Your resume needs improvement."
        )

        suggestions.append(
            "Add more relevant skills, projects and certifications."
        )
        return f"""
<!DOCTYPE html>
<html>

<head>

    <title>ResumeSync AI</title>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet">

</head>

<body class="bg-light">

<div class="container mt-5">

<div class="card shadow-lg p-5">

<h1 class="text-center text-success">
🤖 ResumeSync AI
</h1>

<hr>

<h3>
ATS Score : {ats_score}%
</h3>

<div class="progress mb-4" style="height:30px;">

<div class="progress-bar bg-{color}"
role="progressbar"
style="width:{ats_score}%">

{ats_score}%

</div>

</div>

<h4 class="text-primary">
✅ Skills Found
</h4>

<ul>
{"".join(f"<li>{skill}</li>" for skill in found_skills) if found_skills else "<li>No Skills Found</li>"}
</ul>

<h4 class="text-danger mt-4">
❌ Missing Skills
</h4>

<ul>
{"".join(f"<li>{skill}</li>" for skill in missing_skills) if missing_skills else "<li>No Missing Skills</li>"}
</ul>

<h4 class="text-success mt-4">
💡 Suggestions
</h4>

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