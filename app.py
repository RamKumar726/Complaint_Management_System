from flask import Flask, render_template, request, session, flash, redirect, url_for, jsonify
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import os

from datetime import datetime
app = Flask(__name__)
# MySQL configuration
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_PORT'] = 3308  # Change this to the new port number
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "internal"

mysql = MySQL(app)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SECRET_KEY'] = "ram"

def fetchUser(userid):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE userid = %s", (userid,))
    user = cur.fetchone()
    cur.close()
    return user;

def fetchuserComplaints(userid):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM complaints WHERE userid = %s", (userid,))
    comp = cur.fetchall()
    cur.close()
    return comp;
def fetchuserDummyComplaints(userid):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM dummy WHERE userid = %s", (userid,))
    comp = cur.fetchall()
    cur.close()
    return comp;
def fetchAllDummyComplaints():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM dummy")
    comp = cur.fetchall()
    cur.close()
    return comp;

def fetchAllComplaints():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM complaints")
    comp = cur.fetchall()
    cur.close()
    return comp;
def fetchNoofComp(userid):
    cur = mysql.connection.cursor()
    cur.execute("SELECT no_of_comp FROM users WHERE userid = %s", (userid,))
    nocomp = cur.fetchall()
    cur.close()
    return nocomp;
def acceptComp():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM accept")
    accomp = cur.fetchall()
    cur.close()
    return accomp;
def rejectComp():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM reject")
    rejcomp = cur.fetchall()
    cur.close()
    return rejcomp;


@app.route("/")
def func():
    return render_template('login.html')

@app.route("/login")
def loginPage():
    return render_template('login.html')

@app.route("/signup")
def signupPage():
    return render_template('signup.html')



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        userid = request.form['userid']
        dept= request.form['dept']
        usertype= request.form['user_type']
        files = request.files.getlist('files[]')
        print(files)
        if(usertype=='technician'):
            roomno=""
            labno= request.form['lab_no']
        else:
            roomno=request.form['room_no']
            labno= ""
        password = request.form['password']
        cpassword = request.form['confirm-password']

        for file in files:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(file)
        # print(filename)

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE  userid= %s", (userid,))
        user = cur.fetchone();

        if user:
            return render_template("login.html")
        else:
            if password == cpassword:
                cur.execute("INSERT INTO users (name, userid, dept,usertype,room_no,lab_no,no_of_comp,password,profileurl) VALUES (%s, %s, %s,%s, %s, %s, %s,%s,%s)",
                            (name, userid, dept,usertype, roomno,labno,"0",password,filename))
               
                mysql.connection.commit()
                cur.close();

                flash('User successfully registered!', 'success')
                return render_template("login.html")
        #     else:
        #         return render_template("signup.html")
    return render_template('signup.html')




@app.route("/login_route",methods=["GET","POST"])
def login():
    if request.method == "POST":
        userid = request.form['userid']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE userid = %s", (userid,))
        user = cur.fetchone()
        usertype = user[4]
        db_pass = user[8]
        cur.close()
        if user and db_pass == password:
            # return url_for('dashboard')
            session['user'] = userid
            print(user)
            if user[4]=='admin':
                return redirect('/dashboard/' + usertype +'/'+userid +'/'+ 'all' +'/all' )
            else:
                return redirect('/dashboard/' + usertype +'/'+userid)

        else:
            return render_template('login.html');



@app.route("/dashboard/<role>/<userid>/<usertype>/<comptype>")
def dashboard(userid,role,usertype,comptype):
    user = fetchUser(userid)
    role = user[4]
    userComp = fetchuserComplaints(userid)
    allcomp = fetchAllComplaints()
    # if session['usertype'] is None and  session['comptype'] is None:
    session['usertype'] = "all"
    session['comptype'] = "all"
    print(userComp)
    if(role=='student'):
        return render_template('studentDashboard.html',user=user, userComp=userComp)
    elif(role=='teacher'):
        return render_template('FacultyDashboard.html',user=user,  userComp=userComp)
    elif (role=='technician'):
        return render_template('technitionDashboard.html',user=user,  userComp=userComp)
    elif (role=='admin'):
        return render_template('adminDashboard.html',user=user,  allcomp=allcomp ,fetchUser=fetchUser,usertype=usertype,comptype=comptype,userid=userid)
    



