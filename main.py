import smtplib
import pandas as pd
import sqlite3
import plotly.express as px
from functools import wraps
from flask import abort
from flask import Flask, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from sqlalchemy.orm import relationship
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FileField, IntegerField, SelectField, RadioField, \
    FloatField
from wtforms.validators import DataRequired, Email, Length
from werkzeug.utils import secure_filename
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class HealthForm(FlaskForm):
    choices = ["Me", "Me & My Partner", "Me, My Partner and Child", "My Parents"]
    user_choice = SelectField("Whom To Insure", choices=choices, validators=[DataRequired()])
    radio = RadioField("Does any member have illness?", coerce=int, choices=[(1, 'Yes'), (0, 'No')])
    desc = StringField("If yes, Specify here")
    covid = RadioField("Covid Positive?", coerce=int, choices=[(1, 'Yes'), (0, 'No')])
    surgery = RadioField("Any member went through a surgery?", coerce=int, choices=[(1, 'Yes'), (0, 'No')])
    income = FloatField("Enter your Income(Per Annum)", validators=[DataRequired()])
    submit = SubmitField("Submit")


class LifeForm(HealthForm):
    choices = ["Me", "Me & My Partner", "Me, My Partner and Child", "My Parents"]
    user_choice = SelectField("Whom To Insure", choices=choices, validators=[DataRequired()])
    radio = RadioField("Does any member have illness?", coerce=int, choices=[(1, 'Yes'), (0, 'No')])
    desc = StringField("If yes, Specify here")
    income = FloatField("Enter your Income(Per Annum)", validators=[DataRequired()])
    submit = SubmitField("Submit")


class CarForm(FlaskForm):
    numberplate = StringField("Enter the vehicle registration year:", validators=[DataRequired(), Length(min=4, max=4)])
    choices = ["Maharashtra", "Gujarat", "Delhi","Madhya Pradesh"]
    user_choice = SelectField("Choose the location", choices=choices, validators=[DataRequired()])
    radio_car = SelectField("Select four wheeler make:", choices=["Honda","Ford","Hyundai","Audi","Mercedes"])
    submit = SubmitField("Submit")


class BikeForm(CarForm):
    radio_bike = SelectField("Select two wheeler make:", choices=["Honda","Bajaj","Tvs","Harley Davidson","Suzuki"])


class FormForTwo(LifeForm):
    fname_partner = StringField("First Name Of Your Partner")
    lname_partner = StringField("Last Name Of Your Partner")
    mobile_partner = StringField("Mobile No Of Your Partner", validators=[Length(min=10, max=10)])
    aadharno_partner = StringField("Aadhar No Of Your Partner", validators=[Length(min=12, max=12)])
    aadarphoto_partner = FileField("Upload your aadhar pdf of Your Partner")
    fname_child = StringField("First Name Of Your Child")
    lname_child = StringField("Last Name Of Your Child")
    fname_parent1 = StringField("First Name Of Your Parent")
    lname_parent1 = StringField("First Name Of Your Parent")
    mobile_parent1 = StringField("Mobile No Of Your Parent", validators=[Length(min=10, max=10)])
    aadharno_parent1 = StringField("Aadhar No Of Your Parent", validators=[Length(min=12, max=12)])
    aadarphoto_parent1 = FileField("Upload your aadhar pdf of Your Parent")
    fname_parent2 = StringField("First Name Of Your Parent")
    lname_parent2 = StringField("First Name Of Your Parent")
    mobile_parent2 = StringField("Mobile No Of Your Parent", validators=[Length(min=10, max=10)])
    aadharno_parent2 = StringField("Aadhar No Of Your Parent", validators=[Length(min=12, max=12)])
    aadarphoto_parent2 = FileField("Upload your aadhar pdf of Your Parent")
    submit = SubmitField("Submit")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Up")


