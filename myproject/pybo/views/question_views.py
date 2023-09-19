from datetime import datetime

from flask import Blueprint, render_template, request, url_for, g, flash, escape, session
from sqlalchemy import func
from werkzeug.utils import redirect

from .. import db
from ..forms import QuestionForm, AnswerForm
from ..models import Question, Answer, User, question_voter, Subscriber
from ..views.auth_views import login_required
import smtplib
from email.message import EmailMessage

bp = Blueprint('question', __name__, url_prefix='/question')


@bp.route('/data_science_list/')
def ds_list():
    # 입력 파라미터
    page = request.args.get('page', type=int, default=1)
    kw = request.args.get('kw', type=str, default='')
    so = request.args.get('so', type=str, default='recent')

    # 정렬
    if so == 'recommend':
        sub_query = db.session.query(question_voter.c.question_id, func.count('*').label('num_voter')) \
            .group_by(question_voter.c.question_id).subquery()
        question_list = Question.query.filter(Question.category == 'Data Science') \
            .outerjoin(sub_query, Question.id == sub_query.c.question_id) \
            .order_by(sub_query.c.num_voter.desc(), Question.create_date.desc())
    elif so == 'popular':
        sub_query = db.session.query(Answer.question_id, func.count('*').label('num_answer')) \
            .group_by(Answer.question_id).subquery()
        question_list = Question.query.filter(Question.category == 'Data Science') \
            .outerjoin(sub_query, Question.id == sub_query.c.question_id) \
            .filter(Question.category == 'Data Science') \
            .order_by(sub_query.c.num_answer.desc(), Question.create_date.desc())
    else:  # recent
        question_list = Question.query.order_by(Question.create_date.desc()).filter(Question.category == 'Data Science')

    # 조회
    if kw:
        search = '%%{}%%'.format(kw)
        sub_query = db.session.query(Answer.question_id, Answer.content, User.username) \
            .join(User, Answer.user_id == User.id).subquery()
        question_list = question_list \
            .join(User) \
            .outerjoin(sub_query, sub_query.c.question_id == Question.id) \
            .filter(Question.subject.ilike(search) |  # 질문제목
                    Question.content.ilike(search) |  # 질문내용
                    User.username.ilike(search) |  # 질문작성자
                    sub_query.c.content.ilike(search) |  # 답변내용
                    sub_query.c.username.ilike(search)  # 답변작성자
                    ) \
            .distinct()

    # 태그 리스트 생성
    tag_list = question_list.with_entities(Question.tag).all()
    tag_list = list(set(tag_list))
    tag_list = [tag[0] for tag in tag_list]
    # 페이징
    question_list = question_list.paginate(page=page, per_page=10, error_out=False)
    return render_template('question/question_list.html', question_list=question_list, page=page,
                           kw=kw, so=so, view_name='question.ds_list', tag_list=tag_list, category='Data Science')


@bp.route('/development_list/')
def d_list():
    # 입력 파라미터
    tag_list = Question.query.with_entities(Question.tag).all()
    tag_list = list(set(tag_list))
    tag_list = [tag[0] for tag in tag_list]
    page = request.args.get('page', type=int, default=1)
    kw = request.args.get('kw', type=str, default='')
    so = request.args.get('so', type=str, default='recent')
    question_list = Question.query.order_by(Question.create_date.desc()).filter(Question.category == 'Development')
    question_list = question_list.paginate(page=page, per_page=10, error_out=False)
    return render_template('question/development_list.html', question_list=question_list, page=page,
                           kw=kw, so=so, view_name='question.d_list', tag_list=tag_list, category='Development')