@app.route("/dashboard/<role>/<userid>")
def dashboardother(userid,role):
    user = fetchUser(userid)
    role = user[4]
    userComp = fetchuserDummyComplaints(userid)
    allcomp = fetchAllComplaints()
    print(userComp)
    if(role=='student'):
        return render_template('studentDashboard.html',user=user, userComp=userComp)
    elif(role=='teacher'):
        return render_template('FacultyDashboard.html',user=user,  userComp=userComp)
    elif (role=='technician'):
        return render_template('technitionDashboard.html',user=user,  userComp=userComp)




@app.route("/complaints" , methods=['GET' , 'POST'])
def complaints():
    if request.method == "POST":
        name = request.form['name']
        userid = request.form['userid']
        about = request.form['about']
        files = request.files.getlist('files[]')
        now = datetime.now()
        username = session['user']
        type = request.form['type']
        user = fetchUser(username)
        print(user)
        print(userid)
       
        for file in files:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(file)
        
        
        cur = mysql.connection.cursor()
        update_query = "UPDATE users set no_of_comp=no_of_comp+1 where userid=%s"
        cur.execute(update_query, (userid,))
        user = fetchUser(username)
        compid=str(user[2])+str(user[7])
        cur.execute("INSERT INTO complaints ( userid, fileurl,about,date,type,comp_id) VALUES (%s, %s, %s,%s,%s,%s)",
                            (userid, filename,about,now,type,compid,))
        cur.execute("INSERT INTO dummy ( userid, fileurl,about,date,type,comp_id) VALUES (%s, %s, %s,%s,%s,%s)",
                            (userid, filename,about,now,type,compid,))
        mysql.connection.commit()
        cur.close();


    return redirect(url_for('dashboardother' , userid=userid , role=user[4]  ))


@app.route('/dashboard/profile/<username>')
def profile(username):
    user = fetchUser(username)
    print(profile)
    return render_template('profile.html', user=user)




@app.route("/profile", methods=['GET', 'POST'])
def profileUpdate():
    if request.method == 'POST':
        name = request.form['name']
        userid = request.form['userid']
        dept= request.form['dept']
        usertype= request.form['user_type']
        files = request.files.getlist('files[]')
        print(files)
        if(usertype=='technician'):
            roomno=""
            labno= request.form['lab_no']
        else:
            roomno=request.form['room_no']
            labno= ""
        for file in files:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(file)
        cur = mysql.connection.cursor()
        cur.execute(" UPDATE users SET name = %s, dept = %s,usertype = %s,room_no = %s,lab_no = %s,profileurl = %sWHERE userid = %s", (name, dept, usertype, roomno, labno, filename, userid))
        mysql.connection.commit()
        cur.close();
    return redirect(url_for('profile', username=userid))



@app.route("/filteruser", methods=['GET', 'POST'])
def filteruser():
    if request.method == 'POST':
        usertype = request.form['user_type']
        # print("usertype",usertype)
        comptype = request.form['comp_type']
#         print("usertype",comptype)
        # print(url_for('dashboard'))
        session['usertype'] = usertype
        session['comptype'] = comptype

        user=fetchUser('admin')
        print("user",user)
    return redirect(url_for('dashboard' , userid='admin' , role='admin',usertype=usertype,comptype=comptype))

@app.route("/finduser", methods=['GET', 'POST'])
def finduser():
    if request.method == 'POST':
        userid = request.form['finduserid']
        print("usertype",userid)
        finduser = fetchUser(userid)
        user=fetchUser('admin')
        print("user",user)
        session['finduser'] = userid
        usertype =  session['usertype']
        comptype = session['comptype']
        print(session['comptype'] ,session['usertype'],"kdc vskdh" )

        print(usertype,comptype)
    return redirect(url_for('dashboard' , userid='admin' , role='admin',usertype= usertype,comptype=comptype ))



