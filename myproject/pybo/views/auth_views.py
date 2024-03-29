import os

from flask import Blueprint, url_for, render_template, flash, request, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect
import functools


from pybo import db
from pybo.forms import UserCreateForm, UserLoginForm, EmailForm
from pybo.models import User, Question, question_voter, Subscriber
import random, string


bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view


def power_login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None or g.user.username != "강민석":
            flash("Special Access Required!!", "warning")
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view


@bp.route('/signup/', methods=('GET', 'POST'))
def signup():
    form = UserCreateForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            profile_img = form.profile_img.data
            filename = profile_img.filename
            profile_img.save(os.path.join('/Users/minseokkang/projects/myproject/pybo/static/image', filename))
            user = User(username=form.username.data, password=generate_password_hash(form.password1.data),
                        email=form.email.data, profile_img=filename)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('main.index'))
        else:
            flash('이미 존재하는 사용자입니다.')
    return render_template('auth/signup.html', form=form)


@bp.route('/login/', methods=('GET', 'POST'))
def login():
    form = UserLoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        error = None
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            error = "존재하지 않는 사용자입니다."
        elif not check_password_hash(user.password, form.password.data):
            error = "비밀번호가 올바르지 않습니다."
        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('main.index'))
        flash(error)
    return render_template('auth/login.html', form=form)


@bp.route('/forgot/', methods=('GET', 'POST'))
def forgot():
    form = EmailForm()
    error = None
    if request.method == 'POST' and form.validate_on_submit():
        mail = User.query.filter_by(email=form.email.data).first()
        if not mail:
            error = "이메일을 확인해주세요"
            flash(error)
        if error is None:
            session.clear()
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                # 순서가 중요하다! : 임시 비밀번호 생성 -> 임시 비밀번호 flash해주기 -> 임시비밀번호 hash함수 적용
                # -> db에 commit해줌으로서 데이터 수정 및 저장
                # 나중에 password random generatot를 만들도록 하자.
                lowercase_letters = ''.join(random.choices(string.ascii_lowercase, k=4))
                digits = ''.join(random.choices(string.digits, k=4))
                generated_password = lowercase_letters + digits
                user.password = generated_password
                flash(f"Your temporary password is: {user.password}")
                user.password = generate_password_hash(user.password)
                db.session.commit()

    return render_template('auth/forgot.html', form=form)


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)


@bp.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('main.index'))


@bp.route('/user_info/<int:user_id>/')
@login_required
def user_info(user_id):
    page = request.args.get('page', type=int, default=1)
    user_question_list = Question.query.filter(Question.user_id == user_id).order_by(Question.create_date.desc())
    user_question_num = user_question_list.count()
    user_question_list = user_question_list.paginate(page=page, per_page=10, error_out=False)
    user = User.query.get_or_404(user_id)
    user_name = user.username
    user_total_recommend = db.session.query(question_voter).filter(question_voter.c.user_id == user_id).count()
    profile_img_path = User.query.get_or_404(user_id).profile_img
    user_subscribe_num = user.subscribe_num
    return render_template('auth/user_information.html', to_user_id=user_id,
                           user_question_list=user_question_list, user_name=user_name,
                           user_question_num=user_question_num, user_total_recommend=user_total_recommend,
                           profile_img_path=profile_img_path, user_subscribe_num=user_subscribe_num)


@bp.route('/subscribe/<int:to_user_id>/<int:from_user_id>/', methods=('GET', 'POST'))
@login_required
def subscribe(from_user_id, to_user_id):
    user = User.query.get_or_404(to_user_id)
    if request.method == 'POST':
        existing_subscription = Subscriber.query.filter_by(
            from_user_id=from_user_id,
            to_user_id=to_user_id
        ).first()
        if from_user_id == to_user_id:
            flash('본인을 구독할 수 없습니다!')
        else:
            if not existing_subscription:
                user.subscribe_num += 1
                subscribe_status = Subscriber(
                    from_user_id=from_user_id,
                    to_user_id=to_user_id
                )
                db.session.add(subscribe_status)
                db.session.commit()
                return redirect(url_for('auth.user_info', user_id=to_user_id))
            else:
                flash('이미 구독을 하셨습니다!')
    return redirect(url_for('auth.user_info', user_id=to_user_id))





