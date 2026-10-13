"""P6 成绩统计与分析：仅教师可用。

- /stats/scores    按科目/班级统计平均分、最高/最低分、及格率、优秀率、分数段分布
- /stats/knowledge 按章节/知识点统计得分率与错误率
"""

from flask import Blueprint, request
from flask_jwt_extended import get_jwt

from ..extensions import db
from ..models import Exam, Paper, PaperQuestion, Submission, SubmissionDetail
from ..utils.responses import fail, ok
from ..utils.security import role_required

bp = Blueprint("stats", __name__)

PASS_RATIO = 0.6
EXCELLENT_RATIO = 0.85
BUCKETS = [(0, 60), (60, 70), (70, 80), (80, 90), (90, 101)]


def _query_submissions(teacher_id, exam_id=None, course_id=None, class_name=None):
    paper_ids = [p.paper_id for p in Paper.query.filter(Paper.teacher_id == teacher_id).all()]
    query = (
        Submission.query.join(Exam, Submission.exam_id == Exam.exam_id)
        .join(Paper, Exam.paper_id == Paper.paper_id)
        .filter(Paper.paper_id.in_(paper_ids or [-1]))
    )
    if exam_id:
        query = query.filter(Exam.exam_id == int(exam_id))
    if course_id:
        query = query.filter(Paper.course_id == course_id)
    if class_name:
        query = query.filter(Exam.class_name == class_name)
    return query.all()


@bp.get("/stats/scores")
@role_required("teacher")
def score_statistics():
    teacher_id = get_jwt().get("uid")
    submissions = _query_submissions(
        teacher_id,
        exam_id=request.args.get("exam_id"),
        course_id=request.args.get("course_id"),
        class_name=request.args.get("class"),
    )
    if not submissions:
        return fail("没有符合条件的成绩记录", http_status=404)

    ratios = []
    for s in submissions:
        total = s.exam.paper.total_score or 0
        ratios.append(s.score / total if total else 0)

    distribution = []
    for low, high in BUCKETS:
        upper = 100 if high > 100 else high - 1
        count = sum(1 for r in ratios if low <= r * 100 < high)
        distribution.append({"range": f"{low}-{upper}", "count": count})

    count = len(ratios)
    return ok(
        {
            "count": count,
            "average": round(sum(ratios) / count * 100, 2),
            "max": round(max(ratios) * 100, 2),
            "min": round(min(ratios) * 100, 2),
            "pass_rate": round(sum(1 for r in ratios if r >= PASS_RATIO) / count * 100, 2),
            "excellent_rate": round(
                sum(1 for r in ratios if r >= EXCELLENT_RATIO) / count * 100, 2
            ),
            "distribution": distribution,
        }
    )


@bp.get("/stats/knowledge")
@role_required("teacher")
def knowledge_analysis():
    teacher_id = get_jwt().get("uid")
    course_id = request.args.get("course_id")
    if not course_id:
        return fail("请指定课程")
    dimension = request.args.get("dimension", "chapter")

    submissions = _query_submissions(
        teacher_id, course_id=course_id, class_name=request.args.get("class")
    )
    if not submissions:
        return fail("没有符合条件的答卷记录", http_status=404)

    # (paper_id, question_id) -> 该题在试卷中的分值
    paper_ids = {s.exam.paper_id for s in submissions}
    score_map = {
        (item.paper_id, item.question_id): item.score
        for item in PaperQuestion.query.filter(PaperQuestion.paper_id.in_(paper_ids)).all()
    }

    details = SubmissionDetail.query.filter(
        SubmissionDetail.submission_id.in_([s.submission_id for s in submissions])
    ).all()

    stats = {}
    for detail in details:
        question = detail.question
        if question.course_id != course_id:
            continue
        key = (question.chapter if dimension == "chapter" else question.knowledge_point) or "未标注"
        full = score_map.get((detail.submission.exam.paper_id, question.question_id), 0)
        entry = stats.setdefault(key, {"full": 0, "obtained": 0, "wrong": 0, "total": 0})
        entry["full"] += full
        entry["obtained"] += detail.score_obtained
        entry["total"] += 1
        if detail.score_obtained < full:
            entry["wrong"] += 1

    items = [
        {
            "name": key,
            "score_rate": round(v["obtained"] / v["full"] * 100, 2) if v["full"] else 0,
            "error_rate": round(v["wrong"] / v["total"] * 100, 2) if v["total"] else 0,
        }
        for key, v in sorted(stats.items())
    ]
    return ok({"dimension": dimension, "items": items})