class KycForm1(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    moodle_id = StringField("Moodle Id", validators=[DataRequired(), Length(min=8, max=8)])
    submit = SubmitField("Submit")


class KycForm2(FlaskForm):
    firstname = StringField("First Name", validators=[DataRequired()])
    lastname = StringField("Last Name", validators=[DataRequired()])
    mobileno = StringField("Mobile No", validators=[DataRequired(), Length(min=10, max=10)])
    image = FileField("Upload your photo", validators=[DataRequired()])
    submit = SubmitField("Submit")


class KycForm3(FlaskForm):
    aadharno = StringField("Aadhar No", validators=[DataRequired(), Length(min=12, max=12)])
    aadarphoto = FileField("Upload your aadhar pdf", validators=[DataRequired()])
    submit = SubmitField("Submit")


class SubmitForm(FormForTwo):
    submit = SubmitField("Submit")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")


class RejectForm(FlaskForm):
    choices = ["invalid aadhar no", "incorrect photo", "incorrect document"]
    user_choice = SelectField("Type of issue", choices=choices, validators=[DataRequired()])
    text = StringField("Description", validators=[DataRequired()])
    submit = SubmitField("Submit")


app = Flask(__name__)
app.config['SECRET_KEY'] = "Kuchbhi"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///usersfinalfinal.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
my_email = "insurance.notifier@yahoo.com"
password = "mgjrrdjhwxuwoctu"
choices = ""
fnamep = ""
lnamep = ""
mbnop = ""
adnop = ""
adptp = ""
fnamec = ""
lnamec = ""
fnamep1 = ""
lnamep1 = ""
mbnop1 = ""
adnop1 = ""
adptp1 = ""
fnamep2 = ""
lnamep2 = ""
mbnop2 = ""
adnop2 = ""
adptp2 = ""




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    policies = relationship("Insurance", back_populates="user_name")
    kyc = db.Column(db.String(100), default="Pending")
    mobileno = db.Column(db.String(15))
    aadharno = db.Column(db.Integer)
    image = db.Column(db.String(150))
    aadharphoto = db.Column(db.String(150))
    selfie = db.Column(db.String(150))


class Policy(db.Model):
    __tablename__ = "policy"
    id = db.Column(db.Integer, primary_key=True)
    ins = relationship("Insurance", back_populates="policy_name")
    image = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    cover = db.Column(db.String(10))
    monthly = db.Column(db.String(20))
    yearly = db.Column(db.String(20))
    features = db.Column(db.String(500), nullable=False)
    claim = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(50), nullable=False)


class Insurance(db.Model):
    __tablename__ = "insurance"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    policy_id = db.Column(db.Integer, db.ForeignKey("policy.id"))
    policy_name = relationship("Policy", back_populates="ins")
    user_name = relationship("User", back_populates="policies")
    insurance_for = db.Column(db.String(100), nullable=False)
    yearly = db.Column(db.Integer)


class Dependencies(db.Model):
    __tablename__ = "dependencies"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey("users.id"))
    policy = db.Column(db.Integer, db.ForeignKey("policy.id"))
    desc = db.Column(db.String(1500), nullable=False)


policy = Policy(
    id=6,
    image="images/NEW INDIA.jfif",
    name="New India Assurance-Floater Mediclaim",
    cover="Rs.5 L",
    monthly="Rs.947",
    yearly="Rs.11,375 ",
    type="Health",
    features="Existing Illness Waiting Period"
"There is a waiting period of 4 years for coverage on conditions declared and existing at the time of first purchase"
"Why is it Important"
"The shorter waiting period, the better as the cost of your current illness can be expensive"
"Network Hospitals covered"
"1800+ Network hospitals",




    claim="97% Claim Settlement Ratio"
"This is explained as (Number of Claims Settled / Number of Claims) by the Insurance Company."
"Source: Public Disclosures (NL25 for 2018-19)."
"4 yrs"
"Existing Illness Waiting Period"
"There is a waiting period of 4 years for coverage on conditions declared and existing at the time of first purchase"








)


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template('InsurancePlanner.html')

