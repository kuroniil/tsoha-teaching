from app import app
import users
import courses
from flask import redirect, render_template, request, session
from sqlalchemy.sql import text
from db import db


@app.route("/")
def index():
    if users.get_user_id():
        courses2 = users.get_user_courses()
        return render_template("index.html", courses2=courses2, count=len(courses2), is_teacher=users.is_teacher)
    return render_template("index.html")


# Everything related to coursepages:
@app.route("/courses")
def courses_page():
    return courses.courses_page()


# Create a new course
@app.route("/newcoursename", methods=["GET","POST"])
def new_course_name():
    if request.method == "GET":
        return render_template("namecourse.html")
    elif request.method == "POST":
        name_and_id = courses.create_course_name()
        print(name_and_id[0])
        course_name = name_and_id[0]
        teacher_id = name_and_id[1]
        try:
            sql = (text("INSERT INTO Courses (name, teacher_id, visible) VALUES (:name, :teacher_id, TRUE) RETURNING id"))
            result = db.session.execute(sql, {"name":course_name, "teacher_id":teacher_id})
            course_id = result.fetchone()[0]
            db.session.commit()
            return render_template("newcourse.html", course_id=course_id, course_name=course_name)
        except:
            return render_template("error.html", message="kurssin nimi on jo käytössä")


@app.route("/newcourse", methods=["GET","POST"])
def new_course():
    return courses.create_course()


@app.route("/course/<int:id>", methods=["GET", "POST"])
def course_page(id):
    if users.user_in_course(id):
        return courses.course_page(id)
    else:
        users.add_user_to_course(id)
        return courses.course_page(id)


@app.route("/confirmation/joincourse/<int:id>")
def confirm_joincourse(id):
    sql = text("SELECT name FROM Courses WHERE id = :id")
    result = db.session.execute(sql, {"id":id})
    course_name = result.fetchone()[0]
    return render_template("confirmation.html", message=f"Oletko varma, että haluat liittyä kurssille {course_name}", routeto=f"/course/{id}", routeback="/courses")


# Edit the course
@app.route("/edit/<int:id>")
def edit_course(id):
    sql = text("SELECT teacher_id FROM Courses WHERE id = :course_id")
    result = db.session.execute(sql, {"course_id":id})
    teacher_id = result.fetchone()[0]
    if teacher_id == users.get_user_id():
        return render_template("edit.html", id=id, textcontent=courses.get_textcontent(id))
    return render_template("error.html", message="Ei oikeutta sivulle")


@app.route("/addtocourse/<int:id>")
def add_content(id):
    return render_template("addcontent.html", id=id)


# Add course text materials
@app.route("/addcontent/<int:id>", methods=["POST"])
def add_textcontent(id):
    if courses.is_editing(id):
        courses.add_textcontent(id)
        return redirect(f"/addtocourse/{id}")
    else:
        courses.add_textcontent(id)
        return render_template("newchoiceproblem.html", id=id)


# Create a choiceproblem
@app.route("/create/<int:id>", methods=["POST"])
def create_choiceproblem(id):
    editing = False
    if courses.is_editing(id):
        editing = True
    courses.create_choiceproblem(id)
    if editing:
        return redirect(f"/addtocourse/{id}")
    return render_template("newtextproblem.html", id=id)


# Create a text problem
@app.route("/addtextproblem/<int:id>", methods=["POST"])
def add_text_problem(id):
    editing = True
    if courses.get_textproblems(id) == []:
        editing = False
    courses.create_textproblem(id)
    if editing:
        return redirect(f"/addtocourse/{id}")
    return redirect(f"/course/{id}")


# Delete the course
@app.route("/deletecourseconfirm/<int:id>")
def delete_course_confirmation(id):
    return render_template("confirmation.html", message="Oletko varma, että haluat poistaa kurssin", routeto=f"/deletecourse/{id}", routeback=f"/edit/{id}")


@app.route("/deletecourse/<int:id>")
def delete_course(id):
    if courses.delete_course(id):
        return redirect("/courses")
    else:
        return render_template("error.html", message="Kurssin poistaminen ei onnistunut")


# Check answers
@app.route("/answer/<int:id>", methods=["POST"])
def problem_check(id):
    courses.choice_problem_check(id)
    return redirect(f"/course/{id}#check")
    

# login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return redirect("/")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.login(username, password):
            return redirect("/")
        else:
            return render_template("error.html", message="Virheellinen käyttäjänimi tai salasana")
        

