from flask import Blueprint, render_template, request, redirect, url_for
from ..forms import CalendarForm
from ..models import Calendar
from .. import db

bp = Blueprint('calendar', __name__, url_prefix="/calendar")


@bp.route('/show/')
def show():
    schedule_list = Calendar.query.all()
    schedule_data = []
    for schedule in schedule_list:
        schedule_data.append({
            'title': schedule.title,
            'content': schedule.content,
            'start_date': schedule.start_date.strftime("%Y-%m-%d"),
            'end_date': schedule.end_date.strftime("%Y-%m-%d")
        })

    return render_template('calendar/calendar.html', schedule_list=schedule_list,
                           schedule_data=schedule_data)


@bp.route('/create/', methods=['POST'])
def create():
    form = CalendarForm()
    if request.method == 'POST':
        schedule = Calendar(
            title=form.title.data,
            content=form.content.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data
        )
        db.session.add(schedule)
        db.session.commit()
        return redirect(url_for('calendar.show'))

    return render_template('calendar/calendar_form.html', form=form)




