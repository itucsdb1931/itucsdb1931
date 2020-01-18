from flask import Flask, render_template, request, redirect, url_for, session
from passlib.hash import pbkdf2_sha256 as hasher
import psycopg2 as dbapi2
from configurations import db_url

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

INIT_STATEMENTS = [
]

with dbapi2.connect(db_url) as connection:
    cursor = connection.cursor()
    for statement in INIT_STATEMENTS:
        cursor.execute(statement)
    cursor.close()

def zero():
    session['count'] = session['count_hei'] = session['count_exam'] = session['blood_count'] = session['count_fam'] = \
    session['count_fam_del'] = \
        session["count_add_fam"] = session['count_medi'] = session['count_medi_del'] = session["count_add_medi"] = \
    session['count_disco'] = \
        session['count_disco_del'] = session["count_add_disco"] = session['count_med_dev'] = session[
        'count_med_dev_del'] = \
        session["count_add_med_dev"] = session['count_surge'] = session['count_surge_del'] = session[
        "count_add_surge"] = \
        session['count_aller'] = session['count_aller_del'] = session["count_add_aller"] = 0

@app.route("/")
def home():
    zero()
    return render_template('home.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["uname"]
        passw = request.form["passw"]
        tup = (uname,)
        state = "SELECT ID, ISADMIN, PASSWORD FROM USERS WHERE USERNAME=%s"
        with dbapi2.connect(db_url) as connection:
            cursor = connection.cursor()
            cursor.execute(state, tup)
            record = cursor.fetchone()
            if record != None:
                if record[1]: # admin
                    if hasher.verify(passw, record[2]):
                        return redirect(url_for("admin_page"))
                    else: ###################################### hatalı şifre
                        render_template("login.html")
                else: # doctor
                    if hasher.verify(passw, record[2]):
                        return render_template('doctor.html', display="none")
                    else:  ###################################### hatalı şifre
                        render_template("login.html")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        uname = request.form['uname']
        state = "SELECT ID FROM USERS WHERE USERNAME=%s"
        tup = (uname,)
        with dbapi2.connect(db_url) as connection:
            cursor = connection.cursor()
            cursor.execute(state, tup)
            record = cursor.fetchone()
            cursor.close()
        if record == None:
            mail = request.form['mail']
            passw = request.form['passw']
            hashed = hasher.hash(passw)
            state = "INSERT INTO USERS(USERNAME, PASSWORD, MAIL) VALUES(%s, %s, %s) "
            with dbapi2.connect(db_url) as connection:
                cursor = connection.cursor()
                cursor.execute(state, (uname, hashed, mail))
                cursor.close()
        else:
            return render_template("register.html")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/admin", methods=["GET", "POST"])
def admin_page():
    return render_template('admin.html', display="none")

@app.route("/doctor", methods=["GET", "POST"])
def doctor_page():
    return render_template('doctor.html', display="none")

@app.route("/add_patient")
def add_patient():
    zero()
    return render_template('add_patient.html')

@app.route("/del_patient/<int:patient_id>",  methods=['GET', 'POST'])
def del_patient(patient_id):
    state = "DELETE FROM PATIENT WHERE ID=%s"
    with dbapi2.connect(db_url) as connection:
        cursor = connection.cursor()
        cursor.execute(state, (patient_id,))
        cursor.close()
    return redirect(url_for('show_patients'))

@app.route("/del_user/<int:user_id>",  methods=['GET', 'POST'])
def del_user(user_id):
    state = "DELETE FROM USERS WHERE ID=%s"
    with dbapi2.connect(db_url) as connection:
        cursor = connection.cursor()
        cursor.execute(state, (user_id,))
        cursor.close()
    return redirect(url_for('show_users'))

@app.route("/ShowAllPatients/",  methods=['GET', 'POST'])
def show_patients():
    state = "SELECT ALL * FROM PATIENT"
    with dbapi2.connect(db_url) as connection:
        cursor = connection.cursor()
        cursor.execute(state)
        patients = cursor.fetchall()
        cursor.close()
    return render_template('admin.html', patients=patients, display="visible", sel = 'p')

@app.route("/ShowAllUsers/",  methods=['GET', 'POST'])
def show_users():
    state = "SELECT ALL * FROM USERS"
    with dbapi2.connect(db_url) as connection:
        cursor = connection.cursor()
        cursor.execute(state)
        users = cursor.fetchall()
        cursor.close()
    return render_template('admin.html', users=users, display="visible", sel='u')

@app.route("/Exit/",  methods=['GET', 'POST'])
def Exit():
    return render_template('home.html')

@app.route("/add_new_patient/", methods=['GET', 'POST'])
def add_new_patient():
    bloody = request.form["blood"]
    blood_new = None
    if (bloody != ""):
        if bloody == "AB+":
            blood_new = 1
        elif bloody == "AB-":
            blood_new = 2
        elif bloody == "0+":
            blood_new = 3
        elif bloody == "0-":
            blood_new = 4
        elif bloody == "A+":
            blood_new = 5
        elif bloody == "AB-":
            blood_new = 6
        elif bloody == "B+":
            blood_new = 7
        elif bloody == "B-":
            blood_new = 8
        else:
            blood_new = None
    statements = ["INSERT INTO PATIENT(NAME, AGE, WEIGHT, HEIGHT, LAST_EXAMINATION_DATE, "
                  "BLOOD_TYPE) VALUES(%s, %s, %s, %s, %s, %s) RETURNING ID"]
    with dbapi2.connect(db_url) as connection:
        cursor = connection.cursor()
        cursor.execute(statements[0], (request.form["name"], request.form["age"],
                                                                          request.form["weight"] or 0,
                                                                          request.form["height"] or 0, request.form["exam_date"] or None,
                                                                          blood_new))
        x = cursor.fetchone()
        cursor.close()

    statements = []
    formats = []
    if request.form["fam_dis"] != "":
        state = "INSERT INTO FAMILY_DISEASE(NAME, AREA, PERSON) VALUES(%s, %s, %s)"
        statements.append(state)
        formats.append((request.form["fam_dis"], request.form["fam_area"], x[0]))
    if int(request.form["fam_dis_num"]) != 0:
        for i in range(int(request.form["fam_dis_num"])):
            state = "INSERT INTO FAMILY_DISEASE(NAME, AREA, PERSON) VALUES(%s, %s, %s)"
            statements.append(state)
            formats.append((request.form["fam_dis" + str(i)], request.form["fam_area" + str(i)], x[0]))
    if request.form["disco"] != "":
        state = "INSERT INTO DISCOMFORT(NAME, AREA, LEVELS, PERSON) VALUES(%s, %s, %s, %s)"
        statements.append(state)
        formats.append((request.form["disco"], request.form["disco_area"], request.form["disco_level"], x[0]))
    if int(request.form["disco_number"]) != 0:
        for i in range(int(request.form["disco_number"])):
            state = "INSERT INTO DISCOMFORT(NAME, AREA, LEVELS, PERSON) VALUES(%s, %s, %s, %s)"
            statements.append(state)
            formats.append((request.form["disco" + str(i)], request.form["disco_area" + str(i)], request.form["disco_level" + str(i)], x[0]))
    if request.form["med_dev"] != "":
        state = "INSERT INTO MEDICAL_DEVICE(NAME, AREA, PERSON) VALUES(%s, %s, %s)"
        statements.append(state)
        formats.append((request.form["med_dev"], request.form["med_dev_area"], x[0]))
    if int(request.form["med_dev_number"]) != 0:
        for i in range(int(request.form["med_dev_number"])):
            state = "INSERT INTO MEDICAL_DEVICE(NAME, AREA, PERSON) VALUES(%s, %s, %s)"
            statements.append(state)
            formats.append((request.form["med_dev" + str(i)], request.form["med_dev_area" + str(i)], x[0]))
    if request.form["medi"] != "":
        state = "INSERT INTO MEDICATION(NAME, USAGES, PERSON) VALUES(%s, %s, %s)"
        statements.append(state)
        formats.append((request.form["medi"], request.form["medi_area"], x[0]))
    if int(request.form["medi_number"]) != 0:
        for i in range(int(request.form["medi_number"])):
            state = "INSERT INTO MEDICATION(NAME, USAGES, PERSON) VALUES(%s, %s, %s)"
            statements.append(state)
            formats.append((request.form["medi" + str(i)], request.form["medi_area" + str(i)], x[0]))
    if request.form["surge"] != "":
        state = "INSERT INTO SURGERY(NAME, AREA, LEVELS, PERSON) VALUES(%s, %s, %s, %s)"
        statements.append(state)
        formats.append((request.form["surge"], request.form["surge_area"], request.form["surge_level"], x[0]))
    if int(request.form["surge_number"]) != 0:
        for i in range(int(request.form["surge_number"])):
            state = "INSERT INTO SURGERY(NAME, AREA, LEVELS, PERSON) VALUES(%s, %s, %s, %s)"
            statements.append(state)
            formats.append((request.form["surge" + str(i)], request.form["surge_area" + str(i)], request.form["surge_level" + str(i)], x[0]))
    if request.form["allergy"] != "":
        state = "INSERT INTO ALLERGY(NAME, AREA, PERSON) VALUES(%s, %s, %s)"
        statements.append(state)
        formats.append((request.form["allergy"], request.form["allergy_area"], x[0]))
    if int(request.form["allergy_number"]) != 0:
        for i in range(int(request.form["allergy_number"])):
            state = "INSERT INTO ALLERGY(NAME, AREA, PERSON) VALUES(%s, %s, %s)"
            statements.append(state)
            formats.append((request.form["allergy" + str(i)], request.form["allergy_area" + str(i)], x[0]))

    with dbapi2.connect(db_url) as connection:
        cursor = connection.cursor()
        index = 0
        for state in statements:
            cursor.execute(state, formats[index])
            index+=1
        cursor.close()

    return render_template('doctor.html', name="", age="", weight="", height="",
                                examinate_date="", blood_type="", family_diseases="", discomforts="",
                                medications="", surgeries="", medical_device="", allergies="", uw='n', display="none",
                                display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                                display_fam_del="none")


@app.route('/check/',  methods=['GET', 'POST'])
def check():
    array = []
    zero()
    id = request.form["id"]
    session["id"] = id
    statements = ["SELECT WEIGHT FROM PATIENT WHERE ID=%s",
                 "SELECT HEIGHT FROM PATIENT WHERE ID=%s",
                 "SELECT NAME FROM PATIENT WHERE ID=%s",
                 "SELECT AGE FROM PATIENT WHERE ID=%s",
                 "SELECT NAME, AREA FROM ALLERGY WHERE PERSON=%s",
                 "SELECT LAST_EXAMINATION_DATE FROM PATIENT WHERE ID=%s",
                 "SELECT BLOOD_TYPE FROM PATIENT WHERE ID=%s",
                 "SELECT NAME, AREA, LEVELS FROM DISCOMFORT WHERE PERSON=%s",
                 "SELECT NAME, USAGES FROM MEDICATION WHERE PERSON=%s",
                 "SELECT NAME, AREA FROM MEDICAL_DEVICE WHERE PERSON=%s",
                 "SELECT NAME, AREA, LEVELS FROM SURGERY WHERE PERSON=%s",
                 "SELECT NAME, AREA FROM FAMILY_DISEASE WHERE PERSON=%s"
                 ]

    with dbapi2.connect(db_url) as connection:
        cursor = connection.cursor()
        tup = (id,)
        for state in statements:
            cursor.execute(state, tup)
            array.append(cursor.fetchall())
        cursor.close()
    blood = "-"
    if(array[6] != [] ):
        if (array[6][0][0] == 1):
            blood = "AB+"
        elif (array[6][0][0] == 2):
            blood = "AB-"
        elif (array[6][0][0] == 3):
            blood = "0+"
        elif (array[6][0][0] == 4):
            blood = "0-"
        elif (array[6][0][0] == 5):
            blood = "A+"
        elif (array[6][0][0] == 6):
            blood = "AB-"
        elif (array[6][0][0] == 7):
            blood = "B+"
        elif (array[6][0][0] == 8):
            blood = "B-"
        else:
            blood = ""
            ############################################
    session["blood"] = blood
    family_diseases = list()
    for i in array[11]:
        family_diseases.append(i[0] + " area: " + i[1])
    session["fam_dis"] = family_diseases
    discomp = list()
    for i in array[7]:
        discomp.append(i[0] + " area: " + i[1] + " level: " + str(i[2]))
    session["discomp"] = discomp
    medi = list()
    for i in array[8]:
        medi.append(i[0] + " usage: " + i[1])
    session["medi"] = medi
    surge = list()
    for i in array[10]:
        surge.append(i[0] + " area: " + i[1] + " level: " + str(i[2]))
    session["surge"] = surge
    med_dev = list()
    for i in array[9]:
        med_dev.append( i[0]  + " area: " + i[1])
    session["med_dev"] = med_dev
    aller = list()
    for i in array[4]:
        aller.append( i[0] + " area: " + i[1])
    session["aller"] = aller
        ###############################################################
    if (array[1] != [] and array[1][0][0] > 1):
        height = array[1][0][0]
        session["height"] = height
    else:
        height = "-"
        session["height"] = height

    if (array[0] != [] and array[0][0][0] > 1):
        weight = array[0][0][0]
        session["weight"] = weight
    else:
        weight = "-"
        session["weight"] = weight

    if (array[5] != []):
        exam = array[5][0][0]
        session["exam"] = exam
    else:
        exam = "no_date"
        session["exam"] = exam

    if (array[2] == []):
        return render_template('doctor.html', name="", age="", weight="", height="",
                           examinate_date="", blood_type="", family_diseases="", discomforts="", display_blood="none", upblood='n',
                           medications="", surgeries="", medical_device="", allergies="", uw='n', uphei='n', display_hei="none",
                           display="none", display_wei="none", display_fam="none", uf='n', display_date="none", up_exam_date="n", display_fam_ad="none",
                           display_fam_del="none", no_res="Patient didn't found!")
    else:
        session["name"] = array[2][0][0]
        session["age"] = array[3][0][0]
        return render_template('doctor.html', name=array[2][0][0], age=array[3][0][0], weight=weight, height=height,
                           examinate_date=exam, blood_type=blood, family_diseases=family_diseases, discomforts=discomp, updisco='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                           medications=medi, surgeries=surge, medical_device=med_dev, uphei='n', display_hei="none", display_blood="none", upblood='n',
                           allergies=aller, display_date="none", up_exam_date="n", uw='n', display="visible", display_wei="none", display_fam="none",
                           uf='n', display_fam_ad="none", display_fam_del="none", display_disco="none", display_disco_ad="none", display_disco_del="none", display_medi="none",
                           display_medi_ad="none", display_medi_del="none", upmedi='n', display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',)

@app.route("/Update_wei/", methods=['GET', 'POST'])
def update_wei():
    count = session["count"]
    zero()
    if (count == 0):
        session["count"] = 1
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], uw='y',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                display="visible", display_wei="visible", display_fam="none", uf='n', display_fam_ad="none",
                                display_fam_del="none", uphei='n', display_hei="none", display_blood="none", upblood='n',display_date="none", up_exam_date="n",
                                display_disco="none", display_disco_ad="none", display_disco_del="none", updisco='n', display_medi="none",
                               display_medi_ad="none", display_medi_del="none", upmedi='n', display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',)
    else :
        session["count"] = 0
        weight = request.form["new_weight"]
        if (weight != ""):
            id = session["id"]
            state = "UPDATE PATIENT SET WEIGHT=%s WHERE ID=%s"
            with dbapi2.connect(db_url) as connection:
                cursor = connection.cursor()
                cursor.execute(state, (weight, id))
                cursor.close()
            session["weight"] = weight
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], uw='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                                display_fam_del="none", uphei='n', display_hei="none", display_blood="none", upblood='n',display_date="none", up_exam_date="n",
                                display_disco="none", display_disco_ad="none", display_disco_del="none", updisco='n', display_medi="none",
                               display_medi_ad="none", display_medi_del="none", upmedi='n', display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',)

