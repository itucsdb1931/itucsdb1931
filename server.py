from flask import Flask, render_template, Response, request, redirect, url_for
import psycopg2 as dbapi2
from configurations import db_url

app = Flask(__name__)

DNS = {'user' : "postgres",
      'password' : "123",
      'host' : "localhost",
      'port' : "5432",
      'database' : "dummy"}

count = 0
blood = id = ""
age = name = weight = height = "-"
aller = med_dev = surge = medi = discomp = family_diseases = list()
exam = "no_date"

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["uname"]
        passw = request.form["passw"]

        state = "SELECT ID, ISADMIN FROM USERS WHERE USERNAME='{}' AND PASSWORD='{}'".format(uname,passw)
        with dbapi2.connect(db_url) as connection:
            cursor = connection.cursor()
            cursor.execute(state)
            record = cursor.fetchone()
            if record != None:
                if record[1]: # admin
                    return redirect(url_for("admin_page"))
                else:
                    return redirect(url_for("doctor_page"))
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        uname = request.form['uname']
        mail = request.form['mail']
        passw = request.form['passw']

        state = "INSERT INTO USERS(USERNAME, PASSWORD, MAIL) VALUES('{}','{}','{}') ".format(uname, passw, mail)
        with dbapi2.connect(db_url) as connection:
            cursor = connection.cursor()
            cursor.execute(state)

        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/admin", methods=["GET", "POST"])
def admin_page():
    statement = "SELECT ALL * FROM PATIENT"
    with dbapi2.connect(db_url) as connection:
        cursor = connection.cursor()
        cursor.execute(statement)
        patients = cursor.fetchall()
    return render_template('admin.html', patients = patients)

@app.route("/doctor", methods=["GET", "POST"])
def doctor_page():
    return render_template('doctor.html', display="none")

@app.route("/add_patient")
def add_patient():
    return render_template('add_patient.html')

@app.route("/del_patient/<int:patient_id>",  methods=['GET', 'POST'])
def del_patient(patient_id):
    state = "DELETE FROM PATIENT WHERE ID={}".format(patient_id)
    with dbapi2.connect(db_url) as connection:
        cursor = connection.cursor()
        cursor.execute(state)
        cursor.close()
    return redirect(url_for('show_patients'))

@app.route("/ShowAll/",  methods=['GET', 'POST'])
def show_patients():
    state = "SELECT ALL * FROM PATIENT"
    with dbapi2.connect(db_url) as connection:
        cursor = connection.cursor()
        cursor.execute(state)
        patients = cursor.fetchall()
        print(patients)
    return render_template('admin.html', patients=patients)

@app.route("/add_new_patient/", methods=['GET', 'POST'])
def add_new_patient():
    bloody = request.form["blood"]
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
    statements = ["INSERT INTO PATIENT(NAME, AGE, WEIGHT, HEIGHT, LAST_EXAMINATION_DATE, "
                  "BLOOD_TYPE) VALUES('{}', {}, {}, {}, '{}', {})".format(request.form["name"], request.form["age"],
                                                                          request.form["weight"],
                                                                          request.form["height"], request.form["exam_date"],
                                                                          blood_new)]
    state = "SELECT MAX(ID) FROM PATIENT"
    with dbapi2.connect(db_url) as connection:
        cursor = connection.cursor()
        cursor.execute(statements[0])
        cursor.close()
        cursor = connection.cursor()
        cursor.execute(state)
        x = cursor.fetchall()[0][0]
    print(x)
    if request.form["fam_dis"] != "":
        state = "INSERT INTO FAMILY_DISEASE(NAME, AREA, PERSON) VALUES('{}', '{}', {})".format(request.form["fam_dis"],
                                                                                               request.form["fam_area"],
                                                                                               x)
        statements.append(state)
    if int(request.form["fam_dis_num"]) != 0:
        for i in range(int(request.form["fam_dis_num"])):
            state = "INSERT INTO FAMILY_DISEASE(NAME, AREA, PERSON) VALUES('{}', '{}', {})".format(request.form["fam_dis" + str(i)],
                                                                                                   request.form["fam_area" + str(i)],
                                                                                                   x)
            statements.append(state)
    if request.form["disco"] != "":
        state = "INSERT INTO DISCOMFORT(NAME, AREA, LEVELS, PERSON) VALUES('{}', '{}', {}, {})".format(request.form["disco"],
                                                                                               request.form["disco_area"], request.form["disco_level"],
                                                                                               x)
        statements.append(state)
    if int(request.form["disco_number"]) != 0:
        for i in range(int(request.form["disco_number"])):
            state = "INSERT INTO DISCOMFORT(NAME, AREA, LEVELS, PERSON) VALUES('{}', '{}', {}, {})".format(request.form["disco" + str(i)],
                                                                                              request.form["disco_area" + str(i)], request.form["disco_level" + str(i)], x)
            statements.append(state)
    if request.form["med_dev"] != "":
        state = "INSERT INTO MEDICAL_DEVICE(NAME, AREA, PERSON) VALUES('{}', '{}', {})".format(request.form["med_dev"],
                                                                                               request.form["med_dev_area"],
                                                                                               x)
        statements.append(state)
    if int(request.form["med_dev_number"]) != 0:
        for i in range(int(request.form["med_dev_number"])):
            state = "INSERT INTO MEDICAL_DEVICE(NAME, AREA, PERSON) VALUES('{}', '{}', {})".format(request.form["med_dev" + str(i)],
                                                                                                   request.form["med_dev_area" + str(i)],
                                                                                                   x)
            statements.append(state)
    if request.form["medi"] != "":
        state = "INSERT INTO MEDICATION(NAME, USAGES, PERSON) VALUES('{}', '{}', {})".format(request.form["medi"],
                                                                                               request.form["medi_area"],
                                                                                               x)
        statements.append(state)
    if int(request.form["medi_number"]) != 0:
        for i in range(int(request.form["medi_number"])):
            state = "INSERT INTO MEDICATION(NAME, USAGES, PERSON) VALUES('{}', '{}', {})".format(request.form["medi" + str(i)],
                                                                                                   request.form["medi_area" + str(i)],
                                                                                                   x)
            statements.append(state)
    if request.form["surge"] != "":
        state = "INSERT INTO SURGERY(NAME, AREA, LEVELS, PERSON) VALUES('{}', '{}', {}, {})".format(request.form["surge"],
                                                                                               request.form["surge_area"], request.form["surge_level"],
                                                                                               x)
        statements.append(state)
    if int(request.form["surge_number"]) != 0:
        for i in range(int(request.form["surge_number"])):
            state = "INSERT INTO SURGERY(NAME, AREA, LEVELS, PERSON) VALUES('{}', '{}', {}, {})".format(request.form["surge" + str(i)],
                                                                                                   request.form["surge_area" + str(i)], request.form["surge_level" + str(i)],
                                                                                                   x)
            statements.append(state)
    if request.form["allergy"] != "":
        state = "INSERT INTO ALLERGY(NAME, AREA, PERSON) VALUES('{}', '{}', {})".format(request.form["allergy"],
                                                                                               request.form["allergy_area"],
                                                                                               x)
        statements.append(state)
    if int(request.form["allergy_number"]) != 0:
        for i in range(int(request.form["allergy_number"])):
            state = "INSERT INTO ALLERGY(NAME, AREA, PERSON) VALUES('{}', '{}', {})".format(request.form["allergy" + str(i)],
                                                                                                   request.form["allergy_area" + str(i)],
                                                                                                   x)
            statements.append(state)

    with dbapi2.connect(db_url) as connection:
        cursor = connection.cursor()
        for state in statements:
            cursor.execute(state)
        cursor.close()

    return render_template('doctor.html', name="", age="", weight="", height="",
                                examinate_date="", blood_type="", family_diseases="", discomforts="",
                                medications="", surgeries="", medical_device="", allergies="", uw='n', display="none",
                                display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                                display_fam_del="none")


