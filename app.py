from flask import Flask , request , render_template ,flash, redirect , url_for , session 
import utils
import db
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import validators
import os

app = Flask(__name__)
connection = db.connect_to_database()
app.secret_key = "kjdfv@lkngb35165!.jfngv;kdlm"
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["50 per minute"])

@app.route("/welcome" , methods = ["POST" , "GET"])
def welcome():
    if request.method == 'POST':
        register_button = request.form['button']
        if register_button == "register_button" :
            return redirect(url_for("register"))   
        else :
            return redirect(url_for("login"))
    else:
        return render_template("welcome.html")    

@app.route("/home" , methods = ["POST" , "GET"])
def home():
    if not 'email' in session:
        flash("You are not allowed to do this action without logging in , please log in first" , "danger")
        return redirect(url_for("welcome"))  

    if request.method == 'POST':
        button = request.form['button']
        if button == "upload" :
            return redirect(url_for("uploadcourse"))   
        elif button == "users":
            return redirect(url_for("return_users"))
        elif button == "courses":
            return redirect(url_for("index"))
        elif button == "profile":
            return redirect(url_for("profile"))
        else :
            return redirect(url_for("logout"))
    else:
        if session["Student"] == 1:
            return render_template("home.html",role = "s")
        elif session["Instructor"] == 1 :
            return render_template("home.html",role = "i")
        else :    
            return render_template("home.html") 


@app.route("/users")
def return_users():
    if not 'email' in session:
        flash("You are not allowed to do this action without logging in , please log in first" , "danger")
        return redirect(url_for("welcome"))  

    if session['email'] == 'admin1@gmail.com': 
        return render_template("users.html", courses = db.get_all_users(connection))

    return redirect(url_for("welcome"))



@app.route("/")
def index():
    if 'email' in session:
        if session['Instructor']==1 :
            return render_template("index.html" , courses = db.get_user_courses(connection,session['user_id']))
        else:
            return render_template("index.html" , courses = db.get_all_courses(connection))

        
    return redirect(url_for("welcome"))

@app.route("/login" , methods = ["POST" , "GET"])
@limiter.limit("5 per minute")
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user_found = db.get_user(connection,email)

        if user_found:
            if utils.is_password_match(password,user_found[2]):
                session['email'] = user_found[3]
                session['user_id'] = user_found[0]
                session['Student']=user_found[5]
                session['Instructor']=user_found[6]
                return redirect(url_for("home"))

                    
            else:
                flash("Invalid email or password" , "danger")
                return render_template("login.html")
        
        else:
            flash("Invalid email or password" , "danger")
            return render_template("login.html")

    return render_template("login.html")            

@app.route("/register" , methods = ["POST" , "GET"])
@limiter.limit("5 per minute")
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        role = request.form['role']
        Student = False
        Instructor= False
        if role == 'Student' :
            Student = True 
        elif role == 'Instructor':
            Instructor=True

        if not utils.is_strong_password(password):
            flash("Please choose a stronger password" , "danger")
            return render_template("register.html")


        user_found = db.get_user(connection,email)

        if user_found:
            flash("User is already created" , "danger")
            return render_template("register.html")
        else:
            db.add_user(connection,username,password ,email,Student,Instructor)
            flash("User is created successfully" , "success")
            return redirect(url_for("login"))
    else:
        return render_template("register.html")

@app.route("/upload-course" , methods = ["POST" , "GET"])
@limiter.limit("5 per minute")
def uploadcourse():
    if not 'email' in session:
        flash("You are not allowed to do this action without logging in , please log in first" , "danger")
        return redirect(url_for("welcome"))     


    if request.method == "POST":
        courseImage = request.files['image']
        if not courseImage or courseImage.filename == '':
            flash("Image is required" , "danger")
            return render_template("upload-course.html")


        if not validators.allowed_file(courseImage.filename) or not validators.allowed_file_size(courseImage):
            flash("Invalid file is uploaded" , "danger")
            return render_template("upload-course.html")


        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        image_url = f"uploads/{courseImage.filename}"
        courseImage.save(os.path.join("static" , image_url))
        user_id = session['user_id']
        db.add_course(connection,user_id,title,description,price,image_url)
        return redirect(url_for("index"))

    else:
        if 'email' in session :
            return render_template("upload-course.html")     