@app.route("/Update_hei/", methods=['GET', 'POST'])
def update_hei():
    count_hei = session["count_hei"]
    zero()
    if (count_hei == 0):
        session["count_hei"] = 1
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], uw='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                display="visible", uphei='y', display_hei="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                                display_fam_del="none", display_blood="none", upblood='n',display_date="none", up_exam_date="n",
                                display_disco="none", display_disco_ad="none", display_disco_del="none", updisco='n', display_medi="none",
                               display_medi_ad="none", display_medi_del="none", upmedi='n', display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',)
    else :
        session["count_hei"] = 0
        height = request.form["new_height"]
        if (height != ""):
            id = session["id"]
            state = "UPDATE PATIENT SET HEIGHT=%s WHERE ID=%s"
            with dbapi2.connect(db_url) as connection:
                cursor = connection.cursor()
                cursor.execute(state, (height, id))
                cursor.close()
            session["height"] = height
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], uw='n',
                                display="visible", uphei='n', display_hei="none", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                                display_fam_del="none", display_blood="none", upblood='n',display_date="none", up_exam_date="n",
                                display_disco="none", display_disco_ad="none", display_disco_del="none", updisco='n', display_medi="none",
                               display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none", upmed_dev='n',
                               display_medi_ad="none", display_medi_del="none", upmedi='n', display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',)


