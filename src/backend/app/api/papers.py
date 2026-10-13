"""P4 组卷管理（一）：试卷生成、查询、预览与调整，仅教师可用。"""

from flask import Blueprint, request
from flask_jwt_extended import get_jwt

from ..extensions import db
from ..models import Paper, PaperQuestion, Question
from ..utils.responses import fail, ok
from ..utils.security import role_required
from .questions import teacher_course_ids

bp = Blueprint("papers", __name__)


def _paper_brief(p):
    return {
        "paper_id": p.paper_id,
        "paper_name": p.paper_name,
        "course_id": p.course_id,
        "course_name": p.course.course_name if p.course else None,
        "total_score": p.total_score,
        "duration": p.duration,
        "question_count": len(p.items),
        "created_time": p.created_time.strftime("%Y-%m-%d %H:%M:%S") if p.created_time else None,
    }


def _paper_detail(p):
    data = _paper_brief(p)
    data["items"] = [
        {
            "seq": item.seq,
            "score": item.score,
            "question_id": item.question_id,
            "question_type": item.question.question_type,
            "content": item.question.content,
            "options": item.question.options,
            "answer": item.question.answer,
            "chapter": item.question.chapter,
            "knowledge_point": item.question.knowledge_point,
        }
        for item in p.items
    ]
    return data


def _save_items(paper, items):
    """用传入的题目清单重建试卷组成，返回错误信息或 None。"""
    paper.items.clear()
    db.session.flush()  # 先落库删除旧组成，避免同批删/插触发主键冲突
    total = 0
    for index, raw in enumerate(items, start=1):
        question = db.session.get(Question, raw.get("question_id"))
        if not question:
            return f"试题 {raw.get('question_id')} 不存在"
        if question.course_id != paper.course_id:
            return f"试题 {question.question_id} 不属于本试卷课程"
        score = int(raw.get("score") or 0)
        if score <= 0:
            return f"试题 {question.question_id} 的分值必须大于 0"
        paper.items.append(
            PaperQuestion(
                question_id=question.question_id,
                seq=int(raw.get("seq") or index),
                score=score,
            )
        )
        total += score
    paper.total_score = total
    return None


@bp.get("/papers")
@role_required("teacher")
def list_papers():
    teacher_id = get_jwt().get("uid")
    papers = (
        Paper.query.filter(Paper.teacher_id == teacher_id)
        .order_by(Paper.paper_id.desc())
        .all()
    )
    return ok([_paper_brief(p) for p in papers])


@bp.get("/papers/<int:pid>")
@role_required("teacher")
def get_paper(pid):
    paper = db.session.get(Paper, pid)
    if not paper:
        return fail("试卷不存在", http_status=404)
    if paper.teacher_id != get_jwt().get("uid"):
        return fail("只能查看本人组卷的试卷", http_status=403)
    return ok(_paper_detail(paper))


@bp.post("/papers")
@role_required("teacher")
def create_paper():
    teacher_id = get_jwt().get("uid")
    data = request.get_json(silent=True) or {}
    paper_name = (data.get("paper_name") or "").strip()
    course_id = data.get("course_id")
    duration = int(data.get("duration") or 0)
    if not all([paper_name, course_id]) or duration <= 0:
        return fail("试卷名称、课程、考试时长（>0）均为必填项")
    if course_id not in teacher_course_ids(teacher_id):
        return fail("只能对本人所授课程组卷", http_status=403)

    paper = Paper(
        paper_name=paper_name,
        course_id=course_id,
        duration=duration,
        teacher_id=teacher_id,
    )
    error = _save_items(paper, data.get("items") or [])
    if error:
        return fail(error)
    db.session.add(paper)
    db.session.commit()
    return ok({"paper_id": paper.paper_id}, msg="试卷生成成功")


@bp.put("/papers/<int:pid>")
@role_required("teacher")
def update_paper(pid):
    paper = db.session.get(Paper, pid)
    if not paper:
        return fail("试卷不存在", http_status=404)
    if paper.teacher_id != get_jwt().get("uid"):
        return fail("只能调整本人组卷的试卷", http_status=403)

    data = request.get_json(silent=True) or {}
    if data.get("paper_name"):
        paper.paper_name = data["paper_name"]
    if data.get("duration"):
        paper.duration = int(data["duration"])
    if "items" in data:
        error = _save_items(paper, data.get("items") or [])
        if error:
            return fail(error)
    db.session.commit()
    return ok(msg="试卷已更新")


@bp.delete("/papers/<int:pid>")
@role_required("teacher")
def delete_paper(pid):
    paper = db.session.get(Paper, pid)
    if not paper:
        return fail("试卷不存在", http_status=404)
    if paper.teacher_id != get_jwt().get("uid"):
        return fail("只能删除本人组卷的试卷", http_status=403)
    db.session.delete(paper)
    db.session.commit()
    return ok(msg="试卷已删除")
