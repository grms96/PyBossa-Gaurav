#import __init__
#from .__init__ import db
from pybossa.core import db
from pybossa.model.user import User

class quiz(db.Model):
	quiz_id = db.Column(db.Integer, primary_key=True) #Primary key identifying a quiz
	name = db.Column(db.String) # Name of the quiz
	project_id = db.Column(db.Integer, db.ForeignKey('project.id')) # Name of the project
	models= db.relationship('question', backref='que', lazy='dynamic') #Stores all questions as a list of question objects for the corresponding quiz
	responses = db.relationship('response', backref='res_quiz', lazy='dynamic') #Stores all responses as a list of response objects for the corre4sponding quiz

class question(db.Model):
	question_id = db.Column(db.Integer, primary_key=True) #Primary Key identifying a question
	quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.quiz_id')) #Foreign Key to refer to corresponding quiz
	q_text = db.Column(db.String) #Text of the question to be solved
	file_path = db.Column(db.String) #Object of type File which stores link and alt text to image
	option1 = db.Column(db.String) #option A
	option2 = db.Column(db.String) #option B
	option3 = db.Column(db.String) #option C
	option4 = db.Column(db.String) #option D
	answer = db.Column(db.String) #correct answer to the question (A/B/C/D)
	#file_path = db.Column(db.String) # adress of the uploaded media
	category = db.Column(db.String) #category to which question belongs to
	responses = db.relationship('response', backref='res_question', lazy='dynamic') #Stores all responses to theis question as a list of response objects

"""
class user(db.Model):
	user_id = db.Column(db.Integer, primary_key=True) #Primary key identifying a user
	name = db.Column(db.String) # name of the user
	responses = db.relationship('response', backref='res_user', lazy='dynamic') # Stores all responses submitted by the corresponding user as a list of response objects
"""

class response(db.Model):
	response_id = db.Column(db.Integer, primary_key=True) # Primary key identifying a response
	user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #Foriegn key to the user of the response
	quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.quiz_id')) #Foriegn key to the corresponding quiz for the response
	question_id = db.Column(db.Integer, db.ForeignKey('question.question_id')) #Foriegn key to the corresponding question for the response
	response = db.Column(db.String) #Response submitted by the user
	result = db.Column(db.Boolean) #True if matches correct answer, False if does not match correct answer

