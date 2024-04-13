from db import db
import users
from flask import render_template, request, session
from sqlalchemy.sql import text


def courses_page():
    user_courses = []
    if session.get("username", 0) != 0:
        user_courses = users.get_user_courses()
        user_courses = help_function(user_courses, 1)
    result = db.session.execute(text("SELECT name, id FROM Courses WHERE visible = TRUE"))
    courses = result.fetchall()
    return render_template("courses.html", count=len(courses), courses=courses, is_teacher=users.is_teacher, user_courses=user_courses)


def help_function(t, index):
    f = []
    for i in range(len(t)):
        f.append(t[i][index])
    return f


def course_page(id):
    sql = text("SELECT content FROM TextContent WHERE course_id = :id AND visible = TRUE")
    result = db.session.execute(sql, {"id":id})
    contents = result.fetchall()
    
    sql = text("SELECT id, question, answer FROM ChoiceProblems WHERE course_id = :course_id AND visible = TRUE")
    result = db.session.execute(sql, {"course_id":id})
    questions = result.fetchall()
    
    sql = text("SELECT problem_id, content, choice_number FROM Choices WHERE course_id = :course_id ORDER BY problem_id;")
    result = db.session.execute(sql, {"course_id":id})
    choices = result.fetchall()

    sql = text("SELECT COUNT(id) FROM ChoiceProblems WHERE course_id = :course_id AND visible = TRUE")
    result = db.session.execute(sql, {"course_id":id})
    count = result.fetchone()[0]

    res = {}
    for i in range(len(choices)):
        if choices[i][0] in res:
            res[choices[i][0]].append((choices[i][1], choices[i][2]))
        else:
            res[choices[i][0]] = [(choices[i][1], choices[i][2])]

    return render_template("course.html", id=id, contents=contents, textproblems=get_textproblems(id), questions=questions, res=res, is_teacher=users.is_teacher(), choices=choices, solved_problems=solved_problems, course_problems=get_course_problems, count=count) 


def create_course():
    users.check_csrf()
    course_name = request.form["course_name"]
    username = session.get("username", 0)
    sql = text("SELECT id FROM Users WHERE username = :username")
    result = db.session.execute(sql, {"username":username})
    user_id = result.fetchone()[0]
    create_course_name()
    return render_template("newcourse.html", teacher_id=user_id, course_name=course_name)


def create_course_name():
    users.check_csrf()
    course_name = request.form["course_name"]
    username = session.get("username", 0)
    sql = text("SELECT id FROM Users WHERE username = :username")
    result = db.session.execute(sql, {"username":username})
    user_id = result.fetchone()[0]
    return course_name, user_id


# Checking if the course has multiple-choice problems
def is_editing(id):
    sql = text("SELECT id FROM ChoiceProblems WHERE course_id = :course_id")
    result = db.session.execute(sql, {"course_id":id})
    if result.fetchall() == []:
        return False
    return True


def add_textcontent(id):
    users.check_csrf()
    content = request.form["content"]
    add(content, id)
    

def add(content, course_id):
    sql = text("INSERT INTO TextContent (content, course_id, visible) VALUES (:content, :course_id, TRUE)")
    db.session.execute(sql, {"content":"\n" + "\n" + content, "course_id":course_id})
    db.session.commit()


def create_choiceproblem(id):
    users.check_csrf()
    question = request.form["question"]    
    answer = request.form["answer"]
    sql = text("INSERT INTO ChoiceProblems (question, course_id, answer, visible) VALUES (:question, :id, :answer, TRUE) RETURNING id")
    result = db.session.execute(sql, {"question":question, "id":id, "answer":answer})
    problem_id = result.fetchone()[0]
    
    sql = text("SELECT COALESCE((SELECT id_number FROM CourseProblems WHERE course_id = :course_id ORDER BY id_number DESC LIMIT 1), 1)")
    result = db.session.execute(sql, {"course_id":id})
    id_number = result.fetchone()[0]
    if id_number != 1:
        id_number += 1
    sql = text("INSERT INTO CourseProblems (problem_id, id_number, course_id, type) VALUES (:problem_id, :id_number, :course_id, 'choice')")
    result = db.session.execute(sql, {"course_id":id, "id_number":id_number, "problem_id":problem_id})
    
    db.session.commit()
    choices = request.form.getlist("choice")
    for count, choice in enumerate(choices, 1):    
        if choice != "":
            sql = text("INSERT INTO Choices (content, course_id, choice_number, problem_id) VALUES (:choice, :id, :count, :problem_id)")
            db.session.execute(sql, {"choice":choice, "id":id, "count":count, "problem_id":problem_id})
    
    db.session.commit()