@app.route("/Update_date/", methods=['GET', 'POST'])
def update_date():
    count_date = session["count_exam"]
    zero()
    if (count_date == 0):
        session["count_exam"] = 1
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], uw='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                display="visible", display_date="visible", up_exam_date="y", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                                display_fam_del="none", uphei='n', display_hei="none", display_blood="none", upblood='n',
                                display_disco="none", display_disco_ad="none", display_disco_del="none", updisco='n',
                               display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n', display_surge="none",
                               display_surge_ad="none", display_surge_del="none", upsurge='n',)
    else :
        session["count_exam"] = 0
        exam = request.form["new_date"]
        if (exam != ""):
            id = session["id"]
            state = "UPDATE PATIENT SET LAST_EXAMINATION_DATE=%s WHERE ID=%s"
            with dbapi2.connect(db_url) as connection:
                cursor = connection.cursor()
                cursor.execute(state, (exam, id))
                cursor.close()
            session["exam"] = exam
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], uw='n',
                                display="visible", display_date="none", up_exam_date="n", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                                display_fam_del="none", uphei='n', display_hei="none", display_blood="none", upblood='n',
                                display_disco="none", display_disco_ad="none", display_disco_del="none", updisco='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n', display_surge="none",
                               display_surge_ad="none", display_surge_del="none", upsurge='n')