@app.route("/contactus", methods=["GET", "POST"])
def contactus():
    return render_template('contactus.html')


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    # #user1 = Insurance.query.filter_by(id=1).first()
    # db.session.add(policy)
    # #db.session.delete(user1)
    # db.session.commit()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))
        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("home"))

    return render_template("Register.html", form=form, current_user=current_user)


@app.route("/health")
def health():
    return redirect(url_for("test", type="Health"))


@app.route("/life")
def life():
    return redirect(url_for("test", type="Life"))


@app.route("/car")
def car():
    return redirect(url_for("test2", type="Car"))


@app.route("/bike")
def bike():
    return redirect(url_for("test2", type="Bike"))


@app.route("/healthpol")
def healthpol():
    return render_template("Health Policy1.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please register.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))
    return render_template("admin.html", form=form, current_user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/kyc", methods=["GET", "POST"])
def kyc():
    form = KycForm1()
    if form.validate_on_submit():

        if form.moodle_id.data[:4] == '2010':
            return redirect(url_for("kyc2"))
        else:
            flash("Incorrect moodle id", "error")
            return redirect(url_for("kyc"))
    return render_template("kyc.html", form=form, current_user=current_user)


@app.route("/kyc2", methods=["GET", "POST"])
def kyc2():
    form = KycForm2()
    if form.validate_on_submit():
        firstname = form.firstname.data
        lastname = form.lastname.data
        mobileno = form.mobileno.data
        f = form.image.data
        file = f'static/userimages/{current_user.name}{secure_filename(f.filename)}'
        f.save(file)
        user = User.query.filter_by(id=current_user.id).first()
        user.image = file
        user.mobileno = mobileno
        db.session.commit()
        return redirect(url_for("kyc3"))
    return render_template("kyc.html", form=form, current_user=current_user)


@app.route("/kyc3", methods=["GET", "POST"])
def kyc3():
    form = KycForm3()
    if request.method == "POST":
        aadharno = form.aadharno.data
        f = form.aadarphoto.data
        file = f'static/userimages/{current_user.name}{secure_filename(f.filename)}'
        f.save(file)
        user = User.query.filter_by(id=current_user.id).first()
        user.aadharphoto = file
        user.aadharno = aadharno
        db.session.commit()
        return redirect(url_for('upload'))
    return render_template("kyc.html", form=form, current_user=current_user)


@app.route("/read-more/<int:id>/<int:newmonthly>/<int:new_amt>")
def read_more(id, newmonthly, new_amt):
    policy = Policy.query.filter_by(id=id).first()
    return render_template("adityabirla.html", policy=policy, newmonthly=newmonthly, new_amt=new_amt)


@admin_only
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    users = User.query.all()
    return render_template("dashboard.html", users=users)


@app.route("/submit/<int:user_id>", methods=["GET", "POST"])
def submit(user_id):
    user = User.query.filter_by(id=user_id).first()
    user.kyc = "Active"
    db.session.commit()
    message = """

<html>
        	<head>
        		<meta charset="utf-8" />
        		<title></title>
        		<style>
        		    a:link {
                        text-decoration: none;
                      }
        			.invoice-box {
        				max-width: 800px;
        				margin: auto;
        				padding: 30px;
        				border: 1px solid #eee;
        				box-shadow: 0 0 10px rgba(0, 0, 0, 0.15);
        				font-size: 16px;
        				line-height: 24px;
        				font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif;
        				color: #555;
        			}
        			.invoice-box table {
        				width: 100%;
        				line-height: inherit;
        				text-align: left;
        			}
        			.invoice-box table td {
        				padding: 5px;
        				vertical-align: top;
        			}
        			.invoice-box table tr td:nth-child(2) {
        				text-align: right;
        			}
        			.invoice-box table tr.top table td {
        				padding-bottom: 20px;
        			}
        			.invoice-box table tr.top table td.title {
        				font-size: 45px;
        				line-height: 45px;
        				color: #333;
        			}
        			.invoice-box table tr.information table td {
        				padding-bottom: 40px;
        			}
                  .idno{
                  	font-weight: bold;
                    font-size: 60px;
                    padding-top:70px;
                    text-align: center;
                  }
                  .invoiceid{
                  	text-align: center;
                  }
        			.invoice-box table tr.heading td {
        				background: #eee;
        				border-bottom: 1px solid #ddd;
        				font-weight: bold;
        			}
        			.invoice-box table tr.details td {
        				padding-bottom: 20px;
        			}
        			.invoice-box table tr.item td {
        				border-bottom: 1px solid #eee;
        			}
        			.invoice-box table tr.item.last td {
        				border-bottom: none;
        			}
        			.invoice-box table tr.total td:nth-child(2) {
        				border-top: 2px solid #eee;
        				font-weight: bold;
        			}
        			@media only screen and (max-width: 600px) {
        				.invoice-box table tr.top table td {
        					width: 100%;
        					display: block;
        					text-align: center;
        				}
        				.invoice-box table tr.information table td {
        					width: 100%;
        					display: block;
        					text-align: center;
        				}
        			}
        			/** RTL **/
        			.invoice-box.rtl {
        				direction: rtl;
        				font-family: Tahoma, 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif;
        			}
        			.invoice-box.rtl table {
        				text-align: right;
        			}
        			.invoice-box.rtl table tr td:nth-child(2) {
        				text-align: left;
        			}
        		</style>
        	</head>
        	<body>
        		<div class="invoice-box">
        			<table cellpadding="0" cellspacing="0">
        				<tr class="top">
        					<td colspan="2">
        						<table>
        							<tr>
        								<td class="title">
        									<img src="https://tse4.mm.bing.net/th?id=OIP.jj3q0BXl_mZZWq4UjDRRgQAAAA&pid=Api&P=0&w=157&h=157" style="width: 100%; max-width: 150px" />
        								</td>
        								<td>
                                          <table>
                                            <tr class>
                                              <td class="invoiceid">Insurance Planner</td>
                                            </tr>
                                            <tr>
                                              <td class="idno"></td>
                                            </tr>
                                          </table>
        								</td>
        							</tr>
        						</table>
        					</td>
        				</tr>
        				<tr class="information heading">
        					<td colspan="2">
        						<table>
        							<tr>
        								<td>
        									Contact Us
        								</td>
        							<td>
        									insurance.notifier@yahoo.com
        								</td>
        							</tr>
        						</table>
        					</td>
        				</tr>

        			</table>
					<p>Hi """ + user.name + """<br>Your KYC has been approved. You can now start purchasing our policies
						<br>Regards,<br><a href="/">Insurance Planner</a></p>
        		</div>
        	</body>
        </html>

    """
    with smtplib.SMTP("smtp.mail.yahoo.com") as smtp:
        msg = MIMEMultipart("alternative")
        msg.attach(MIMEText(message, 'html'))
        msg['Subject'] = 'KYC Validation Email'
        msg['From'] = my_email
        msg['To'] = user.email
        smtp.starttls()
        smtp.login(user=my_email, password=password)
        smtp.sendmail(
            from_addr=my_email,
            to_addrs=user.email,
            msg=msg.as_string()
        )
        flash("email sent", "success")
    return redirect(url_for("dashboard"))


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    file = ""
    form = SubmitForm()
    if request.method == 'POST':
        fs = request.files.get('snap')
        if fs:
            file = f'static/userimages/{current_user.name}{secure_filename("selfie.jpg")}'
            fs.save(file)
            flash("Image captured successfully", "success")
        if request.method == 'POST':
            flash("KYC info updated and will get back to u soon", "success")
            return redirect(url_for('home'))
        else:
            flash("Unable to capture image", "error")
        current_user.selfie = file
        db.session.commit()

    return render_template("camera.html", form=form)


@admin_only
@app.route("/reject/<int:user_id>", methods=["GET", "POST"])
def reject(user_id):
    form = RejectForm()
    if form.validate_on_submit():
        user = User.query.filter_by(id=user_id).first()
        user.kyc = "Rejected"
        db.session.commit()
        subject = form.user_choice.data
        desc = form.text.data
        message = """

        <html>
                	<head>
                		<meta charset="utf-8" />
                		<title></title>
                		<style>
                		    a:link {
                                text-decoration: none;
                              }
                			.invoice-box {
                				max-width: 800px;
                				margin: auto;
                				padding: 30px;
                				border: 1px solid #eee;
                				box-shadow: 0 0 10px rgba(0, 0, 0, 0.15);
                				font-size: 16px;
                				line-height: 24px;
                				font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif;
                				color: #555;
                			}
                			.invoice-box table {
                				width: 100%;
                				line-height: inherit;
                				text-align: left;
                			}
                			.invoice-box table td {
                				padding: 5px;
                				vertical-align: top;
                			}
                			.invoice-box table tr td:nth-child(2) {
                				text-align: right;
                			}
                			.invoice-box table tr.top table td {
                				padding-bottom: 20px;
                			}
                			.invoice-box table tr.top table td.title {
                				font-size: 45px;
                				line-height: 45px;
                				color: #333;
                			}
                			.invoice-box table tr.information table td {
                				padding-bottom: 40px;
                			}
                          .idno{
                          	font-weight: bold;
                            font-size: 60px;
                            padding-top:70px;
                            text-align: center;
                          }
                          .invoiceid{
                          	text-align: center;
                          }
                			.invoice-box table tr.heading td {
                				background: #eee;
                				border-bottom: 1px solid #ddd;
                				font-weight: bold;
                			}
                			.invoice-box table tr.details td {
                				padding-bottom: 20px;
                			}
                			.invoice-box table tr.item td {
                				border-bottom: 1px solid #eee;
                			}
                			.invoice-box table tr.item.last td {
                				border-bottom: none;
                			}
                			.invoice-box table tr.total td:nth-child(2) {
                				border-top: 2px solid #eee;
                				font-weight: bold;
                			}
                			@media only screen and (max-width: 600px) {
                				.invoice-box table tr.top table td {
                					width: 100%;
                					display: block;
                					text-align: center;
                				}
                				.invoice-box table tr.information table td {
                					width: 100%;
                					display: block;
                					text-align: center;
                				}
                			}
                			/** RTL **/
                			.invoice-box.rtl {
                				direction: rtl;
                				font-family: Tahoma, 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif;
                			}
                			.invoice-box.rtl table {
                				text-align: right;
                			}
                			.invoice-box.rtl table tr td:nth-child(2) {
                				text-align: left;
                			}
                		</style>
                	</head>
                	<body>
                		<div class="invoice-box">
                			<table cellpadding="0" cellspacing="0">
                				<tr class="top">
                					<td colspan="2">
                						<table>
                							<tr>
                								<td class="title">
                									<img src="https://tse4.mm.bing.net/th?id=OIP.jj3q0BXl_mZZWq4UjDRRgQAAAA&pid=Api&P=0&w=157&h=157" style="width: 100%; max-width: 150px" />
                								</td>
                								<td>
                                                  <table>
                                                    <tr class>
                                                      <td class="invoiceid">Insurance Planner</td>
                                                    </tr>
                                                    <tr>
                                                      <td class="idno"></td>
                                                    </tr>
                                                  </table>
                								</td>
                							</tr>
                						</table>
                					</td>
                				</tr>
                				<tr class="information heading">
                					<td colspan="2">
                						<table>
                							<tr>
                								<td>
                									Contact Us
                								</td>
                							<td>
                									insurance.notifier@yahoo.com
                								</td>
                							</tr>
                						</table>
                					</td>
                				</tr>

                			</table>
        					<p>Hi """ + user.name + """<br>Your KYC has been rejected. The team's response was<br>""" + desc + """
        						<br>Regards,<br><a href="/">Insurance Planner</a></p>
                		</div>
                	</body>
                </html>

            """
        with smtplib.SMTP("smtp.mail.yahoo.com") as smtp:
            msg = MIMEMultipart("alternative")
            msg.attach(MIMEText(message, 'html'))
            msg['Subject'] = 'KYC Rejection Email'
            msg['From'] = my_email
            msg['To'] = user.email
            smtp.starttls()
            smtp.login(user=my_email, password=password)
            smtp.sendmail(
                from_addr=my_email,
                to_addrs=user.email,
                msg=msg.as_string()
            )
            flash("email sent", "success")
        return redirect(url_for("dashboard"))
    return render_template("reject.html", form=form)


@app.route("/analysis")
def analysis():
    policy = []
    cnx = sqlite3.connect('usersfinalfinal.db')
    df = pd.read_sql_query("SELECT * FROM insurance", cnx)
    count = df['policy_id'].value_counts()
    for idx in df['policy_id'].unique():
        policy.append(str(Policy.query.filter_by(id=int(idx)).first().name))
    if policy:
        fig = px.bar(df, x=policy, y=count,  labels={'x': 'Policy', 'y': 'No. of Policy Purchased'})
        fig.write_html("templates/analysis.html")
        return render_template("analysis.html", fig=fig)
    else:
        return "No Data"


@app.route("/test/<type>", methods=["GET", "POST"])
def test(type):
    global choices, data
    global fname, lnamep, mbnop, adnop, adptp,fnamec, lnamec,fnamep1, lnamep1, mbnop1, adnop1, adptp1, fnamep2, lnamep2, mbnop2, adnop2, adptp2
    form = FormForTwo()
    if request.method == "POST":
        income = form.income.data
        fnamep = form.fname_partner.data
        lnamep = form.lname_partner.data
        mbnop = form.mobile_partner.data
        adnop = form.aadharno_partner.data
        adptp = form.aadarphoto_partner.data
        fnamec = form.fname_child.data
        lnamec = form.lname_child.data
        fnamep1 = form.fname_parent1.data
        lnamep1 = form.lname_parent1.data
        mbnop1 = form.mobile_parent1.data
        adnop1 = form.aadharno_parent1.data
        adptp1 = form.aadarphoto_parent1.data
        fnamep2 = form.fname_parent2.data
        lnamep2 = form.lname_parent2.data
        mbnop2 = form.mobile_parent2.data
        adnop2 = form.aadharno_parent2.data
        adptp2 = form.aadarphoto_parent2.data
        choices = request.form.get("user_choice")
        policies = Policy.query.filter_by(type=type).all()
        return render_template("Health Policy1.html", income=income, policies=policies, choices=choices, type=type)
    return render_template("advancetest.html", form=form, type=type)


@app.route("/test2/<type>", methods=["GET", "POST"])
def test2(type):
    income = 10000
    form = BikeForm()
    if request.method == "POST":
        policies = Policy.query.filter_by(type=type).all()
        return render_template("Health Policy1.html", income=income, policies=policies, choices=choices, type=type)
    return render_template("test.html", form=form, type=type)


@app.route("/checkout/<int:id>/<int:newmonthly>/<int:new_amt>", methods=["GET", "POST"])
def checkout(id, newmonthly, new_amt):
    global fname, lnamep, mbnop, adnop, adptp,fnamec, lnamec,fnamep1, lnamep1, mbnop1, adnop1, adptp1, fnamep2, lnamep2, mbnop2, adnop2, adptp2
    current_policy = Policy.query.filter_by(id=id).first()
    policies = Policy.query.all()
    form = SubmitForm()
    user = Insurance.query.filter_by(user_id=current_user.id, policy_id=current_policy.id).first()
    if not user:
        if request.url[-6:] == "Submit":
            new_insurance = Insurance(
                user_id=current_user.id,
                policy_id=current_policy.id,
                insurance_for=str(choices),
                yearly=new_amt,
            )
            db.session.add(new_insurance)
            db.session.commit()
            return redirect(url_for("home"))
        # with open(f"static/userdata/{current_user.name}-{current_policy.name}-details.txt", "w") as f:
        if choices == "Me":
            new_dependency = Dependencies(
                user=current_user.id,
                policy=current_policy.id,
                desc=f'''Policy for : {choices}\n{current_user.name}\n{current_user.mobileno}\n{current_user.aadharno}\n'''
            )
            # f.write(f"{current_user.name}\n"
            #         f"{current_user.mobileno}\n"
            #         f"{current_user.aadharno}\n")
        if choices == "Me & My Partner":
            new_dependency = Dependencies(
                user=current_user.id,
                policy=current_policy.id,
                desc=f"Policy for : {choices}"
                    f"Partner first name: {fnamep}\n"
                    f"Partner last name: {lnamep}\n"
                    f"Partner mobile no: {mbnop}\n"
                    f"Partner aadhar no: {adnop}\n"
                    f"Partner aadhar photo:{adptp}\n")

            # f.write(f"{fnamep}\n"
            # f"{lnamep}\n"
            # f"{mbnop}\n"
            # f"{adnop}\n"
            # f"{adptp}\n")
        if choices == "Me, My Partner & Child":
            new_dependency = Dependencies(
                user=current_user.id,
                policy=current_policy.id,
                desc=f"Policy for : {choices}"
                    f"Partner first name: {fnamep}\n"
                    f"Partner last name: {lnamep}\n"
                    f"Partner mobile no: {mbnop}\n"
                    f"Partner aadhar no: {adnop}\n"
                    f"Partner aadhar photo:{adptp}\n"
                    f"Child first name: {fnamec}\n"
                    f"Child last name: {lnamec}\n")
            # f.write(f"{fnamep}\n"
            # f"{lnamep}\n"
            # f"{mbnop}\n"
            # f"{adnop}\n"
            # f"{adptp}\n"
            # f"{fnamec}\n"
            # f"{lnamec}\n")
        if choices == "My Parents":
            new_dependency = Dependencies(
                user=current_user.id,
                policy=current_policy.id,
                desc=f"Policy for : {choices}"
                    f"Parent 1 first name: {fnamep1}\n"
                    f"Parent 1 last name: {lnamep1}\n"
                    f"Parent 1 mobile no: {mbnop1}\n"
                    f"Parent 1 aadhar no: {adnop1}\n"
                    f"Parent 1 aadhar photo: {adptp1}\n"
                    f"Parent 2 first name: {fnamep2}\n"
                    f"Parent 2 last name: {lnamep2}\n"
                    f"Parent 2 mobile no: {mbnop2}\n"
                    f"Parent 2 aadhar no: {adnop2}\n"
                    f"Parent 2 aadhar photo: {adptp2}\n")
        db.session.add(new_dependency)
        db.session.commit()

                # f.write(f"{fnamep1}\n"
                # f"{lnamep1}\n"
                # f"{mbnop1}\n"
                # f"{adnop1}\n"
                # f"{adptp1}\n"
                # f"{fnamep2}\n"
                # f"{lnamep2}\n"
                # f"{mbnop2}\n"
                # f"{adnop2}\n"
                # f"{adptp2}\n")
    else:
        return redirect(url_for("policies", id=current_user.id))
    return render_template("checkout.html", form=form, current_policy=current_policy, policies=policies, newmonthly=newmonthly, new_amt=new_amt)


@app.route("/mypolicies/<int:id>")
def policies(id):
    insurance = Insurance.query.filter_by(user_id=id).all()
    return render_template("my_policy.html", insurances=insurance)


@app.route("/details/<current_policy>")
def details(current_policy):
    # with open(f"static/userdata/{current_user.name}-{current_policy}-details.txt") as f:
    #     lines = f.readlines()
    policy = Policy.query.filter_by(name=current_policy).first()
    dependency = Dependencies.query.filter_by(user=current_user.id, policy=policy.id).first()
    return render_template("details.html", current_user=current_user, lines=dependency, current_policy=current_policy)


if __name__ == "__main__":
    app.run(debug=True)