@app.route('/check/',  methods=['GET', 'POST'])
def check():
    global blood, age, name, weight, height, aller, med_dev, surge, medi, discomp, family_diseases, exam
    array = []
    global id
    id = request.form["id"]
    statements = ["SELECT WEIGHT FROM PATIENT WHERE ID={}".format(request.form["id"]),
                 "SELECT HEIGHT FROM PATIENT WHERE ID={}".format(request.form["id"]),
                 "SELECT NAME FROM PATIENT WHERE ID={}".format(request.form["id"]),
                 "SELECT AGE FROM PATIENT WHERE ID={}".format(request.form["id"]),
                 "SELECT NAME, AREA FROM ALLERGY WHERE PERSON={}".format(request.form["id"]),
                 "SELECT LAST_EXAMINATION_DATE FROM PATIENT WHERE ID={}".format(request.form["id"]),
                 "SELECT BLOOD_TYPE FROM PATIENT WHERE ID={}".format(request.form["id"]),
                 "SELECT NAME, AREA, LEVELS FROM DISCOMFORT WHERE PERSON={}".format(request.form["id"]),
                 "SELECT NAME, USAGES FROM MEDICATION WHERE PERSON={}".format(request.form["id"]),
                 "SELECT NAME, AREA FROM MEDICAL_DEVICE WHERE PERSON={}".format(request.form["id"]),
                 "SELECT NAME, AREA, LEVELS FROM SURGERY WHERE PERSON={}".format(request.form["id"]),
                 "SELECT NAME, AREA FROM FAMILY_DISEASE WHERE PERSON={}".format(request.form["id"])
                 ]

    with dbapi2.connect(db_url) as connection:
        cursor = connection.cursor()
        for state in statements:
            cursor.execute(state)
            array.append(cursor.fetchall())
        cursor.close()
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
        family_diseases = list()
        for i in array[11]:
            family_diseases.append(i[0] + " area: " + i[1])
        discomp = list()
        for i in array[7]:
            discomp.append(i[0] + " area: " + i[1] + " level: " + str(i[2]))
        medi = list()
        for i in array[8]:
            medi.append(i[0] + " usage: " + i[1])
        surge = list()
        for i in array[10]:
            surge.append(i[0] + " area: " + i[1] + " level: " + str(i[2]))
        med_dev = list()
        for i in array[9]:
            med_dev.append( i[0]  + " area: " + i[1])
        aller = list()
        for i in array[4]:
            aller.append( i[0] + " area: " + i[1])

            ###############################################################
        if (array[1] != []):
            height = array[1][0][0]
        else:
            height = "-"
        if (array[0] != []):
            weight = array[0][0][0]
        else:
            weight = "-"
        if (array[5] != []):
            exam = array[5][0][0]
        else:
            exam = "no_date"
    if (array[2] == []):
        return render_template('doctor.html', name="", age="", weight="", height="",
                           examinate_date="", blood_type="", family_diseases="", discomforts="", display_blood="none", upblood='n',
                           medications="", surgeries="", medical_device="", allergies="", uw='n', uphei='n', display_hei="none",
                           display="none", display_wei="none", display_fam="none", uf='n', display_date="none", up_exam_date="n", display_fam_ad="none",
                           display_fam_del="none", no_res="Patient didn't found!")
    else:
        name = array[2][0][0]
        age = array[3][0][0]
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
    global count, height, weight, age, name, exam, blood, family_diseases, discomp, medi, surge, med_dev, aller
    if (count == 0):
        count = 1
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                                examinate_date=exam, blood_type=blood, family_diseases=family_diseases, discomforts=discomp,
                                medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='y',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                display="visible", display_wei="visible", display_fam="none", uf='n', display_fam_ad="none",
                                display_fam_del="none", uphei='n', display_hei="none", display_blood="none", upblood='n',display_date="none", up_exam_date="n",
                                display_disco="none", display_disco_ad="none", display_disco_del="none", updisco='n', display_medi="none",
                               display_medi_ad="none", display_medi_del="none", upmedi='n', display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',)
    else :
        count = 0
        old_wei = weight
        weight = request.form["new_weight"]
        if (weight != ""):
            state = "UPDATE PATIENT SET WEIGHT={} WHERE ID={}".format(weight, id)
            with dbapi2.connect(db_url) as connection:
                cursor = connection.cursor()
                cursor.execute(state)
                cursor.close()
        else:
            weight = old_wei
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                                examinate_date=exam, blood_type=blood, family_diseases=family_diseases, discomforts=discomp,
                                medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                                display_fam_del="none", uphei='n', display_hei="none", display_blood="none", upblood='n',display_date="none", up_exam_date="n",
                                display_disco="none", display_disco_ad="none", display_disco_del="none", updisco='n', display_medi="none",
                               display_medi_ad="none", display_medi_del="none", upmedi='n', display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',)

