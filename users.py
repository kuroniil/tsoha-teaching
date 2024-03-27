from db import db
import secrets
from flask import render_template, request, session
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash


def login(username, password):
    sql = text("SELECT id, password FROM Users WHERE username = :username")
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if not user:
        return False
    else:
        if check_password_hash(user[1], password):
            session["username"] = username
            session["csrf_token"] = secrets.token_hex(16)
            return True
        else:
            return False


def logout():
    del session["username"]


def register(username, password, title):
    hash_val = generate_password_hash(password)
    try:
        sql = text("INSERT INTO Users (username, password, title) VALUES (:username, :password, :title)")
        db.session.execute(sql, {"username":username, "password":hash_val, "title":title})
        db.session.commit()
        return True
    except:
        return False
    

def is_teacher():
    user = session.get("username", 0)
    sql = text("SELECT title FROM Users WHERE username = :username")
    result = db.session.execute(sql, {"username":user})
    if result.fetchone()[0] == "teacher":
        return True
    return False


def user_in_course(course_id):
    user_id = get_user_id()
    if user_id != False:
        sql = text("SELECT id FROM CourseStudents WHERE user_id = :user_id AND course_id = :course_id")
        result = db.session.execute(sql, {"user_id":user_id, "course_id":course_id})
        if result.fetchone() != None:
            return True
    return False


def add_user_to_course(course_id):
    user_id = get_user_id()
    sql = text("INSERT INTO CourseStudents (user_id, course_id) VALUES (:user_id, :course_id)")
    db.session.execute(sql, {"user_id":user_id, "course_id":course_id})
    db.session.commit()


def get_user_id():
    user = session.get("username", 0)
    if user != 0:
        sql = text("SELECT id FROM Users WHERE username = :username")
        result = db.session.execute(sql, {"username":user})
        return result.fetchone()[0]
    return False


def get_user_courses():
    user_id = get_user_id()
    sql = text("SELECT title FROM Users WHERE id = :user_id")
    result = db.session.execute(sql, {"user_id":user_id})
    title = result.fetchone()[0]    
    if title == "teacher":
        sql = text("SELECT name, id FROM Courses WHERE teacher_id = :user_id AND visible = TRUE")
        result = db.session.execute(sql, {"user_id":user_id})
        courses = result.fetchall()
        return courses
    if title == "student":
        sql = text("SELECT c.name, c.id FROM Courses c LEFT JOIN CourseStudents cs ON c.id = cs.course_id WHERE user_id = :user_id AND c.visible = TRUE")
        result = db.session.execute(sql, {"user_id":user_id})
        courses = result.fetchall()
        return courses
    return []