@app.route("/course/<course_id>" , methods = ['POST' , 'GET'])
def getCourse(course_id):
    
    if not 'email' in session:
        flash("You are not allowed to do this action without logging in , please log in first" , "danger")
        return redirect(url_for("welcome"))
    else:
        course = db.get_course(connection,course_id)
        comments = db.get_comments_for_course(connection,course[0])
        if session['Instructor'] == 1:
            return render_template("course.html", course = course , comments =comments , user = session['user_id'], role = "i")

        return render_template("course.html", course = course , comments =comments , user = session['user_id'])




@app.route("/add-comment/<course_id>" , methods = [ "POST" ,'GET'])
def addComment(course_id):
    if not 'email' in session:
            flash("You are not allowed to do this action without logging in , please log in first" , "danger")
            return redirect(url_for("welcome"))

    if request.method == 'POST':
        text = request.form['comment']
        user_id = session['user_id']
        db.add_comment(connection,course_id,user_id,text)

    return redirect(url_for("getCourse" , course_id = course_id))


@app.route("/enroll_course/<course_id>" , methods=['POST' , 'GET'])
def enroll_course(course_id):
    
    if not 'email' in session:
        flash("You are not allowed to do this action without logging in , please log in first" , "danger")
        return redirect(url_for("welcome"))

    course_is_found = db.get_course(connection,course_id)
    course_already_bpought = db.cheak_history(connection,session['user_id'],course_id)
    
    if course_is_found :
        if course_already_bpought:
            flash(f"You are already enrolled this Course" , "danger")
            return redirect(url_for("getCourse" , course_id=course_id))
        
        db.update_balance(connection,course_id)
        db.add_to_history(connection,session['user_id'],course_id)
        flash(f"Congratulations You have enrolled the course !" , "success")
        return redirect(url_for("getCourse" , course_id=course_id))


@app.route("/MyCourses")
def MyCourses():
    if not 'email' in session:
            flash("You are not allowed to do this action without logging in , please log in first" , "danger")
            return redirect(url_for("welcome"))
            
    return render_template("index.html" , courses = db.get_courses_for_user(connection,session['user_id']))
    

@app.route("/profile" , methods=['POST','GET'])
def profile():
    if request.method == 'POST':
        button = request.form.get('button')
        if button == 'withdraw':
            db.update_user_balance(connection , session['email'])
            return redirect(url_for("withdraw"))
        elif button =='My_Courses':
            return redirect(url_for("MyCourses"))
    else:
        if 'email' in session:
            if session["Student"] == 1 :
                return render_template("profile.html" , user=db.get_user(connection,session['email']) , role = "s")
            elif session["Instructor"] == 1 :
                return render_template("profile.html" , user=db.get_user(connection,session['email']) , role = "i")
            else :
                return render_template("profile.html" , user=db.get_user(connection,session['email']))

        flash("You are not logged in" , "danger")
        return redirect(url_for("login"))

@app.route("/withdraw")
def withdraw():        
    if 'email' in session:
        return render_template("withdraw.html")
        

    flash("You are not logged in" , "danger")
    return redirect(url_for("login"))

                        


@app.route("/logout")
def logout():
    session.pop("email" , None)
    return redirect(url_for("welcome"))

if __name__ == "__main__":
    db.init_db(connection)
    db.seed_admin_user(connection)
    db.init_courses_table(connection)
    db.init_comments_table(connection)
    db.init_purchase_history(connection)

    app.run(debug=True) 