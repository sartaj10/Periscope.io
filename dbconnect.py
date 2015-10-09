import MySQLdb

def connection():
	conn = MySQLdb.connect(host = "localhost",
						   user = "root",
						   passwd = "zomato",
						   db = "test2")
	cursor = conn.cursor()

	return conn,cursor