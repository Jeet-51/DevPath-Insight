from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', '1234')
csrf = CSRFProtect(app) 
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ... your Flask app setup ...



from flask_migrate import Migrate

db = SQLAlchemy(app)
# Initialize Migrate
# Set up CSRF protection

migrate = Migrate(app, db)
 
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    profiles = db.relationship('UserProfile', backref='user', lazy=True)

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    education_level = db.Column(db.String(100))
    work_experience_years = db.Column(db.Integer)
    current_role = db.Column(db.String(100))
    desired_role = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    preferred_location = db.Column(db.String(100))
    skills = db.Column(db.Text)  # Storing serialized JSON of skills


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id  # Store user's ID in session
            return redirect(url_for('dashboard'))
        else:
            return render_template('home.html', error='Invalid username or password')
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = generate_password_hash(request.form.get('password'))
        role = request.form.get('role')

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('register.html', error='Username already exists')
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            return render_template('register.html', error='Email already registered')

        user = User(username=username, email=email, password=password, role=role)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id  # Store user's ID in session
        return redirect(url_for('dashboard'))

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user_profile = UserProfile.query.filter_by(user_id=user_id).first()
    return render_template('dashboard.html', user_profile=user_profile)


#############################################
#user-profile
from flask import jsonify 
@app.route('/User-Profile', methods=['GET', 'POST'])
def add_listing():
    if request.method == 'POST':
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))

        skills_data = {
            "skill": request.form.get('skillName'),
            "proficiency": request.form.get('proficiencyLevel'),
            "years": request.form.get('yearsOfExperience'),
            "last_used": request.form.get('lastUsed'),
            "interest": request.form.get('interestLevel')
        }
        
        new_profile = UserProfile(
            user_id=user_id,
            education_level=request.form.get('educationLevel'),
            work_experience_years=request.form.get('workExperienceYears'),
            current_role=request.form.get('currentRole'),
            desired_role=request.form.get('desiredRole'),
            industry=request.form.get('industry'),
            preferred_location=request.form.get('preferredLocation'),
            skills=json.dumps([skills_data])  # Storing as JSON string
        )
        db.session.add(new_profile)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return str(e)  # For debugging
        
        # Determine the skill gaps
        current_role = request.form.get('currentRole')
        user_skills = [skills_data['skill']]  # Assuming single skill entry for now
        skill_gaps = []

        # Define the required skills for each role
        required_skills = {
    'Data Science Intern': ["SQL", "Deep Learning", "Data Analysis", "Data Wrangling", 
                            "Strong Mathematical Foundation", "R", "Big Data and Distributed Computing"],
    'Software Developer': ["Algorithmic Thinking and Problem-Solving", "Testing and Debugging", 
                           "Cloud Computing and DevOps", "Version Control Systems", "Security Best Practices"],
    'Project Manager': ["Leadership", "Risk Management", "Agile and Scrum Methodologies", 
                        "Budget Management", "Communication", "Stakeholder Management", "Project Lifecycle Management"],
    'Marketing Specialist': ["SEO", "Content Marketing", "Data Analytics", "Customer Engagement", 
                             "Social Media Strategy", "Campaign Management", "Graphic Design Tools"],
    'Human Resources Manager': ["Employee Relations", "Recruitment Strategies", "Compliance Knowledge", 
                                "Performance Management", "HR Information Systems", "Training and Development"],
    'Network Engineer': ["Network Security", "Cisco Routing and Switching", "WAN/LAN", 
                         "Firewall Administration", "VPN", "Network Protocols", "VoIP Configuration"],
    'UI/UX Designer': ["Prototyping and Wireframing", "User Research", "Visual Design", 
                       "Interaction Design", "Responsive Design", "User Testing", "Adobe Creative Suite"],
    'Data Analyst': ["SQL", "Statistical Analysis", "Excel", "Data Visualization Tools", 
                     "Critical Thinking", "Data Mining Techniques", "Programming with Python or R"]
}

        # Determine the skill gaps
        if current_role in required_skills:
            skill_gaps = [skill for skill in required_skills[current_role] if skill not in user_skills]

        return jsonify({'message': 'Your information has been submitted successfully!', 'skill_gaps': skill_gaps})
    
    return render_template('UserProfile.html', csrf_token=generate_csrf())

######################
## explore
@app.route('/Explore-Trends')
def discover_trends():
    return render_template('ExploreTrends.html')

from flask import json  # Make sure to import json at the beginning of your file