@app.route("/Update_blood/", methods=['GET', 'POST'])
def update_blood():
    blood_count = session["blood_count"]
    zero()
    if (blood_count == 0):
        session["blood_count"] = 1
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"],
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n', uw='n',
                                display="visible", display_blood="visible", upblood='y', display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                                display_fam_del="none", uphei='n', display_hei="none", display_date="none", up_exam_date="n",
                                display_disco="none", display_disco_ad="none", display_disco_del="none", updisco='n',
                               display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n', display_surge="none", display_surge_ad="none",
                               display_surge_del="none", upsurge='n')
    else :
        session["blood_count"] = 0
        bloody = request.form["new_blood"]
        blood_new = "null"
        if (bloody != ""):
            if bloody == "AB+":
                blood_new = 1
            elif bloody == "AB-":
                blood_new = 2
            elif bloody == "0+":
                blood_new = 3
            elif bloody == "0-":
                blood_new = 4
            elif bloody == "A+":
                blood_new = 5
            elif bloody == "AB-":
                blood_new = 6
            elif bloody == "B+":
                blood_new = 7
            elif bloody == "B-":
                blood_new = 8
            else:
                blood_new = "null"

        if (blood_new != "null"):
            id = session["id"]
            state = "UPDATE PATIENT SET BLOOD_TYPE=%s WHERE ID=%s"
            with dbapi2.connect(db_url) as connection:
                cursor = connection.cursor()
                cursor.execute(state, (blood_new, id))
                cursor.close()
            session["blood"] = bloody
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"],
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n', uw='n',
                                display="visible", display_blood="none", upblood='n', display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                                display_fam_del="none", uphei='n', display_hei="none", display_date="none", up_exam_date="n",
                                display_disco="none", display_disco_ad="none", display_disco_del="none", updisco='n', display_medi="none",
                               display_medi_ad="none", display_medi_del="none", upmedi='n', display_surge="none", display_surge_ad="none", display_surge_del="none",
                               upsurge='n')


@app.route("/Delete_fam/", methods=['GET', 'POST'])
def delete_fam():
    family_diseases = session["fam_dis"]
    delete_fam_count = session["count_fam_del"]
    zero()
    if (delete_fam_count == 0):
        if family_diseases == "-" or family_diseases == []:
            return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n',
                                    updisco='n', uw='n', display="visible", display_wei="none", display_fam="none",
                                   uf='n', display_fam_ad="none", display_blood="none", upblood='n',  uphei='n', display_hei="none", display_date="none", up_exam_date="n",
                                   display_fam_del="none", display_disco="none", display_disco_ad="none", display_disco_del="none",
                                   display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                                   upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                   display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n')
        else:
            session["count_fam_del"] = 1
            return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"],
                                   display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                                   upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n', uw='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                                   display_blood="none", upblood='n', uphei='n', display_hei="none",
                                   display_date="none", up_exam_date="n", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n',
                                display_fam_del="visible", display_disco="none", display_disco_ad="none", display_disco_del="none",
                                   display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n')
    else :
        session["count_fam_del"] = 0
        statement = []
        formats=[]
        for x in request.form.getlist("OK"):
            y = x.split(" area: ")
            statement.append("DELETE FROM FAMILY_DISEASE WHERE NAME=%s")
            formats.append((y[0],))
            family_diseases.remove(x)
        with dbapi2.connect(db_url) as connection:
            cursor = connection.cursor()
            index = 0
            for state in statement:
                cursor.execute(state, formats[index])
                index +=1
            cursor.close()
        session["fam_dis"] = family_diseases
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], display_blood="none",
                               upblood='n',  uphei='n', display_hei="none", display_date="none", up_exam_date="n",uw='n',
                               display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               display_disco="none", display_disco_ad="none", display_disco_del="none",
                               display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')


@app.route("/Update_fam/", methods=['GET', 'POST'])
def update_fam():
    count_fam = session["count_fam"]
    family_diseases = session["fam_dis"]
    zero()
    if (count_fam == 0):
        session["count_fam"] = 1
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"],
                               uw='n', display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                display="visible", display_wei="none", display_fam="visible", uf='y', display_fam_ad="none",
                                display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none", updisco='n',
                                up_exam_date="n", display_fam_del="none", display_disco="none", display_disco_ad="none", display_disco_del="none",
                                display_surge = "none", display_surge_ad = "none", display_surge_del = "none", upsurge = 'n',
                                display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')
    else :
        session["count_fam"] = 0
        i = 1
        statement = []
        formats = []
        if family_diseases == "-" or family_diseases == []:
            if (request.form["fam_dis"] != ""):
                family_diseases.append(request.form["fam_dis"] + " area: " + request.form["area"])
                ad = session["id"]
                statement.append("INSERT INTO FAMILY_DISEASE(NAME, AREA, PERSON) VALUES(%s, %s, %s)")
                formats.append((request.form["fam_dis"], request.form["area"], ad))
        else:
            for fam in family_diseases:
                x = fam.split(' area: ')
                new_name = request.form[str(i) + x[0]]
                new_area = request.form[str(i)+x[1]]
                if (new_name != "" or new_area != ""):
                    statement.append("UPDATE FAMILY_DISEASE SET NAME=%s, AREA=%s WHERE NAME=%s")
                    if new_name == "":
                        new_name = x[0]
                    if new_area == "":
                        new_area = x[1]
                    family_diseases[i - 1] = (new_name + " area: " + new_area)
                    formats.append((new_name, new_area, x[0]))
                i+=1
        with dbapi2.connect(db_url) as connection:
            cursor = connection.cursor()
            i = 0
            for state in statement:
                cursor.execute(state, formats[i])
                i+=1
            cursor.close()
        session["fam_dis"] = family_diseases
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], uw='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               up_exam_date="n", display_disco="none", display_disco_ad="none", display_disco_del="none",
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                                display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')


@app.route("/Add_fam/", methods=['GET', 'POST'])
def add_fam():
    count_add_fam = session["count_add_fam"]
    family_diseases = session["fam_dis"]
    zero()
    if count_add_fam == 0:
        session["count_add_fam"] = 1
        return render_template('doctor.html',name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], uw='n', display="visible", display_wei="none", display_fam="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               up_exam_date="n", display_disco="none", display_disco_ad="none", display_disco_del="none",
                               uf='n', display_fam_ad="visible", display_fam_del="none", updisco='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')
    else:
        session["count_add_fam"] = 0
        if request.form["new_fam"] != "":
            family_diseases.append(request.form["new_fam"] + " area: " + request.form["fam_area"])
            session["fam_dis"] = family_diseases
            id = session["id"]
            state = "INSERT INTO FAMILY_DISEASE(NAME, AREA, PERSON) VALUES(%s, %s, %s)"
            with dbapi2.connect(db_url) as connection:
                cursor = connection.cursor()
                cursor.execute(state, (request.form["new_fam"], request.form["fam_area"], id))
                cursor.close()
        session["fam_dis"] = family_diseases
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], uw='n', display="visible", display_wei="none", display_fam="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               up_exam_date="n", uf='n', display_fam_ad="none", display_fam_del="none",
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               display_disco="none", display_disco_ad="none", display_disco_del="none", updisco='n',
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')


