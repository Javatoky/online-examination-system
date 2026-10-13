"""P4 考试安排 + P5 在线考试（试卷分发、在线答题、自动评阅）。"""

from datetime import datetime

from flask import Blueprint, request
from flask_jwt_extended import get_jwt

from ..extensions import db
from ..models import Exam, Paper, Question, Student, Submission, SubmissionDetail
from ..utils.responses import fail, ok
from ..utils.security import role_required

bp = Blueprint("exams", __name__)

DT_FORMATS = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M")


def _parse_dt(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    for fmt in DT_FORMATS:
        try:
            return datetime.strptime(str(value), fmt)
        except ValueError:
            continue
    return None


def _normalize(text):
    return "".join(str(text or "").split()).upper()


def _exam_brief(e):
    return {
        "exam_id": e.exam_id,
        "paper_id": e.paper_id,
        "paper_name": e.paper.paper_name if e.paper else None,
        "course_name": e.paper.course.course_name if e.paper and e.paper.course else None,
        "class": e.class_name,
        "start_time": e.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": e.end_time.strftime("%Y-%m-%d %H:%M:%S"),
        "duration": e.paper.duration if e.paper else None,
    }


# --------------------------------------------------------------------------- #
# 考试安排
# --------------------------------------------------------------------------- #
@bp.get("/exams")
@role_required("teacher", "student")
def list_exams():
    claims = get_jwt()
    if claims.get("role") == "teacher":
        exams = (
            Exam.query.join(Paper, Exam.paper_id == Paper.paper_id)
            .filter(Paper.teacher_id == claims.get("uid"))
            .order_by(Exam.exam_id.desc())
            .all()
        )
    else:
        student = db.session.get(Student, claims.get("uid"))
        exams = (
            Exam.query.filter(Exam.class_name == (student.class_name if student else None))
            .order_by(Exam.exam_id.desc())
            .all()
        )
    return ok([_exam_brief(e) for e in exams])


@bp.post("/exams")
@role_required("teacher")
def create_exam():
    teacher_id = get_jwt().get("uid")
    data = request.get_json(silent=True) or {}
    paper = db.session.get(Paper, data.get("paper_id") or 0)
    if not paper or paper.teacher_id != teacher_id:
        return fail("试卷不存在或非本人组卷", http_status=403)
    class_name = (data.get("class") or "").strip()
    start_time = _parse_dt(data.get("start_time"))
    end_time = _parse_dt(data.get("end_time"))
    if not class_name or not start_time or not end_time:
        return fail("应考班级、开始时间、结束时间均为必填项")
    if end_time <= start_time:
        return fail("结束时间必须晚于开始时间")

    exam = Exam(
        paper_id=paper.paper_id,
        class_name=class_name,
        start_time=start_time,
        end_time=end_time,
    )
    db.session.add(exam)
    db.session.commit()
    return ok({"exam_id": exam.exam_id}, msg="考试安排成功")


# --------------------------------------------------------------------------- #
# 试卷分发 / 在线答题
# --------------------------------------------------------------------------- #
def _accessible_exam(exam_id, student):
    """校验考试存在、班级匹配且当前处于考试时间窗口内。"""
    exam = db.session.get(Exam, exam_id)
    if not exam:
        return None, "考试不存在"
    if not student or exam.class_name != student.class_name:
        return None, "该考试不面向你的班级"
    now = datetime.now()
    if now < exam.start_time:
        return None, "考试尚未开始"
    if now > exam.end_time:
        return None, "考试已结束"
    return exam, None


@bp.get("/exams/<int:eid>/paper")
@role_required("student")
def get_exam_paper(eid):
    student = db.session.get(Student, get_jwt().get("uid"))
    exam, error = _accessible_exam(eid, student)
    if error:
        return fail(error, http_status=403)
    if Submission.query.filter_by(student_id=student.student_id, exam_id=eid).first():
        return fail("你已提交过本场考试", http_status=409)

    paper = exam.paper
    return ok(
        {
            "exam_id": exam.exam_id,
            "paper_name": paper.paper_name,
            "duration": paper.duration,
            "total_score": paper.total_score,
            "start_time": exam.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": exam.end_time.strftime("%Y-%m-%d %H:%M:%S"),
            "questions": [
                {
                    "question_id": item.question_id,
                    "seq": item.seq,
                    "score": item.score,
                    "question_type": item.question.question_type,
                    "content": item.question.content,
                    "options": item.question.options,
                }
                for item in paper.items
            ],
        }
    )


@bp.post("/exams/<int:eid>/submit")
@role_required("student")
def submit_exam(eid):
    student = db.session.get(Student, get_jwt().get("uid"))
    exam, error = _accessible_exam(eid, student)
    if error:
        return fail(error, http_status=403)
    if Submission.query.filter_by(student_id=student.student_id, exam_id=eid).first():
        return fail("你已提交过本场考试", http_status=409)

    answers = {
        int(item["question_id"]): item.get("answer")
        for item in (request.get_json(silent=True) or {}).get("answers", [])
        if item.get("question_id")
    }

    submission = Submission(student_id=student.student_id, exam_id=eid, score=0)
    total = 0
    for item in exam.paper.items:
        question = item.question
        student_answer = answers.get(question.question_id)
        obtained = (
            item.score if _normalize(student_answer) == _normalize(question.answer) else 0
        )
        total += obtained
        submission.details.append(
            SubmissionDetail(
                question_id=question.question_id,
                student_answer=student_answer,
                score_obtained=obtained,
            )
        )
    submission.score = total
    submission.submit_time = datetime.now()
    db.session.add(submission)
    db.session.commit()

    return ok(
        {
            "submission_id": submission.submission_id,
            "score": total,
            "total_score": exam.paper.total_score,
        },
        msg="交卷成功",
    )


@bp.get("/exams/<int:eid>/result")
@role_required("student")
def get_exam_result(eid):
    student = db.session.get(Student, get_jwt().get("uid"))
    submission = Submission.query.filter_by(student_id=student.student_id, exam_id=eid).first()
    if not submission:
        return fail("尚未提交本场考试", http_status=404)
    exam = db.session.get(Exam, eid)
    return ok(
        {
            "submission_id": submission.submission_id,
            "exam_id": eid,
            "paper_name": exam.paper.paper_name if exam else None,
            "score": submission.score,
            "total_score": exam.paper.total_score if exam else None,
            "submit_time": submission.submit_time.strftime("%Y-%m-%d %H:%M:%S"),
            "details": [
                {
                    "question_id": d.question_id,
                    "question_type": d.question.question_type,
                    "content": d.question.content,
                    "student_answer": d.student_answer,
                    "correct_answer": d.question.answer,
                    "score_obtained": d.score_obtained,
                    "correct": _normalize(d.student_answer) == _normalize(d.question.answer),
                }
                for d in submission.details
            ],
        }
    )