#############################
#view data
@app.route('/View-data')
def find_deals():
    # Start with the base query
    query = UserProfile.query

    # Retrieve query parameters for filters from the request
    education_level = request.args.get('education_level')
    work_experience_years = request.args.get('work_experience_years')
    desired_role = request.args.get('desired_role')
    industry = request.args.get('industry')
    preferred_location = request.args.get('preferred_location')
    skills = request.args.get('skills')

    # Apply filters to the query based on the provided parameters
    if education_level:
        query = query.filter(UserProfile.education_level.ilike(f'%{education_level}%'))
    if work_experience_years:
        query = query.filter(UserProfile.work_experience_years == work_experience_years)
    if desired_role:
        query = query.filter(UserProfile.desired_role.ilike(f'%{desired_role}%'))
    if industry:
        query = query.filter(UserProfile.industry.ilike(f'%{industry}%'))
    if preferred_location:
        query = query.filter(UserProfile.preferred_location.ilike(f'%{preferred_location}%'))
    if skills:
        # Assuming skills is stored as a JSON string; adjust the query logic as needed based on your database structure
        query = query.filter(UserProfile.skills.ilike(f'%{skills}%'))

    # Execute the filtered query
    user_profiles = query.all()

    # Convert the JSON string in the skills attribute to a Python list for each profile
    for profile in user_profiles:
        profile.skills_list = json.loads(profile.skills) if profile.skills else []

    # Render the template with the filtered profiles
    return render_template('ViewData.html', user_profiles=user_profiles)


##############################
## edit section
from flask import request, redirect, url_for, render_template, flash
from flask import flash, redirect, render_template, request, url_for, session
from flask_wtf.csrf import generate_csrf
from werkzeug.exceptions import abort
@app.route('/edit-profile/<int:profile_id>', methods=['GET', 'POST'])
def edit_profile(profile_id):
    profile = UserProfile.query.get_or_404(profile_id)  # Fetch the profile or 404

    if request.method == 'POST':
        if 'user_id' not in session or session['user_id'] != profile.user_id:
            flash('Unauthorized to edit this profile.', 'error')
            return redirect(url_for('view_data'))  # Ensure user is logged in and authorized
  # Ensure user is logged in and authorized

        # Update the profile with form data
        profile.education_level = request.form['educationLevel']
        profile.work_experience_years = request.form['workExperienceYears']
        profile.current_role = request.form['currentRole']
        profile.desired_role = request.form['desiredRole']
        profile.industry = request.form['industry']
        profile.preferred_location = request.form['preferredLocation']

        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('view_data'))  # Redirect to view data page
        except Exception as e:
            db.session.rollback()
            flash('Error updating profile: ' + str(e), 'error')
            return redirect(url_for('edit_profile', profile_id=profile_id))

    else:
        # Convert JSON skills string back to Python list for form rendering
        profile.skills_list = json.loads(profile.skills) if profile.skills else []
        return render_template('editprofile.html', profile=profile, csrf_token=generate_csrf())

################################
# delete section
@app.route('/delete-profile/<int:profile_id>', methods=['POST'])
def delete_profile(profile_id):
    # Ensure the user is logged in and has the right to delete the profile
    # Your authorization logic here

    profile = UserProfile.query.get_or_404(profile_id)
    try:
        db.session.delete(profile)
        db.session.commit()
        flash('Profile deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting profile.', 'error')
    return redirect(url_for('find_deals'))





@app.route('/some-route', methods=['POST'])
def some_route():
    # your logic here
    flash('This is a flash message!', 'success')  # The second argument is optional and represents the category of the message
    return redirect(url_for('some_other_route'))


from flask import json
import sys
from flask import request, render_template


@app.route('/View-data', methods=['GET'])
def view_data():
    query = UserProfile.query

    education_level = request.args.get('education_level')
    if education_level:
        query = query.filter(UserProfile.education_level.ilike(f"%{education_level}%"))

    work_experience_years = request.args.get('work_experience_years')
    if work_experience_years is not None:
        query = query.filter(UserProfile.work_experience_years == int(work_experience_years))

    current_role = request.args.get('current_role')
    if current_role:
        query = query.filter(UserProfile.current_role.ilike(f"%{current_role}%"))

    desired_role = request.args.get('desired_role')
    if desired_role:
        query = query.filter(UserProfile.desired_role.ilike(f"%{desired_role}%"))

    industry = request.args.get('industry')
    if industry:
        query = query.filter(UserProfile.industry.ilike(f"%{industry}%"))

    preferred_location = request.args.get('preferred_location')
    if preferred_location:
        query = query.filter(UserProfile.preferred_location.ilike(f"%{preferred_location}%"))

    skills = request.args.get('skills')
    if skills:
        # Filter by skills here, adjusting for your database's capabilities

        user_profiles = UserProfile.query.all()
    for profile in user_profiles:
        profile.skills_list = json.loads(profile.skills) if profile.skills else []

    return render_template('ViewData.html', user_profiles=user_profiles)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/login')
def login():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
 app.run(host='0.0.0.0', port=8000)
    with app.app_context():
        db.create_all()
    app.run(debug=True)





