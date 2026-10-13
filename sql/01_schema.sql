-- ============================================================================
-- 在线考试系统 —— 建库建表脚本
-- 《数据库原理实践》课程设计
-- 与需求分析文档 2.4 节数据字典一致；MySQL 8.x / InnoDB / utf8mb4
-- 执行方式：mysql -u root -p < sql/01_schema.sql
-- ============================================================================

SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS online_exam
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_general_ci;

USE online_exam;

-- 按外键依赖倒序删除，便于重复执行
DROP TABLE IF EXISTS submission_detail;
DROP TABLE IF EXISTS submission;
DROP TABLE IF EXISTS exam;
DROP TABLE IF EXISTS paper_question;
DROP TABLE IF EXISTS paper;
DROP TABLE IF EXISTS question;
DROP TABLE IF EXISTS teacher_course;
DROP TABLE IF EXISTS teacher;
DROP TABLE IF EXISTS student;
DROP TABLE IF EXISTS admin;
DROP TABLE IF EXISTS course;

-- ----------------------------------------------------------------------------
-- 课程（数据结构：课程 = 课程号 + 课程名）
-- ----------------------------------------------------------------------------
CREATE TABLE course (
  course_id   CHAR(8)     NOT NULL COMMENT '课程号',
  course_name VARCHAR(50) NOT NULL COMMENT '课程名',
  PRIMARY KEY (course_id)
) ENGINE = InnoDB COMMENT = '课程';

-- ----------------------------------------------------------------------------
-- 管理员（D1 用户信息组成部分）
-- ----------------------------------------------------------------------------
CREATE TABLE admin (
  admin_id INT         NOT NULL AUTO_INCREMENT COMMENT '管理员编号',
  username VARCHAR(30) NOT NULL COMMENT '用户名',
  password VARCHAR(64) NOT NULL COMMENT '登录密码（散列值）',
  PRIMARY KEY (admin_id),
  UNIQUE KEY uk_admin_username (username)
) ENGINE = InnoDB COMMENT = '管理员';

-- ----------------------------------------------------------------------------
-- 学生（D1 用户信息组成部分）
-- ----------------------------------------------------------------------------
CREATE TABLE student (
  student_id   CHAR(12)    NOT NULL COMMENT '学号',
  student_name VARCHAR(30) NOT NULL COMMENT '姓名',
  gender       CHAR(2)     NOT NULL COMMENT '性别',
  major        VARCHAR(30) NULL COMMENT '专业',
  `class`      VARCHAR(30) NULL COMMENT '班级',
  username     VARCHAR(30) NOT NULL COMMENT '用户名',
  password     VARCHAR(64) NOT NULL COMMENT '登录密码（散列值）',
  PRIMARY KEY (student_id),
  UNIQUE KEY uk_student_username (username),
  KEY idx_student_class (`class`)
) ENGINE = InnoDB COMMENT = '学生';

-- ----------------------------------------------------------------------------
-- 教师（D1 用户信息组成部分）
-- ----------------------------------------------------------------------------
CREATE TABLE teacher (
  teacher_id   CHAR(8)     NOT NULL COMMENT '工号',
  teacher_name VARCHAR(30) NOT NULL COMMENT '姓名',
  username     VARCHAR(30) NOT NULL COMMENT '用户名',
  password     VARCHAR(64) NOT NULL COMMENT '登录密码（散列值）',
  PRIMARY KEY (teacher_id),
  UNIQUE KEY uk_teacher_username (username)
) ENGINE = InnoDB COMMENT = '教师';

-- ----------------------------------------------------------------------------
-- 教师教授课程（教师 = 工号 + 姓名 + 教授课程 + 用户名 + 登录密码）
-- ----------------------------------------------------------------------------
CREATE TABLE teacher_course (
  teacher_id CHAR(8) NOT NULL COMMENT '工号',
  course_id  CHAR(8) NOT NULL COMMENT '课程号',
  PRIMARY KEY (teacher_id, course_id),
  KEY idx_teacher_course_course (course_id),
  CONSTRAINT fk_teacher_course_teacher FOREIGN KEY (teacher_id)
    REFERENCES teacher (teacher_id),
  CONSTRAINT fk_teacher_course_course FOREIGN KEY (course_id)
    REFERENCES course (course_id)
) ENGINE = InnoDB COMMENT = '教师教授课程';

-- ----------------------------------------------------------------------------
-- 试题（D2 试题库）
-- ----------------------------------------------------------------------------
CREATE TABLE question (
  question_id     INT          NOT NULL AUTO_INCREMENT COMMENT '试题号',
  course_id       CHAR(8)      NOT NULL COMMENT '课程号',
  chapter         VARCHAR(30)  NULL COMMENT '章节',
  knowledge_point VARCHAR(50)  NULL COMMENT '知识点',
  question_type   CHAR(4)      NOT NULL COMMENT '题型（选择/填空）',
  content         VARCHAR(500) NOT NULL COMMENT '题干',
  options         VARCHAR(400) NULL COMMENT '选项（仅选择题）',
  answer          VARCHAR(200) NOT NULL COMMENT '正确答案',
  difficulty      INT          NOT NULL DEFAULT 1 COMMENT '难度系数 1~5',
  teacher_id      CHAR(8)      NOT NULL COMMENT '录入教师工号',
  PRIMARY KEY (question_id),
  KEY idx_question_course (course_id),
  KEY idx_question_query (course_id, chapter, knowledge_point, question_type, difficulty),
  CONSTRAINT fk_question_course FOREIGN KEY (course_id)
    REFERENCES course (course_id),
  CONSTRAINT fk_question_teacher FOREIGN KEY (teacher_id)
    REFERENCES teacher (teacher_id),
  CONSTRAINT chk_question_difficulty CHECK (difficulty BETWEEN 1 AND 5)
) ENGINE = InnoDB COMMENT = '试题';