@bp.route('/computer_science_list/')
def cs_list():
    # 입력 파라미터
    page = request.args.get('page', type=int, default=1)
    kw = request.args.get('kw', type=str, default='')
    so = request.args.get('so', type=str, default='recent')

    # 정렬
    if so == 'recommend':
        sub_query = db.session.query(question_voter.c.question_id, func.count('*').label('num_voter')) \
            .group_by(question_voter.c.question_id).subquery()
        question_list = Question.query.filter(Question.category == 'Computer Science') \
            .outerjoin(sub_query, Question.id == sub_query.c.question_id) \
            .order_by(sub_query.c.num_voter.desc(), Question.create_date.desc())
    elif so == 'popular':
        sub_query = db.session.query(Answer.question_id, func.count('*').label('num_answer')) \
            .group_by(Answer.question_id).subquery()
        question_list = Question.query.filter(Question.category == 'Computer Science') \
            .outerjoin(sub_query, Question.id == sub_query.c.question_id) \
            .order_by(sub_query.c.num_answer.desc(), Question.create_date.desc())
    else:  # recent
        question_list = Question.query.order_by(Question.create_date.desc()).filter(
            Question.category == 'Computer Science')

    # 조회
    if kw:
        search = '%%{}%%'.format(kw)
        sub_query = db.session.query(Answer.question_id, Answer.content, User.username) \
            .join(User, Answer.user_id == User.id).subquery()
        question_list = question_list \
            .join(User) \
            .outerjoin(sub_query, sub_query.c.question_id == Question.id) \
            .filter(Question.subject.ilike(search) |  # 질문제목
                    Question.content.ilike(search) |  # 질문내용
                    User.username.ilike(search) |  # 질문작성자
                    sub_query.c.content.ilike(search) |  # 답변내용
                    sub_query.c.username.ilike(search)  # 답변작성자
                    ) \
            .distinct()

    # 태그 리스트 생성
    tag_list = question_list.with_entities(Question.tag).all()
    tag_list = list(set(tag_list))
    tag_list = [tag[0] for tag in tag_list]
    # 페이징
    question_list = question_list.paginate(page=page, per_page=10, error_out=False)
    return render_template('question/question_list.html', question_list=question_list, page=page, kw=kw, so=so,
                           view_name='question.cs_list', tag_list=tag_list, category='Computer Science')


@bp.route('/artificial_intelligence_list/')
def ai_list():
    # 입력 파라미터
    page = request.args.get('page', type=int, default=1)
    kw = request.args.get('kw', type=str, default='')
    so = request.args.get('so', type=str, default='recent')

    # 정렬
    if so == 'recommend':
        sub_query = db.session.query(question_voter.c.question_id, func.count('*').label('num_voter')) \
            .group_by(question_voter.c.question_id).subquery()
        question_list = Question.query.filter(Question.category == 'Artificial Intelligence') \
            .outerjoin(sub_query, Question.id == sub_query.c.question_id) \
            .order_by(sub_query.c.num_voter.desc(), Question.create_date.desc())
    elif so == 'popular':
        sub_query = db.session.query(Answer.question_id, func.count('*').label('num_answer')) \
            .group_by(Answer.question_id).subquery()
        question_list = Question.query.filter(Question.category == 'Artificial Intelligence') \
            .outerjoin(sub_query, Question.id == sub_query.c.question_id) \
            .order_by(sub_query.c.num_answer.desc(), Question.create_date.desc())
    else:  # recent
        question_list = Question.query.filter(Question.category == 'Artificial Intelligence').order_by(
            Question.create_date.desc())

    # 조회
    if kw:
        search = '%%{}%%'.format(kw)
        sub_query = db.session.query(Answer.question_id, Answer.content, User.username) \
            .join(User, Answer.user_id == User.id).subquery()
        question_list = question_list \
            .join(User) \
            .outerjoin(sub_query, sub_query.c.question_id == Question.id) \
            .filter(Question.subject.ilike(search) |  # 질문제목
                    Question.content.ilike(search) |  # 질문내용
                    User.username.ilike(search) |  # 질문작성자
                    sub_query.c.content.ilike(search) |  # 답변내용
                    sub_query.c.username.ilike(search)  # 답변작성자
                    ) \
            .distinct()

    # 태그 리스트 생성
    tag_list = question_list.with_entities(Question.tag).all()
    tag_list = list(set(tag_list))
    tag_list = [tag[0] for tag in tag_list]
    # 페이징
    question_list = question_list.paginate(page=page, per_page=10, error_out=False)
    return render_template('question/question_list.html', question_list=question_list, page=page,
                           kw=kw, so=so, view_name='question.ai_list', tag_list=tag_list, category='Artificial Intelligence')


