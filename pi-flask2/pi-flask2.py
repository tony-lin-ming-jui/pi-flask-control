from flask import Flask,render_template,request,redirect,url_for,session,g,escape,Markup,flash
from datetime import datetime
from flask_wtf import FlaskForm,RecaptchaField#RecaptchaField用於GOOGLE的Recaptcha驗證
from wtforms import StringField,PasswordField,DateTimeField,SubmitField
from wtforms.validators import InputRequired,Length
import os
import hashlib  
import pymysql
import io
import base64
import time
import os
import matplotlib.pyplot as plt
#from gpiozero import Servo
#from time import sleep
#GPIO.setmode(GPIO.BCM)
'''
#設定LED pin變數
LED1 = 4   
LED2 = 17
LED3 = 27
LED4 = 22

#設定為輸出
GPIO.setup(LED1,GPIO.OUT)
GPIO.setup(LED2,GPIO.OUT)
GPIO.setup(LED3,GPIO.OUT)
GPIO.setup(LED4,GPIO.OUT)
'''

db = pymysql.connect("127.0.0.1","root","1qaz1qaz","pi")
cursor = db.cursor()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
'''
GPIO.output(LED1,GPIO.LOW)
GPIO.output(LED2,GPIO.LOW)
GPIO.output(LED3,GPIO.LOW)
GPIO.output(LED4,GPIO.LOW)
'''
class loginform(FlaskForm):
    name = StringField(u'用戶名:',validators=[InputRequired(message=u'用戶名未填'),Length(min=3,max=10,message=u'必須輸入3到10個數字或英文字母')])#從這裡取表單的東西,StringField取字串 
    password = PasswordField(u'密碼:',validators=[InputRequired(message=u'密碼未填'),Length(min=4,max=12,message=u'必須輸入4到12個數字或英文字母')])#PasswordField取密碼
    #InputRequired()功能:如果表單未填跳出提醒
   
    submit = SubmitField(u'登入')
class registform(FlaskForm):
    name = StringField(u'用戶名:',validators=[InputRequired(message=u'用戶名未填'),Length(min=3,max=10,message=u'必須輸入3到10個數字或英文字母')])#從這裡取表單的東西,StringField取字串 
    #InputRequired()功能:如果表單未填跳出提醒
    
    password1 = PasswordField('密碼:',validators=[InputRequired(message=u'密碼未填'),Length(min=4,max=12,message=u'必須輸入4到12個數字或英文字母')])
    password2 = PasswordField('密碼確認:',validators=[InputRequired(message=u'密碼確認未填'),Length(min=4,max=12,message=u'必須輸入4到12個數字或英文字母')])
    submit = SubmitField(u'註冊')
class fixpasswordform(FlaskForm):
    oldpassword = PasswordField(u'舊密碼:',validators=[InputRequired(message=u'舊密碼未填'),Length(min=4,max=12,message=u'必須輸入4到12個數字或英文字母')])#PasswordField取密碼
    newpassword1 = PasswordField(u'新密碼:',validators=[InputRequired(message=u'新密碼未填'),Length(min=4,max=12,message=u'必須輸入4到12個數字或英文字母')])#PasswordField取密碼
    newpassword2 = PasswordField(u'新密碼確認:',validators=[InputRequired(message=u'新密碼確認未填'),Length(min=4,max=12,message=u'必須輸入4到12個數字或英文字母')])#PasswordField取密碼
    submit = SubmitField(u'修改完成')
class dateform(FlaskForm):                   #抓到時
    entrydate1 = DateTimeField('查詢的初始時間',format='%Y-%m-%d %H',validators=[InputRequired(message=u'查詢的初始時間未填')])#format='%Y-%m-%d %H:%M:%S'
    entrydate2 = DateTimeField('查詢的結束時間',format='%Y-%m-%d %H',validators=[InputRequired(message=u'查詢的結束時間未填')])#format='%Y-%m-%d %H:%M:%S'
    #name = StringField('name')   #從這裡取表單的東西,StringField取字串
    #password = PasswordField('password')#PasswordField取密碼
    submit = SubmitField(u'確認')

