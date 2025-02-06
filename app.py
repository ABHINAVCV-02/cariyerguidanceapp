from flask import Flask, render_template_string, request
import requests
from transformers import pipeline

app = Flask(__name__)

# Initialize Hugging Face pipelines
career_guidance_pipeline = pipeline("text-generation", model="gpt2")
course_recommendation_pipeline = pipeline("text-classification", model="distilbert-base-uncased")

# Home route for displaying the form
@app.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Career Guidance</title>
    </head>
    <body>
        <h1>Career Guidance Form</h1>
        <form action="/submit" method="post">
            <label for="name">Name:</label><br>
            <input type="text" id="name" name="name" required><br><br>
            
            <label for="age">Age:</label><br>
            <input type="text" id="age" name="age" required><br><br>
            
            <label for="email">Email:</label><br>
            <input type="email" id="email" name="email" required><br><br>
            
            <label for="school_name">School Name:</label><br>
            <input type="text" id="school_name" name="school_name" required><br><br>
            
            <label for="interested_fields">Interested Fields:</label><br>
            <input type="checkbox" id="engineering" name="interested_fields" value="Engineering"> Engineering
            <input type="checkbox" id="medical" name="interested_fields" value="Medical"> Medical
            <input type="checkbox" id="arts" name="interested_fields" value="Arts"> Arts
            <input type="checkbox" id="commerce" name="interested_fields" value="Commerce"> Commerce<br><br>

            <h2>11th Standard Marks</h2>
            <label for="math_11">Math's:</label><br>
            <input type="number" id="math_11" name="math_11" required><br><br>
            
            <label for="physics_11">Physics:</label><br>
            <input type="number" id="physics_11" name="physics_11" required><br><br>
            
            <label for="chemistry_11">Chemistry:</label><br>
            <input type="number" id="chemistry_11" name="chemistry_11" required><br><br>
            
            <label for="english_11">English:</label><br>
            <input type="number" id="english_11" name="english_11" required><br><br>
            
            <label for="hindi_11">Hindi:</label><br>
            <input type="number" id="hindi_11" name="hindi_11" required><br><br>
            
            <label for="malayalam_11">Malayalam:</label><br>
            <input type="number" id="malayalam_11" name="malayalam_11" required><br><br>
            
            <h2>12th Standard Marks</h2>
            <label for="math_12">Math's:</label><br>
            <input type="number" id="math_12" name="math_12" required><br><br>
            
            <label for="physics_12">Physics:</label><br>
            <input type="number" id="physics_12" name="physics_12" required><br><br>
            
            <label for="chemistry_12">Chemistry:</label><br>
            <input type="number" id="chemistry_12" name="chemistry_12" required><br><br>
            
            <label for="english_12">English:</label><br>
            <input type="number" id="english_12" name="english_12" required><br><br>
            
            <label for="hindi_12">Hindi:</label><br>
            <input type="number" id="hindi_12" name="hindi_12" required><br><br>
            
            <label for="malayalam_12">Malayalam:</label><br>
            <input type="number" id="malayalam_12" name="malayalam_12" required><br><br>
            
            <label for="biology">Biology (Optional):</label><br>
            <input type="checkbox" id="biology" name="biology" value="Biology"><br><br>
            
            <label for="computer_science">Computer Science (Optional):</label><br>
            <input type="checkbox" id="computer_science" name="computer_science" value="Computer Science"><br><br>

            <input type="submit" value="Submit">
        </form>
    </body>
    </html>
    """)

# Route to handle form submission and give results
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    age = request.form['age']
    email = request.form['email']
    school_name = request.form['school_name']
    interested_fields = request.form.getlist('interested_fields')
    
    # Marks of 11th and 12th standard subjects
    marks_11th = { 
        'math': int(request.form['math_11']),
        'physics': int(request.form['physics_11']),
        'chemistry': int(request.form['chemistry_11']),
        'english': int(request.form['english_11']),
        'hindi': int(request.form['hindi_11']),
        'malayalam': int(request.form['malayalam_11']),
    }
    
    marks_12th = { 
        'math': int(request.form['math_12']),
        'physics': int(request.form['physics_12']),
        'chemistry': int(request.form['chemistry_12']),
        'english': int(request.form['english_12']),
        'hindi': int(request.form['hindi_12']),
        'malayalam': int(request.form['malayalam_12']),
    }

    weak_subjects = identify_weak_subjects(marks_11th, marks_12th)
    guidance = generate_guidance(interested_fields, weak_subjects)
    
    # Generate YouTube video recommendations based on weak subjects
    video_recommendations = get_video_recommendations(weak_subjects)

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Career Guidance Results</title>
    </head>
    <body>
        <h1>Career Guidance for {{ name }}</h1>
        <h2>Weak Subjects: {{ weak_subjects }}</h2>
        <h3>Career Guidance and Tips:</h3>
        <p>{{ guidance }}</p>
        <h3>Recommended YouTube Videos:</h3>
        <ul>
            {% for video in video_recommendations %}
                <li><a href="{{ video }}" target="_blank">{{ video }}</a></li>
            {% endfor %}
        </ul>
    </body>
    </html>
    """, name=name, guidance=guidance, video_recommendations=video_recommendations, weak_subjects=weak_subjects)


# Function to identify weak subjects based on marks
def identify_weak_subjects(marks_11th, marks_12th):
    weak_subjects = []
    
    # Check marks and identify weak subjects based on a threshold (e.g., below 50)
    for subject, mark in {**marks_11th, **marks_12th}.items():
        if mark < 50:
            weak_subjects.append(subject)
    
    return weak_subjects

# Function to generate career guidance and tips based on the student's interest
def generate_guidance(interested_fields, weak_subjects):
    interested_fields_str = ", ".join(interested_fields)
    weak_subjects_str = ", ".join(weak_subjects)
    prompt = f"Give career guidance for a student interested in {interested_fields_str}. The student is weak in {weak_subjects_str}. Provide tips and course recommendations."
    
    # Get career guidance from Hugging Face pipeline
    guidance = career_guidance_pipeline(prompt, max_length=1000, num_return_sequences=1)[0]['generated_text']
    
    return guidance

# Function to generate video recommendations from YouTube
def get_video_recommendations(weak_subjects):
    video_recommendations = []
    for subject in weak_subjects:
        query = f"{subject} study tutorial"
        # Call YouTube API or just return a link (this is a simple placeholder)
        video_recommendations.append(f"https://www.youtube.com/results?search_query={query}")
    
    return video_recommendations


if __name__ == '__main__':
    app.run(debug=True)
