from flask import Flask, render_template, request, redirect, json, url_for
from flask.ext.mysql import MySQL

mysql = MySQL()
app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'zomato'
app.config['MYSQL_DATABASE_DB'] = 'test2'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route('/')
def main():
	return render_template('index.html')

@app.route('/showAddQuery')
def addQuery():
	return render_template('addOrder.html')

@app.route('/userHome',methods = ['POST','GET'])
def getQuery():
	if request.method == 'GET':
		try:
			main_list = show_output();
			return render_template('userHome.html', name = main_list);
		except Exception as e:
			return json.dumps({'error':str(e)})
	else: 
		try:
			userQuery();
			return redirect('/userHome')
		except Exception as e:
			return json.dumps({'error':str(e)})

# This function returns data that is used to draw charts
def show_output():
	main_list = []
	
	conn = mysql.connect()
	cursor = conn.cursor()

	cursor.execute("SELECT DISTINCT uid FROM a;")
	query_indexes = cursor.fetchall()

	for index in query_indexes:
		outer_list = []
		curr_index = int(index[0])
		sql = "SELECT query, chart FROM a WHERE uid = %d;" % (curr_index)
		cursor.execute(sql)
		data = cursor.fetchall()
		outer_list.append(json.loads(data[0][0]))
		outer_list.append(str(data[0][1]))
		main_list.append(outer_list)

	cursor.close() 
	conn.close()

	return main_list

# This function inputs the user query and stores the returned data
def userQuery():
	order_list = []
			
	conn = mysql.connect()
	cursor = conn.cursor()
	
	cursor.execute("UPDATE check_val SET last_val = last_val + 1 WHERE uid = 1;")
	data2 = cursor.fetchall()

	chart_type = request.form.get('chartType')
	
	sql = request.form['inputQuery']
	cursor.execute(sql)
	data = cursor.fetchall()

	for order in data:
		order_dict = [ order[0], order[1] ]
		order_list.append(order_dict)
	
	sqlQuery = "INSERT INTO a(query,chart,user_query) VALUES('%s','%s','%s');" % ((json.dumps(order_list)),str(chart_type),sql)
	cursor.execute(sqlQuery)
	conn.commit()
	cursor.close() 
	conn.close()

# App Run
if __name__ == '__main__':
	app.run(debug=True, port = 5002)