count_hei = 0
@app.route("/Update_hei/", methods=['GET', 'POST'])
def update_hei():
    global count_hei, height, weight, age, name, exam, blood, family_diseases, discomp, medi, surge, med_dev, aller
    if (count_hei == 0):
        count_hei = 1
        return render_template('doctor.html', name=name, age=age, weight= weight, height=height,
                                examinate_date=exam, blood_type=blood, family_diseases=family_diseases, discomforts=discomp,
                                medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                display="visible", uphei='y', display_hei="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                                display_fam_del="none", display_blood="none", upblood='n',display_date="none", up_exam_date="n",
                                display_disco="none", display_disco_ad="none", display_disco_del="none", updisco='n', display_medi="none",
                               display_medi_ad="none", display_medi_del="none", upmedi='n', display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',)
    else :
        count_hei = 0
        old_hei = height
        height = request.form["new_height"]
        if (height != ""):
            state = "UPDATE PATIENT SET HEIGHT={} WHERE ID={}".format(height, id)
            with dbapi2.connect(db_url) as connection:
                cursor = connection.cursor()
                cursor.execute(state)
                cursor.close()
        else:
            height = old_hei
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                                examinate_date=exam, blood_type=blood, family_diseases=family_diseases, discomforts=discomp,
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='n',
                                display="visible", uphei='n', display_hei="none", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                                display_fam_del="none", display_blood="none", upblood='n',display_date="none", up_exam_date="n",
                                display_disco="none", display_disco_ad="none", display_disco_del="none", updisco='n', display_medi="none",
                               display_medi_ad="none", display_medi_del="none", upmedi='n', display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',)

count_date = 0
@app.route("/Update_date/", methods=['GET', 'POST'])
def update_date():
    global count_date, height, weight, age, name, exam, blood, family_diseases, discomp, medi, surge, med_dev, aller
    if (count_date == 0):
        count_date = 1
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                                examinate_date=exam, blood_type=blood, family_diseases=family_diseases, discomforts=discomp,
                                medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                display="visible", display_date="visible", up_exam_date="y", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                                display_fam_del="none", uphei='n', display_hei="none", display_blood="none", upblood='n',
                                display_disco="none", display_disco_ad="none", display_disco_del="none", updisco='n',
                               display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n', display_surge="none",
                               display_surge_ad="none", display_surge_del="none", upsurge='n',)
    else :
        count_date = 0
        old_exam = exam
        exam = request.form["new_date"]
        if (exam != ""):
            state = "UPDATE PATIENT SET LAST_EXAMINATION_DATE='{}' WHERE ID={}".format(exam, id)
            with dbapi2.connect(db_url) as connection:
                cursor = connection.cursor()
                cursor.execute(state)
                cursor.close()
        else:
            exam = old_exam
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                                examinate_date=exam, blood_type=blood, family_diseases=family_diseases, discomforts=discomp,
                                medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='n',
                                display="visible", display_date="none", up_exam_date="n", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                                display_fam_del="none", uphei='n', display_hei="none", display_blood="none", upblood='n',
                                display_disco="none", display_disco_ad="none", display_disco_del="none", updisco='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n', display_surge="none",
                               display_surge_ad="none", display_surge_del="none", upsurge='n')

blood_count = 0
@app.route("/Update_blood/", methods=['GET', 'POST'])
def update_blood():
    global blood_count, height, weight, age, name, exam, blood, family_diseases, discomp, medi, surge, med_dev, aller
    if (blood_count == 0):
        blood_count = 1
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                                examinate_date=exam, blood_type=blood, family_diseases=family_diseases, discomforts=discomp,
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='n',
                                display="visible", display_blood="visible", upblood='y', display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                                display_fam_del="none", uphei='n', display_hei="none", display_date="none", up_exam_date="n",
                                display_disco="none", display_disco_ad="none", display_disco_del="none", updisco='n',
                               display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n', display_surge="none", display_surge_ad="none",
                               display_surge_del="none", upsurge='n')
    else :
        blood_count = 0
        old_blood = blood
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
            blood = bloody
            state = "UPDATE PATIENT SET BLOOD_TYPE={} WHERE ID={}".format(blood_new, id)
            with dbapi2.connect(db_url) as connection:
                cursor = connection.cursor()
                cursor.execute(state)
                cursor.close()
        else:
            blood = old_blood
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                                examinate_date=exam, blood_type=blood, family_diseases=family_diseases, discomforts=discomp,
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='n',
                                display="visible", display_blood="none", upblood='n', display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                                display_fam_del="none", uphei='n', display_hei="none", display_date="none", up_exam_date="n",
                                display_disco="none", display_disco_ad="none", display_disco_del="none", updisco='n', display_medi="none",
                               display_medi_ad="none", display_medi_del="none", upmedi='n', display_surge="none", display_surge_ad="none", display_surge_del="none",
                               upsurge='n')

delete_fam_count=0
@app.route("/Delete_fam/", methods=['GET', 'POST'])
def delete_fam():
    global delete_fam_count, family_diseases
    if (delete_fam_count == 0):
        if family_diseases == "-" or family_diseases == []:
            return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                                   examinate_date=exam, blood_type=blood, family_diseases=family_diseases,
                                   discomforts=discomp, display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n',
                                   medications=medi, surgeries=surge, medical_device=med_dev, updisco='n',
                                   allergies=aller, uw='n', display="visible", display_wei="none", display_fam="none",
                                   uf='n', display_fam_ad="none", display_blood="none", upblood='n',  uphei='n', display_hei="none", display_date="none", up_exam_date="n",
                                   display_fam_del="none", display_disco="none", display_disco_ad="none", display_disco_del="none",
                                   display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                                   upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                   display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n')
        else:
            delete_fam_count = 1
            return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                                examinate_date=exam, blood_type=blood, family_diseases=family_diseases, discomforts=discomp,
                                   display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                                   upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                                   display_blood="none", upblood='n', uphei='n', display_hei="none",
                                   display_date="none", up_exam_date="n", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n',
                                display_fam_del="visible", display_disco="none", display_disco_ad="none", display_disco_del="none",
                                   display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n')
    else :
        delete_fam_count = 0
        statement = []
        for x in request.form.getlist("OK"):
            y = x.split(" area: ")
            print(x, y)
            statement.append("DELETE FROM FAMILY_DISEASE WHERE NAME='{}'".format(y[0]))
            family_diseases.remove(x)
        with dbapi2.connect(db_url) as connection:
            cursor = connection.cursor()
            for state in statement:
                cursor.execute(state)
            cursor.close()
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                               examinate_date=exam, blood_type=blood, family_diseases=family_diseases,
                               discomforts=discomp, display_blood="none", upblood='n',  uphei='n', display_hei="none", display_date="none", up_exam_date="n",
                               medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='n',
                               display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')