@bp.route('/relaxation_list/')
def r_list():
    # 입력 파라미터
    page = request.args.get('page', type=int, default=1)
    kw = request.args.get('kw', type=str, default='')
    so = request.args.get('so', type=str, default='recent')

    # 정렬
    if so == 'recommend':
        sub_query = db.session.query(question_voter.c.question_id, func.count('*').label('num_voter')) \
            .group_by(question_voter.c.question_id).subquery()
        question_list = Question.query.filter(Question.category == 'Relaxation') \
            .outerjoin(sub_query, Question.id == sub_query.c.question_id) \
            .order_by(sub_query.c.num_voter.desc(), Question.create_date.desc())
    elif so == 'popular':
        sub_query = db.session.query(Answer.question_id, func.count('*').label('num_answer')) \
            .group_by(Answer.question_id).subquery()
        question_list = Question.query.filter(Question.category == 'Relaxation') \
            .outerjoin(sub_query, Question.id == sub_query.c.question_id) \
            .order_by(sub_query.c.num_answer.desc(), Question.create_date.desc())
    else:  # recent
        question_list = Question.query.filter(Question.category == 'Relaxation').order_by(Question.create_date.desc())

    # 조회
    if kw:
        search = '%%{}%%'.format(kw)
        sub_query = db.session.query(Answer.question_id, Answer.content, User.username) \
            .join(User, Answer.user_id == User.id).subquery()
        question_list = question_list \
            .join(User) \
            .outerjoin(sub_query, sub_query.c.question_id == Question.id) \
            .filter(Question.subject.ilike(search) |  # 질문제목
                    Question.content.ilike(search) |  # 질문내용
                    User.username.ilike(search) |  # 질문작성자
                    sub_query.c.content.ilike(search) |  # 답변내용
                    sub_query.c.username.ilike(search)  # 답변작성자
                    ) \
            .distinct()

    # 태그 리스트 생성
    tag_list = question_list.with_entities(Question.tag).all()
    tag_list = list(set(tag_list))
    tag_list = [tag[0] for tag in tag_list]
    # 페이징
    question_list = question_list.paginate(page=page, per_page=10, error_out=False)
    return render_template('question/question_list.html', question_list=question_list, page=page,
                           kw=kw, so=so, view_name='question.r_list', tag_list=tag_list, category='Relaxation')


@bp.route('/communication_list/')
def c_list():
    # 입력 파라미터
    page = request.args.get('page', type=int, default=1)
    kw = request.args.get('kw', type=str, default='')
    so = request.args.get('so', type=str, default='recent')

    if so == 'recommend':
        sub_query = db.session.query(question_voter.c.question_id, func.count('*').label('num_voter')) \
            .group_by(question_voter.c.question_id).subquery()
        question_list = Question.query.filter(Question.category == 'Communication') \
            .outerjoin(sub_query, Question.id == sub_query.c.question_id) \
            .order_by(sub_query.c.num_voter.desc(), Question.create_date.desc())
    elif so == 'popular':
        sub_query = db.session.query(Answer.question_id, func.count('*').label('num_answer')) \
            .group_by(Answer.question_id).subquery()
        question_list = Question.query.filter(Question.category == 'Communication') \
            .outerjoin(sub_query, Question.id == sub_query.c.question_id) \
            .order_by(sub_query.c.num_answer.desc(), Question.create_date.desc())
    else:  # recent
        question_list = Question.query.filter(Question.category == 'Communication').order_by(
            Question.create_date.desc())

    # 조회
    if kw:
        search = '%%{}%%'.format(kw)
        sub_query = db.session.query(Answer.question_id, Answer.content, User.username) \
            .join(User, Answer.user_id == User.id).subquery()
        question_list = question_list \
            .join(User) \
            .outerjoin(sub_query, sub_query.c.question_id == Question.id) \
            .filter(Question.subject.ilike(search) |  # 질문제목
                    Question.content.ilike(search) |  # 질문내용
                    User.username.ilike(search) |  # 질문작성자
                    sub_query.c.content.ilike(search) |  # 답변내용
                    sub_query.c.username.ilike(search)  # 답변작성자
                    ) \
            .distinct()

    # 태그 리스트 생성
    tag_list = question_list.with_entities(Question.tag).all()
    tag_list = list(set(tag_list))
    tag_list = [tag[0] for tag in tag_list]
    # 페이징
    question_list = question_list.paginate(page=page, per_page=10, error_out=False)
    return render_template('question/question_list.html', question_list=question_list, page=page,
                           kw=kw, so=so, view_name='question.c_list', tag_list=tag_list, category='Communication')


