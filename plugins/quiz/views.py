from flask import current_app,render_template, session,flash
from flask import request, redirect, url_for
import models
from .models import question,quiz, response
from .forms import Create_quiz, Display_quiz
from .forms import Display_question, Add_quiz
#from .__init__ import db
import os,shutil #used for creation of folders
from werkzeug.utils import secure_filename
from flask import send_from_directory
from flask import Blueprint
from pybossa.core import db
from flask.ext.login import login_required, current_user
from pybossa.view.projects import project_by_shortname, pro_features

blueprint = Blueprint('quiz', __name__, template_folder="templates")

CONTAINER="quiz_directory"

@blueprint.route('/')
@blueprint.route('/index')
@login_required
def index():
    user = {'nickname': 'Miguel'}  # fake user
    posts = [  # fake array of posts
        {
            'author': {'nickname': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'nickname': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template("index.html",
                           title='Home',
                           user=user,
                           posts=posts)

def allowed_file(filename):
    """Return True if valid, otherwise false."""
    if '.' in filename:
        if filename.rsplit('.', 1)[1].lower() in ["jpg", "png", "mp3", "mp4", "pdf", "jpeg","MKV"] :    
		return True
    flash('Only zip and tar.gz extensions are allowed','danger')
    return False


@blueprint.route('/<short_name>/addquestions', methods=['GET', 'POST'])
@login_required
def quiz_form(short_name):
	(project, owner, n_tasks, n_task_runs,overall_progress, last_activity,n_results) = project_by_shortname(short_name)
	form = Create_quiz() # Fetch appropriate form from forms.py
	if request.method == "POST" and form.validate():
		#collecting data from forms.py
		que=form.question_text.data #collect the entered question text
		_file=request.files['file_field']
		if _file and allowed_file(_file.filename):
			parent_path=current_app.root_path[:current_app.root_path.rfind("/")]
			_file.save(os.path.join((parent_path+'/uploads/'+CONTAINER) , _file.filename))
		file_path='/uploads/'+CONTAINER+'/'+_file.filename
		option_A=form.oA.data #collect entered option A text
		option_B=form.oB.data #collect entered option B text
		option_C=form.oC.data #collect entered option C text
		option_D=form.oD.data #collect entered option D text
		correct_answer=form.correct_answer.data #collect entered correct answer
        	# Based on entered answer, store the option text in the answer field in the database
        	if correct_answer == 'A':
            		correct_answer = option_A
        	elif correct_answer == 'B':
            		correct_answer = option_B
        	elif correct_answer == 'C':
            		correct_answer = option_C
       		elif correct_answer == 'D':
            		correct_answer = option_D
        	category=form.category.data #collect entered question category
	        q=question(quiz_id = session['quiz_id'],q_text=que,file_path=file_path,option1=option_A,option2=option_B,option3=option_C,option4=option_D,answer=correct_answer,category=category)# Create object of class question from questions.py
        	db.session.add(q) # Add object q to db.session
        	db.session.commit() # Commit changes to app.db
		if request.form['submit'] == 'ADD':
            		return redirect(url_for('quiz.quiz_form',short_name=short_name))
		elif request.form['submit'] == 'SUBMIT':
			return redirect(url_for('quiz.display_quiz',short_name=short_name))
    	return render_template("create_quiz.html", title = "Add Question", quiz_name = session['quiz_name'], form=form,project=project,pro_features=pro_features()) # Render form template
@blueprint.route('/<short_name>/display_question', methods=['GET', 'POST'])
@login_required
def display_question(short_name):
	form = Display_question() # Fetch appropriate form to get user response
	(project, owner, n_tasks, n_task_runs,overall_progress, last_activity,n_results) = project_by_shortname(short_name)
	if request.method == "POST":
		#Collect user submisstion
		submission = form.submission.data
		if submission==session['correct_answer']:
			result=True
		else:
			result=False
		q=response(quiz_id=session['quiz_id'],user_id=current_user.id,question_id=session['question_id'],response=submission,result=result)
		db.session.add(q)
		db.session.commit()
		# Display Next Question
		if session['question_id'] != 0:
			session['question_id'] = session['question_id'] + 1
		else:
			session['question_id'] = 1
		q = models.question.query.filter_by(quiz_id=session['quiz_id'],question_id=session['question_id']).first()
		if q:
			form.submission.choices = [(q.option1, q.option1), (q.option2, q.option2), (q.option3, q.option3), (q.option4, q.option4)]
			session['question_id']=q.question_id
			session['correct_answer']=q.answer
			return render_template("display_question.html", q = q, quiz_name=session['quiz_name'], form=form,project=project,pro_features=pro_features())

		else:
		#	session['quiz_id']=-1;
			user = {'nickname': 'Miguel'}
			return redirect(url_for('quiz.display_result',short_name=short_name))
	else:
		q = models.question.query.filter_by(quiz_id=session['quiz_id']).first()
		form.submission.choices = [(q.option1, q.option1), (q.option2, q.option2), (q.option3, q.option3), (q.option4, q.option4)]
		session['question_id']=q.question_id
		session['correct_answer']=q.answer
		file_type = gettype(q.file_path)
		#session['q_no']=1;
		return render_template("display_question.html", q = q,file_type=file_type, form=form,project=project,pro_features=pro_features())

def gettype(filename):
	if filename.rsplit('.', 1)[1].lower() in ["jpeg", "jpg", "png"]:
		return "image"
	elif filename.rsplit('.', 1)[1].lower() in ["mp3"]:
		return "audio"
	elif filename.rsplit('.', 1)[1].lower() in ["mp4"]:
		return "video"
	elif filename.rsplit('.', 1)[1].lower() in ["pdf"]:
		return "document"

# create Quiz

@blueprint.route('/<short_name>/create_quiz', methods=['GET', 'POST'])
@login_required
def create_quiz(short_name):
	(project, owner, n_tasks, n_task_runs,overall_progress, last_activity,n_results) = project_by_shortname(short_name)
	project_id=project.id
	form = Add_quiz()
	if request.method == "POST" and form.validate():
		quiz_name=form.name.data
		q=quiz(name=quiz_name,project_id=project_id)
		db.session.add(q)
		db.session.commit()
		session['quiz_name']=quiz_name
		session['quiz_id'] = models.quiz.query.filter_by(name=quiz_name).first().quiz_id
		return redirect(url_for('quiz.quiz_form',short_name=short_name))
	return render_template("add_quiz.html", title = "create quiz", form=form,project=project,pro_features=pro_features())

@blueprint.route('/<short_name>/displayquiz', methods=['GET', 'POST'])
@login_required
def display_quiz(short_name):
    form = Display_quiz()
    (project, owner, n_tasks, n_task_runs,overall_progress, last_activity,n_results) = project_by_shortname(short_name)
    project_id=project.id
    if request.method == "POST":
        quiz_name = form.name.data
        session['quiz_name'] = quiz_name
        session['quiz_id'] = models.quiz.query.filter_by(name=quiz_name).first().quiz_id
        return redirect(url_for('quiz.display_question',short_name=short_name))
    q = models.quiz.query.filter_by(project_id=project_id).all()
    form.name.choices = []
    for quiz in q:
        form.name.choices.append((quiz.name, quiz.name))
    return render_template("display_quiz.html", title="Display Quiz", form=form,project=project,pro_features=pro_features())

@blueprint.route('/<short_name>/displayresult')
@login_required
def display_result(short_name):
	(project, owner, n_tasks, n_task_runs,overall_progress, last_activity,n_results) = project_by_shortname(short_name)
        total=len(models.response.query.filter_by(quiz_id=session['quiz_id'],user_id=current_user.id).all())
	print total
        correct=len(models.response.query.filter_by(result=True,quiz_id=session['quiz_id'],user_id=current_user.id).all())
        marks=(correct*100.0)/total;
        session['quiz_id']=-1
        return render_template("display_result.html",title="display result",marks=marks,total=total,correct=correct,project=project,pro_features=pro_features())