count_fam = 0
@app.route("/Update_fam/", methods=['GET', 'POST'])
def update_fam():
    global count_fam, family_diseases
    if (count_fam == 0):
        count_fam = 1
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                                examinate_date=exam, blood_type=blood, family_diseases=family_diseases, discomforts=discomp,
                                medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                display="visible", display_wei="none", display_fam="visible", uf='y', display_fam_ad="none",
                                display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none", updisco='n',
                                up_exam_date="n", display_fam_del="none", display_disco="none", display_disco_ad="none", display_disco_del="none",
                                display_surge = "none", display_surge_ad = "none", display_surge_del = "none", upsurge = 'n',
                                display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')
    else :
        count_fam = 0
        i = 0
        statement = []
        if family_diseases == "-" or family_diseases == []:
            if (request.form["fam_dis"] != ""):
                family_diseases.append(request.form["fam_dis"] + " area: " + request.form["area"])
                ad = id
                statement.append("INSERT INTO FAMILY_DISEASE(NAME, AREA, PERSON) VALUES('{}', '{}', {})".format(request.form["fam_dis"],
                                                                                                    request.form["area"], ad))
        else:
            for fam in family_diseases:
                x = fam.split(' area: ')
                print(family_diseases, x[0])
                if (request.form[x[0]] != ""):
                    old_name = x[0]
                    family_diseases[i] = (request.form[x[0]] + " area: " + request.form[x[1]])
                    print(family_diseases, old_name)
                    statement.append("UPDATE FAMILY_DISEASE SET NAME='{}', AREA='{}' WHERE NAME='{}'".format(request.form[x[0]], request.form[x[1]], old_name))
                i+=1

        with dbapi2.connect(db_url) as connection:
            cursor = connection.cursor()
            for state in statement:
                cursor.execute(state)
            cursor.close()
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                                examinate_date=exam, blood_type=blood, family_diseases=family_diseases, discomforts=discomp,
                                medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               up_exam_date="n", display_disco="none", display_disco_ad="none", display_disco_del="none",
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                                display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')

count_add_fam = 0
@app.route("/Add_fam/", methods=['GET', 'POST'])
def add_fam():
    global count_add_fam, family_diseases
    if count_add_fam == 0:
        count_add_fam = 1
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                               examinate_date=exam, blood_type=blood, family_diseases=family_diseases,
                               discomforts=discomp, medications=medi, surgeries=surge, medical_device=med_dev,
                               allergies=aller, uw='n', display="visible", display_wei="none", display_fam="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               up_exam_date="n", display_disco="none", display_disco_ad="none", display_disco_del="none",
                               uf='n', display_fam_ad="visible", display_fam_del="none", updisco='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')
    else:
        count_add_fam = 0
        if request.form["new_fam"] != "":
            family_diseases.append(request.form["new_fam"] + " area: " + request.form["fam_area"])
            ad = id
            state = "INSERT INTO FAMILY_DISEASE(NAME, AREA, PERSON) VALUES('{}', '{}', {})".format(request.form["new_fam"], request.form["fam_area"], ad)
            with dbapi2.connect(db_url) as connection:
                cursor = connection.cursor()
                cursor.execute(state)
                cursor.close()
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                               examinate_date=exam, blood_type=blood, family_diseases=family_diseases,
                               discomforts=discomp, medications=medi, surgeries=surge, medical_device=med_dev,
                               allergies=aller, uw='n', display="visible", display_wei="none", display_fam="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               up_exam_date="n", uf='n', display_fam_ad="none", display_fam_del="none",
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               display_disco="none", display_disco_ad="none", display_disco_del="none", updisco='n',
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')

delete_disco_count=0
@app.route("/Delete_disco/", methods=['GET', 'POST'])
def delete_disco():
    global delete_disco_count, discomp
    if (delete_disco_count == 0):
        if discomp == "-" or discomp == []:
            return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                                   examinate_date=exam, blood_type=blood, family_diseases=family_diseases,
                                   discomforts=discomp,
                                   display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                                   upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                   medications=medi, surgeries=surge, medical_device=med_dev,
                                   allergies=aller, uw='n', display="visible", display_wei="none", display_fam="none",
                                   display_disco="none", display_disco_ad="none", display_disco_del="none",
                                   display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                                   uf='n', display_fam_ad="none", display_blood="none", upblood='n',  uphei='n', display_hei="none", display_date="none", up_exam_date="n",
                                   display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')
        else:
            delete_disco_count = 1
            return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                                examinate_date=exam, blood_type=blood, family_diseases=family_diseases, discomforts=discomp,
                                medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                                display_blood="none", upblood='n', uphei='n', display_hei="none",
                                   display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                                   upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                display_date="none", up_exam_date="n", display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                                display_disco="none", display_disco_ad="none", display_disco_del="visible",
                                display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')
    else :
        delete_disco_count = 0
        statement = []
        for x in request.form.getlist("OK"):
            y = x.split(" area: ")
            statement.append("DELETE FROM DISCOMFORT WHERE NAME='{}'".format(y[0]))
            discomp.remove(x)
        with dbapi2.connect(db_url) as connection:
            cursor = connection.cursor()
            for state in statement:
                cursor.execute(state)
            cursor.close()
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                               examinate_date=exam, blood_type=blood, family_diseases=family_diseases,
                               discomforts=discomp, display_blood="none", upblood='n',  uphei='n', display_hei="none", display_date="none", up_exam_date="n",
                               medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='n',
                               display_disco="none", display_disco_ad="none", display_disco_del="none",
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')


