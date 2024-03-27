from db import db
import users
from flask import render_template, request, session
from sqlalchemy.sql import text


def courses_page():
    user_courses = []
    if session.get("username", 0) != 0:
        user_courses = users.get_user_courses()
        user_courses = help_function(user_courses)
    result = db.session.execute(text("SELECT name, id FROM Courses WHERE visible = TRUE"))
    courses = result.fetchall()
    return render_template("courses.html", count=len(courses), courses=courses, is_teacher=users.is_teacher, user_courses=user_courses)


def help_function(t):
    f = []
    for i in range(len(t)):
        f.append(t[i][1])
    return f


def course_page(id):
    sql = text("SELECT content FROM TextContent WHERE course_id = :id")
    result = db.session.execute(sql, {"id":id})
    contents = result.fetchall()
    f_contents = []
    for content in contents:
        f_content = content[0].replace("\n", "<br>")
        f_content = f_content.replace("\r", "")
        f_contents.append(f_content)
    
    sql2 = text("SELECT id, question, answer FROM ChoiceProblems WHERE course_id = :course_id;")
    result = db.session.execute(sql2, {"course_id":id})
    questions = result.fetchall()
    
    sql3 = text("SELECT problem_id, content, choice_number FROM Choices WHERE course_id = :course_id ORDER BY problem_id;")
    result = db.session.execute(sql3, {"course_id":id})
    choices = result.fetchall()

    res = {}
    for i in range(len(choices)):
        if choices[i][0] in res:
            res[choices[i][0]].append((choices[i][1], choices[i][2]))
        else:
            res[choices[i][0]] = [(choices[i][1], choices[i][2])]

    return render_template("course.html", id=id, f_contents=f_contents, questions=questions, res=res, is_teacher=users.is_teacher(), choices=choices, solved_problems=solved_problems(id), course_problems=get_course_problems) 


def create_course():
    course_name = request.form["course_name"]
    username = session.get("username", 0)
    sql = text("SELECT id FROM Users WHERE username = :username")
    result = db.session.execute(sql, {"username":username})
    user_id = result.fetchone()[0]
    create_course_name()
    return render_template("newcourse.html", teacher_id=user_id, course_name=course_name)


def create_course_name():
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
    content = request.form["content"]
    add(content, id)
    

def add(content, course_id):
    sql = text("INSERT INTO TextContent (content, course_id) VALUES (:content, :course_id)")
    db.session.execute(sql, {"content":"\n" + "\n" + content, "course_id":course_id})
    db.session.commit()


def create_poll(id):
    question = request.form["question"]    
    answer = request.form["answer"]
    sql = text("INSERT INTO ChoiceProblems (question, course_id, answer, visible) VALUES (:question, :id, :answer, TRUE) RETURNING id")
    result = db.session.execute(sql, {"question":question, "id":id, "answer":answer})
    problem_id = result.fetchone()[0]

    sql = text("SELECT id_number FROM CourseProblems WHERE course_id = :course_id ORDER BY id_number")
    result = db.session.execute(sql, {"course_id":id})
    id_number = result.fetchall()
    if id_number == []:
        id_number = 1
    else:
        id_number = id_number[-1][0] + 1

    sql = text("INSERT INTO CourseProblems (id_number, problem_id, course_id) VALUES (:id_number, :problem_id, :course_id)")
    result = db.session.execute(sql, {"id_number":id_number, "problem_id":problem_id, "course_id":id})
    
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


def solved_problems(course_id):
    user_id = users.get_user_id()
    sql = text("SELECT DISTINCT problem_id, type FROM SolvedProblems WHERE course_id = :course_id " \
               "AND user_id = :user_id")
    result = db.session.execute(sql, {"course_id":course_id, "user_id":user_id})
    return result.fetchall()


def get_course_problems(course_id):
    sql = text("SELECT problem_id, id_number FROM CourseProblems WHERE course_id = :course_id")
    result = db.session.execute(sql, {"course_id":course_id})
    return result.fetchall()