@app.route('/',methods=['GET','POST'])
def login():
	form = loginform()        
	if form.validate_on_submit():
		print('name',form.name.data)
		print('password',form.password.data)
		pwd_temp = hashlib.sha1(form.password.data.encode("utf8"))# sha1哈希加密
		password = pwd_temp.hexdigest()# sha1哈希加密
		cursor.execute("SELECT * FROM users WHERE name = '" + str(form.name.data) + "'")
		A=cursor.fetchall()
		print(A)
		if not A:
			flash(u'用戶名或密碼錯誤')
			print("用戶名錯誤") #用戶名與資料庫不相同
			return redirect(url_for('login'))
		else:
			cursor.execute("SELECT * FROM users WHERE name = '" + str(form.name.data) + "' AND password = '" + str(password) + "'")
			B=cursor.fetchall()
			print(B)
			if not B:
				flash(u'用戶名或密碼錯誤')
				print("密碼錯誤")
				return redirect(url_for('login'))
			else:
				print("密碼正確")
				session['session_name']=form.name.data
				return redirect(url_for('times'))

	return render_template('login.html',form=form)

@app.route('/regist',methods=['GET','POST'])
def regist():
	form = registform()
	if form.validate_on_submit():
		print('name',form.name.data)
		print('formpassword1',form.password1.data)
		print('formpassword2',form.password2.data)
		pwd_temp1 = hashlib.sha1(form.password1.data.encode("utf8"))# sha1哈希加密
		password1 = pwd_temp1.hexdigest()# sha1哈希加密
		pwd_temp2 = hashlib.sha1(form.password2.data.encode("utf8"))# sha1哈希加密
		password2 = pwd_temp2.hexdigest()# sha1哈希加密
		cursor.execute("SELECT * FROM users WHERE name = '" + str(form.name.data) + "'")
		print(password1)
		print(password2)
		A=cursor.fetchall()	
		print(A)
		if A:
			flash(u'已有相同用戶名')
			print('已有相同用戶名')
			return redirect(url_for('regist'))
		else:
			if password1 != password2:
				flash(u'兩次密碼不相等，請重新輸入')
				#return u'兩次密碼不相等，請重新輸入'
				return redirect(url_for('regist'))
			else:
				password=password1                
				cursor.execute("INSERT INTO users (name,password) VALUES ('" + str(form.name.data) + "','" + str(password) + "')") # str(form.password.data)
				db.commit()            	
				print("INSERT INTO users (name,password) VALUES ('" + str(form.name.data) + "','" + str(password) + "')")
				print(form.name.data)     #匯進數據庫
				print(password)                                          
				return redirect(url_for('login'))
	return render_template('regist.html',form=form)

@app.route('/times',methods=['GET','POST'])
def times():
	form = dateform()
	name = session.get('session_name')
	if form.validate_on_submit():
		if name:
			print(form.entrydate1.data)
			print(form.entrydate2.data)
			cursor.execute("SELECT * FROM ptqs WHERE create_time BETWEEN '" + str(form.entrydate1.data) + "' AND '" + str(form.entrydate2.data) + "'")
			A=cursor.fetchall()
			print(A)
			if not A:
				flash(u'資料庫沒有此時間')
				print('資料庫沒有此時間')
				return redirect(url_for('times'))
			else :
				#return redirect(url_for("data", entrydate1= str(form.entrydate1.data) , entrydate2= str(form.entrydate2.data)))
				return redirect(url_for("plot", entrydate1= str(form.entrydate1.data) , entrydate2= str(form.entrydate2.data)))
		else:
			return redirect('/')
	if name:
    		return render_template('times.html',form=form,name=name)
	else:
        	return redirect('/')

	