@app.route("/Delete_disco/", methods=['GET', 'POST'])
def delete_disco():
    delete_disco_count = session["count_disco_del"]
    discomp = session["discomp"]
    zero()
    if (delete_disco_count == 0):
        if discomp == "-" or discomp == []:
            return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"],
                                   display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                                   upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                   uw='n', display="visible", display_wei="none", display_fam="none",
                                   display_disco="none", display_disco_ad="none", display_disco_del="none",
                                   display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                                   uf='n', display_fam_ad="none", display_blood="none", upblood='n',  uphei='n', display_hei="none", display_date="none", up_exam_date="n",
                                   display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')
        else:
            session["count_disco_del"] = 1
            return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], uw='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                                display_blood="none", upblood='n', uphei='n', display_hei="none",
                                   display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                                   upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                display_date="none", up_exam_date="n", display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                                display_disco="none", display_disco_ad="none", display_disco_del="visible",
                                display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')
    else :
        session["count_disco_del"] = 0
        statement = []
        formats = []
        for x in request.form.getlist("OK"):
            y = x.split(" area: ")
            statement.append("DELETE FROM DISCOMFORT WHERE NAME=%s")
            formats.append((y[0],))
            discomp.remove(x)
        with dbapi2.connect(db_url) as connection:
            cursor = connection.cursor()
            i=0
            for state in statement:
                cursor.execute(state, formats[i])
                i+=1
            cursor.close()
        session["discomp"] = discomp
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], uw='n',
                               display_disco="none", display_disco_ad="none", display_disco_del="none",
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')



@app.route("/Update_disco/", methods=['GET', 'POST'])
def update_disco():
    count_disco = session["count_disco"]
    discomp = session["discomp"]
    zero()
    if (count_disco == 0):
        session["count_disco"] = 1
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], uw='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               display_disco="visible", display_disco_ad="none", display_disco_del="none",
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               up_exam_date="n", display_fam_del="none", updisco='y', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')
    else :
        session["count_disco"] = 0
        i = 0
        statement = []
        formats = []
        if discomp == "-" or discomp == []:
            if (request.form["disco"] != ""):
                discomp.append(request.form["disco"] + " area: " + request.form["area"] + " level: " + request.form["level"])
                ad = session["id"]
                statement.append("INSERT INTO DISCOMFORT(NAME, AREA, LEVELS, PERSON) VALUES(%s, %s, %s, %s)")
                formats.append((request.form["disco"], request.form["area"], request.form["level"], ad))
        else:
            for disco in discomp:
                x = disco.split(' area: ')
                if (request.form[x[0]] != ""):
                    old_name = x[0]
                    y = x[1].split(' level: ')
                    discomp[i] = (request.form[x[0]] + " area: " + request.form[y[0]] + " level: " + request.form[y[1]])
                    statement.append("UPDATE DISCOMFORT SET NAME=%s, AREA=%s, LEVELS=%s WHERE NAME=%s")
                    formats.append((request.form[x[0]], request.form[y[0]], request.form[y[1]], old_name))
                i+=1

        with dbapi2.connect(db_url) as connection:
            cursor = connection.cursor()
            i=0
            for state in statement:
                cursor.execute(state, formats[i])
                i+=1
            cursor.close()
        session["discomp"] = discomp
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], uw='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               up_exam_date="n", display_disco="none", display_disco_ad="none", display_disco_del="none",
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                                display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')

@app.route("/Add_disco/", methods=['GET', 'POST'])
def add_disco():
    count_add_disco = session["count_add_disco"]
    discomp = session["discomp"]
    zero()
    if count_add_disco == 0:
        session["count_add_disco"] = 1
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], uw='n', display="visible", display_wei="none", display_fam="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               up_exam_date="n", display_disco="none", display_disco_ad="visible", display_disco_del="none",
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               uf='n', display_fam_ad="none", display_fam_del="none", updisco='n', display_medi="none",
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               display_medi_ad="none", display_medi_del="none", upmedi='n')
    else:
        session["count_add_disco"] = 0
        if request.form["new_disco"] != "":
            discomp.append(request.form["new_disco"] + " area: " + request.form["disco_area"] + " level: " + request.form["disco_level"])
            ad = session["id"]
            state = "INSERT INTO DISCOMFORT(NAME, AREA, LEVELS, PERSON) VALUES(%s, %s, %s, %s)"
            with dbapi2.connect(db_url) as connection:
                cursor = connection.cursor()
                cursor.execute(state, (request.form["new_disco"], request.form["disco_area"],  request.form["disco_level"], ad))
                cursor.close()
        session["discomp"] = discomp
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], uw='n', display="visible", display_wei="none", display_fam="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               display_disco="none", display_disco_ad="none", display_disco_del="none",
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               up_exam_date="n", uf='n', display_fam_ad="none", display_fam_del="none", updisco='n',
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')


@app.route("/Delete_medi/", methods=['GET', 'POST'])
def delete_medi():
    delete_medi_count = session["count_medi_del"]
    medi = session["medi"]
    zero()
    if (delete_medi_count == 0):
        if medi == "-" or medi == []:
            return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n',
                                    uw='n', display="visible", display_wei="none", display_fam="none",
                                   display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                                   display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                                   upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                   display_disco="none", display_disco_ad="none", display_disco_del="none",
                                   uf='n', display_fam_ad="none", display_blood="none", upblood='n',  uphei='n', display_hei="none", display_date="none", up_exam_date="n",
                                   display_fam_del="none", updisco='n')
        else:
            session["count_medi_del"] = 1
            return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"],
                                   display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                                   upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n', uw='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                                display_blood="none", upblood='n', uphei='n', display_hei="none",
                                display_date="none", up_exam_date="n", display_medi="none", display_medi_ad="none", display_medi_del="visible", upmedi='n',
                                display_disco="none", display_disco_ad="none", display_disco_del="none",
                                display_fam_del="none", updisco='n', display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n')
    else :
        session["count_medi_del"] = 0
        statement = []
        formats=[]
        for x in request.form.getlist("OK"):
            y = x.split(" usage: ")
            statement.append("DELETE FROM MEDICATION WHERE NAME=%s")
            formats.append((y[0],))
            medi.remove(x)
        with dbapi2.connect(db_url) as connection:
            cursor = connection.cursor()
            i=0
            for state in statement:
                cursor.execute(state, formats[i])
                i+=1
            cursor.close()
        session["medi"] = medi
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], display_blood="none", upblood='n',  uphei='n', display_hei="none", display_date="none", up_exam_date="n",
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n', uw='n',
                               display_disco="none", display_disco_ad="none", display_disco_del="none",
                               display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n',
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n')



