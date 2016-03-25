#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
import operator

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

uid=""
hid=""
er=""


#
# The following uses the sqlite3 database test.db -- you can use this for debugging purposes
# However for the project you will need to connect to your Part 2 database in order to use the
# data
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@w4111db.eastus.cloudapp.azure.com/username
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@w4111db.eastus.cloudapp.azure.com/ewu2493"
#
DATABASEURI = "sqlite:///Reg_User.db"
#DATABASEURI= "postgresql://cep2141:PPDZNL@w4111db.eastus.cloudapp.azure.com/cep2141"

#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


#
# START SQLITE SETUP CODE
#
# after these statements run, you should see a file test.db in your webserver/ directory
# this is a sqlite database that you can query like psql typing in the shell command line:
# 
#     sqlite3 test.db
#
# The following sqlite3 commands may be useful:
# 
#     .tables               -- will list the tables in the database
#     .schema <tablename>   -- print CREATE TABLE statement for table
# 
# The setup code should be deleted once you switch to using the Part 2 postgresql database
#

#
# END SQLITE SETUP CODE
#



@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost%sa=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print request.args


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT * FROM Reg_User")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  if uid:
	return redirect('/uhome')
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
@app.route('/userregister')
def uregister():
  if uid:
	return redirect('/uhome')
  if hid:
	return redirect('/hhome')
  return render_template("userregister.html")

@app.route('/uri', methods=['POST'])
def uri():
	error=None
	global uid
	if uid:
		return redirect('/uhome')
	if hid:
		return redirect('/hhome')
	uid=request.form['uid']
	name=request.form['name']
	password=request.form['password']
	loc=request.form['loc']
	try:
		uid=int(uid)
	except:
		error="UID must be an integer"
		return render_template("userregister.html", error=error)
	stmt="INSERT INTO Reg_User VALUES (%s, %s, %s, %s)"
	g.conn.execute(stmt, (uid, name, password, loc))
	cursor=g.conn.execute("SELECT * from Reg_User")
	names=[]
	for result in cursor:
		names.append(result)
	print names
	return redirect('/uhome')


@app.route('/hri', methods=['POST'])
def hri():
	error=None
	global hid
	if uid:
		return redirect('/uhome')
	if hid:
		return redirect('/hhome')
	hid=request.form['uid']
	name=request.form['name']
	password=request.form['password']
	hname=request.form['hname']
	try:
		hid=int(hid)
	except:
		error="UID must be an integer"
		return render_template("userregister.html", error=error)
	stmt="INSERT INTO Host VALUES (%s, %s, %s, %s)"
	g.conn.execute(stmt, (hid, name, password, hname))
	cursor=g.conn.execute("SELECT * from Host")
	names=[]
	for result in cursor:
		names.append(result)
	print names
	return redirect('/hhome')


@app.route('/hostregister')
def hregister():
  if uid:
	return redirect('/uhome')
  if hid:
	return redirect('/hhome')
  return render_template("hostregister.html")

@app.route('/userlogin')
def ulogin():
  if uid:
	return redirect('/uhome')
  if hid:
	return redirect('/hhome')
  return render_template("userlogin.html")

@app.route('/uli', methods=['POST'])
def uli():
	error=None
	global uid
        if uid:
		return redirect('/uhome')
	if hid:
		return redirect('/hhome')
	uid=request.form['uid']
	try:
		uid=int(uid)
	except:
		error= "UID must be an integer"
		return render_template("userlogin.html", error=error)

	password=request.form['password']
	stmt="SELECT password FROM Reg_User WHERE uid = %s"
	cursor=g.conn.execute(stmt, (uid,))
	pw=[]
  	for result in cursor:
    		pw.append(result)
	if pw[0]==(password,):
		return redirect('/uhome')
	error= "Invalid username/password"
	uid=""
	return render_template("userlogin.html", error=error)


@app.route('/hostlogin')
def hlogin():
  if uid:
	return redirect('/uhome')
  if hid:
	return redirect('/hhome')
  return render_template("hostlogin.html")

@app.route('/hli', methods=['POST'])
def hli():
	error=None
	global hid
        if uid:
		return redirect('/uhome')
	if hid:
		return redirect('/hhome')
	hid=request.form['uid']
	try:
		hid=int(hid)
	except:
		error= "UID must be an integer"
		return render_template("hostlogin.html", error=error)

	password=request.form['password']
	stmt="SELECT password FROM Host WHERE uid = %s"
	cursor=g.conn.execute(stmt, (hid,))
	pw=[]
  	for result in cursor:
    		pw.append(result)
	if pw[0]==(password,):
		return redirect('/hhome')
	else:
		error= "Invalid username/password"
		hid=""
		return render_template("hostlogin.html", error=error)