count_disco = 0
@app.route("/Update_disco/", methods=['GET', 'POST'])
def update_disco():
    global count_disco, discomp
    if (count_disco == 0):
        count_disco = 1
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                                examinate_date=exam, blood_type=blood, family_diseases=family_diseases, discomforts=discomp,
                                medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               display_disco="visible", display_disco_ad="none", display_disco_del="none",
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               up_exam_date="n", display_fam_del="none", updisco='y', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')
    else :
        count_disco = 0
        i = 0
        statement = []
        print(discomp)
        if discomp == "-" or discomp == []:
            if (request.form["disco"] != ""):
                discomp.append(request.form["disco"] + " area: " + request.form["area"] + " level: " + request.form["level"])
                ad = id
                statement.append("INSERT INTO DISCOMFORT(NAME, AREA, LEVELS, PERSON) VALUES('{}', '{}', {}, {})".format(request.form["disco"],
                                                                                                    request.form["area"], request.form["level"], ad))
        else:
            for disco in discomp:
                x = disco.split(' area: ')
                if (request.form[x[0]] != ""):
                    old_name = x[0]
                    y = x[1].split(' level: ')
                    discomp[i] = (request.form[x[0]] + " area: " + request.form[y[0]] + " level: " + request.form[y[1]])
                    statement.append("UPDATE DISCOMFORT SET NAME='{}', AREA='{}', LEVELS='{}' WHERE NAME='{}'".format(request.form[x[0]], request.form[y[0]], request.form[y[1]], old_name))
                i+=1

        with dbapi2.connect(db_url) as connection:
            cursor = connection.cursor()
            for state in statement:
                cursor.execute(state)
            cursor.close()
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                                examinate_date=exam, blood_type=blood, family_diseases=family_diseases, discomforts=discomp,
                                medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               up_exam_date="n", display_disco="none", display_disco_ad="none", display_disco_del="none",
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                                display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')

count_add_disco = 0
@app.route("/Add_disco/", methods=['GET', 'POST'])
def add_disco():
    global count_add_disco, discomp
    if count_add_disco == 0:
        count_add_disco = 1
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                               examinate_date=exam, blood_type=blood, family_diseases=family_diseases,
                               discomforts=discomp, medications=medi, surgeries=surge, medical_device=med_dev,
                               allergies=aller, uw='n', display="visible", display_wei="none", display_fam="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               up_exam_date="n", display_disco="none", display_disco_ad="visible", display_disco_del="none",
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               uf='n', display_fam_ad="none", display_fam_del="none", updisco='n', display_medi="none",
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               display_medi_ad="none", display_medi_del="none", upmedi='n')
    else:
        count_add_disco = 0
        if request.form["new_disco"] != "":
            discomp.append(request.form["new_disco"] + " area: " + request.form["disco_area"] + " level: " + request.form["disco_level"])
            ad = id
            state = "INSERT INTO DISCOMFORT(NAME, AREA, LEVELS, PERSON) VALUES('{}', '{}', {}, {})".format(request.form["new_disco"], request.form["disco_area"],  request.form["disco_level"], ad)
            with dbapi2.connect(db_url) as connection:
                cursor = connection.cursor()
                cursor.execute(state)
                cursor.close()
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                               examinate_date=exam, blood_type=blood, family_diseases=family_diseases,
                               discomforts=discomp, medications=medi, surgeries=surge, medical_device=med_dev,
                               allergies=aller, uw='n', display="visible", display_wei="none", display_fam="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               display_disco="none", display_disco_ad="none", display_disco_del="none",
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               up_exam_date="n", uf='n', display_fam_ad="none", display_fam_del="none", updisco='n',
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')

delete_medi_count=0
@app.route("/Delete_medi/", methods=['GET', 'POST'])
def delete_medi():
    global delete_medi_count, medications, medi
    if (delete_medi_count == 0):
        if medi == "-" or medi == []:
            return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                                   examinate_date=exam, blood_type=blood, family_diseases=family_diseases,
                                   discomforts=discomp, display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n',
                                   medications=medi, surgeries=surge, medical_device=med_dev,
                                   allergies=aller, uw='n', display="visible", display_wei="none", display_fam="none",
                                   display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                                   display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                                   upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                   display_disco="none", display_disco_ad="none", display_disco_del="none",
                                   uf='n', display_fam_ad="none", display_blood="none", upblood='n',  uphei='n', display_hei="none", display_date="none", up_exam_date="n",
                                   display_fam_del="none", updisco='n')
        else:
            delete_medi_count = 1
            return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                                examinate_date=exam, blood_type=blood, family_diseases=family_diseases, discomforts=discomp,
                                   display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                                   upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                                display_blood="none", upblood='n', uphei='n', display_hei="none",
                                display_date="none", up_exam_date="n", display_medi="none", display_medi_ad="none", display_medi_del="visible", upmedi='n',
                                display_disco="none", display_disco_ad="none", display_disco_del="none",
                                display_fam_del="none", updisco='n', display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n')
    else :
        delete_medi_count = 0
        statement = []
        for x in request.form.getlist("OK"):
            y = x.split(" usage: ")
            statement.append("DELETE FROM MEDICATION WHERE NAME='{}'".format(y[0]))
            medi.remove(x)
        with dbapi2.connect(db_url) as connection:
            cursor = connection.cursor()
            for state in statement:
                cursor.execute(state)
            cursor.close()
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                               examinate_date=exam, blood_type=blood, family_diseases=family_diseases,
                               discomforts=discomp, display_blood="none", upblood='n',  uphei='n', display_hei="none", display_date="none", up_exam_date="n",
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='n',
                               display_disco="none", display_disco_ad="none", display_disco_del="none",
                               display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n',
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n')


count_medi = 0
@app.route("/Update_medi/", methods=['GET', 'POST'])
def update_medi():
    global count_medi, medi
    if (count_medi == 0):
        count_medi = 1
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                                examinate_date=exam, blood_type=blood, family_diseases=family_diseases, discomforts=discomp,
                                medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               display_disco="none", display_disco_ad="none", display_disco_del="none",display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               up_exam_date="n", display_fam_del="none", updisco='n', display_medi="visible", display_medi_ad="none", display_medi_del="none", upmedi='y')
    else :
        count_medi = 0
        i = 0
        statement = []
        print(medi)
        if medi == "-" or medi == []:
            if (request.form["medi"] != ""):
                medi.append(request.form["medi"] + " usage: " + request.form["area"])
                ad = id
                statement.append("INSERT INTO MEDICATION(NAME, USAGES, PERSON) VALUES('{}', '{}', {})".format(request.form["medi"],
                                                                                                    request.form["area"], ad))
        else:
            for med_in in medi:
                x = med_in.split(' usage: ')
                if (request.form[x[0]] != ""):
                    old_name = x[0]
                    medi[i] = (request.form[x[0]] + " usage: " + request.form[x[1]])
                    statement.append("UPDATE MEDICATION SET NAME='{}', USAGES='{}' WHERE NAME='{}'".format(request.form[x[0]], request.form[x[1]], old_name))
                i+=1

        with dbapi2.connect(db_url) as connection:
            cursor = connection.cursor()
            for state in statement:
                cursor.execute(state)
            cursor.close()
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                                examinate_date=exam, blood_type=blood, family_diseases=family_diseases, discomforts=discomp,
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               up_exam_date="n", display_disco="none", display_disco_ad="none", display_disco_del="none",
                                display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n',
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',)