@app.route('/handle_operation', methods=['POST'])
def handle_operation():
    operation = request.form['operation']
    comp_id = request.form['huser']
    usertype =  session['usertype']
    comptype = session['comptype']
    cur = mysql.connection.cursor()
    now = datetime.now()

    if operation == 'accept':
        update_query = "UPDATE complaints set status=%s where comp_id=%s"
        cur.execute(update_query, ('accept',comp_id	,))
        update_query1 = "UPDATE dummy set status=%s where comp_id=%s"
        cur.execute(update_query1, ('accept',comp_id	,))
        mysql.connection.commit()
        cur.execute("SELECT * FROM complaints WHERE comp_id = %s", (comp_id,))
        accepted_complaint = cur.fetchone()
        cur.execute("DELETE FROM complaints WHERE comp_id = %s", (comp_id,))
        mysql.connection.commit()
        print(accepted_complaint[1])
        cur.execute("SELECT * FROM accept WHERE comp_id = %s", (comp_id,))
        compinaccept = cur.fetchone()
        if compinaccept:
            pass
        else:
            insert_query = "INSERT INTO accept ( userid, fileurl,about,date,type,status,comp_id)  VALUES (%s, %s,%s,%s,%s,%s,%s)"
            cur.execute(insert_query, (accepted_complaint[1], accepted_complaint[2],accepted_complaint[3],now,accepted_complaint[5],accepted_complaint[6],accepted_complaint[7]))
            mysql.connection.commit()

    elif operation == 'reject':
        update_query = "UPDATE complaints set status=%s where comp_id=%s"
        cur.execute(update_query, ('reject',comp_id	,))
        update_query1 = "UPDATE dummy set status=%s where comp_id=%s"
        cur.execute(update_query1, ('reject',comp_id	,))
        
        mysql.connection.commit()
        cur.execute("SELECT * FROM complaints WHERE comp_id = %s", (comp_id,))
        accepted_complaint = cur.fetchone()
        cur.execute("DELETE FROM complaints WHERE comp_id = %s", (comp_id,))
        mysql.connection.commit()
        print(accepted_complaint[1])
        cur.execute("SELECT * FROM reject WHERE comp_id = %s", (comp_id,))
        compinaccept = cur.fetchone()
        if compinaccept:
            pass
        else:
            insert_query = "INSERT INTO reject ( userid, fileurl,about,date,type,status,comp_id)  VALUES (%s, %s,%s,%s,%s,%s,%s)"
            cur.execute(insert_query, (accepted_complaint[1], accepted_complaint[2],accepted_complaint[3],now,accepted_complaint[5],accepted_complaint[6],accepted_complaint[7]))
            mysql.connection.commit()

        cur.close();
    
    return redirect(url_for('dashboard' , userid='admin' , role='admin',usertype= usertype,comptype=comptype ))

@app.route("/accept")
def accept():
    acceptcomp = acceptComp()
    return render_template('acceptedcomp.html', acceptcomp=acceptcomp , fetchUser=fetchUser)

@app.route("/reject")
def reject():
    rejectcomp = rejectComp()
    return render_template('rejectcomp.html',rejectcomp=rejectcomp,fetchUser=fetchUser)

@app.route("/fetchdatecomp" , methods=['GET' , 'POST'])
def fetchdatecomp():
    complaintsCount=0
    acceptCount=0
    rejectCount=0;
    if(request.method == 'POST'):
        pdate = request.form['predate']
        
        date_obj = datetime.strptime(pdate, "%Y-%m-%d").date()
        
        comps = fetchAllDummyComplaints()
        for comp in comps:
            if(comp[4]==date_obj):
                complaintsCount+=1
        accomps = acceptComp()
        for accomp in accomps:
            if(accomp[4] == date_obj):
                acceptCount+=1
        rejcomps = rejectComp()
        for rejcomp in rejcomps:
            if(rejcomp[4] == date_obj):
                rejectCount+=1
        # print(acceptCount,rejectCount,complaintsCount)


    return redirect(url_for("analysis" ,accept = acceptCount,reject=rejectCount,comp=complaintsCount ))
    
@app.route("/analysis/<accept>/<reject>/<comp>")
def analysis(accept,reject,comp):

    return render_template('analysis.html',accept=accept,reject=reject,comp=comp)




@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('finduser', None)
    session.pop('usertype', None)
    session.pop('comptype', None)
    return redirect('/login')





if __name__ == '__main__':
    app.run(debug=True)