@app.route('/uhome')
def uhome():
	if hid:
		return redirect('/hhome')
	print uid
	stmt = "SELECT e.ename, h.hname, t.tname, l.city, l.zip, l.state, l.loc_name, e.edate, e.time, e.photo FROM Event_Create_Where e, Host h, Tags t, Marked m, Location l, Going g where e.lid=l.lid and e.uid=h.uid and t.tag_id=m.tag_id and e.eid=m.eid and e.eid = g.eid and g.uid = %s"
	cursor = g.conn.execute(stmt, (uid,))
	pw=[]
	enames=[]
	tagdict={}
	for result in cursor:
		if result[0] in enames:
			l=len(pw)
			for i in range(0,l):
				if str(pw[i][0])==str(result[0]):
					dictval= tagdict[result[0]]
					newdictval = dictval+", "+str(result[2])
					tagdict[result[0]]=newdictval
		else:
			enames.append(result[0])
			tagdict[result[0]]=result[2]
			pw.append(result)
	fin=[]	
	for thing in pw:
		p=[]
		for x in range(0,len(thing)):
			p.extend([thing[x]])
			tags=tagdict[thing[0]]
		p.extend([tags])
		fin.append(p)

	pw=sorted(fin, key=operator.itemgetter(2,3))
	return render_template("userhome.html", lis=pw)

@app.route('/logout')
def logout():
	global uid
	global hid
	uid=""
	hid=""
	return redirect('/')

@app.route('/usettings')
def usettings():
	error=None
	global er
	if hid:
		return redirect('/hsettings')
	if er:
		error=er
		er=""
	stmt = "SELECT name, password, loc from Reg_User where uid = %s"
	cursor=g.conn.execute(stmt, (uid,))
	pw=[]
	for result in cursor:
		pw.append(result)
	name = pw[0][0]
	password = pw[0][1]
	plen=len(password)
	password='x'*plen
	loc = pw[0][2]
	stmt = "SELECT tname from Tags EXCEPT SELECT t.tname from Tags t, Interested i where t.tag_id = i.tag_id and i.uid= %s"
	cursor=g.conn.execute(stmt, (uid,))
	xw=[]
	for result in cursor:
		for thing in result:
			xw.append(thing)
	print xw
	stmt = "SELECT tname from Tags INTERSECT SELECT t.tname from Tags t, Interested i where t.tag_id = i.tag_id and i.uid= %s"
	cursor=g.conn.execute(stmt, (uid,))
	yw=[]
	for result in cursor:
		for thing in result:
			yw.append(thing)
	print yw
	return render_template("usersettings.html", name=name, pw=password, loc=loc, seltags=yw, tags=xw, error=error)


@app.route('/friends')
def friends():
	return render_template("friends.html")

@app.route('/esearch')
def esearch():
	pw=[]
	if hid:
		return render_template("heventsearch.html", lis=pw)
	else:
		return render_template("eventsearch.html", lis=pw)

@app.route('/es', methods=['POST'])
def es():
	error=None
	dval=request.form['drop']
	sval=request.form['searched']
	pw = []
	stmt=""
	if not sval:
		error="No searchable value entered"
		if hid:
			return render_template("heventsearch.html", error=error)
		else:
			return render_template("eventsearch.html", error=error)
	sval=str(sval).lower()
	stmt="SELECT e.ename, h.hname, t.tname, l.city, l.zip, l.state, l.loc_name, e.edate, e.time, e.photo FROM Event_Create_Where e, Host h, Tags t, Marked m, Location l where e.lid=l.lid and e.uid=h.uid and t.tag_id=m.tag_id and e.eid=m.eid"
	cursor=g.conn.execute(stmt)
	enames=[]
	tagdict={}
	for result in cursor:
		if result[0] in enames:
			l=len(pw)
			for i in range(0,l):
				if str(pw[i][0])==str(result[0]):
					dictval= tagdict[result[0]]
					newdictval = dictval+", "+str(result[2])
					tagdict[result[0]]=newdictval
		else:
			enames.append(result[0])
			tagdict[result[0]]=result[2]
			pw.append(result)
	res=[]
	for thing in pw:
		if dval=='ename':
			if sval in str(thing[0]).lower():
				res.append(thing)
		if dval=='hname':
			if sval in str(thing[1]).lower():
				res.append(thing)
		if dval=='city':
			if sval in str(thing[3]).lower():
				res.append(thing)
		if dval=='zip':
			if sval in str(thing[4]).lower():
				res.append(thing)
		if dval=='state':
			if sval in str(thing[5]).lower():
				res.append(thing)
		if dval=='loc_name':
			if sval in str(thing[6]).lower():
				res.append(thing)
	if dval=='tag_name':
		for en, tg in tagdict.iteritems():
			if sval in str(tg).lower():
				for thing in pw:
					if thing[0]==en:
						res.append(thing)

	fin=[]	
	for thing in res:
		p=[]
		for x in range(0,len(thing)):
			p.extend([thing[x]])
			tags=tagdict[thing[0]]
		p.extend([tags])
		fin.append(p)
	if hid:
		return render_template("heventsearch.html", lis=fin)
	else:
		return render_template("eventsearch.html", lis=fin)

