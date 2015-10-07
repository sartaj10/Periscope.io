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
		# Fetch all data from the database test2 and table output -- if we have 1 query
		try:
			main_list = []
			index_list = []
			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.execute("SELECT DISTINCT query_index FROM output;")
			query_indexes = cursor.fetchall()
			for index in query_indexes:
				result_list = []
				curr_index = int(index[0])
				sql = "SELECT field1, field2 FROM output WHERE query_index = %d;" % (curr_index)
				cursor.execute(sql)
				data = cursor.fetchall()
				for result in data:
					result_dict = [int(result[0]),int(result[1])]
					result_list.append(result_dict)
				main_list.append(result_list)
			return render_template('userHome.html', name = main_list, div_id = 0);
		except Exception as e:
			return json.dumps({'error':str(e)})
		finally:
			cursor.close() 
			conn.close()
		pass
	else: 
		# Fetch data from input query and add that to output table
		try:
			order_list = []
			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.execute("UPDATE check_val SET last_val = last_val + 1 WHERE uid = 1;")
			data2 = cursor.fetchall()
			sql = request.form['inputQuery']
			cursor.execute(sql)
			data = cursor.fetchall()
			for order in data:
				order_dict = {
					'field1' : order[0],
					'field2' : order[1] }
				cursor.execute("USE test2")
				cursor.execute("SELECT last_val FROM check_val;")
				data2 = cursor.fetchall()
				query = "INSERT INTO output(field1,field2,query_index) VALUES (%s,%s,%s);" % (order_dict['field1'], order_dict['field2'],int(data2[0][0]))
				cursor.execute(query)
				conn.commit()
				order_list.append(order_dict)
			return redirect('/userHome')
		except Exception as e:
			return json.dumps({'error':str(e)})
		finally:
			cursor.close() 
			conn.close()

if __name__ == '__main__':
	app.run(debug=True, port = 5002)
