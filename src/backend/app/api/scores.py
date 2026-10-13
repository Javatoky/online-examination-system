"""P7 成绩查询：学生查本人，教师按科目/班级/姓名（模糊）查询。"""

from flask import Blueprint, request
from flask_jwt_extended import get_jwt

from ..extensions import db
from ..models import Exam, Paper, Student, Submission
from ..utils.responses import ok
from ..utils.security import role_required

bp = Blueprint("scores", __name__)


def _record(s):
    paper = s.exam.paper if s.exam else None
    return {
        "submission_id": s.submission_id,
        "student_id": s.student_id,
        "student_name": s.student.student_name if s.student else None,
        "class": s.exam.class_name if s.exam else None,
        "course_name": paper.course.course_name if paper and paper.course else None,
        "paper_name": paper.paper_name if paper else None,
        "score": s.score,
        "total_score": paper.total_score if paper else None,
        "submit_time": s.submit_time.strftime("%Y-%m-%d %H:%M:%S") if s.submit_time else None,
    }


@bp.get("/scores/mine")
@role_required("student")
def my_scores():
    submissions = (
        Submission.query.filter_by(student_id=get_jwt().get("uid"))
        .order_by(Submission.submission_id.desc())
        .all()
    )
    return ok([_record(s) for s in submissions])


@bp.get("/scores")
@role_required("teacher")
def query_scores():
    teacher_id = get_jwt().get("uid")
    paper_ids = [p.paper_id for p in Paper.query.filter(Paper.teacher_id == teacher_id).all()]

    query = (
        Submission.query.join(Exam, Submission.exam_id == Exam.exam_id)
        .join(Paper, Exam.paper_id == Paper.paper_id)
        .join(Student, Submission.student_id == Student.student_id)
        .filter(Paper.paper_id.in_(paper_ids or [-1]))
    )
    args = request.args
    if args.get("course_id"):
        query = query.filter(Paper.course_id == args["course_id"])
    if args.get("class"):
        query = query.filter(Exam.class_name == args["class"])
    if args.get("exam_id"):
        query = query.filter(Exam.exam_id == int(args["exam_id"]))
    if args.get("student_name"):
        query = query.filter(Student.student_name.like(f"%{args['student_name']}%"))

    return ok([_record(s) for s in query.order_by(Submission.submission_id.desc()).all()])
