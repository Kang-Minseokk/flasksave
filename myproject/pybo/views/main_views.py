from flask import Blueprint, render_template
from ..models import VisitCount, Question
from .. import db


bp = Blueprint('main', __name__, url_prefix='/')


@bp.route('/hello')
def hello_pybo():
    return 'Hello, Pybo!'


@bp.route('/')
def index():
    visit_count = VisitCount.query.first()
    question_list = Question.query.order_by(Question.create_date.desc()).limit(5).all()

    # Increment the visit count and update the database
    if visit_count is not None:
        visit_count.count += 1
        db.session.commit()
    else:
        new_visit_count = VisitCount(count=1)
        db.session.add(new_visit_count)
        db.session.commit()

    return render_template('home.html', visit_count=visit_count, question_list=question_list)