count_add_medi = 0
@app.route("/Add_medi/", methods=['GET', 'POST'])
def add_medi():
    global count_add_medi, medi
    if count_add_medi == 0:
        count_add_medi = 1
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                               examinate_date=exam, blood_type=blood, family_diseases=family_diseases,
                               discomforts=discomp, medications=medi, surgeries=surge, medical_device=med_dev,
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               allergies=aller, uw='n', display="visible", display_wei="none", display_fam="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               up_exam_date="n", display_disco="none", display_disco_ad="none", display_disco_del="none",
                               uf='n', display_fam_ad="none", display_fam_del="none", updisco='n', display_medi="none",
                               display_medi_ad="visible", display_medi_del="none", upmedi='n',
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',)
    else:
        count_add_medi = 0
        if request.form["new_medi"] != "":
            medi.append(request.form["new_medi"] + " usage: " + request.form["medi_area"])
            ad = id
            state = "INSERT INTO MEDICATION(NAME, USAGES, PERSON) VALUES('{}', '{}', {})".format(request.form["new_medi"], request.form["medi_area"], ad)
            with dbapi2.connect(db_url) as connection:
                cursor = connection.cursor()
                cursor.execute(state)
                cursor.close()
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                               examinate_date=exam, blood_type=blood, family_diseases=family_diseases,
                               discomforts=discomp, medications=medi, surgeries=surge, medical_device=med_dev,
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               allergies=aller, uw='n', display="visible", display_wei="none", display_fam="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               display_disco="none", display_disco_ad="none", display_disco_del="none",
                               up_exam_date="n", uf='n', display_fam_ad="none", display_fam_del="none", updisco='n',
                               display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n',
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',)

delete_surge_count=0
@app.route("/Delete_surge/", methods=['GET', 'POST'])
def delete_surge():
    global delete_surge_count, surge
    if (delete_surge_count == 0):
        if surge == "-" or surge == []:
            return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                                   examinate_date=exam, blood_type=blood, family_diseases=family_diseases,
                                   discomforts=discomp,
                                   display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                                   upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                   medications=medi, surgeries=surge, medical_device=med_dev,
                                   allergies=aller, uw='n', display="visible", display_wei="none", display_fam="none",
                                   display_disco="none", display_disco_ad="none", display_disco_del="none",
                                   display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                                   uf='n', display_fam_ad="none", display_blood="none", upblood='n',  uphei='n', display_hei="none", display_date="none", up_exam_date="n",
                                   display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')
        else:
            delete_surge_count = 1
            return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                                examinate_date=exam, blood_type=blood, family_diseases=family_diseases, discomforts=discomp,
                                   display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                                   upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                                display_blood="none", upblood='n', uphei='n', display_hei="none",
                                display_date="none", up_exam_date="n", display_surge="none", display_surge_ad="none", display_surge_del="visible", upsurge='n',
                                display_disco="none", display_disco_ad="none", display_disco_del="none",
                                display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')
    else :
        delete_surge_count = 0
        statement = []
        for x in request.form.getlist("OK"):
            y = x.split(" area: ")
            statement.append("DELETE FROM SURGERY WHERE NAME='{}'".format(y[0]))
            surge.remove(x)
        with dbapi2.connect(db_url) as connection:
            cursor = connection.cursor()
            for state in statement:
                cursor.execute(state)
            cursor.close()
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                               examinate_date=exam, blood_type=blood, family_diseases=family_diseases,
                               discomforts=discomp, display_blood="none", upblood='n',  uphei='n', display_hei="none", display_date="none", up_exam_date="n",
                               medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               display_disco="none", display_disco_ad="none", display_disco_del="none", display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')


count_surge = 0
@app.route("/Update_surge/", methods=['GET', 'POST'])
def update_surge():
    global count_surge, surge
    if (count_surge == 0):
        count_surge = 1
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                                examinate_date=exam, blood_type=blood, family_diseases=family_diseases, discomforts=discomp,
                                medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               display_disco="none", display_disco_ad="none", display_disco_del="none",
                               display_surge="visible", display_surge_ad="none", display_surge_del="none", upsurge='y',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               up_exam_date="n", display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')
    else :
        count_surge = 0
        i = 0
        statement = []
        if surge == "-" or surge == []:
            if (request.form["surge"] != ""):
                surge.append(request.form["surge"] + " area: " + request.form["area"] + " level: " + request.form["level"])
                ad = id
                statement.append("INSERT INTO SURGERY(NAME, AREA, LEVELS, PERSON) VALUES('{}', '{}', {}, {})".format(request.form["surge"],
                                                                                                    request.form["area"], request.form["level"], ad))
        else:
            for sur in surge:
                x = sur.split(' area: ')
                if (request.form[x[0]] != ""):
                    old_name = x[0]
                    y = x[1].split(' level: ')
                    surge[i] = (request.form[x[0]] + " area: " + request.form[y[0]] + " level: " + request.form[y[1]])
                    statement.append("UPDATE SURGERY SET NAME='{}', AREA='{}', LEVELS={} WHERE NAME='{}'".format(request.form[x[0]], request.form[y[0]], request.form[y[1]], old_name))
                i+=1

        with dbapi2.connect(db_url) as connection:
            cursor = connection.cursor()
            for state in statement:
                cursor.execute(state)
            cursor.close()
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                                examinate_date=exam, blood_type=blood, family_diseases=family_diseases, discomforts=discomp,
                                medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               up_exam_date="n", display_disco="none", display_disco_ad="none", display_disco_del="none",
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')

