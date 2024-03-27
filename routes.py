from app import app
import users
import courses
from flask import redirect, render_template, request, session
from sqlalchemy.sql import text
from db import db


@app.route("/")
def index():
    if users.get_user_id():
        courses = users.get_user_courses()
        return render_template("index.html", courses=courses, count=len(courses))
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
    if users.is_teacher():
        return render_template("edit.html", id=id)
    return render_template("error.html", message="Ei oikeutta sivulle")


# Add course text materials
@app.route("/addcontent/<int:id>", methods=["POST"])
def add_textcontent(id):
    if courses.is_editing(id):
        courses.add_textcontent(id)
        return redirect(f"/edit/{id}")
    else:
        courses.add_textcontent(id)
        return render_template("newcoursepoll.html", id=id)


# Create a poll
@app.route("/create/<int:id>", methods=["POST"])
def create_poll(id):
    editing = False
    if courses.is_editing(id):
        editing = True
    courses.create_poll(id)
    if editing:
        return redirect(f"/edit/{id}")
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
    return redirect(f"/course/{id}")
    

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
    return render_template("stats.html")


@app.route("/stats/<int:id>")
def stats_by_course(id):
    return render_template("stats.html")