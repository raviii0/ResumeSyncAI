from flask import Flask, render_template, request
import os
import pdfplumber
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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

    # Read PDF
    resume_text = ""

    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                resume_text += text + "\n"

    # Job Description
    job_description = request.form["job_description"]

    # ATS Score
    documents = [resume_text, job_description]

    vectorizer = CountVectorizer()

    vectors = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(vectors)

    ats_score = round(similarity[0][1] * 100, 2)

    # Skills
    skills = job_description.splitlines()
    skills = [skill.strip() for skill in skills if skill.strip()]

    found_skills = []
    missing_skills = []

    print("==========")
    print(resume_text)
    print("==========")
    
    resume_lower = resume_text.lower()

    for skill in skills:
        if skill.lower() in resume_lower:
            found_skills.append(skill)
        else:
            missing_skills.append(skill)
            # AI Suggestions
    suggestions = []

    if ats_score < 60:
        suggestions.append("Improve your resume by adding more relevant skills.")
        suggestions.append("Use ATS-friendly formatting.")
        suggestions.append("Add more projects and certifications.")
    elif ats_score < 80:
        suggestions.append("Good resume. Add more keywords from the Job Description.")
    else:
        suggestions.append("Excellent! Your resume is ATS Friendly.")

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
AI Resume Analysis
</h1>

<hr>

<h3>ATS Score : {ats_score}%</h3>

<h4 class="mt-4 text-primary">
Skills Found
</h4>

<p>{", ".join(found_skills) if found_skills else "No matching skills found."}</p>

<h4 class="mt-4 text-danger">
Missing Skills
</h4>

<p>{", ".join(missing_skills)}</p>

<h4 class="mt-4 text-success">
AI Suggestions
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