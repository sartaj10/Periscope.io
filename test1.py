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
			main_list, chart_list = show_output();
			return render_template('userHome.html', name = main_list, charts = chart_list);
		except Exception as e:
			return json.dumps({'error':str(e)})
	else: 
		try:
			user_query();
			return redirect('/userHome')
		except Exception as e:
			return json.dumps({'error':str(e)})

# This function returns data that is used to draw charts
def show_output():
	main_list = []

	index_list = []
	chart_list = []
	
	conn = mysql.connect()
	cursor = conn.cursor()

	cursor.execute("SELECT DISTINCT chart FROM output;")
	chart_list = cursor.fetchall()

	cursor.execute("SELECT DISTINCT query_index FROM output;")
	query_indexes = cursor.fetchall()

	for index in query_indexes:
		outer_list = []
		result_list = []
		
		curr_index = int(index[0])	

		sql = "SELECT DISTINCT chart FROM output WHERE query_index = %d;" % (curr_index)
		cursor.execute(sql)
		chart_list = cursor.fetchall()

		sql = "SELECT field1, field2 FROM output WHERE query_index = %d;" % (curr_index)
		cursor.execute(sql)
		data = cursor.fetchall()
		
		for result in data:
			result_dict = [int(result[0]),int(result[1])]
			result_list.append(result_dict)

		outer_list.append(result_list)
		outer_list.append(str(chart_list[0][0]))
		main_list.append(outer_list)

	cursor.close() 
	conn.close()

	return main_list, chart_list

# This function inputs the user query and stores the returned data
def user_query():
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
		order_dict = {
			'field1' : order[0],
			'field2' : order[1] }

		cursor.execute("SELECT last_val FROM check_val;")
		data2 = cursor.fetchall()
		
		query = "INSERT INTO output(field1,field2,query_index,chart) VALUES (%s,%s,%s,'%s');" % (order_dict['field1'], order_dict['field2'],int(data2[0][0]),str(chart_type))
		cursor.execute(query)
		
		conn.commit()
		order_list.append(order_dict)
	
	print order_list

	cursor.close() 
	conn.close()

# App Run
if __name__ == '__main__':
	app.run(debug=True, port = 5002)