-- ----------------------------------------------------------------------------
-- 试卷（D3 试卷库）
-- ----------------------------------------------------------------------------
CREATE TABLE paper (
  paper_id     INT         NOT NULL AUTO_INCREMENT COMMENT '试卷号',
  paper_name   VARCHAR(50) NOT NULL COMMENT '试卷名称',
  course_id    CHAR(8)     NOT NULL COMMENT '课程号',
  total_score  INT         NOT NULL DEFAULT 0 COMMENT '卷面总分',
  duration     INT         NOT NULL COMMENT '考试时长（分钟）',
  teacher_id   CHAR(8)     NOT NULL COMMENT '组卷教师工号',
  created_time DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '组卷时间',
  PRIMARY KEY (paper_id),
  KEY idx_paper_course (course_id),
  CONSTRAINT fk_paper_course FOREIGN KEY (course_id)
    REFERENCES course (course_id),
  CONSTRAINT fk_paper_teacher FOREIGN KEY (teacher_id)
    REFERENCES teacher (teacher_id)
) ENGINE = InnoDB COMMENT = '试卷';

-- ----------------------------------------------------------------------------
-- 试卷组成（试卷号 + 试题号 + 题序 + 分值）
-- ----------------------------------------------------------------------------
CREATE TABLE paper_question (
  paper_id    INT NOT NULL COMMENT '试卷号',
  question_id INT NOT NULL COMMENT '试题号',
  seq         INT NOT NULL COMMENT '题序',
  score       INT NOT NULL COMMENT '分值',
  PRIMARY KEY (paper_id, question_id),
  KEY idx_paper_question_question (question_id),
  CONSTRAINT fk_paper_question_paper FOREIGN KEY (paper_id)
    REFERENCES paper (paper_id) ON DELETE CASCADE,
  CONSTRAINT fk_paper_question_question FOREIGN KEY (question_id)
    REFERENCES question (question_id)
) ENGINE = InnoDB COMMENT = '试卷组成';

-- ----------------------------------------------------------------------------
-- 考试安排（D4 考试安排）
-- ----------------------------------------------------------------------------
CREATE TABLE exam (
  exam_id    INT         NOT NULL AUTO_INCREMENT COMMENT '考试编号',
  paper_id   INT         NOT NULL COMMENT '试卷号',
  `class`    VARCHAR(30) NOT NULL COMMENT '应考班级',
  start_time DATETIME    NOT NULL COMMENT '开始时间',
  end_time   DATETIME    NOT NULL COMMENT '结束时间',
  PRIMARY KEY (exam_id),
  KEY idx_exam_class (`class`),
  CONSTRAINT fk_exam_paper FOREIGN KEY (paper_id)
    REFERENCES paper (paper_id),
  CONSTRAINT chk_exam_time CHECK (end_time > start_time)
) ENGINE = InnoDB COMMENT = '考试安排';

-- ----------------------------------------------------------------------------
-- 答卷（D5 答卷与成绩）
-- ----------------------------------------------------------------------------
CREATE TABLE submission (
  submission_id INT      NOT NULL AUTO_INCREMENT COMMENT '答卷编号',
  student_id    CHAR(12) NOT NULL COMMENT '学号',
  exam_id       INT      NOT NULL COMMENT '考试编号',
  score         INT      NOT NULL DEFAULT 0 COMMENT '整卷得分',
  submit_time   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '提交时间',
  PRIMARY KEY (submission_id),
  UNIQUE KEY uk_submission_student_exam (student_id, exam_id),
  KEY idx_submission_exam (exam_id),
  CONSTRAINT fk_submission_student FOREIGN KEY (student_id)
    REFERENCES student (student_id),
  CONSTRAINT fk_submission_exam FOREIGN KEY (exam_id)
    REFERENCES exam (exam_id)
) ENGINE = InnoDB COMMENT = '答卷';

-- ----------------------------------------------------------------------------
-- 答题明细（答卷编号 + 试题号 + 学生答案 + 实际得分）
-- ----------------------------------------------------------------------------
CREATE TABLE submission_detail (
  submission_id  INT          NOT NULL COMMENT '答卷编号',
  question_id    INT          NOT NULL COMMENT '试题号',
  student_answer VARCHAR(200) NULL COMMENT '学生答案',
  score_obtained INT          NOT NULL DEFAULT 0 COMMENT '本题得分',
  PRIMARY KEY (submission_id, question_id),
  KEY idx_submission_detail_question (question_id),
  CONSTRAINT fk_submission_detail_submission FOREIGN KEY (submission_id)
    REFERENCES submission (submission_id) ON DELETE CASCADE,
  CONSTRAINT fk_submission_detail_question FOREIGN KEY (question_id)
    REFERENCES question (question_id)
) ENGINE = InnoDB COMMENT = '答题明细';
