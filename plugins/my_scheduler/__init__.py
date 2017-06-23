import pybossa.sched as sched
from pybossa.forms.forms import TaskSchedulerForm
from flask.ext.plugins import Plugin
from functools import wraps
from pybossa.core import project_repo
from pybossa.model.user import User
from flask.ext.login import current_user

__plugin__ = "FRGScheduler"
__version__ = "0.0.1"

SCHEDULER_NAME = 'FRG'
SCHEDULER_DISPLAY_NAME = "FRG"


def get_task(project_id, user_id=None, user_ip=None, n_answers=30, offset=0):
	project = project_repo.get(project_id)
	if project and len(project.tasks)>0:
		if current_user.image_score>50:
			return
		elif current_user.video_score>50:
			return
		elif current_user.audio_score>50:
			return
		elif current_user.doc_score>50:
			return
		return others
	else:
		return None
    #pass


def with_frg_scheduler(f):
    @wraps(f)
    def wrapper(project_id, sched, user_id=None, user_ip=None, offset=0):
        if sched == SCHEDULER_NAME:
            return get_task(project_id, user_id, user_ip, offset=offset)
        return f(project_id, sched, user_id=user_id, user_ip=user_ip, offset=offset)
    return wrapper


def variants_with_frg_scheduler(f):
    @wraps(f)
    def wrapper():
        return f() + [(SCHEDULER_NAME, SCHEDULER_DISPLAY_NAME)]
    return wrapper


class FRGScheduler(Plugin):

    def setup(self):
        sched.new_task = with_frg_scheduler(sched.new_task)
        sched.sched_variants = variants_with_frg_scheduler(sched.sched_variants)
TaskSchedulerForm.update_sched_options(sched.sched_variants())
