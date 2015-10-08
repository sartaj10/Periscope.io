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

@app.route('/editChart',methods = ['POST','GET'])
def editChart():
	
	if request.method == 'GET':
		
		chart_id = request.args.get('chart_num')
		conn = mysql.connect()
		cursor = conn.cursor()
		
		sql = "SELECT user_query FROM a WHERE uid = %s;" % (chart_id)
		cursor.execute(sql)
		data = cursor.fetchall()
		
		return render_template('editOrder.html', query = str(data[0][0]), chartID = chart_id);
	
	else:
		
		chart_type = request.form.get('chartType')
		chart_id = request.args.get('chart_num')

		conn = mysql.connect()
		cursor = conn.cursor()

		sql = "UPDATE a SET chart = '%s' WHERE uid = %s;" % (chart_type, chart_id)
		cursor.execute(sql)
		conn.commit()

		return redirect('/userHome')

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
		
		sql = "SELECT query, chart, xaxis, yaxis FROM a WHERE uid = %d;" % (curr_index)
		cursor.execute(sql)
		data = cursor.fetchall()
		
		outer_list.append(json.loads(data[0][0]))
		outer_list.append(str(data[0][1]))
		outer_list.append(str(data[0][2]))
		outer_list.append(str(data[0][3]))
		main_list.append(outer_list)

	cursor.close() 
	conn.close()

	return main_list

# This function inputs the user query and stores the returned data
def userQuery():
	main = []	
	conn = mysql.connect()
	cursor = conn.cursor()
	
	cursor.execute("UPDATE check_val SET last_val = last_val + 1 WHERE uid = 1;")
	data2 = cursor.fetchall()

	chart_type = request.form.get('chartType')
	
	sql = request.form['inputQuery']
	cursor.execute(sql)
	query_return = cursor.fetchall()

	if(len(cursor.description) == 3):

		# Find parameters after SELECT
		val1 = cursor.description[0][0] 
		val2 = cursor.description[1][0] # month
		val3 = cursor.description[2][0] # temperature

		# Find Table Name
		query_words = sql.split()
		N = len(query_words)
		for i in range(N):
			if query_words[i] == 'FROM' or query_words[i] == 'from':
				table_name = query_words[i+1]
				break
		
		for i in range(N):
			if query_words[i] == 'ORDER' or query_words[i] == 'order':
				order_name = query_words[i+2]
				break

		query = "SELECT DISTINCT " + order_name + " FROM " + table_name + ";"

		cursor.execute(query)
		data = cursor.fetchall() 
		
		for order in data:
			
			order_list = []
			
			query = "SELECT " + str(val2) + "," + str(val3) + " FROM " + table_name + " WHERE " + str(order_name) + " = '" + str(order[0]) + "';"
			cursor.execute(query)
			data2 = cursor.fetchall()
			
			for value in data2 :
				order_dict = [ int(value[0]), int(value[1]) ]
				order_list.append(order_dict)
			
			series_name = {
				'name' : str(order[0]),
				'data' : order_list
			}
			main.append(series_name)
		
		sqlQuery = "INSERT INTO a(query,chart,user_query,xaxis,yaxis) VALUES('%s','%s','%s','%s','%s');" % ((json.dumps(main)),str(chart_type),sql,val2,val3)
		cursor.execute(sqlQuery)
		
		conn.commit()
		cursor.close() 
		conn.close()

	else:

		val2 = cursor.description[0][0] 
		val3 = cursor.description[1][0]

		main = []
		order_list = []
		for order in query_return:
			order_dict = [ int(order[0]), int(order[1]) ]
			order_list.append(order_dict)
		
		series_name = {
				'name' : 'Chart',
				'data' : order_list
		}

		main.append(series_name)
		
		sqlQuery = "INSERT INTO a(query,chart,user_query,xaxis,yaxis) VALUES('%s','%s','%s','%s','%s');" % ((json.dumps(main)),str(chart_type),sql,val2,val3)
		cursor.execute(sqlQuery)

		conn.commit()
		cursor.close() 
		conn.close()

# App Run
if __name__ == '__main__':
	app.run(debug=True, port = 5002)