@app.route("/Update_medi/", methods=['GET', 'POST'])
def update_medi():
    count_medi = session["count_medi"]
    medi = session["medi"]
    zero()
    if (count_medi == 0):
        session["count_medi"] = 1
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], uw='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               display_disco="none", display_disco_ad="none", display_disco_del="none",display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               up_exam_date="n", display_fam_del="none", updisco='n', display_medi="visible", display_medi_ad="none", display_medi_del="none", upmedi='y')
    else :
        session["count_medi"] = 0
        i = 0
        statement = []
        formats=[]
        if medi == "-" or medi == []:
            if (request.form["medi"] != ""):
                medi.append(request.form["medi"] + " usage: " + request.form["area"])
                ad = session["id"]
                statement.append("INSERT INTO MEDICATION(NAME, USAGES, PERSON) VALUES(%s, %s, %s)")
                formats.append((request.form["medi"], request.form["area"], ad))
        else:
            for med_in in medi:
                x = med_in.split(' usage: ')
                if (request.form[x[0]] != ""):
                    old_name = x[0]
                    medi[i] = (request.form[x[0]] + " usage: " + request.form[x[1]])
                    statement.append("UPDATE MEDICATION SET NAME=%s, USAGES=%s WHERE NAME=%s")
                    formats.append((request.form[x[0]], request.form[x[1]], old_name))
                i+=1

        with dbapi2.connect(db_url) as connection:
            cursor = connection.cursor()
            i=0
            for state in statement:
                cursor.execute(state, formats[i])
                i+=1
            cursor.close()
        session["medi"] = medi
        return render_template('doctor.html', nname=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"],
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n', uw='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               up_exam_date="n", display_disco="none", display_disco_ad="none", display_disco_del="none",
                                display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n',
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',)


@app.route("/Add_medi/", methods=['GET', 'POST'])
def add_medi():
    count_add_medi = session["count_add_medi"]
    medi = session["medi"]
    zero()
    if count_add_medi == 0:
        session["count_add_medi"] = 1
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"],
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                uw='n', display="visible", display_wei="none", display_fam="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               up_exam_date="n", display_disco="none", display_disco_ad="none", display_disco_del="none",
                               uf='n', display_fam_ad="none", display_fam_del="none", updisco='n', display_medi="none",
                               display_medi_ad="visible", display_medi_del="none", upmedi='n',
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',)
    else:
        session["count_add_medi"] = 0
        if request.form["new_medi"] != "":
            medi.append(request.form["new_medi"] + " usage: " + request.form["medi_area"])
            ad = session["id"]
            state = "INSERT INTO MEDICATION(NAME, USAGES, PERSON) VALUES(%s, %s, %s)"
            with dbapi2.connect(db_url) as connection:
                cursor = connection.cursor()
                cursor.execute(state, (request.form["new_medi"], request.form["medi_area"], ad))
                cursor.close()
        session["medi"] = medi
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"],
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n', uw='n', display="visible", display_wei="none", display_fam="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               display_disco="none", display_disco_ad="none", display_disco_del="none",
                               up_exam_date="n", uf='n', display_fam_ad="none", display_fam_del="none", updisco='n',
                               display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n',
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',)

@app.route("/Delete_surge/", methods=['GET', 'POST'])
def delete_surge():
    delete_surge_count = session["count_surge_del"]
    surge = session["surge"]
    zero()
    if (delete_surge_count == 0):
        if surge == "-" or surge == []:
            return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"],
                                   display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                                   upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n', uw='n', display="visible", display_wei="none", display_fam="none",
                                   display_disco="none", display_disco_ad="none", display_disco_del="none",
                                   display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                                   uf='n', display_fam_ad="none", display_blood="none", upblood='n',  uphei='n', display_hei="none", display_date="none", up_exam_date="n",
                                   display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')
        else:
            session["count_surge_del"] = 1
            return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"],
                                   display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                                   upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n', uw='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                                display_blood="none", upblood='n', uphei='n', display_hei="none",
                                display_date="none", up_exam_date="n", display_surge="none", display_surge_ad="none", display_surge_del="visible", upsurge='n',
                                display_disco="none", display_disco_ad="none", display_disco_del="none",
                                display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')
    else :
        session["count_surge_del"] = 0
        statement = []
        formats=[]
        for x in request.form.getlist("OK"):
            y = x.split(" area: ")
            statement.append("DELETE FROM SURGERY WHERE NAME=%s")
            formats.append((y[0],))
            surge.remove(x)
        with dbapi2.connect(db_url) as connection:
            cursor = connection.cursor()
            i=0
            for state in statement:
                cursor.execute(state, formats[i])
                i+=1
            cursor.close()
        session["surge"] = surge
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"],
                                display_blood="none", upblood='n',  uphei='n', display_hei="none", display_date="none", up_exam_date="n",
                                uw='n',display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               display_disco="none", display_disco_ad="none", display_disco_del="none", display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')

@app.route("/Update_surge/", methods=['GET', 'POST'])
def update_surge():
    count_surge = session["count_surge"]
    surge = session["surge"]
    zero()
    if (count_surge == 0):
        session["count_surge"] = 1
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], uw='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               display_disco="none", display_disco_ad="none", display_disco_del="none",
                               display_surge="visible", display_surge_ad="none", display_surge_del="none", upsurge='y',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               up_exam_date="n", display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')
    else :
        session["count_surge"] = 0
        i = 0
        statement = []
        formats = []
        if surge == "-" or surge == []:
            if (request.form["surge"] != ""):
                surge.append(request.form["surge"] + " area: " + request.form["area"] + " level: " + request.form["level"])
                ad = session["id"]
                statement.append("INSERT INTO SURGERY(NAME, AREA, LEVELS, PERSON) VALUES(%s, %s, %s, %s)")
                formats.append((request.form["surge"], request.form["area"], request.form["level"], ad))
        else:
            for sur in surge:
                x = sur.split(' area: ')
                if (request.form[x[0]] != ""):
                    old_name = x[0]
                    y = x[1].split(' level: ')
                    surge[i] = (request.form[x[0]] + " area: " + request.form[y[0]] + " level: " + request.form[y[1]])
                    statement.append("UPDATE SURGERY SET NAME=%s, AREA=%s, LEVELS=%s WHERE NAME=%s")
                    formats.append((request.form[x[0]], request.form[y[0]], request.form[y[1]], old_name))
                i+=1

        with dbapi2.connect(db_url) as connection:
            cursor = connection.cursor()
            i=0
            for state in statement:
                cursor.execute(state, formats[i])
                i+=1
            cursor.close()
        session["surge"] = surge
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], uw='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               up_exam_date="n", display_disco="none", display_disco_ad="none", display_disco_del="none",
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')

