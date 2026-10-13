"""P2 用户管理（学生/教师维护，仅管理员）与个人信息维护。

- 学生、教师信息的增删改查仅管理员可用；
- 任何角色均可维护自己的用户名与登录密码（个人信息维护模块）。
"""

from flask import Blueprint, request
from flask_jwt_extended import get_jwt, jwt_required
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db
from ..models import Admin, Course, Student, Teacher
from ..utils.responses import fail, ok
from ..utils.security import role_required

bp = Blueprint("users", __name__)

_ROLE_MODEL = {"admin": Admin, "teacher": Teacher, "student": Student}


def _username_taken(username, exclude_role=None, exclude_id=None):
    """用户名在三类账户表中全局唯一。"""
    for role, model in _ROLE_MODEL.items():
        user = model.query.filter_by(username=username).first()
        if not user:
            continue
        if role == exclude_role and str(getattr(user, f"{role}_id")) == str(exclude_id):
            continue
        return True
    return False


def student_dict(s):
    return {
        "student_id": s.student_id,
        "student_name": s.student_name,
        "gender": s.gender,
        "major": s.major,
        "class": s.class_name,
        "username": s.username,
    }


def teacher_dict(t):
    return {
        "teacher_id": t.teacher_id,
        "teacher_name": t.teacher_name,
        "username": t.username,
        "courses": [{"course_id": c.course_id, "course_name": c.course_name} for c in t.courses],
    }


def _load_courses(course_ids):
    if not course_ids:
        return []
    return Course.query.filter(Course.course_id.in_(course_ids)).all()


# --------------------------------------------------------------------------- #
# 课程
# --------------------------------------------------------------------------- #
@bp.get("/courses")
@role_required("admin", "teacher")
def list_courses():
    return ok([{"course_id": c.course_id, "course_name": c.course_name} for c in Course.query.all()])


@bp.post("/courses")
@role_required("admin")
def create_course():
    data = request.get_json(silent=True) or {}
    course_id = (data.get("course_id") or "").strip()
    course_name = (data.get("course_name") or "").strip()
    if not course_id or not course_name:
        return fail("课程号与课程名不能为空")
    if db.session.get(Course, course_id):
        return fail("课程号已存在")
    db.session.add(Course(course_id=course_id, course_name=course_name))
    db.session.commit()
    return ok(msg="课程创建成功")


# --------------------------------------------------------------------------- #
# 学生管理（仅管理员）
# --------------------------------------------------------------------------- #
@bp.get("/students")
@role_required("admin")
def list_students():
    keyword = (request.args.get("keyword") or "").strip()
    class_name = (request.args.get("class") or "").strip()
    query = Student.query
    if keyword:
        query = query.filter(Student.student_name.like(f"%{keyword}%"))
    if class_name:
        query = query.filter(Student.class_name == class_name)
    return ok([student_dict(s) for s in query.order_by(Student.student_id).all()])


@bp.post("/students")
@role_required("admin")
def create_student():
    data = request.get_json(silent=True) or {}
    sid = (data.get("student_id") or "").strip()
    name = (data.get("student_name") or "").strip()
    gender = (data.get("gender") or "").strip()
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not all([sid, name, gender, username, password]):
        return fail("学号、姓名、性别、用户名、密码均为必填项")
    if db.session.get(Student, sid):
        return fail("学号已存在")
    if _username_taken(username):
        return fail("用户名已被占用")
    db.session.add(
        Student(
            student_id=sid,
            student_name=name,
            gender=gender,
            major=data.get("major"),
            class_name=data.get("class"),
            username=username,
            password=generate_password_hash(password),
        )
    )
    db.session.commit()
    return ok(msg="学生添加成功")