# logout
@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")


# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        title = request.form["title"]
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if password1 == password2:
            if 1 < len(username) < 11:
                if users.register(username, password1, title):
                    users.login(username, password1)
                    return redirect("/")
                else:
                    return render_template("error.html", message="Käyttäjätunnus on jo käytössä")
            else:
                return render_template("error.html", message="Käyttäjätunnuksen tulee olle vähintään kaksi ja enintään 10 merkkiä.")
        elif password1 != password2:
            return render_template("error.html", message="Anna sama salasana kaksi kertaa")
        

# statistics
@app.route("/stats")
def stats():
    return render_template("stats.html", len=len, textproblems=courses.get_textproblems, choiceproblems=courses.get_choiceproblems, solved_problems=courses.solved_problems, courses=users.get_user_courses, problems=courses.get_course_problems, help_function=courses.help_function, is_teacher=users.is_teacher)


@app.route("/stats/<int:id>")
def stats_by_course(id):
    sql = text("SELECT name, teacher_id from Courses WHERE id = :course_id AND visible = TRUE")
    result = db.session.execute(sql, {"course_id":id})
    product = result.fetchone()
    course_name = product[0]
    teacher_id = product[1]
    user_id = users.get_user_id()
    if users.is_teacher():
        if user_id == teacher_id:
            return render_template("coursestats.html", len=len, get_username=users.get_username, help_function=courses.help_function, solved_problems=courses.solved_problems, course_id=id, course_problems=courses.get_course_problems(id), course_students=courses.course_students(id), course_name=course_name, get_user_id=users.get_user_id, choiceproblems=courses.get_choiceproblems, textproblems=courses.get_textproblems)
        else:
            return render_template("error.html", message="Ei oikeutta sivulle")
    else:
        sql = text("SELECT user_id FROM CourseStudents WHERE course_id = :course_id")
        result = db.session.execute(sql, {"course_id":id})
        students = result.fetchall()
        studentlist = courses.help_function(students, 0)
        if user_id in studentlist:
            return render_template("stats.html", len=len, solved_problems=courses.solved_problems, courses=users.get_user_courses, problems=courses.get_course_problems, help_function=courses.help_function, is_teacher=users.is_teacher, id=id, course_name=course_name, choiceproblems=courses.get_choiceproblems, textproblems=courses.get_textproblems)
        else:
            return render_template("error.html", message="Et ole kurssilla tai et ole kirjautunut sisään")
        

@app.route("/textproblemcheck/<int:id>", methods=["POST"])
def textproblem_check(id):
    users.check_csrf()
    courses.textproblem_check(id)
    problem_id = request.form["problem_id"]
    return redirect(f"/course/{id}#{problem_id}")


@app.route("/edittext/<int:id>", methods=["POST"])
def textcontent_edit(id):
    users.check_csrf()
    oldcontent = courses.get_textcontent(id)
    ids = courses.help_function(oldcontent, 0)
    for c_id in ids:
        sql = text("UPDATE TextContent SET visible = FALSE WHERE id = :id")
        db.session.execute(sql, {"id":c_id})
    db.session.commit()
    newcontent = request.form["textcontent"]
    sql = text("INSERT INTO TextContent (content, course_id, visible) VALUES (:content, :course_id, TRUE)")
    db.session.execute(sql, {"content":newcontent, "course_id":id})
    db.session.commit()
    return redirect(f"/course/{id}")


@app.route("/removeproblems/<int:id>", methods=["GET", "POST"])
def remove_courseproblems(id):
    if request.method == "GET":
        return render_template("removeproblems.html", id=id, choiceproblems=courses.get_choiceproblems(id), textproblems=courses.get_textproblems(id), count=len(courses.get_choiceproblems(id)))
    if request.method == "POST":
        type = request.form["problemtype"]
        problem_id = request.form["pid"]
        print(problem_id)
        print(type)
        if type == "choice":
            sql = text("UPDATE ChoiceProblems SET visible = FALSE WHERE id = :id")
            db.session.execute(sql, {"id":problem_id})
            db.session.commit()
        elif type == "text":
            sql = text("UPDATE TextProblems SET visible = FALSE WHERE problem_id = :problem_id")
            db.session.execute(sql, {"problem_id":problem_id})
            db.session.commit()
    return redirect(f"/edit/{id}")