@app.route('/plot')
def plot():
	name = session.get('session_name')
	if name:
		img = io.BytesIO()
		#cursor.execute("SELECT * FROM pms WHERE create_time BETWEEN '2018-07-09 22:54:21' AND '2018-07-09 22:55:11'")
		print("SELECT * FROM ptqs WHERE create_time BETWEEN '" + str(request.args.get('entrydate1')) + "' AND '" + str(request.args.get('entrydate2')) + "'")
		a = "SELECT * FROM ptqs WHERE create_time BETWEEN '" + str(request.args.get('entrydate1')) + "' AND '" + str(request.args.get('entrydate2')) + "'"
		cursor.execute(a)    
		listpm25=[]
		listTVOC=[]
		listHCHO=[]
		listCO2=[]
		listtem=[]
		listhum=[]
		create_time=[]
		i=0
		for row in cursor.fetchall():
			#print(row[7].strftime('%Y-%m-%d %H:%M:%S'))
			listpm25.append(int(row[1]))
			listTVOC.append(int(row[2]))
			listHCHO.append(int(row[3]))
			listCO2.append(int(row[4]))
			listtem.append(int(row[5]))
			listhum.append(int(row[6]))
			create_time.append(row[7].strftime('%Y-%m-%d %H:%M:%S'))
			#create_time.append(row[7].strftime('%H:%M:%S'))
			i=i+1
		db.commit()
		db.rollback()
		#db.close

		print('listpm25',listpm25)
		print('listTVOC',listTVOC)
		print('listHCHO',listHCHO)
		print('listCO2',listCO2)
		print('listtem',listtem)
		print('listhum',listhum)
		print('create_time',create_time)
		print('i',i)
		#return u'測試'

		#x = [1,2,3,4,5]
		#y = [1,2,3,4,5]
		plt.cla()#加這個 圖片就不會一直疊
		plt.plot(create_time,listpm25, 'o-', label=u'pm25')
		plt.plot(create_time,listTVOC, 'o-', label=u'揮發性有機物')
		plt.plot(create_time,listHCHO, 'o-', label=u'甲醛')

		plt.plot(create_time,listCO2, 'o-', label=u'二氧化碳:')
		plt.plot(create_time,listtem, 'o-', label=u'溫度')
		plt.plot(create_time,listhum, 'o-', label=u'濕度')

    
		plt.gcf().set_size_inches(i+5,6)  #調整大小 先常在高 先Y軸在X軸 有點怪 把長度改成回全浮動 設未知數在上面 a=a++
		plt.xticks(create_time,rotation=15) #=90是直的 但是底下會被切掉 原因不明
		plt.xlabel('date-time')
		plt.ylabel(u'微克/立方公尺')
		plt.legend(loc='upper right')
		plt.savefig(img, format='png')
		img.seek(0)
                                                                #getvalue()
		plot_url = base64.b64encode(img.getvalue()).decode()        #使用Base64格式解碼或編碼二進制數據
                                                                #encode:編碼 decode:解碼
		return render_template('plot.html', plot_url=plot_url,name=name)
	else:
		return redirect('/')

@app.route('/door',methods=['GET','POST'])
def door():
	name = session.get('session_name')
	if name:
		if request.method =='GET': 
			return render_template('door.html')
	else:
		return redirect('/')
'''
@app.route('/door',methods=['GET','POST'])
def door():
	MotorPin=17
	GPIO.setup(MotorPin,GPIO.OUT)
	pwm_motor = GPIO.PWM(MotorPin, 50)
	pwm_motor.start(3.3)
	name = session.get('session_name')
	if name:
		if request.method =='GET': 
			return render_template('door.html')
		else:
			action = request.form.get('action','NULL')#將按鈕抓進來
			print(action)
			if action == 'on': #判斷按鈕的地方
				for a in range(100):
					pwm_motor.ChangeDutyCycle(3.3)
					time.sleep(0.01)
					print (a)
				#pwm_motor.stop()
				return redirect('/')
			elif action == 'off':
				for b in range(100):
					pwm_motor.ChangeDutyCycle(7.5)
					time.sleep(0.01)
					print (b)
				#pwm_motor.stop()
				return redirect('/door')	
	else:
		return redirect('/')
'''
@app.route('/LED',methods=['GET','POST'])
def LED():
	name = session.get('session_name')
	if name:
		if request.method =='GET':
			return render_template('LED.html')
	else:
		return redirect('/')
'''
@app.route('/LED',methods=['GET','POST'])
def LED():
	name = session.get('session_name')
	if name:
		if request.method =='GET':
			return render_template('LED.html')
    	else:
        	action = request.form.get('action','NULL')#將按鈕抓進來
        	print(action)
        	if action == 'light1-on': #判斷按鈕的地方
            	GPIO.output(LED1,GPIO.HIGH)
            	return redirect('/')
        	elif action == 'light1-off':
            	GPIO.output(LED1,GPIO.LOW)
            	return redirect('/')
        	elif action == 'light2-on':
            	GPIO.output(LED2,GPIO.HIGH)
            	return redirect('/')
        	elif action == 'light2-off':
				GPIO.output(LED2,GPIO.LOW)
            	return redirect('/')
        	elif action == 'light3-on':
            	GPIO.output(LED3,GPIO.HIGH)
            	return redirect('/')
        	elif action == 'light3-off':
            	GPIO.output(LED3,GPIO.LOW)
            	return redirect('/')
        	elif action == 'light4-on':
            GPIO.output(LED4,GPIO.HIGH)
            return redirect('/')
        elif action == 'light4-off':
            GPIO.output(LED4,GPIO.LOW)
            return redirect('/')
'''

@app.route('/logout/')
def logout():
        session.clear()
        return redirect(url_for('login'))
                                                              

if __name__ == '__main__':
    app.run(port=8000,debug =True)