@bp.put("/students/<sid>")
@role_required("admin")
def update_student(sid):
    student = db.session.get(Student, sid)
    if not student:
        return fail("学生不存在", http_status=404)
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    if username and username != student.username:
        if _username_taken(username, exclude_role="student", exclude_id=sid):
            return fail("用户名已被占用")
        student.username = username
    if data.get("student_name"):
        student.student_name = data["student_name"]
    if data.get("gender"):
        student.gender = data["gender"]
    if "major" in data:
        student.major = data["major"]
    if "class" in data:
        student.class_name = data["class"]
    if data.get("password"):
        student.password = generate_password_hash(data["password"])
    db.session.commit()
    return ok(msg="学生信息已更新")


@bp.delete("/students/<sid>")
@role_required("admin")
def delete_student(sid):
    student = db.session.get(Student, sid)
    if not student:
        return fail("学生不存在", http_status=404)
    db.session.delete(student)
    db.session.commit()
    return ok(msg="学生已删除")


# --------------------------------------------------------------------------- #
# 教师管理（仅管理员）
# --------------------------------------------------------------------------- #
@bp.get("/teachers")
@role_required("admin")
def list_teachers():
    keyword = (request.args.get("keyword") or "").strip()
    query = Teacher.query
    if keyword:
        query = query.filter(Teacher.teacher_name.like(f"%{keyword}%"))
    return ok([teacher_dict(t) for t in query.order_by(Teacher.teacher_id).all()])


@bp.post("/teachers")
@role_required("admin")
def create_teacher():
    data = request.get_json(silent=True) or {}
    tid = (data.get("teacher_id") or "").strip()
    name = (data.get("teacher_name") or "").strip()
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not all([tid, name, username, password]):
        return fail("工号、姓名、用户名、密码均为必填项")
    if db.session.get(Teacher, tid):
        return fail("工号已存在")
    if _username_taken(username):
        return fail("用户名已被占用")
    teacher = Teacher(
        teacher_id=tid,
        teacher_name=name,
        username=username,
        password=generate_password_hash(password),
    )
    teacher.courses = _load_courses(data.get("course_ids"))
    db.session.add(teacher)
    db.session.commit()
    return ok(msg="教师添加成功")


@bp.put("/teachers/<tid>")
@role_required("admin")
def update_teacher(tid):
    teacher = db.session.get(Teacher, tid)
    if not teacher:
        return fail("教师不存在", http_status=404)
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    if username and username != teacher.username:
        if _username_taken(username, exclude_role="teacher", exclude_id=tid):
            return fail("用户名已被占用")
        teacher.username = username
    if data.get("teacher_name"):
        teacher.teacher_name = data["teacher_name"]
    if data.get("password"):
        teacher.password = generate_password_hash(data["password"])
    if "course_ids" in data:
        teacher.courses = _load_courses(data.get("course_ids"))
    db.session.commit()
    return ok(msg="教师信息已更新")


@bp.delete("/teachers/<tid>")
@role_required("admin")
def delete_teacher(tid):
    teacher = db.session.get(Teacher, tid)
    if not teacher:
        return fail("教师不存在", http_status=404)
    db.session.delete(teacher)
    db.session.commit()
    return ok(msg="教师已删除")


# --------------------------------------------------------------------------- #
# 个人信息维护（所有角色）
# --------------------------------------------------------------------------- #
@bp.get("/me")
@jwt_required()
def get_profile():
    claims = get_jwt()
    return ok({"role": claims.get("role"), "username": claims.get("username"), "name": claims.get("name")})


@bp.put("/me")
@jwt_required()
def update_profile():
    claims = get_jwt()
    role, uid = claims.get("role"), claims.get("uid")
    model = _ROLE_MODEL.get(role)
    user = db.session.get(model, uid) if model else None
    if not user:
        return fail("用户不存在", http_status=404)

    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    if username and username != user.username:
        if _username_taken(username, exclude_role=role, exclude_id=uid):
            return fail("用户名已被占用")
        user.username = username

    new_password = data.get("new_password") or ""
    if new_password:
        if not check_password_hash(user.password, data.get("old_password") or ""):
            return fail("原密码不正确")
        user.password = generate_password_hash(new_password)

    db.session.commit()
    return ok(msg="个人信息已更新")