@bp.route('/detail/<int:question_id>/')
@login_required
def detail(question_id):
    # 조회수 중복을 막는 코드..
    user_id = g.user.id
    if 'user_data' not in session:
        session['user_data'] = []
    question = Question.query.get_or_404(question_id)
    if {question_id: user_id} not in session['user_data']:
        session['user_data'].append({question_id: user_id})
        question.views += 1
    else:
        pass
    # 조회수 중복 방지 코드 끝..
    form = AnswerForm()
    question_content = question.content
    db.session.commit()
    return render_template('question/question_detail.html', question=question, form=form,
                           question_content=escape(question_content))


@bp.route('/create/', methods=('GET', 'POST'))
@login_required
def create():
    form = QuestionForm()
    tag_list = Question.query.with_entities(Question.tag).all()
    tag_list = list(set(tag_list))
    tag_list = [tag[0] for tag in tag_list]
    subscriber_rows = Subscriber.query.filter_by(to_user_id=g.user.id).all()
    user_emails = [User.query.get_or_404(row.from_user_id).email for row in subscriber_rows]

    if request.method == 'POST' and form.validate_on_submit():
        question = Question(
            subject=form.subject.data,
            content=form.content.data,
            create_date=datetime.now(),
            user=g.user,
            category=form.category.data,
            tag=form.tag.data
        )
        db.session.add(question)
        db.session.commit()
        # STMP 서버의 url과 port 번호
        SMTP_SERVER = 'smtp.gmail.com'
        SMTP_PORT = 465

        # 1. SMTP 서버 연결
        smtp = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)

        EMAIL_ADDR = 'm23235180@gmail.com'
        EMAIL_PASSWORD = 'bpzwmnstpwrxmevk'

        # 2. SMTP 서버에 로그인
        smtp.login(EMAIL_ADDR, EMAIL_PASSWORD)

        # 3. MIME 형태의 이메일 메세지 작성
        message = EmailMessage()
        message.set_content(f'글을 확인하기 위해서 아래의 링크를 클릭해주세요! \n http://127.0.0.1:5000/question/detail/{question.id}/')
        message["Subject"] = f"{g.user.username}님의 새로운 글이 올라왔어요!"
        message["From"] = EMAIL_ADDR  # 보내는 사람의 이메일 계정
        message["To"] = ','.join(user_emails)

        # 4. 서버로 메일 보내기
        smtp.send_message(message)

        # 5. 메일을 보내면 서버와의 연결 끊기
        smtp.quit()
        return redirect(url_for('main.index'))

    return render_template('question/question_form.html', form=form, tag_list=tag_list)


@bp.route('/modify/<int:question_id>', methods=('GET', 'POST'))
@login_required
def modify(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash('수정권한이 없습니다')
        return redirect(url_for('question.detail', question_id=question_id))
    if request.method == 'POST':
        form = QuestionForm()
        if form.validate_on_submit():
            form.populate_obj(question)
            question.modify_date = datetime.now()  # 수정일시 저장
            db.session.commit()
            return redirect(url_for('question.detail', question_id=question_id))
    else:
        form = QuestionForm(obj=question)
    return render_template('question/question_form.html', form=form)


@bp.route('/delete/<int:question_id>')
@login_required
def delete(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash('삭제권한이 없습니다')
        return redirect(url_for('question.detail', question_id=question_id))
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('main.index'))


@bp.route('/tagged_list/<string:tag>/<string:category>')
@login_required
def tagged_list(tag, category):
    question_list = Question.query.filter(Question.tag == tag, Question.category == category)
    page = request.args.get('page', type=int, default=1)
    question_list = question_list.paginate(page=page, per_page=10, error_out=False)
    return render_template('question/tagged_list.html', question_list=question_list, page=page, tag=tag,
                           category=category)