@app.route("/Add_surge/", methods=['GET', 'POST'])
def add_surge():
    count_add_surge = session["count_add_surge"]
    surge = session["surge"]
    zero()
    if count_add_surge == 0:
        session["count_add_surge"] = 1
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], uw='n', display="visible", display_wei="none", display_fam="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               up_exam_date="n", display_disco="none", display_disco_ad="none", display_disco_del="none",
                               uf='n', display_fam_ad="none", display_fam_del="none", updisco='n', display_medi="none",
                               display_medi_ad="none", display_medi_del="none", upmedi='n', display_surge="none",
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               display_surge_ad="visible", display_surge_del="none", upsurge='n',)
    else:
        session["count_add_surge"] = 0
        if request.form["new_surge"] != "":
            surge.append(request.form["new_surge"] + " area: " + request.form["surge_area"] + " level: " + request.form["surge_level"])
            ad = session["id"]
            state = "INSERT INTO SURGERY(NAME, AREA, LEVELS, PERSON) VALUES(%s, %s, %s, %s)"
            with dbapi2.connect(db_url) as connection:
                cursor = connection.cursor()
                cursor.execute(state, (request.form["new_surge"], request.form["surge_area"], request.form["surge_level"], ad))
                cursor.close()
        session["surge"] = surge
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], uw='n', display="visible", display_wei="none", display_fam="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               display_disco="none", display_disco_ad="none", display_disco_del="none",
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               up_exam_date="n", uf='n', display_fam_ad="none", display_fam_del="none", updisco='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')

@app.route("/Delete_med_dev/", methods=['GET', 'POST'])
def delete_med_dev():
    delete_med_dev_count = session["count_med_dev_del"]
    med_dev = session["med_dev"]
    zero()
    if (delete_med_dev_count == 0):
        if med_dev == "-" or med_dev == []:
            return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                   display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",  upmed_dev='n', uw='n', display="visible", display_wei="none", display_fam="none",
                                   display_disco="none", display_disco_ad="none", display_disco_del="none",
                                   display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                                   uf='n', display_fam_ad="none", display_blood="none", upblood='n',  uphei='n', display_hei="none", display_date="none", up_exam_date="n",
                                   display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')
        else:
            session["count_med_dev_del"] = 1
            return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], uw='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                                display_blood="none", upblood='n', uphei='n', display_hei="none", display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                display_date="none", up_exam_date="n", display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                                display_disco="none", display_disco_ad="none", display_disco_del="none",
                                display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="visible", upmed_dev='n',
                                display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')
    else :
        session["count_med_dev_del"] =  0
        statement = []
        formats=[]
        for x in request.form.getlist("OK"):
            y = x.split(" area: ")
            statement.append("DELETE FROM MEDICAL_DEVICE WHERE NAME=%s")
            formats.append((y[0],))
            med_dev.remove(x)
        with dbapi2.connect(db_url) as connection:
            cursor = connection.cursor()
            i=0
            for state in statement:
                cursor.execute(state, formats[i])
                i+=1
            cursor.close()
        session["med_dev"] = med_dev
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], display_blood="none", upblood='n',  uphei='n', display_hei="none", display_date="none", up_exam_date="n",
                                uw='n', display_disco="none", display_disco_ad="none", display_disco_del="none",
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')

@app.route("/Update_med_dev/", methods=['GET', 'POST'])
def update_med_dev():
    count_med_dev = session["count_med_dev"]
    med_dev = session["med_dev"]
    zero()
    if (count_med_dev == 0):
        session["count_med_dev"] = 1
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], uw='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               display_disco="none", display_disco_ad="none", display_disco_del="none",
                               display_med_dev="visible", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='y', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               up_exam_date="n", display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')
    else :
        session["count_med_dev"] = 0
        i = 0
        statement = []
        formats=[]
        if med_dev == "-" or med_dev == []:
            if (request.form["med_dev"] != ""):
                med_dev.append(request.form["med_dev"] + " area: " + request.form["area"])
                ad = session["id"]
                statement.append("INSERT INTO MEDICAL_DEVICE(NAME, AREA, PERSON) VALUES(%s, %s, %s)")
                formats.append((request.form["med_dev"], request.form["area"], ad))
        else:
            for med in med_dev:
                x = med.split(' area: ')
                if (request.form[x[0]] != ""):
                    old_name = x[0]
                    med_dev[i] = (request.form[x[0]] + " area: " + request.form[x[1]])
                    statement.append("UPDATE MEDICAL_DEVICE SET NAME=%s, AREA=%s WHERE NAME=%s")
                    formats.append((request.form[x[0]], request.form[x[1]], old_name))
                i+=1

        with dbapi2.connect(db_url) as connection:
            cursor = connection.cursor()
            i=0
            for state in statement:
                cursor.execute(state, formats[i])
                i+=1
            cursor.close()
        session["med_dev"] = med_dev
        return render_template('doctor.html',name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], uw='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               up_exam_date="n", display_disco="none", display_disco_ad="none", display_disco_del="none",
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                                display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')

