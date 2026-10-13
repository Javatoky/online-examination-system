"""数据模型，对应需求分析文档 2.4 节数据字典中的数据结构。

用户信息 D1 按角色拆分为 admin / teacher / student 三张表；
teacher 与 course 通过 teacher_course 关联（教授课程）。
"""

from datetime import datetime

from .extensions import db

# 教师—课程 多对多关联表（教师教授课程）
teacher_course = db.Table(
    "teacher_course",
    db.Column("teacher_id", db.String(8), db.ForeignKey("teacher.teacher_id"), primary_key=True),
    db.Column("course_id", db.String(8), db.ForeignKey("course.course_id"), primary_key=True),
)


class Admin(db.Model):
    __tablename__ = "admin"

    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)


class Student(db.Model):
    __tablename__ = "student"

    student_id = db.Column(db.String(12), primary_key=True)
    student_name = db.Column(db.String(30), nullable=False)
    gender = db.Column(db.String(2), nullable=False)
    major = db.Column(db.String(30))
    class_name = db.Column("class", db.String(30))
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)


class Teacher(db.Model):
    __tablename__ = "teacher"

    teacher_id = db.Column(db.String(8), primary_key=True)
    teacher_name = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)

    courses = db.relationship("Course", secondary=teacher_course, backref="teachers")


class Course(db.Model):
    __tablename__ = "course"

    course_id = db.Column(db.String(8), primary_key=True)
    course_name = db.Column(db.String(50), nullable=False)


class Question(db.Model):
    __tablename__ = "question"

    question_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.String(8), db.ForeignKey("course.course_id"), nullable=False)
    chapter = db.Column(db.String(30))
    knowledge_point = db.Column(db.String(50))
    question_type = db.Column(db.String(4), nullable=False)  # 选择 / 填空
    content = db.Column(db.String(500), nullable=False)
    options = db.Column(db.String(400))  # 仅选择题使用，形如 "A.xx|B.xx|C.xx|D.xx"
    answer = db.Column(db.String(200), nullable=False)
    difficulty = db.Column(db.Integer, nullable=False, default=1)  # 1~5
    teacher_id = db.Column(db.String(8), db.ForeignKey("teacher.teacher_id"), nullable=False)

    course = db.relationship("Course")


class Paper(db.Model):
    __tablename__ = "paper"

    paper_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    paper_name = db.Column(db.String(50), nullable=False)
    course_id = db.Column(db.String(8), db.ForeignKey("course.course_id"), nullable=False)
    total_score = db.Column(db.Integer, nullable=False, default=0)
    duration = db.Column(db.Integer, nullable=False)  # 分钟
    teacher_id = db.Column(db.String(8), db.ForeignKey("teacher.teacher_id"), nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.now)

    course = db.relationship("Course")
    items = db.relationship(
        "PaperQuestion",
        backref="paper",
        cascade="all, delete-orphan",
        order_by="PaperQuestion.seq",
    )


class PaperQuestion(db.Model):
    __tablename__ = "paper_question"

    paper_id = db.Column(db.Integer, db.ForeignKey("paper.paper_id"), primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("question.question_id"), primary_key=True)
    seq = db.Column(db.Integer, nullable=False)  # 题序
    score = db.Column(db.Integer, nullable=False)

    question = db.relationship("Question")


class Exam(db.Model):
    __tablename__ = "exam"

    exam_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    paper_id = db.Column(db.Integer, db.ForeignKey("paper.paper_id"), nullable=False)
    class_name = db.Column("class", db.String(30), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    paper = db.relationship("Paper")


class Submission(db.Model):
    __tablename__ = "submission"

    submission_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.String(12), db.ForeignKey("student.student_id"), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey("exam.exam_id"), nullable=False)
    score = db.Column(db.Integer, default=0)
    submit_time = db.Column(db.DateTime, default=datetime.now)

    student = db.relationship("Student")
    exam = db.relationship("Exam")
    details = db.relationship(
        "SubmissionDetail", backref="submission", cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.UniqueConstraint("student_id", "exam_id", name="uq_submission_student_exam"),
    )


class SubmissionDetail(db.Model):
    __tablename__ = "submission_detail"

    submission_id = db.Column(
        db.Integer, db.ForeignKey("submission.submission_id"), primary_key=True
    )
    question_id = db.Column(
        db.Integer, db.ForeignKey("question.question_id"), primary_key=True
    )
    student_answer = db.Column(db.String(200))
    score_obtained = db.Column(db.Integer, default=0)

    question = db.relationship("Question")