count_add_surge = 0
@app.route("/Add_surge/", methods=['GET', 'POST'])
def add_surge():
    global count_add_surge, surge
    if count_add_surge == 0:
        count_add_surge = 1
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                               examinate_date=exam, blood_type=blood, family_diseases=family_diseases,
                               discomforts=discomp, medications=medi, surgeries=surge, medical_device=med_dev,
                               allergies=aller, uw='n', display="visible", display_wei="none", display_fam="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               up_exam_date="n", display_disco="none", display_disco_ad="none", display_disco_del="none",
                               uf='n', display_fam_ad="none", display_fam_del="none", updisco='n', display_medi="none",
                               display_medi_ad="none", display_medi_del="none", upmedi='n', display_surge="none",
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               display_surge_ad="visible", display_surge_del="none", upsurge='n',)
    else:
        count_add_surge = 0
        if request.form["new_surge"] != "":
            surge.append(request.form["new_surge"] + " area: " + request.form["surge_area"] + " level: " + request.form["surge_level"])
            ad = id
            state = "INSERT INTO SURGERY(NAME, AREA, LEVELS, PERSON) VALUES('{}', '{}', {}, {})".format(request.form["new_surge"], request.form["surge_area"], request.form["surge_level"], ad)
            with dbapi2.connect(db_url) as connection:
                cursor = connection.cursor()
                cursor.execute(state)
                cursor.close()
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                               examinate_date=exam, blood_type=blood, family_diseases=family_diseases,
                               discomforts=discomp, medications=medi, surgeries=surge, medical_device=med_dev,
                               allergies=aller, uw='n', display="visible", display_wei="none", display_fam="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               display_disco="none", display_disco_ad="none", display_disco_del="none",
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               up_exam_date="n", uf='n', display_fam_ad="none", display_fam_del="none", updisco='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')

delete_med_dev_count=0
@app.route("/Delete_med_dev/", methods=['GET', 'POST'])
def delete_med_dev():
    global delete_med_dev_count, med_dev
    if (delete_med_dev_count == 0):
        if med_dev == "-" or med_dev == []:
            return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                                   examinate_date=exam, blood_type=blood, family_diseases=family_diseases,
                                   discomforts=discomp, display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                   display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",  upmed_dev='n',
                                   medications=medi, surgeries=surge, medical_device=med_dev,
                                   allergies=aller, uw='n', display="visible", display_wei="none", display_fam="none",
                                   display_disco="none", display_disco_ad="none", display_disco_del="none",
                                   display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                                   uf='n', display_fam_ad="none", display_blood="none", upblood='n',  uphei='n', display_hei="none", display_date="none", up_exam_date="n",
                                   display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')
        else:
            delete_med_dev_count = 1
            return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                                examinate_date=exam, blood_type=blood, family_diseases=family_diseases, discomforts=discomp,
                                medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                                display_blood="none", upblood='n', uphei='n', display_hei="none", display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                display_date="none", up_exam_date="n", display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                                display_disco="none", display_disco_ad="none", display_disco_del="none",
                                display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="visible", upmed_dev='n',
                                display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')
    else :
        delete_med_dev_count = 0
        statement = []
        for x in request.form.getlist("OK"):
            y = x.split(" area: ")
            statement.append("DELETE FROM MEDICAL_DEVICE WHERE NAME='{}'".format(y[0]))
            med_dev.remove(x)
        with dbapi2.connect(db_url) as connection:
            cursor = connection.cursor()
            for state in statement:
                cursor.execute(state)
            cursor.close()
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                               examinate_date=exam, blood_type=blood, family_diseases=family_diseases,
                               discomforts=discomp, display_blood="none", upblood='n',  uphei='n', display_hei="none", display_date="none", up_exam_date="n",
                               medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='n',
                               display_disco="none", display_disco_ad="none", display_disco_del="none",
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')


count_med_dev = 0
@app.route("/Update_med_dev/", methods=['GET', 'POST'])
def update_med_dev():
    global count_med_dev, med_dev
    if (count_med_dev == 0):
        count_med_dev = 1
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                                examinate_date=exam, blood_type=blood, family_diseases=family_diseases, discomforts=discomp,
                                medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               display_disco="none", display_disco_ad="none", display_disco_del="none",
                               display_med_dev="visible", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='y', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               up_exam_date="n", display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')
    else :
        count_med_dev = 0
        i = 0
        statement = []
        print(med_dev)
        if med_dev == "-" or med_dev == []:
            if (request.form["med_dev"] != ""):
                med_dev.append(request.form["med_dev"] + " area: " + request.form["area"])
                ad = id
                statement.append("INSERT INTO MEDICAL_DEVICE(NAME, AREA, PERSON) VALUES('{}', '{}', {})".format(request.form["med_dev"],
                                                                                                    request.form["area"], ad))
        else:
            for med in med_dev:
                x = med.split(' area: ')
                if (request.form[x[0]] != ""):
                    old_name = x[0]
                    med_dev[i] = (request.form[x[0]] + " area: " + request.form[x[1]])
                    statement.append("UPDATE MEDICAL_DEVICE SET NAME='{}', AREA='{}' WHERE NAME='{}'".format(request.form[x[0]], request.form[x[1]], old_name))
                i+=1

        with dbapi2.connect(db_url) as connection:
            cursor = connection.cursor()
            for state in statement:
                cursor.execute(state)
            cursor.close()
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                                examinate_date=exam, blood_type=blood, family_diseases=family_diseases, discomforts=discomp,
                                medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='n',
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
    global count_add_med_dev, med_dev
    if count_add_med_dev == 0:
        count_add_med_dev = 1
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                               examinate_date=exam, blood_type=blood, family_diseases=family_diseases,
                               discomforts=discomp, medications=medi, surgeries=surge, medical_device=med_dev,
                               allergies=aller, uw='n', display="visible", display_wei="none", display_fam="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               up_exam_date="n", display_disco="none", display_disco_ad="none", display_disco_del="none",
                               uf='n', display_fam_ad="none", display_fam_del="none", updisco='n', display_medi="none",
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               display_med_dev="none", display_med_dev_ad="visible", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               display_medi_ad="none", display_medi_del="none", upmedi='n')
    else:
        count_add_med_dev = 0
        if request.form["new_med_dev"] != "":
            med_dev.append(request.form["new_med_dev"] + " area: " + request.form["med_dev_area"])
            ad = id
            state = "INSERT INTO MEDICAL_DEVICE(NAME, AREA, PERSON) VALUES('{}', '{}', {})".format(request.form["new_med_dev"], request.form["med_dev_area"], ad)
            with dbapi2.connect(db_url) as connection:
                cursor = connection.cursor()
                cursor.execute(state)
                cursor.close()
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                               examinate_date=exam, blood_type=blood, family_diseases=family_diseases,
                               discomforts=discomp, medications=medi, surgeries=surge, medical_device=med_dev,
                               allergies=aller, uw='n', display="visible", display_wei="none", display_fam="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               display_disco="none", display_disco_ad="none", display_disco_del="none",
                               up_exam_date="n", uf='n', display_fam_ad="none", display_fam_del="none", updisco='n',
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')

