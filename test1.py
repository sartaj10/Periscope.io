from flask import Flask, render_template, request, redirect, json, url_for
from dbconnect import connection

app = Flask(__name__)

# Home Page
@app.route('/')
def main():
	return render_template('index.html')

# Add Query Page
@app.route('/showAddQuery', methods = ['POST','GET'])
def addQuery():
	if request.method == 'GET':
		return render_template('addOrder.html')
	else:
		try:
			main_list = userQuery();
			return render_template('addOrder.html', name = main_list)
		except Exception as e:
			return json.dumps({'error':str(e)})

# User Dashboard
@app.route('/userHome',methods = ['GET'])
def getQuery():
	try:
		main_list = show_output();
		return render_template('userHome.html', name = main_list);
	except Exception as e:
		return json.dumps({'error':str(e)})

# Edit Chart 
@app.route('/editChart',methods = ['POST','GET'])
def editChart():
	if request.method == 'GET':
		data, chart_id = get_chart();
		return render_template('editOrder.html', query = str(data[0][0]), chartID = chart_id, chart_type = str(data[0][1]));
	else:
		main_list, chart_id = update_chart();
		return render_template('editOrder.html', name = main_list )

# Store Chart
@app.route('/storeChart',methods = ['POST'])
def storeChart():
	post_id = request.args.get('id')
	post_chart = json.dumps(request.args.get('chart'))
	
	conn, cursor = connection()
	sql = "INSERT INTO charts(hc) VALUES ('%s');" % (post_chart)
	cursor.execute(sql)
	conn.commit()

	return "True"

# Get chart data for editing
def get_chart():

	chart_id = request.args.get('chart_num')
	conn, cursor = connection()
	sql = "SELECT user_query, chart FROM a WHERE uid = %s;" % (chart_id)
	cursor.execute(sql)
	data = cursor.fetchall()

	return data,chart_id

# Update chart data
def update_chart():
	chart_type = request.form.get('chartType')
	chart_id = request.args.get('chart_num')

	conn, cursor = connection()
	sql = "UPDATE a SET chart = '%s' WHERE uid = %s;" % (chart_type, chart_id)
	cursor.execute(sql)
	conn.commit()

	sql = "SELECT query, chart, xaxis, yaxis FROM a WHERE uid = %s;" % (chart_id)
	cursor.execute(sql)
	data = cursor.fetchall()
	
	main_list = []
	outer_list = []

	outer_list = append_list(data,outer_list)
	main_list.append(outer_list)

	conn.commit()
	cursor.close() 
	conn.close()

	return main_list, chart_id

# This function returns data that is used to draw charts
def show_output():
	main_list = []
	
	conn, cursor = connection()
	cursor.execute("SELECT DISTINCT uid FROM a;")
	query_indexes = cursor.fetchall()

	for index in query_indexes:

		outer_list = []
		curr_index = int(index[0])
		
		sql = "SELECT query, chart, xaxis, yaxis FROM a WHERE uid = %d;" % (curr_index)
		cursor.execute(sql)
		data = cursor.fetchall()
		
		outer_list = append_list(data,outer_list)
		main_list.append(outer_list)

	cursor.close() 
	conn.close()

	return main_list

# This function inputs the user query and stores the returned data
def userQuery():
	main = []

	conn, cursor = connection()	
	cursor.execute("UPDATE check_val SET last_val = last_val + 1 WHERE uid = 1;")
	data2 = cursor.fetchall()

	chart_type = request.form.get('chartType')
	
	sql = request.form['inputQuery']
	cursor.execute(sql)
	query_return = cursor.fetchall()

	if(len(cursor.description) == 3):

		val1 = cursor.description[0][0] 
		val2 = cursor.description[1][0]
		val3 = cursor.description[2][0]

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
			
			order_list.sort(key=lambda x: x[0])
			series_name = {
				'name' : str(order[0]),
				'data' : order_list
			}
			main.append(series_name)

	else:

		val2 = cursor.description[0][0] 
		val3 = cursor.description[1][0]

		main = []
		order_list = []
		for order in query_return:
			order_dict = [ int(order[0]), int(order[1]) ]
			order_list.append(order_dict)
		
		order_list.sort(key=lambda x: x[0])
		series_name = {
				'name' : 'Chart',
				'data' : order_list
		}

		main.append(series_name)
	
	# Outside of if-else loop
	sqlQuery = "INSERT INTO a(query,chart,user_query,xaxis,yaxis) VALUES('%s','%s','%s','%s','%s');" % ((json.dumps(main)),str(chart_type),sql,val2,val3)
	cursor.execute(sqlQuery)

	sqlQuery = "SELECT last_val FROM check_val;"
	cursor.execute(sqlQuery)
	data = cursor.fetchall()

	sql = "SELECT query, chart, xaxis, yaxis FROM a WHERE uid = %d;" % (int(data[0][0]))
	cursor.execute(sql)
	data = cursor.fetchall()
	
	main_list = []
	outer_list = []

	outer_list = append_list(data,outer_list)
	main_list.append(outer_list)

	conn.commit()
	cursor.close() 
	conn.close()

	return main_list

def append_list(data, outer_list):

	outer_list.append(json.loads(data[0][0]))
	outer_list.append(str(data[0][1]))
	outer_list.append(str(data[0][2]))
	outer_list.append(str(data[0][3]))

	return outer_list

'''
# Delete Chart
@app.route('/deleteChart',methods = ['GET'])
def deleteChart():

	chart_id = request.args.get('chart_num')

	conn, cursor = connection()
	sql = "DELETE FROM a WHERE uid = %s;" % (chart_id)
	cursor.execute(sql)
	conn.commit()
	return redirect('/userHome')
'''

# App Run
if __name__ == '__main__':
	app.run(debug=True, port = 5002)