count_add_med_dev = 0
@app.route("/Add_med_dev/", methods=['GET', 'POST'])
def add_med_dev():
    count_add_med_dev = session["count_add_med_dev"]
    med_dev = session["med_dev"]
    zero()
    if count_add_med_dev == 0:
        session["count_add_med_dev"] = 1
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], uw='n', display="visible", display_wei="none", display_fam="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               up_exam_date="n", display_disco="none", display_disco_ad="none", display_disco_del="none",
                               uf='n', display_fam_ad="none", display_fam_del="none", updisco='n', display_medi="none",
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               display_med_dev="none", display_med_dev_ad="visible", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               display_medi_ad="none", display_medi_del="none", upmedi='n')
    else:
        session["count_add_med_dev"] = 0
        if request.form["new_med_dev"] != "":
            med_dev.append(request.form["new_med_dev"] + " area: " + request.form["med_dev_area"])
            ad = session["id"]
            state = "INSERT INTO MEDICAL_DEVICE(NAME, AREA, PERSON) VALUES(%s, %s, %s)"
            with dbapi2.connect(db_url) as connection:
                cursor = connection.cursor()
                cursor.execute(state, (request.form["new_med_dev"], request.form["med_dev_area"], ad))
                cursor.close()
        session["med_dev"] = med_dev
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], uw='n', display="visible", display_wei="none", display_fam="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               display_disco="none", display_disco_ad="none", display_disco_del="none",
                               up_exam_date="n", uf='n', display_fam_ad="none", display_fam_del="none", updisco='n',
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')


@app.route("/Delete_aller/", methods=['GET', 'POST'])
def delete_aller():
    delete_aller_count = session["count_aller_del"]
    aller = session["aller"]
    zero()
    if (delete_aller_count == 0):
        if aller == "-" or aller == []:
            return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"],
                                   display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                                   upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n', uw='n', display="visible", display_wei="none", display_fam="none",
                                   display_disco="none", display_disco_ad="none", display_disco_del="none",
                                   display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                                   uf='n', display_fam_ad="none", display_blood="none", upblood='n',  uphei='n', display_hei="none", display_date="none", up_exam_date="n",
                                   display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')
        else:
            session["count_aller_del"] = 1
            return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"],
                                   display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                                   upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="visible", upaller='n', uw='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                                display_blood="none", upblood='n', uphei='n', display_hei="none",
                                display_date="none", up_exam_date="n", display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                                display_disco="none", display_disco_ad="none", display_disco_del="none",
                                display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')
    else :
        session["count_aller_del"] = 0
        statement = []
        formats=[]
        for x in request.form.getlist("OK"):
            y = x.split(" area: ")
            statement.append("DELETE FROM ALLERGY WHERE NAME=%s")
            formats.append((y[0],))
            aller.remove(x)
        with dbapi2.connect(db_url) as connection:
            cursor = connection.cursor()
            i=0
            for state in statement:
                cursor.execute(state, formats[i])
                i+=1
            cursor.close()
        session["aller"] = aller
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], display_blood="none", upblood='n',  uphei='n', display_hei="none", display_date="none", up_exam_date="n",
                                uw='n', display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               display_disco="none", display_disco_ad="none", display_disco_del="none", display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')

@app.route("/Update_aller/", methods=['GET', 'POST'])
def update_aller():
    count_aller = session["count_aller"]
    aller = session["aller"]
    zero()
    if (count_aller == 0):
        session["count_aller"] = 1
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], uw='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               display_disco="none", display_disco_ad="none", display_disco_del="none",
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="visible", display_aller_ad="none", display_aller_del="none", upaller='y',
                               up_exam_date="n", display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')
    else :
        session["count_aller"] = 0
        i = 0
        statement = []
        formats = []
        if aller == "-" or aller == []:
            if (request.form["aller"] != ""):
                aller.append(request.form["aller"] + " area: " + request.form["area"])
                ad = session["id"]
                statement.append("INSERT INTO ALLERGY(NAME, AREA, PERSON) VALUES(%s, %s, %s)")
                formats.append((request.form["aller"], request.form["area"], ad))
        else:
            for sur in aller:
                x = sur.split(' area: ')
                if (request.form[x[0]] != ""):
                    old_name = x[0]
                    aller[i] = (request.form[x[0]] + " area: " + request.form[x[1]])
                    statement.append("UPDATE ALLERGY SET NAME=%s, AREA=%s WHERE NAME=%s")
                    formats.append((request.form[x[0]], request.form[x[1]], old_name))
                i+=1

        with dbapi2.connect(db_url) as connection:
            cursor = connection.cursor()
            i=0
            for state in statement:
                cursor.execute(state, formats[i])
                i+=1
            cursor.close()
        session["aller"] = aller
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], uw='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               up_exam_date="n", display_disco="none", display_disco_ad="none", display_disco_del="none",
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')

@app.route("/Add_aller/", methods=['GET', 'POST'])
def add_aller():
    count_add_aller = session["count_add_aller"]
    aller = session["aller"]
    zero()
    if count_add_aller == 0:
        session["count_add_aller"] = 1
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], uw='n', display="visible", display_wei="none", display_fam="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               up_exam_date="n", display_disco="none", display_disco_ad="none", display_disco_del="none",
                               uf='n', display_fam_ad="none", display_fam_del="none", updisco='n', display_medi="none",
                               display_medi_ad="none", display_medi_del="none", upmedi='n', display_surge="none",
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="visible", display_aller_del="none", upaller='n',
                               display_surge_ad="none", display_surge_del="none", upsurge='n',)
    else:
        session["count_add_aller"] = 0
        if request.form["new_aller"] != "":
            aller.append(request.form["new_aller"] + " area: " + request.form["aller_area"])
            ad = session["id"]
            state = "INSERT INTO ALLERGY(NAME, AREA, PERSON) VALUES(%s, %s, %s)"
            with dbapi2.connect(db_url) as connection:
                cursor = connection.cursor()
                cursor.execute(state, (request.form["new_aller"], request.form["aller_area"], ad))
                cursor.close()
        session["aller"] = aller
        return render_template('doctor.html', name=session["name"], age=session["age"], weight=session["weight"], height=session["height"],
                                examinate_date=session["exam"], blood_type=session["blood"], family_diseases=session["fam_dis"], discomforts=session["discomp"],
                                medications=session["medi"], surgeries=session["surge"], medical_device=session["med_dev"], allergies=session["aller"], uw='n', display="visible", display_wei="none", display_fam="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               display_disco="none", display_disco_ad="none", display_disco_del="none",
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               up_exam_date="n", uf='n', display_fam_ad="none", display_fam_del="none", updisco='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')

if __name__ == "__main__":
    app.run()
