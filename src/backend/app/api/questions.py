"""P3 试题管理：仅授课教师维护本人所授课程的试题。"""

from flask import Blueprint, request
from flask_jwt_extended import get_jwt

from ..extensions import db
from ..models import Course, Question, Teacher
from ..utils.responses import fail, ok
from ..utils.security import role_required

bp = Blueprint("questions", __name__)

QUESTION_TYPES = ("选择", "填空")


def question_dict(q, with_answer=True):
    data = {
        "question_id": q.question_id,
        "course_id": q.course_id,
        "course_name": q.course.course_name if q.course else None,
        "chapter": q.chapter,
        "knowledge_point": q.knowledge_point,
        "question_type": q.question_type,
        "content": q.content,
        "options": q.options,
        "difficulty": q.difficulty,
        "teacher_id": q.teacher_id,
    }
    if with_answer:
        data["answer"] = q.answer
    return data


def teacher_course_ids(teacher_id):
    teacher = db.session.get(Teacher, teacher_id)
    return {c.course_id for c in teacher.courses} if teacher else set()


@bp.get("/questions")
@role_required("teacher")
def list_questions():
    teacher_id = get_jwt().get("uid")
    query = Question.query.filter(Question.teacher_id == teacher_id)

    args = request.args
    if args.get("course_id"):
        query = query.filter(Question.course_id == args["course_id"])
    if args.get("chapter"):
        query = query.filter(Question.chapter == args["chapter"])
    if args.get("knowledge_point"):
        query = query.filter(Question.knowledge_point == args["knowledge_point"])
    if args.get("question_type"):
        query = query.filter(Question.question_type == args["question_type"])
    if args.get("difficulty"):
        query = query.filter(Question.difficulty == int(args["difficulty"]))
    if args.get("keyword"):
        query = query.filter(Question.content.like(f"%{args['keyword']}%"))

    return ok([question_dict(q) for q in query.order_by(Question.question_id).all()])


@bp.post("/questions")
@role_required("teacher")
def create_question():
    teacher_id = get_jwt().get("uid")
    data = request.get_json(silent=True) or {}
    course_id = data.get("course_id")
    content = (data.get("content") or "").strip()
    answer = (data.get("answer") or "").strip()
    qtype = data.get("question_type")
    if not all([course_id, content, answer, qtype]):
        return fail("课程、题型、题干、正确答案均为必填项")
    if qtype not in QUESTION_TYPES:
        return fail("题型只能是选择或填空")
    if course_id not in teacher_course_ids(teacher_id):
        return fail("只能维护本人所授课程的试题", http_status=403)

    question = Question(
        course_id=course_id,
        chapter=data.get("chapter"),
        knowledge_point=data.get("knowledge_point"),
        question_type=qtype,
        content=content,
        options=data.get("options"),
        answer=answer,
        difficulty=int(data.get("difficulty") or 1),
        teacher_id=teacher_id,
    )
    db.session.add(question)
    db.session.commit()
    return ok({"question_id": question.question_id}, msg="试题添加成功")


@bp.put("/questions/<int:qid>")
@role_required("teacher")
def update_question(qid):
    teacher_id = get_jwt().get("uid")
    question = db.session.get(Question, qid)
    if not question:
        return fail("试题不存在", http_status=404)
    if question.teacher_id != teacher_id:
        return fail("只能维护本人录入的试题", http_status=403)

    data = request.get_json(silent=True) or {}
    for field in ("chapter", "knowledge_point", "options"):
        if field in data:
            setattr(question, field, data[field])
    if data.get("content"):
        question.content = data["content"]
    if data.get("answer"):
        question.answer = data["answer"]
    if data.get("question_type"):
        if data["question_type"] not in QUESTION_TYPES:
            return fail("题型只能是选择或填空")
        question.question_type = data["question_type"]
    if data.get("difficulty"):
        question.difficulty = int(data["difficulty"])
    db.session.commit()
    return ok(msg="试题已更新")


@bp.delete("/questions/<int:qid>")
@role_required("teacher")
def delete_question(qid):
    teacher_id = get_jwt().get("uid")
    question = db.session.get(Question, qid)
    if not question:
        return fail("试题不存在", http_status=404)
    if question.teacher_id != teacher_id:
        return fail("只能维护本人录入的试题", http_status=403)
    db.session.delete(question)
    db.session.commit()
    return ok(msg="试题已删除")
