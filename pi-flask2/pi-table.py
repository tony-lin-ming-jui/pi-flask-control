import pymysql #刪除table 重新創建
db = pymysql.connect("127.0.0.1","root","1qaz1qaz","pi")
cursor = db.cursor()

cursor.execute("DROP TABLE IF EXISTS users")

users="""CREATE TABLE users ( 
         number Integer NOT NULL AUTO_INCREMENT,
         name varchar(15),
         password varchar(50),          
         PRIMARY KEY (number))"""
cursor.execute(users)