delete_aller_count=0
@app.route("/Delete_aller/", methods=['GET', 'POST'])
def delete_aller():
    global delete_aller_count, aller
    if (delete_aller_count == 0):
        if aller == "-" or aller == []:
            return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                                   examinate_date=exam, blood_type=blood, family_diseases=family_diseases,
                                   discomforts=discomp,
                                   display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                                   upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                   medications=medi, surgeries=surge, medical_device=med_dev,
                                   allergies=aller, uw='n', display="visible", display_wei="none", display_fam="none",
                                   display_disco="none", display_disco_ad="none", display_disco_del="none",
                                   display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                                   uf='n', display_fam_ad="none", display_blood="none", upblood='n',  uphei='n', display_hei="none", display_date="none", up_exam_date="n",
                                   display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')
        else:
            delete_aller_count = 1
            return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                                examinate_date=exam, blood_type=blood, family_diseases=family_diseases, discomforts=discomp,
                                   display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                                   upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="visible", upaller='n',
                                medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                                display_blood="none", upblood='n', uphei='n', display_hei="none",
                                display_date="none", up_exam_date="n", display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                                display_disco="none", display_disco_ad="none", display_disco_del="none",
                                display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')
    else :
        delete_aller_count = 0
        statement = []
        for x in request.form.getlist("OK"):
            y = x.split(" area: ")
            statement.append("DELETE FROM ALLERGY WHERE NAME='{}'".format(y[0]))
            aller.remove(x)
        with dbapi2.connect(db_url) as connection:
            cursor = connection.cursor()
            for state in statement:
                cursor.execute(state)
            cursor.close()
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                               examinate_date=exam, blood_type=blood, family_diseases=family_diseases,
                               discomforts=discomp, display_blood="none", upblood='n',  uphei='n', display_hei="none", display_date="none", up_exam_date="n",
                               medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               display_disco="none", display_disco_ad="none", display_disco_del="none", display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')


count_aller = 0
@app.route("/Update_aller/", methods=['GET', 'POST'])
def update_aller():
    global count_aller, aller
    if (count_aller == 0):
        count_aller = 1
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                                examinate_date=exam, blood_type=blood, family_diseases=family_diseases, discomforts=discomp,
                                medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               display_disco="none", display_disco_ad="none", display_disco_del="none",
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="visible", display_aller_ad="none", display_aller_del="none", upaller='y',
                               up_exam_date="n", display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')
    else :
        count_aller = 0
        i = 0
        statement = []
        print(aller)
        if aller == "-" or aller == []:
            if (request.form["aller"] != ""):
                aller.append(request.form["aller"] + " area: " + request.form["area"])
                ad = id
                statement.append("INSERT INTO ALLERGY(NAME, AREA, PERSON) VALUES('{}', '{}', {})".format(request.form["aller"],
                                                                                                    request.form["area"], ad))
        else:
            for sur in aller:
                x = sur.split(' area: ')
                if (request.form[x[0]] != ""):
                    old_name = x[0]
                    aller[i] = (request.form[x[0]] + " area: " + request.form[x[1]])
                    statement.append("UPDATE ALLERGY SET NAME='{}', AREA='{}' WHERE NAME='{}'".format(request.form[x[0]], request.form[x[1]], old_name))
                i+=1

        with dbapi2.connect(db_url) as connection:
            cursor = connection.cursor()
            for state in statement:
                cursor.execute(state)
            cursor.close()
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                                examinate_date=exam, blood_type=blood, family_diseases=family_diseases, discomforts=discomp,
                                medications=medi, surgeries=surge, medical_device=med_dev, allergies=aller, uw='n',
                                display="visible", display_wei="none", display_fam="none", uf='n', display_fam_ad="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               up_exam_date="n", display_disco="none", display_disco_ad="none", display_disco_del="none",
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                                display_fam_del="none", updisco='n', display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')

count_add_aller = 0
@app.route("/Add_aller/", methods=['GET', 'POST'])
def add_aller():
    global count_add_aller, aller
    if count_add_aller == 0:
        count_add_aller = 1
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                               examinate_date=exam, blood_type=blood, family_diseases=family_diseases,
                               discomforts=discomp, medications=medi, surgeries=surge, medical_device=med_dev,
                               allergies=aller, uw='n', display="visible", display_wei="none", display_fam="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               up_exam_date="n", display_disco="none", display_disco_ad="none", display_disco_del="none",
                               uf='n', display_fam_ad="none", display_fam_del="none", updisco='n', display_medi="none",
                               display_medi_ad="none", display_medi_del="none", upmedi='n', display_surge="none",
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="visible", display_aller_del="none", upaller='n',
                               display_surge_ad="none", display_surge_del="none", upsurge='n',)
    else:
        count_add_aller = 0
        if request.form["new_aller"] != "":
            aller.append(request.form["new_aller"] + " area: " + request.form["aller_area"])
            ad = id
            state = "INSERT INTO ALLERGY(NAME, AREA, PERSON) VALUES('{}', '{}', {})".format(request.form["new_aller"], request.form["aller_area"], ad)
            with dbapi2.connect(db_url) as connection:
                cursor = connection.cursor()
                cursor.execute(state)
                cursor.close()
        return render_template('doctor.html', name=name, age=age, weight=weight, height=height,
                               examinate_date=exam, blood_type=blood, family_diseases=family_diseases,
                               discomforts=discomp, medications=medi, surgeries=surge, medical_device=med_dev,
                               allergies=aller, uw='n', display="visible", display_wei="none", display_fam="none",
                               display_blood="none", upblood='n', uphei='n', display_hei="none", display_date="none",
                               display_disco="none", display_disco_ad="none", display_disco_del="none",
                               display_surge="none", display_surge_ad="none", display_surge_del="none", upsurge='n',
                               up_exam_date="n", uf='n', display_fam_ad="none", display_fam_del="none", updisco='n',
                               display_med_dev="none", display_med_dev_ad="none", display_med_dev_del="none",
                               upmed_dev='n', display_aller="none", display_aller_ad="none", display_aller_del="none", upaller='n',
                               display_medi="none", display_medi_ad="none", display_medi_del="none", upmedi='n')

if __name__ == "__main__":
    app.run()