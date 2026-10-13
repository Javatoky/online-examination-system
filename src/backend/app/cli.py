"""命令行工具：flask --app run.py init-db / seed。

- init-db：按 ORM 模型创建数据表（与 sql/01_schema.sql 一致）
- seed   ：写入演示数据（三类角色账号密码统一为 123456）
"""

from datetime import datetime, timedelta

import click
from werkzeug.security import generate_password_hash

from .extensions import db
from .models import (
    Admin,
    Course,
    Exam,
    Paper,
    PaperQuestion,
    Question,
    Student,
    Submission,
    SubmissionDetail,
    Teacher,
)

DEMO_PASSWORD = "123456"


def _hash(pw=DEMO_PASSWORD):
    return generate_password_hash(pw)


def _seed_data():
    if Admin.query.first():
        click.echo("检测到已有数据，跳过演示数据写入")
        return

    courses = [
        Course(course_id="CS100001", course_name="数据库原理"),
        Course(course_id="CS100002", course_name="数据结构"),
        Course(course_id="CS100003", course_name="计算机网络"),
    ]
    db.session.add_all(courses)

    db.session.add(Admin(username="admin", password=_hash()))

    t1 = Teacher(teacher_id="10000001", teacher_name="张伟", username="teacher1", password=_hash())
    t1.courses = [courses[0], courses[1]]
    t2 = Teacher(teacher_id="10000002", teacher_name="李娜", username="teacher2", password=_hash())
    t2.courses = [courses[2]]
    db.session.add_all([t1, t2])

    students = [
        ("202101010001", "王小明", "男", "计算机2101"),
        ("202101010002", "李小红", "女", "计算机2101"),
        ("202101010003", "王大力", "男", "计算机2101"),
        ("202101010004", "赵敏", "女", "计算机2101"),
        ("202101010005", "陈晨", "男", "计算机2101"),
        ("202101010006", "刘洋", "女", "计算机2102"),
    ]
    for sid, name, gender, class_name in students:
        db.session.add(
            Student(
                student_id=sid,
                student_name=name,
                gender=gender,
                major="计算机科学与技术",
                class_name=class_name,
                username=f"stu{sid[-4:]}",
                password=_hash(),
            )
        )

    questions = [
        ("选择", "数据库系统三级模式中，描述数据库全体数据逻辑结构的是？", "A.外模式|B.概念模式|C.内模式|D.存储模式", "B", 2, "第1章 绪论", "三级模式"),
        ("填空", "关系数据库中，元组的集合称为____。", None, "关系", 1, "第2章 关系数据库", "关系模型"),
        ("选择", "SQL 中用于查询数据的语句是？", "A.INSERT|B.UPDATE|C.SELECT|D.DELETE", "C", 1, "第3章 SQL", "SQL语句"),
        ("选择", "下列哪一项是关系主键必须具备的特性？", "A.可重复|B.唯一且非空|C.可以为空|D.可重复且可为空", "B", 3, "第2章 关系数据库", "键"),
        ("填空", "用于保证数据库中数据完整性的约束统称为____约束。", None, "完整性", 3, "第2章 关系数据库", "完整性"),
        ("选择", "事务的四个特性英文缩写是？", "A.BASE|B.ACID|C.CAP|D.SQL", "B", 2, "第4章 事务", "事务特性"),
        ("填空", "SQL 中创建数据表的语句是____。", None, "CREATE TABLE", 2, "第3章 SQL", "DDL"),
        ("选择", "视图对应数据库三级模式中的？", "A.外模式|B.概念模式|C.内模式|D.物理模式", "A", 4, "第1章 绪论", "三级模式"),
    ]
    created = []
    for qtype, content, options, answer, difficulty, chapter, kp in questions:
        question = Question(
            course_id="CS100001",
            chapter=chapter,
            knowledge_point=kp,
            question_type=qtype,
            content=content,
            options=options,
            answer=answer,
            difficulty=difficulty,
            teacher_id="10000001",
        )
        db.session.add(question)
        created.append(question)

    db.session.flush()

    paper = Paper(
        paper_name="数据库原理期中测验",
        course_id="CS100001",
        duration=60,
        teacher_id="10000001",
    )
    scores = [15, 10, 10, 15, 10, 10, 10, 20]
    paper.items = [
        PaperQuestion(question_id=q.question_id, seq=index, score=score)
        for index, (q, score) in enumerate(zip(created, scores), start=1)
    ]
    paper.total_score = sum(scores)
    db.session.add(paper)
    db.session.flush()

    now = datetime.now()
    db.session.add(
        Exam(
            paper_id=paper.paper_id,
            class_name="计算机2101",
            start_time=now - timedelta(minutes=5),
            end_time=now + timedelta(hours=2),
        )
    )
    db.session.commit()
    click.echo("演示数据写入完成（所有账号密码均为 123456）")


def register_cli(app):
    @app.cli.command("init-db")
    def init_db():
        """按模型创建数据表"""
        db.create_all()
        click.echo("数据表创建完成")

    @app.cli.command("seed")
    def seed():
        """写入演示数据"""
        _seed_data()