@app.route('/hhome')
def hhome():
	if uid:
		return redirect('/uhome')
	print hid
	stmt = "SELECT ename, edate, time, photo FROM Event_Create_Where WHERE uid = %s"
	cursor = g.conn.execute(stmt, (hid,))
	pw=[]
	for result in cursor:
		pw.append(result)
	pw=sorted(pw, key=operator.itemgetter(2,3))
	for thing in pw:
		print thing
	return render_template("hosthome.html", lis=pw)

@app.route('/hsettings')
def hsettings():
	error=None
	global er
	if uid:
		return redirect('/usettings')
	if er:
		error=er
		er=""
	stmt = "SELECT name, password, hname from Host where uid = %s"
	cursor=g.conn.execute(stmt, (hid,))
	pw=[]
	for result in cursor:
		pw.append(result)
	name = pw[0][0]
	password = pw[0][1]
	plen=len(password)
	password='x'*plen
	hname = pw[0][2]
	return render_template("hostsettings.html", name=name, pw=password, hname=hname, error=error)


@app.route('/ecreate')
def ecreate():
	return render_template("eventcreate.html")

@app.route('/usc', methods=['POST'])
def usc():
	error=""
	global er
	global uid
	if hid:
		return redirect('/hsettings')
	name=request.form['name']
	password=request.form['password']
	loc=request.form['loc']
	stmt = "SELECT tname from Tags INTERSECT SELECT t.tname from Tags t, Interested i where t.tag_id = i.tag_id and i.uid= %s"
	cursor=g.conn.execute(stmt, (uid,))
	yw=[]
	for result in cursor:
		for thing in result:
			yw.append(thing)
	stmt = "SELECT tname from Tags"
	cursor=g.conn.execute(stmt)
	xw=[]
	for result in cursor:
		for thing in result:
			xw.append(thing)
	print xw
	change=False
	for thing in xw:
		x=thing in request.form
		if x and thing in yw:
			continue
		elif x and thing not in yw:
			var=0
			stmt= "SELECT * from Tags"
			cursor=g.conn.execute(stmt)
			alltags=[]
			for result in cursor:
				if result[1]==thing:
					var= int(result[0])
			stmt="INSERT INTO Interested VALUES (%s, %s)"
			cursor=g.conn.execute(stmt, (var, uid))
			change=True
		elif x==False and thing in yw:
			var=0
			stmt= "SELECT * from Tags"
			cursor=g.conn.execute(stmt)
			alltags=[]
			for result in cursor:
				if result[1]==thing:
					var= int(result[0])
			stmt="DELETE FROM Interested WHERE tag_id=%s and uid=%s"
			cursor=g.conn.execute(stmt, (var, uid))
			change=True
		elif x==False and thing not in yw:
			continue
		else:
			er= "Something went wrong"
			return redirect("/usettings")
				 
	if name=="" and password=="" and loc=="" and change==False:
		er= "No new data entered"
		return redirect("/usettings")

	if name:
		stmt="UPDATE Reg_User SET name = %s WHERE uid = %s"
		cursor=g.conn.execute(stmt, (name, uid,))
	if password:
		stmt="UPDATE Reg_User SET password = %s WHERE uid = %s"
		cursor=g.conn.execute(stmt, (password, uid,))
	if loc:
		stmt="UPDATE Reg_User SET loc = %s WHERE uid = %s"
		cursor=g.conn.execute(stmt, (loc, uid,))
	return redirect("/usettings")

@app.route('/hsc', methods=['GET','POST'])
def hsc():
	error=""
	global er
	global hid
	if uid:
		return redirect('/usettings')
	name=request.form['name']
	password=request.form['password']
	hname=request.form['hname']
				 
	if name=="" and password=="" and hname=="":
		er= "No new data entered"
		return redirect("/hsettings")

	if name:
		stmt="UPDATE Host SET name = %s WHERE uid = %s"
		cursor=g.conn.execute(stmt, (name, hid,))
	if password:
		stmt="UPDATE Host SET password = %s WHERE uid = %s"
		cursor=g.conn.execute(stmt, (password, hid,))
	if hname:
		stmt="UPDATE Host SET hname = %s WHERE uid = %s"
		cursor=g.conn.execute(stmt, (hname, hid,))
	return redirect("/hsettings")


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=True, threaded=threaded)


  run()
