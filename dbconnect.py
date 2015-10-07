import MySQLdb

def connection():
	db = MySQLdb.connect(host = "localhost",
						   user = "root",
						   passwd = "zomato",
						   db = "test2")
	cursor = db.cursor()

	return cursor,db