def delete_course(id):
    sql = text("UPDATE Courses SET visible = FALSE WHERE id = :id")
    db.session.execute(sql, {"id":id})
    db.session.commit()
    return True


def choice_problem_check(course_id):
    users.check_csrf()
    user_id = users.get_user_id()
    for choice_id, ans in request.form.items():
        if choice_id != "id" and choice_id != "csrf_token":
            problem_id = choice_id.split(",")[0].strip("(")
            correct = choice_id.split(",")[1].strip(" )")
            if ans == correct:
                sql = text("INSERT INTO SolvedProblems (course_id, problem_id, user_id, type) VALUES (:course_id, :problem_id, :user_id, 'choice')")
                db.session.execute(sql, {"course_id":course_id, "problem_id":problem_id, "user_id":user_id})
                db.session.commit()

            else:
                #incorrect = choice_id.split(",")[0].strip(" (")
                print("väärin")


def solved_problems(course_id, user_id="", type=""):
    if type=="":
        if user_id == "":
            user_id = users.get_user_id()
        sql = text("SELECT DISTINCT problem_id, type FROM SolvedProblems WHERE course_id = :course_id " \
                "AND user_id = :user_id")
        result = db.session.execute(sql, {"course_id":course_id, "user_id":user_id})
        return result.fetchall()
    else:
        if user_id == "":
            user_id = users.get_user_id()
        sql = text("SELECT DISTINCT problem_id, type FROM SolvedProblems WHERE course_id = :course_id " \
                "AND user_id = :user_id AND type = :type")
        result = db.session.execute(sql, {"course_id":course_id, "user_id":user_id, "type":type})
        return result.fetchall()

def get_course_problems(course_id):
    sql = text("SELECT problem_id, type FROM CourseProblems WHERE course_id = :course_id")
    result = db.session.execute(sql, {"course_id":course_id})
    return result.fetchall()


def course_students(course_id):
    sql = text("SELECT user_id FROM CourseStudents WHERE course_id = :course_id")
    result = db.session.execute(sql, {"course_id":course_id})
    return result.fetchall()


def create_textproblem(course_id):
    users.check_csrf()
    sql = text("SELECT COALESCE((SELECT problem_id + 1 FROM TextProblems ORDER BY problem_id DESC LIMIT 1), 1)")
    result = db.session.execute(sql)
    problem_id = result.fetchone()[0]
    answer = request.form["textanswer"]
    question = request.form["textquestion"]
    sql = text("INSERT INTO TextProblems (course_id, problem_id, answer, visible, question) VALUES (:course_id, :problem_id, :answer, TRUE, :question)")
    db.session.execute(sql, {"course_id":course_id, "problem_id":problem_id, "answer":answer, "question":question})
    sql = text("SELECT COALESCE((SELECT id_number FROM CourseProblems WHERE course_id = :course_id ORDER BY id_number DESC LIMIT 1), 1)")
    result = db.session.execute(sql, {"course_id":course_id})
    id_number = result.fetchone()[0]
    if id_number != 1:
        id_number += 1
    sql = text("INSERT INTO CourseProblems (problem_id, id_number, course_id, type) VALUES (:problem_id, :id_number, :course_id, 'text')")
    result = db.session.execute(sql, {"course_id":course_id, "id_number":id_number, "problem_id":problem_id})
    db.session.commit()


def get_textproblems(course_id):
    sql = text("SELECT question, answer, problem_id FROM TextProblems WHERE course_id = :course_id AND visible = TRUE")
    result = db.session.execute(sql, {"course_id":course_id})
    return result.fetchall()


def textproblem_check(course_id):
    users.check_csrf()
    user_id = users.get_user_id()
    problem_id = request.form["problem_id"]
    user_answer = request.form["textanswer"]
    correct_answer = request.form["correctanswer"]
    if user_answer == correct_answer:
        sql = text("INSERT INTO SolvedProblems (course_id, problem_id, user_id, type) VALUES (:course_id, :problem_id, :user_id, 'text')")
        db.session.execute(sql, {"course_id":course_id, "problem_id":problem_id, "user_id":user_id})
        db.session.commit()
    else:
        print("väärin")


def get_textcontent(course_id):
    sql = text("SELECT id, content FROM TextContent WHERE course_id = :course_id AND visible = TRUE")
    result = db.session.execute(sql, {"course_id":course_id})
    return result.fetchall()


def get_choiceproblems(course_id):
    sql = text("SELECT id, question FROM ChoiceProblems WHERE course_id = :course_id AND visible = TRUE")
    result = db.session.execute(sql, {"course_id":course_id})
    return result.fetchall()