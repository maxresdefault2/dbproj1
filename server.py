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
import time

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

uid=""
hid=""
er=""
eev=0
rendedit=False
utoadd=0
gev=0
bid=0


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
#DATABASEURI = "sqlite:///Reg_User.db"
DATABASEURI= "postgresql://cep2141:PPDZNL@w4111db.eastus.cloudapp.azure.com/cep2141"

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
  global er
  if uid:
	return redirect('/uhome')
  if hid:
	return redirect('/hhome')
  return render_template("userregister.html", error=er)

@app.route('/uri', methods=['POST'])
def uri():
	global er
	er=None
	global uid
	if uid:
		return redirect('/uhome')
	if hid:
		return redirect('/hhome')
	uid=request.form['uid']
	name=request.form['name']
	password=request.form['password']
	loc=request.form['loc']
	if not uid or not name or not password:
		uid=""
		er="All required fields must be filled"
		return redirect('/userregister')
	try:
		uid=int(uid)
	except:
		uid=""
		er="UID must be an integer"
		return redirect('/userregister')
	stmt="SELECT * FROM Reg_User WHERE uid=%s"
	cursor=g.conn.execute(stmt, (uid,))
	rc= cursor.rowcount
	if rc!=0:
		uid=""
		er="UID taken, please enter a new number"
		return redirect('/userregister')
	if loc =="":
		stmt="INSERT INTO Reg_User VALUES (%s, %s, %s, null)"
		g.conn.execute(stmt, (uid, name, password,))
	else:
		stmt="INSERT INTO Reg_User VALUES (%s, %s, %s, %s)"
		g.conn.execute(stmt, (uid, name, password, loc))
	return redirect('/uhome')


@app.route('/hri', methods=['POST'])
def hri():
	global er
	er=None
	global hid
	if uid:
		return redirect('/uhome')
	if hid:
		return redirect('/hhome')
	hid=request.form['uid']
	name=request.form['name']
	password=request.form['password']
	hname=request.form['hname']
	if not hid or not name or not password or not hname:
		hid=""
		er="All required fields must be filled"
		return redirect('/hostregister')
	try:
		hid=int(hid)
	except:
		hid=""
		er="UID must be an integer"
		return redirect('/hostregister')
	stmt="SELECT * FROM Host WHERE uid=%s"
	cursor=g.conn.execute(stmt, (hid,))
	rc= cursor.rowcount
	if rc!=0:
		hid=""
		er="UID taken, please enter a new number"
		return redirect('/hostregister')
	stmt="INSERT INTO Host VALUES (%s, %s, %s, %s)"
	g.conn.execute(stmt, (hid, name, password, hname))
	cursor=g.conn.execute("SELECT * from Host")
	names=[]
	for result in cursor:
		names.append(result)
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
  global er
  if uid:
	return redirect('/uhome')
  if hid:
	return redirect('/hhome')
  return render_template("userlogin.html", error=er)

@app.route('/uli', methods=['POST'])
def uli():
	global er
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
		uid=""
		er= "UID must be an integer"
		return redirect('/userlogin')

	password=request.form['password']
	stmt="SELECT password FROM Reg_User WHERE uid = %s"
	cursor=g.conn.execute(stmt, (uid,))
	rc=cursor.rowcount
	if rc==0:
		er= "Invalid username/password"
		uid=""
		return redirect("/userlogin")
	pw=[]
  	for result in cursor:
    		pw.append(result)
	if pw[0]==(password,):
		return redirect('/uhome')
	er= "Invalid username/password"
	uid=""
	return redirect("/userlogin")


@app.route('/hostlogin')
def hlogin():
  global er
  if uid:
	return redirect('/uhome')
  if hid:
	return redirect('/hhome')
  return render_template("hostlogin.html", error=er)

@app.route('/hli', methods=['POST'])
def hli():
	global er
	er=None
	global hid
        if uid:
		return redirect('/uhome')
	if hid:
		return redirect('/hhome')
	hid=request.form['uid']
	try:
		hid=int(hid)
	except:
		hid=""
		er= "UID must be an integer"
		return redirect("/hostlogin")

	password=request.form['password']
	stmt="SELECT password FROM Host WHERE uid = %s"
	cursor=g.conn.execute(stmt, (hid,))
	rc=cursor.rowcount
	if rc==0:
		er= "Invalid username/password"
		hid=""
		return redirect("/hostlogin")
	pw=[]
  	for result in cursor:
    		pw.append(result)
	if pw[0]==(password,):
		return redirect('/hhome')
	else:
		er= "Invalid username/password"
		hid=""
		return redirect("/hostlogin")

@app.route('/uhome')
def uhome():
	if hid:
		return redirect('/hhome')
	global er
	er=None
	stmt = "SELECT e.ename, h.hname, l.city, l.zip, l.state, l.loc_name, e.edate, e.time, e.photo, e.eid FROM Event_Create_Where e, Host h, Going g, Location l where g.eid = e.eid and e.lid=l.lid and e.uid=h.uid and g.uid = %s"
	cursor = g.conn.execute(stmt, (uid,))
	nt=[]
	for thing in cursor:
		nt.append(thing)
	pw=[]
	enames=[]
	tagdict={}
	stmt="SELECT e.eid, t.tag_id, t.tname FROM Event_Create_Where e, Tags t, Marked m, Going g where g.eid = e.eid and e.eid=m.eid and t.tag_id=m.tag_id and g.uid=%s"
	cursor=g.conn.execute(stmt, (uid,))
	for result in cursor:
		r0=result[0]
		if not isinstance(r0, int) and not isinstance(r0, float) and r0:
			r0=r0.encode('ascii', 'ignore')
		r2=result[2]
		if not isinstance(r2, int) and not isinstance(r2, float) and r2:
			r2=r2.encode('ascii', 'ignore')
		if result[0] in enames:
			l=len(pw)
			for i in range(0,l):
				pwi0=pw[i][0]
				if not isinstance(pwi0, int) and not isinstance(pwi0, float) and pwi0:
					pwi0=pwi0.encode('ascii', 'ignore')
				if str(pwi0)==str(r0):
					dictval= tagdict[r0]
					newdictval = dictval+", "+str(r2)
					tagdict[r0]=newdictval
		else:
			enames.append(r0)
			tagdict[r0]=r2
			pw.append(result)
	fin=[]	
	for thing in nt:
		p=[]
		tags=""
		for xthing in pw:
			if xthing[0]==thing[9]:
				for x in range(0,len(thing)):
					p.extend([thing[x]])
				tags=tagdict[xthing[0]]
				p.extend([tags])
				fin.append(p)
		if tags=="":
			for x in range(0,len(thing)):
				p.extend([thing[x]])
			p.extend([tags])
			fin.append(p)
	pw=sorted(fin, key=operator.itemgetter(7,8))
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
	stmt = "SELECT tname, tag_id from Tags EXCEPT SELECT t.tname, t.tag_id from Tags t, Interested i where t.tag_id = i.tag_id and i.uid= %s"
	cursor=g.conn.execute(stmt, (uid,))
	xw=[]
	for result in cursor:
		xw.append(result)
	stmt = "SELECT tname, tag_id from Tags INTERSECT SELECT t.tname, t.tag_id from Tags t, Interested i where t.tag_id = i.tag_id and i.uid= %s"
	cursor=g.conn.execute(stmt, (uid,))
	yw=[]
	for result in cursor:
		yw.append(result	)
	return render_template("usersettings.html", name=name, pw=password, loc=loc, seltags=yw, tags=xw, error=error)


@app.route('/friends')
def friends():
	if hid:
		return redirect('/hhome')
	stmt= "SELECT r2.name, r2.loc, f.since, r2.uid FROM Friend f, Reg_User r1, Reg_User r2 WHERE r1.uid!=r2.uid and r1.uid = %s and r1.uid=f.uid1 and r2.uid=f.uid2 UNION SELECT r2.name, r2.loc, f.since, r2.uid FROM Friend f, Reg_User r1, Reg_User r2 WHERE r1.uid!=r2.uid and r1.uid = %s and r1.uid=f.uid2 and r2.uid=f.uid1"
	cursor=g.conn.execute(stmt, (uid, uid,))
	pw=[]
	for result in cursor:
		pw.append(result)
	pw=sorted(pw, key=operator.itemgetter(2))
	return render_template("friends.html", lis=pw)

@app.route('/esearch')
def esearch():
	pw=[]
	global rendedit
	rendedit = False
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
	if not isinstance(sval, int) and not isinstance (sval, float):
		sval=sval.encode('ascii', 'ignore')
	sval=str(sval).lower()
	stmt = "SELECT e.ename, h.hname, l.city, l.zip, l.state, l.loc_name, e.edate, e.time, e.photo, e.eid FROM Event_Create_Where e, Host h, Location l where e.lid=l.lid and e.uid=h.uid"
	cursor = g.conn.execute(stmt)
	nt=[]
	for thing in cursor:
		nt.append(thing)
	pw=[]
	enames=[]
	tagdict={}
	stmt="SELECT e.eid, t.tag_id, t.tname FROM Event_Create_Where e, Tags t, Marked m where e.eid=m.eid and t.tag_id=m.tag_id"
	cursor=g.conn.execute(stmt)
	for result in cursor:
		r0=result[0]
		if not isinstance(r0, int) and not isinstance(r0, float) and r0:
			r0=r0.encode('ascii', 'ignore')
		r2=result[2]
		if not isinstance(r2, int) and not isinstance(r2, float) and r2:
			r2=r2.encode('ascii', 'ignore')
		if result[0] in enames:
			l=len(pw)
			for i in range(0,l):
				pwi0=pw[i][0]
				if not isinstance(pwi0, int) and not isinstance(pwi0, float) and pwi0:
					pwi0=pwi0.encode('ascii', 'ignore')
				if str(pwi0)==str(r0):
					dictval= tagdict[r0]
					newdictval = dictval+", "+str(r2)
					tagdict[r0]=newdictval
		else:
			enames.append(r0)
			tagdict[r0]=r2
			pw.append(result)
	fin=[]	
	for thing in nt:
		p=[]
		tags=""
		for xthing in pw:
			if xthing[0]==thing[9]:
				for x in range(0,len(thing)):
					p.extend([thing[x]])
				tags=tagdict[xthing[0]]
				p.extend([tags])
				fin.append(p)
		if tags=="":
			for x in range(0,len(thing)):
				p.extend([thing[x]])
			p.extend([tags])
			fin.append(p)
	res=[]
	for thing in fin:
		if dval=='ename':
			val=thing[0]
			if not isinstance(val, int) and not isinstance(val, float):
				val=val.encode('ascii','ignore')
			val=str(val).lower()
			if sval in val:
				res.append(thing)
		if dval=='hname':
			val=thing[1]
			if not isinstance(val, int) and not isinstance(val, float):
				val=val.encode('ascii','ignore')
			val=str(val).lower()
			if sval in val:
				res.append(thing)
		if dval=='city':
			val=thing[2]
			if not isinstance(val, int) and not isinstance(val, float):
				val=val.encode('ascii','ignore')
			val=str(val).lower()
			if sval in val:
				res.append(thing)
		if dval=='zip':
			val=thing[3]
			if not isinstance(val, int) and not isinstance(val, float):
				val=val.encode('ascii','ignore')
			val=str(val).lower()
			if sval in val:
				res.append(thing)
		if dval=='state':
			val=thing[4]
			if not isinstance(val, int) and not isinstance(val, float):
				val=val.encode('ascii','ignore')
			val=str(val).lower()
			if sval in val:
				res.append(thing)
		if dval=='loc_name':
			val=thing[5]
			if not isinstance(val, int) and not isinstance(val, float):
				val=val.encode('ascii','ignore')
			val=str(val).lower()
			if sval in val:
				res.append(thing)
		if dval=='tag_name':
			val=thing[10]
			if not isinstance(val, int) and not isinstance(val, float):
				val=val.encode('ascii','ignore')
			val=str(val).lower()
			if sval in val:
				res.append(thing)

	fin=sorted(res, key=operator.itemgetter(8,9))
	if hid:
		return render_template("heventsearch.html", lis=fin)
	else:
		return render_template("eventsearch.html", lis=fin)

@app.route('/hhome')
def hhome():
	if uid:
		return redirect('/uhome')
	global eev
	global er
	global rendedit
	rendedit=False
	er=None
	eev=0
	stmt = "SELECT e.ename, h.hname, l.city, l.zip, l.state, l.loc_name, e.edate, e.time, e.photo, e.eid FROM Event_Create_Where e, Host h, Location l where e.lid=l.lid and e.uid=h.uid and e.uid = %s"
	cursor = g.conn.execute(stmt, (hid,))
	nt=[]
	for thing in cursor:
		nt.append(thing)
	pw=[]
	enames=[]
	tagdict={}
	stmt="SELECT e.eid, t.tag_id, t.tname FROM Event_Create_Where e, Tags t, Marked m where e.eid=m.eid and t.tag_id=m.tag_id and e.uid=%s"
	cursor=g.conn.execute(stmt, (hid,))
	for result in cursor:
		r0=result[0]
		if not isinstance(r0, int) and not isinstance(r0, float) and r0:
			r0=r0.encode('ascii', 'ignore')
		r2=result[2]
		if not isinstance(r2, int) and not isinstance(r2, float) and r2:
			r2=r2.encode('ascii', 'ignore')
		if result[0] in enames:
			l=len(pw)
			for i in range(0,l):
				pwi0=pw[i][0]
				if not isinstance(pwi0, int) and not isinstance(pwi0, float) and pwi0:
					pwi0=pwi0.encode('ascii', 'ignore')
				if str(pwi0)==str(r0):
					dictval= tagdict[r0]
					newdictval = dictval+", "+str(r2)
					tagdict[r0]=newdictval
		else:
			enames.append(r0)
			tagdict[r0]=r2
			pw.append(result)
	fin=[]	
	for thing in nt:
		p=[]
		tags=""
		for xthing in pw:
			if xthing[0]==thing[9]:
				for x in range(0,len(thing)):
					p.extend([thing[x]])
				tags=tagdict[xthing[0]]
				p.extend([tags])
				fin.append(p)
		if tags=="":
			for x in range(0,len(thing)):
				p.extend([thing[x]])
			p.extend([tags])
			fin.append(p)
	pw=sorted(fin, key=operator.itemgetter(7,8))

	return render_template("hosthome.html", lis=pw)

@app.route('/hsettings')
def hsettings():
	error=None
	global rendedit
	rendedit=False
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
	stmt = "SELECT tag_id from Tags INTERSECT SELECT t.tag_id from Tags t, Interested i where t.tag_id = i.tag_id and i.uid= %s"
	cursor=g.conn.execute(stmt, (uid,))
	yw=[]
	for result in cursor:
		for thing in result:
			yw.append(thing)
	stmt = "SELECT tag_id from Tags"
	cursor=g.conn.execute(stmt)

	xw=[]
	for result in cursor:
		for thing in result:
			xw.append(thing)
			
	change=False
	for thing in xw:
		if not isinstance(thing, int) and not isinstance (thing, float):
			thing=thing.encode('ascii', 'ignore')
		x=str(thing) in request.form
		if x and thing in yw:
			continue
		elif x and thing not in yw:
			stmt="INSERT INTO Interested VALUES (%s, %s)"
			cursor=g.conn.execute(stmt, (thing, uid))
			change=True
		elif not x and thing in yw:
			stmt="DELETE FROM Interested WHERE tag_id=%s and uid=%s"
			cursor=g.conn.execute(stmt, (thing, uid))
			change=True
		elif not x and thing not in yw:
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

@app.route('/addfriend', methods=['GET', 'POST'])
def addfr():
	if hid:
		return redirect('/hhome')
	error=None
	today=time.strftime("%Y-%m-%d")
	stmt= "SELECT * from Friend f where f.uid1=%s and f.uid2=%s UNION SELECT * from FRIEND f where f.uid1=%s and f.uid2=%s"
	cursor=g.conn.execute(stmt, (uid, utoadd, utoadd, uid))
	pw=[]
	for result in cursor:
		pw.append(result)
	friends=False
	if len(pw)>=1:
		friends=True
	if not friends:
		stmt="INSERT into Friend VALUES (%s, %s, %s)"
		cursor=g.conn.execute(stmt, (uid, utoadd, today,))
	return redirect('/friends')
	
@app.route('/delfriend', methods=['GET', 'POST'])
def delfr():
	if hid:
		return redirect('/hhome')
	error=None
	today="2016-03-27"
	stmt= "SELECT * from Friend f where f.uid1=%s and f.uid2=%s"
	cursor=g.conn.execute(stmt, (uid, utoadd,))
	rc=cursor.rowcount
	if rc>0:
		stmt="DELETE FROM Friend WHERE uid1 = %s and uid2 = %s"
		cursor=g.conn.execute(stmt, (uid, utoadd,))
	stmt= "SELECT * from Friend f where f.uid2=%s and f.uid1=%s"
	cursor=g.conn.execute(stmt, (uid, utoadd,))
	rc=cursor.rowcount
	if rc>0:
		stmt="DELETE FROM Friend WHERE uid2 = %s and uid1 = %s)"
		cursor=g.conn.execute(stmt, (uid, utoadd,))
	return redirect('/friends')

@app.route('/viewprof', methods=['GET', 'POST'])
def viewprof():
	user=request.form['drop']
	global utoadd
	utoadd=user
	stmt="SELECT name, loc FROM Reg_User WHERE uid = %s"
	cursor=g.conn.execute(stmt, (user,))
	uinfo=[]
	for result in cursor:
		uinfo.append(result)
	user=int(user)
	fs="Not friends with this user"
	notfriend=True
	friend=False
	if uid:
		stmt= "SELECT * from Friend f where f.uid1=%s and f.uid2=%s UNION SELECT * from FRIEND f where f.uid1=%s and f.uid2=%s"
		cursor=g.conn.execute(stmt, (uid, user, user, uid))
		pw=[]
		for result in cursor:
			pw.append(result)
		if uid and uid==user:
			notfriend=False
			fs="This is you"
		if len(pw)>=1:
			notfriend=False
			for thing in pw:
				fs=thing[2]
	if not notfriend:
		friend = True
	stmt = "SELECT e.ename, h.hname, l.city, l.zip, l.state, l.loc_name, e.edate, e.time, e.photo, e.eid FROM Event_Create_Where e, Host h, Location l, Going g where e.lid=l.lid and e.uid=h.uid and g.eid = e.eid and g.uid = %s"
	cursor = g.conn.execute(stmt, (user,))
	nt=[]
	for thing in cursor:
		nt.append(thing)
	pw=[]
	enames=[]
	tagdict={}
	stmt="SELECT e.eid, t.tag_id, t.tname FROM Event_Create_Where e, Tags t, Marked m, Going g where e.eid=m.eid and t.tag_id=m.tag_id and g.eid=e.eid and g.uid=%s"
	cursor=g.conn.execute(stmt, (user,))
	for result in cursor:
		r0=result[0]
		if not isinstance(r0, int) and not isinstance(r0, float) and r0:
			r0=r0.encode('ascii', 'ignore')
		r2=result[2]
		if not isinstance(r2, int) and not isinstance(r2, float) and r2:
			r2=r2.encode('ascii', 'ignore')
		if result[0] in enames:
			l=len(pw)
			for i in range(0,l):
				pwi0=pw[i][0]
				if not isinstance(pwi0, int) and not isinstance(pwi0, float) and pwi0:
					pwi0=pwi0.encode('ascii', 'ignore')
				if str(pwi0)==str(r0):
					dictval= tagdict[r0]
					newdictval = dictval+", "+str(r2)
					tagdict[r0]=newdictval
		else:
			enames.append(r0)
			tagdict[r0]=r2
			pw.append(result)
	fin=[]	
	for thing in nt:
		p=[]
		tags=""
		for xthing in pw:
			if xthing[0]==thing[9]:
				for x in range(0,len(thing)):
					p.extend([thing[x]])
				tags=tagdict[xthing[0]]
				p.extend([tags])
				fin.append(p)
		if tags=="":
			for x in range(0,len(thing)):
				p.extend([thing[x]])
			p.extend([tags])
			fin.append(p)
	pw=sorted(fin, key=operator.itemgetter(7,8))

	stmt="SELECT t.tname FROM Interested i, Reg_User r, Tags t WHERE i.uid=r.uid and t.tag_id=i.tag_id and r.uid = %s"
	cursor=g.conn.execute(stmt, (user,))
	ints=[]
	for thing in cursor:
		for inter in thing:
			ints.append(inter)
	i=0
	inters=""
	for thing in ints:
		if i==0:
			inters=thing
		else:
			inters+=", "+thing
		i+=1
	if hid:
		return render_template('userpage.html', lis=uinfo, fs=fs, lis2=pw, inters=inters)
	else:
		return render_template('userpage.html', lis=uinfo, fs=fs, lis2=pw, inters=inters, notfriend=notfriend, friend=friend, uid=True)

@app.route('/editevent', methods=['GET', 'POST'])
def editevent():
	if uid:
		return redirect('/uhome')
	global eev
	if rendedit:
		eid=eev
	else:
		eid=request.form['drop']
		eid=int(eid)
		eev=eid
	global er
	global renedit
	renedit=False
	stmt="SELECT * FROM Event_Create_Where e, Location l WHERE e.lid = l.lid and eid = %s"
	cursor=g.conn.execute(stmt, (eid,))
	pw=[]
	for result in cursor:
		pw.append(result)
	name=pw[0][3]
	time=pw[0][4]
	date=pw[0][5]
	qty=pw[0][6]
	photo=pw[0][7]
	roomno=""
	if pw[0][11]:
		p11=pw[0][11]
		if not isinstance(p11, int) and not isinstance(p11, float):
			p11=p11.encode('ascii', 'ignore')
		roomno=" "+str(p11)
		p9=pw[0][9]
		if not isinstance(p9, int) and not isinstance(p9, float) and p9:
			p9=p9.encode('ascii', 'ignore')
		p10=pw[0][10]
		if not isinstance(p10, int) and not isinstance(p10, float) and p10:
			p10=p10.encode('ascii', 'ignore')
		p13=pw[0][13]
		if not isinstance(p13, int) and not isinstance(p13, float) and p13:
			p13=p13.encode('ascii', 'ignore')
		p12=pw[0][12]
		if not isinstance(p12, int) and not isinstance(p12, float) and p12:
			p12=p12.encode('ascii', 'ignore')
		p14=pw[0][14]
		if not isinstance(p14, int) and not isinstance(p14, float) and p14:
			p14=p14.encode('ascii', 'ignore')
		p15=pw[0][15]
		if not isinstance(p15, int) and not isinstance(p15, float) and p15:
			p15=p15.encode('ascii', 'ignore')
	loc=str(p9)+roomno+" "+str(p10)+" "+str(p13)+" "+str(p12)+", "+str(p14)+" "+str(p15)
	stmt="SELECT tt.type, ti.price FROM Tick_Info ti, Tick_Type tt where ti.eid = %s  and ti.typeid = tt.typeid"
	cursor=g.conn.execute(stmt, (eid,))
	tpr=[]
	for result in cursor:
		tpr.append(result)
	ap=0.0
	ch=0.0
	stu=0.0
	sr=0.0
	for thing in tpr:
		if thing[0]=="adult":
			ap=thing[1]
		if thing[0]=="child":
			ch=thing[1]
		if thing[0]=="student":
			stu=thing[1]
		if thing[0]=="senior":
			sr=thing[1]
	ads=0
	chs=0
	sts=0
	srs=0
	stmt="SELECT SUM(qty) FROM Owns_Tickets_Has_For o, Tick_Type t where t.type='adult' and t.typeid=o.typeid and o.eid=%s"
	cursor=g.conn.execute(stmt, (eid,))
	for thing in cursor:
		if thing[0]:
			ads=int(thing[0])
	stmt="SELECT SUM(qty) FROM Owns_Tickets_Has_For o, Tick_Type t where t.type='child' and t.typeid=o.typeid and o.eid=%s"
	cursor=g.conn.execute(stmt, (eid,))
	for thing in cursor:
		if thing[0]:
			chs=int(thing[0])
	stmt="SELECT SUM(qty) FROM Owns_Tickets_Has_For o, Tick_Type t where t.type='student' and t.typeid=o.typeid and o.eid=%s"
	cursor=g.conn.execute(stmt, (eid,))
	for thing in cursor:
		if thing[0]:
			sts=int(thing[0])
	stmt="SELECT SUM(qty) FROM Owns_Tickets_Has_For o, Tick_Type t where t.type='senior' and t.typeid=o.typeid and o.eid=%s"
	cursor=g.conn.execute(stmt, (eid,))
	for thing in cursor:
		if thing[0]:
			srs=int(thing[0])
			
			
	stmt="SELECT e.eid, t.tag_id, t.tname FROM Event_Create_Where e, Tags t, Marked m where e.eid=m.eid and t.tag_id=m.tag_id and e.eid=%s"
	cursor=g.conn.execute(stmt, (eid,))
	tags=""
	rc=cursor.rowcount
	if rc>0:
		beg=True
		for result in cursor:
			t=result[2]
			if not isinstance(t, int) and not isinstance(t, float) and t:
					t=t.encode('ascii', 'ignore')
			if not isinstance(t, int):
				t=t.encode('ascii','ignore')
			if beg:
				beg=False
				tags=str(t)
			else:
				tags+=", "+str(t)
			
	for result in cursor:
		r0=result[0]
		if not isinstance(r0, int) and not isinstance(r0, float) and r0:
			r0=r0.encode('ascii', 'ignore')
		r2=result[2]
		if not isinstance(r2, int) and not isinstance(r2, float) and r2:
			r2=r2.encode('ascii', 'ignore')
		if result[0] in enames:
			l=len(pw)
			for i in range(0,l):
				pwi0=pw[i][0]
				if not isinstance(pwi0, int) and not isinstance(pwi0, float) and pwi0:
					pwi0=pwi0.encode('ascii', 'ignore')
				if str(pwi0)==str(r0):
					dictval= tagdict[r0]
					newdictval = dictval+", "+str(r2)
					tagdict[r0]=newdictval
		else:
			enames.append(r0)
			tagdict[r0]=r2
			pw.append(result)

	stmt="SELECT SUM(o.qty) FROM Owns_Tickets_Has_For o, Event_Create_Where e WHERE o.eid=e.eid and e.eid=%s"
	cursor=g.conn.execute(stmt, (eid,))
	x=[]
	for thing in cursor:
		for num in thing:
			x.append(num)
	sold= x[0]
	stmt="SELECT COUNT(*) FROM Going g WHERE eid=%s"
	cursor=g.conn.execute(stmt, (eid,))
	x=[]
	for thing in cursor:
		for num in thing:
			x.append(num)
	going= x[0]
	seltags=tags.split(',')
	stmt = "SELECT tname, tag_id from Tags EXCEPT SELECT t.tname, t.tag_id from Tags t, Marked m, Event_Create_Where e where t.tag_id = m.tag_id and m.eid=e.eid and e.eid= %s"
	cursor=g.conn.execute(stmt, (eid,))
	tg=[]
	for thing in cursor:
			tg.append(thing)
	stmt="SELECT * from Location"
	cursor=g.conn.execute(stmt)
	locs=[]
	for thing in cursor:
		locs.append(thing)
	stmt = "SELECT t.tname, t.tag_id from Tags t, Marked m, Event_Create_Where e where t.tag_id = m.tag_id and m.eid=e.eid and e.eid= %s"
	cursor=g.conn.execute(stmt, (eid,))
	seltags=[]
	for thing in cursor:
			seltags.append(thing)
	
	return render_template("editevent.html", name=name, time=time, date=date, qty=qty, photo=photo, loc=loc, tags=tags, at=sold, going=going, seltags=seltags, useltags=tg, lis=locs, ap=ap, ch=ch, st=stu, sr=sr, ads=ads, chs=chs, sts=sts, srs=srs, error=er)

@app.route('/delev', methods=['POST', 'GET'])
def delev():
	global eev
	stmt="DELETE FROM Marked WHERE eid = %s"
	cursor=g.conn.execute(stmt, (eev,))
	stmt="DELETE FROM Going WHERE eid = %s"
	cursor=g.conn.execute(stmt, (eev,))
	stmt="DELETE FROM Tick_Info WHERE eid=%s"
	cursor=g.conn.execute(stmt, (eev,))
	stmt="DELETE FROM Owns_Tickets_Has_For WHERE eid=%s"
	cursor=g.conn.execute(stmt, (eev,))
	stmt="DELETE FROM Event_Create_Where WHERE eid = %s"
	cursor=g.conn.execute(stmt, (eev,))
	return redirect('/hhome')

@app.route('/eec', methods=['POST', 'GET'])
def eec():
	global er
	er=None
	global rendedit
	rendedit=True
	if uid:
		return redirect('/usettings')
	name=request.form['name']
	time=request.form['time']
	date=request.form['date']
	qty=request.form['qty']
	photo=request.form['photo']
	ntag=request.form['ntag']
	l=request.form['drop']
	l=int(l)
	ad=request.form['adprice']
	ch=request.form['chprice']
	stu=request.form['stprice']
	sr=request.form['srprice']
	if qty:
		stmt="SELECT SUM(o.qty) FROM Owns_Tickets_Has_For o, Event_Create_Where e WHERE o.eid=e.eid and e.eid=%s"
		cursor=g.conn.execute(stmt, (eev,))
		x=[]
		for thing in cursor:
			for num in thing:
				x.append(num)
		sold= x[0]
		if int(qty)<int(sold):
			er="Ticket quantity cannot be less than amount sold"
			return redirect('/editevent')
	stmt = "SELECT tag_id from Tags INTERSECT SELECT t.tag_id from Tags t, Marked m where t.tag_id = m.tag_id and m.eid= %s"
	cursor=g.conn.execute(stmt, (eev,))
	yw=[]
	for result in cursor:
		for thing in result:
			yw.append(thing)
	stmt = "SELECT tag_id from Tags"
	cursor=g.conn.execute(stmt)
	xw=[]
	for result in cursor:
		for thing in result:
			xw.append(thing)
	change=False
	for thing in xw:
		if not isinstance(thing, int) and not isinstance(thing, float) and thing:
			thing=thing.encode('ascii', 'ignore')
		x=str(thing) in request.form
		if x and thing in yw:
			continue
		elif x and thing not in yw:
			stmt="INSERT INTO Marked VALUES (%s, %s)"
			cursor=g.conn.execute(stmt, (thing, eev))
			change=True
		elif not x and thing in yw:
			stmt="DELETE FROM Marked WHERE tag_id=%s and eid=%s"
			cursor=g.conn.execute(stmt, (thing, eev))
			change=True
		elif not x and thing not in yw:
			continue
		else:
			er= "Something went wrong"
			return redirect("/editevent")
			
	lname=request.form['lname']
	rname=request.form['rname']
	bnum=request.form['bnum']
	st=request.form['st']
	city=request.form['city']
	state=request.form['state']
	zipc=request.form['zipc']

	newloc=False
	if lname!="" and bnum!="" and st!="" and city!="" and state!="" and zipc!="":
		newloc=True
		stmt="SELECT MAX(lid) FROM Location"
		cursor=g.conn.execute(stmt)
		t=[]
		for thing in cursor:
			for xt in thing:
				t.append(xt)
		num=int(t[0])+1
		if rname=="":
			stmt="INSERT INTO Location VALUES (%s, %s, %s, null, %s, %s, %s, %s)"
			cursor=g.conn.execute(stmt, (num, lname, bnum, city, st, state, zipc,))
		else:
			stmt="INSERT INTO Location VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
			cursor=g.conn.execute(stmt, (num, lname, bnum, rname, city, st, state, zipc,))
		stmt="UPDATE Event_Create_Where SET lid = %s where eid = %s"
		cursor=g.conn.execute(stmt, (num, eev,))
	if newloc==False and (lname!="" or bnum!="" or st!="" or city!="" or state!="" or zipc!="" or rname!=""):
		er="Full location must be entered"
		return redirect("/editevent")
	 
	if name=="" and time=="" and date=="" and qty=="" and photo =="" and ntag=="" and ad=="" and ch=="" and stu=="" and sr=="" and change==False and newloc==False and l==0:
		er= "No new data entered"
		return redirect("/editevent")
	else:
		if ad:
			try:
				ad=float(ad)
			except:
				er="Prices must be numbers"
				return redirect("/editevent")
		if ch:
			try:
				ch=float(ch)
			except:
				er="Prices must be numbers"
				return redirect("/editevent")
		if stu:
			try:
				stu=float(stu)
			except:
				er="Prices must be numbers"
				return redirect("/editevent")
		if sr:
			try:
				sr=float(sr)
			except:
				er="Prices must be numbers"
				return redirect("/editevent")
		if ad:
			stmt="SELECT typeid from Tick_Type where type = 'adult'"
			cursor=g.conn.execute(stmt)
			pr=[]
			for thing in cursor:
				for pri in thing:
					pr.append(pri)
			typ=int(pr[0])
			stmt="UPDATE Tick_Info SET price = %s WHERE eid = %s and typeid=%s"
			cursor=g.conn.execute(stmt, (ad, eev, typ,))
		if ch:
			stmt="SELECT typeid from Tick_Type where type = 'child'"
			cursor=g.conn.execute(stmt)
			pr=[]
			for thing in cursor:
				for pri in thing:
					pr.append(pri)
			typ=int(pr[0])
			stmt="UPDATE Tick_Info SET price = %s WHERE eid = %s and typeid=%s"
			cursor=g.conn.execute(stmt, (ch, eev, typ,))
		if stu:
			stmt="SELECT typeid from Tick_Type where type = 'student'"
			cursor=g.conn.execute(stmt)
			pr=[]
			for thing in cursor:
				for pri in thing:
					pr.append(pri)
			typ=int(pr[0])
			stmt="UPDATE Tick_Info SET price = %s WHERE eid = %s and typeid=%s"
			cursor=g.conn.execute(stmt, (stu, eev, typ,))
		if sr:
			stmt="SELECT typeid from Tick_Type where type = 'senior'"
			cursor=g.conn.execute(stmt)
			pr=[]
			for thing in cursor:
				for pri in thing:
					pr.append(pri)
			typ=int(pr[0])
			stmt="UPDATE Tick_Info SET price = %s WHERE eid = %s and typeid=%s"
			cursor=g.conn.execute(stmt, (sr, eev, typ,))
		if name:
			stmt="UPDATE Event_Create_Where SET ename = %s WHERE eid = %s"
			cursor=g.conn.execute(stmt, (name, eev,))
		if time:
			stmt="UPDATE Event_Create_Where SET time = %s WHERE eid = %s"
			cursor=g.conn.execute(stmt, (time, eev,))
		if date:
			stmt="UPDATE Event_Create_Where SET edate = %s WHERE eid = %s"
			cursor=g.conn.execute(stmt, (date, eev,))
		if qty:
			stmt="UPDATE Event_Create_Where SET tickqty = %s WHERE eid = %s"
			cursor=g.conn.execute(stmt, (qty, eev,))
		if photo:
			stmt="UPDATE Event_Create_Where SET photo = %s WHERE eid = %s"
			cursor=g.conn.execute(stmt, (photo, eev,))
		if ntag:
			stmt="SELECT MAX(tag_id) FROM Tags"
			cursor=g.conn.execute(stmt)
			t=[]
			for thing in cursor:
				for xt in thing:
					t.append(xt)
			num=int(t[0])+1
			stmt="INSERT INTO Tags VALUES (%s, %s)"
			cursor=g.conn.execute(stmt, (num, ntag,))
			stmt="INSERT INTO Marked VALUES (%s, %s)"
			cursor=g.conn.execute(stmt, (num, eev,))
		if l!=0:
			stmt="UPDATE Event_Create_Where SET lid = %s WHERE eid = %s"
			cursor=g.conn.execute(stmt, (l, eev,))
	return redirect('/editevent')


@app.route('/evcr', methods=['GET', 'POST'])
def evcr():
	if uid:
		return redirect('/uhome')
	stmt = "SELECT tname from Tags"
	cursor=g.conn.execute(stmt)
	tg=[]
	for thing in cursor:
		for t in thing:
			tg.append(t)
	stmt="SELECT * from Location"
	cursor=g.conn.execute(stmt)
	locs=[]
	for thing in cursor:
		locs.append(thing)
	return render_template("eventcreate.html", useltags=tg, lis=locs, error=er)


@app.route('/create', methods=['POST', 'GET'])
def create():
	global er
	er=None
	if uid:
		return redirect('/usettings')
	
	name=request.form['name']
	time=request.form['time']
	date=request.form['date']
	qty=request.form['qty']
	photo=request.form['photo']
	ntag=request.form['ntag']
	ad=request.form['adprice']
	ch=request.form['chprice']
	stu=request.form['stprice']
	sr=request.form['srprice']
	l=request.form['drop']
	l=int(l)
	stmt= "SELECT MAX(eid) From Event_Create_Where"
	cursor=g.conn.execute(stmt)
	numevs=[]
	for thing in cursor:
		for xt in thing:
			numevs.append(xt)
	enum=int(numevs[0])+1
	stmt = "SELECT tname from Tags"
	cursor=g.conn.execute(stmt)
	xw=[]
	for result in cursor:
		for thing in result:
			xw.append(thing)
	yw=xw
	change=False
	for thing in xw:
		x=thing in request.form
		if x and thing in yw:
			continue
		elif x and thing not in yw:
			change=True
		elif x==False and thing in yw:
			change=True
		elif x==False and thing not in yw:
			continue
		else:
			er= "Something went wrong"
			return redirect("/editevent")
			
	lname=request.form['lname']
	rname=request.form['rname']
	bnum=request.form['bnum']
	st=request.form['st']
	city=request.form['city']
	state=request.form['state']
	zipc=request.form['zipc']
	ntag=request.form['ntag']

	newloc=False
	if lname!="" and bnum!="" and st!="" and city!="" and state!="" and zipc!="":
		newloc=True

	if name=="" or time=="" or date=="" or qty=="" or photo =="" or ad=="" or ch=="" or stu=="" or sr=="" or (newloc==False and l==0):
		er= "All data not entered"
		return redirect("/evcr")
	else:
		if ad:
			try:
				ad=float(ad)
			except:
				er="Prices must be numbers"
				return redirect("/editevent")
		if ch:
			try:
				ch=float(ch)
			except:
				er="Prices must be numbers"
				return redirect("/editevent")
		if stu:
			try:
				stu=float(stu)
			except:
				er="Prices must be numbers"
				return redirect("/editevent")
		if sr:
			try:
				sr=float(sr)
			except:
				er="Prices must be numbers"
				return redirect("/editevent")
		if ad:
			stmt="SELECT typeid from Tick_Type where type = 'adult'"
			cursor=g.conn.execute(stmt)
			pr=[]
			for thing in cursor:
				for pri in thing:
					pr.append(pri)
			typ=int(pr[0])
			stmt="INSERT INTO Tick_Info VALUES(%s, %s, %s)"
			cursor=g.conn.execute(stmt, (enum, typ, ad,))
		if ch:
			stmt="SELECT typeid from Tick_Type where type = 'child'"
			cursor=g.conn.execute(stmt)
			pr=[]
			for thing in cursor:
				for pri in thing:
					pr.append(pri)
			typ=int(pr[0])
			stmt="INSERT INTO Tick_Info VALUES(%s, %s, %s)"
			cursor=g.conn.execute(stmt, (enum, typ, ch,))
		if stu:
			stmt="SELECT typeid from Tick_Type where type = 'student'"
			cursor=g.conn.execute(stmt)
			pr=[]
			for thing in cursor:
				for pri in thing:
					pr.append(pri)
			typ=int(pr[0])
			stmt="INSERT INTO Tick_Info VALUES(%s, %s, %s)"
			cursor=g.conn.execute(stmt, (enum, typ, stu,))
		if sr:
			stmt="SELECT typeid from Tick_Type where type = 'senior'"
			cursor=g.conn.execute(stmt)
			pr=[]
			for thing in cursor:
				for pri in thing:
					pr.append(pri)
			typ=int(pr[0])
			stmt="INSERT INTO Tick_Info VALUES(%s, %s, %s)"
			cursor=g.conn.execute(stmt, (enum, typ, sr,))
	
		lnum=0
		if l!=0:
			lnum=l
		if l==0 and newloc==True:
			stmt="SELECT MAX(lid) FROM Location"
			cursor=g.conn.execute(stmt)
			lnum=0
			t=[]
			for thing in cursor:
				for xt in thing:
					t.append(xt)
				lnum=int(t[0])+1
				if rname=="":
					stmt="INSERT INTO Location VALUES (%s, %s, %s, null, %s, %s, %s, %s)"
					cursor=g.conn.execute(stmt, (lnum, lname, bnum, city, st, state, zipc,))	
				else:
					stmt="INSERT INTO Location VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
					cursor=g.conn.execute(stmt, (lnum, lname, bnum, rname, city, st, state, zipc,))
		
		stmt="INSERT INTO Event_Create_Where VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
		cursor=g.conn.execute(stmt, (enum, lnum, hid, name, time, date, qty, photo,)) 
		
		if ntag:
			stmt="SELECT MAX(tag_id) FROM Tags"
			cursor=g.conn.execute(stmt)
			t=[]
			for thing in cursor:
				for xt in thing:
					t.append(xt)
			num=int(t[0])+1
			stmt="INSERT INTO Tags VALUES (%s, %s)"
			cursor=g.conn.execute(stmt, (num, ntag,))
			stmt="INSERT INTO Marked VALUES (%s, %s)"
			cursor=g.conn.execute(stmt, (num, enum,))
		
		stmt = "SELECT tname from Tags INTERSECT SELECT t.tname from Tags t, Marked m where t.tag_id = m.tag_id and m.eid= %s"
		cursor=g.conn.execute(stmt, (enum,))
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
		for thing in xw:
			x=thing in request.form
			if x and thing not in yw:
				var=0
				stmt= "SELECT * from Tags"
				cursor=g.conn.execute(stmt)
				alltags=[]
				for result in cursor:
					if result[1]==thing:
						var= int(result[0])
				stmt="INSERT INTO Marked VALUES (%s, %s)"
				cursor=g.conn.execute(stmt, (var, enum))

	return redirect('/evcr')


@app.route('/frevs')
def frevs():
	if hid:
		return redirect('/hhome')
	global er
	er=None
	stmt = "SELECT e.ename, h.hname, l.city, l.zip, l.state, l.loc_name, e.edate, e.time, e.photo, e.eid FROM Event_Create_Where e, Host h, Reg_User r1, Reg_User r2, Friend f, Location l, Going g where e.lid=l.lid and e.uid=h.uid and e.eid = g.eid and g.uid = r2.uid and r1.uid!=r2.uid and r1.uid=f.uid1 and r2.uid=f.uid2 and r1.uid = %s UNION SELECT e.ename, h.hname, l.city, l.zip, l.state, l.loc_name, e.edate, e.time, e.photo, e.eid FROM Event_Create_Where e, Host h, Reg_User r1, Reg_User r2, Friend f, Location l, Going g where e.lid=l.lid and e.uid=h.uid and e.eid = g.eid and g.uid = r1.uid and r1.uid!=r2.uid and r1.uid=f.uid1 and r2.uid=f.uid2 and r2.uid = %s"
	cursor = g.conn.execute(stmt, (uid, uid,))
	nt=[]
	for thing in cursor:
		nt.append(thing)
	pw=[]
	enames=[]
	tagdict={}
	stmt="SELECT e.eid, t.tag_id, t.tname FROM Event_Create_Where e, Tags t, Marked m where e.eid=m.eid and t.tag_id=m.tag_id"
	cursor=g.conn.execute(stmt)
	for result in cursor:
		r0=result[0]
		if not isinstance(r0, int) and not isinstance(r0, float) and r0:
			r0=r0.encode('ascii', 'ignore')
		r2=result[2]
		if not isinstance(r2, int) and not isinstance(r2, float) and r2:
			r2=r2.encode('ascii', 'ignore')
		if result[0] in enames:
			l=len(pw)
			for i in range(0,l):
				pwi0=pw[i][0]
				if not isinstance(pwi0, int) and not isinstance(pwi0, float) and pwi0:
					pwi0=pwi0.encode('ascii', 'ignore')
				if str(pwi0)==str(r0):
					dictval= tagdict[r0]
					newdictval = dictval+", "+str(r2)
					tagdict[r0]=newdictval
		else:
			enames.append(r0)
			tagdict[r0]=r2
			pw.append(result)
	fin=[]	
	for thing in nt:
		p=[]
		tags=""
		for xthing in pw:
			if xthing[0]==thing[9]:
				for x in range(0,len(thing)):
					p.extend([thing[x]])
				tags=tagdict[xthing[0]]
				p.extend([tags])
				fin.append(p)
		if tags=="":
			for x in range(0,len(thing)):
				p.extend([thing[x]])
			p.extend([tags])
			fin.append(p)
	pw=sorted(fin, key=operator.itemgetter(7,8))
	return render_template("friendevents.html", lis=pw)
	
@app.route('/usearch')
def usearch():
	if hid:
		return render_template("husersearch.html")
	else:
		return render_template("usersearch.html")


@app.route('/us', methods=['POST'])
def us():
	error=None
	dval=request.form['drop']
	sval=request.form['searched']
	pw = []
	stmt=""
	if not sval:
		error="No searchable value entered"
		if hid:
			return render_template("husersearch.html", error=error)
		else:
			return render_template("usersearch.html", error=error)
	if not isinstance(sval, int) and not isinstance(sval, float):
		sval=sval.encode('ascii','ignore')
	sval=str(sval).lower()
	stmt="SELECT name, loc, uid FROM Reg_User"
	cursor=g.conn.execute(stmt)
	uinfo=[]
	res=[]
	for result in cursor:
		uinfo.append(result)
	for thing in uinfo:
		if dval=='uname':
			val=thing[0]
			if not isinstance(val, int) and not isinstance(val, float) and thing[0]:
				val=val.encode('ascii','ignore')
			val=str(val).lower()
			if sval in val:
				res.append(thing)
		if dval=='city':
			val=thing[1]
			if not isinstance(val, int) and not isinstance(val, float) and thing[1]:
				val=val.encode('ascii','ignore')
			val=str(val).lower()
			if sval in val:
				res.append(thing)
	fin=[]
	if res:
		user=""
		for thing in res:
			user=thing[2]
			fs="Not friends with this user"
			if uid:
				stmt= "SELECT * from Friend f where f.uid1=%s and f.uid2=%s UNION SELECT * from FRIEND f where f.uid1=%s and f.uid2=%s"
				cursor=g.conn.execute(stmt, (uid, user, user, uid))
				if uid and thing[2]==uid:
					fs="This is you"
				pw=[]
				for result in cursor:
					pw.append(result)
				if len(pw)>=1:
					for xthing in pw:
						fs=xthing[2]
			stmt="SELECT t.tname FROM Interested i, Reg_User r, Tags t WHERE i.uid=r.uid and t.tag_id=i.tag_id and r.uid = %s"
			cursor=g.conn.execute(stmt, (user,))
			ints=[]
			for xthing in cursor:
				for inter in xthing:
					ints.append(inter)
			i=0
			inters=""
			for xthing in ints:
				if i==0:
					inters=xthing
				else:
					inters+=", "+xthing
				i+=1
			
			p=[]
			p.extend([thing[0]])
			p.extend([thing[1]])
			p.extend([thing[2]])
			p.extend([fs])
			p.extend([inters])
			fin.append(p)
			
	if hid:
		return render_template("husersearch.html", lis=fin)
	else:
		return render_template("usersearch.html", lis=fin)
		
		
@app.route('/uticks')
def uticks():
	if hid:
		return redirect('/hhome')
	global er
	er=None
	stmt="SELECT ti.eid, tt.type, SUM(o.qty), SUM(ti.price*o.qty) from Owns_Tickets_Has_For o, Tick_Info ti, Tick_Type tt where o.eid=ti.eid and o.typeid=ti.typeid and tt.typeid=ti.typeid and tt.typeid=o.typeid and o.uid = %s group by ti.eid, tt.type"
	cursor=g.conn.execute(stmt, (uid,))
	ev=[]
	for result in cursor:
		ev.append(result)
	nev=[]
	vals=[]
	for thing in ev:
		vals.append(thing[0])
	v=list(set(vals))
	for thing in v:
		if not isinstance(thing, int) and not isinstance(thing, float) and thing:
			thing=thing.encode('ascii', 'ignore')
		p=[]
		p.extend([str(thing)])
		tdic={}
		cost=0
		for i in ev:
			if i[0]==thing:
				if i[1] in tdic.keys():
					tdic[i[1]]+=int(i[2])
				else:
					tdic[i[1]]=int(i[2])
				cost+=i[3]
		typestr=""
		typeitr=0
		for key, value in tdic.iteritems():
			if not isinstance(key, int) and not isinstance(key, float) and key:
				key=key.encode('ascii', 'ignore')
			if not isinstance(value, int) and not isinstance(value, float) and value:
				value=value.encode('ascii', 'ignore')
			if typeitr==0:
				typestr=str(key)+": "+str(value)
			else:
				typestr+=", "+str(key)+": "+str(value)
			typeitr+=1
		p.extend([typestr])
		if isinstance(cost, str) and cost:
				cost=cost.encode('ascii', 'ignore')
		p.extend([str(cost)])
		nev.append(p)
	fin=[]
	for ything in nev:
		eid=int(ything[0])
		stmt = "SELECT e.ename, h.hname, l.city, l.zip, l.state, l.loc_name, e.edate, e.time, e.photo, e.eid FROM Event_Create_Where e, Host h, Location l where e.lid=l.lid and e.uid=h.uid and e.eid = %s"
		cursor = g.conn.execute(stmt, (eid,))
		nt=[]
		for thing in cursor:
			nt.append(thing)
		pw=[]
		enames=[]
		tagdict={}
		stmt="SELECT e.eid, t.tag_id, t.tname FROM Event_Create_Where e, Tags t, Marked m where e.eid=m.eid and t.tag_id=m.tag_id and e.eid=%s"
		cursor=g.conn.execute(stmt, (eid,))
		for result in cursor:
			r0=result[0]
			if not isinstance(r0, int) and not isinstance(r0, float) and r0:
				r0=r0.encode('ascii', 'ignore')
			r2=result[2]
			if not isinstance(r2, int) and not isinstance(r2, float) and r2:
				r2=r2.encode('ascii', 'ignore')
			if result[0] in enames:
				l=len(pw)
				for i in range(0,l):
					pwi0=pw[i][0]
					if not isinstance(pwi0, int) and not isinstance(pwi0, float) and pwi0:
						pwi0=pwi0.encode('ascii', 'ignore')
					if str(pwi0)==str(r0):
						dictval= tagdict[r0]
						newdictval = dictval+", "+str(r2)
						tagdict[r0]=newdictval
			else:
				enames.append(r0)
				tagdict[r0]=r2
				pw.append(result)
		for thing in nt:
			p=[]
			tags=""
			for xthing in pw:
				if xthing[0]==thing[9]:
					for x in range(0,len(thing)):
						p.extend([thing[x]])
					tags=tagdict[xthing[0]]
					p.extend([tags])
			if tags=="":
				for x in range(0,len(thing)):
					p.extend([thing[x]])
				p.extend([tags])
			p.extend([ything[0]])
			p.extend([ything[1]])
			p.extend([ything[2]])
			fin.append(p)
	
	pw=sorted(fin, key=operator.itemgetter(7,8))
	return render_template("usertickets.html", lis=pw)

@app.route('/uviewev', methods=['GET', 'POST'])
def uviewev():
	eid=request.form['drop']
	global gev
	gev=int(eid)
	stmt = "SELECT e.ename, h.hname, l.city, l.zip, l.state, l.loc_name, e.edate, e.time, e.photo, e.eid FROM Event_Create_Where e, Host h, Location l where e.lid=l.lid and e.uid=h.uid and e.eid = %s"
	cursor = g.conn.execute(stmt, (gev,))
	nt=[]
	for thing in cursor:
		nt.append(thing)
	pw=[]
	enames=[]
	tagdict={}
	stmt="SELECT e.eid, t.tag_id, t.tname FROM Event_Create_Where e, Tags t, Marked m where e.eid=m.eid and t.tag_id=m.tag_id and e.eid=%s"
	cursor=g.conn.execute(stmt, (gev,))
	for result in cursor:
		r0=result[0]
		if not isinstance(r0, int) and not isinstance(r0, float) and r0:
			r0=r0.encode('ascii', 'ignore')
		r2=result[2]
		if not isinstance(r2, int) and not isinstance(r2, float) and r2:
			r2=r2.encode('ascii', 'ignore')
		if result[0] in enames:
			l=len(pw)
			for i in range(0,l):
				pwi0=pw[i][0]
				if not isinstance(pwi0, int) and not isinstance(pwi0, float) and pwi0:
					pwi0=pwi0.encode('ascii', 'ignore')
				if str(pwi0)==str(r0):
					dictval= tagdict[r0]
					newdictval = dictval+", "+str(r2)
					tagdict[r0]=newdictval
		else:
			enames.append(r0)
			tagdict[r0]=r2
			pw.append(result)
	fin=[]	
	for thing in nt:
		p=[]
		tags=""
		for xthing in pw:
			if xthing[0]==thing[9]:
				for x in range(0,len(thing)):
					p.extend([thing[x]])
				tags=tagdict[xthing[0]]
				p.extend([tags])
				fin.append(p)
		if tags=="":
			for x in range(0,len(thing)):
				p.extend([thing[x]])
			p.extend([tags])
			fin.append(p)

	pw=sorted(fin, key=operator.itemgetter(7,8))
	
	if hid:
		return render_template('hosteventpage.html', lis=pw)
	else:
		going=False
		stmt="SELECT * FROM Going WHERE uid = %s and eid = %s"
		cursor=g.conn.execute(stmt, (uid, eid,))
		d=[]
		for thing in cursor:
			d.append(thing)
		if d:
			going=True
		return render_template('usereventpage.html', lis=pw, going=going)

@app.route('/going', methods=['POST'])
def going():
	global gev
	print gev
	going=request.form.getlist('going')
	print going
	stmt="SELECT * FROM Going where eid=%s and uid=%s"
	cursor=g.conn.execute(stmt, (gev, uid,))
	rc= cursor.rowcount
	print rc
	if going and rc==0:
		stmt="INSERT INTO Going VALUES(%s, %s)"
		cursor=g.conn.execute(stmt, (uid, gev,))
	if not going and rc>0:
		stmt="DELETE FROM Going WHERE uid=%s and eid=%s"
		cursor=g.conn.execute(stmt, (uid, gev,))
	return redirect('/uhome')
	
@app.route('/buytick')
def buytick():
	if hid:
		return redirect('/hhome')
	global gev
	stmt = "SELECT e.ename, h.hname, l.city, l.zip, l.state, l.loc_name, e.edate, e.time, e.photo, e.eid FROM Event_Create_Where e, Host h, Location l where e.lid=l.lid and e.uid=h.uid and e.eid = %s"
	cursor = g.conn.execute(stmt, (gev,))
	nt=[]
	for thing in cursor:
		nt.append(thing)
	pw=[]
	enames=[]
	tagdict={}
	stmt="SELECT e.eid, t.tag_id, t.tname FROM Event_Create_Where e, Tags t, Marked m where e.eid=m.eid and t.tag_id=m.tag_id and e.eid=%s"
	cursor=g.conn.execute(stmt, (gev,))
	for result in cursor:
		r0=result[0]
		if not isinstance(r0, int) and not isinstance(r0, float) and r0:
			r0=r0.encode('ascii', 'ignore')
		r2=result[2]
		if not isinstance(r2, int) and not isinstance(r2, float) and r2:
			r2=r2.encode('ascii', 'ignore')
		if result[0] in enames:
			l=len(pw)
			for i in range(0,l):
				pwi0=pw[i][0]
				if not isinstance(pwi0, int) and not isinstance(pwi0, float) and pwi0:
					pwi0=pwi0.encode('ascii', 'ignore')
				if str(pwi0)==str(r0):
					dictval= tagdict[r0]
					newdictval = dictval+", "+str(r2)
					tagdict[r0]=newdictval
		else:
			enames.append(r0)
			tagdict[r0]=r2
			pw.append(result)
	fin=[]	
	for thing in nt:
		p=[]
		tags=""
		for xthing in pw:
			if xthing[0]==thing[9]:
				for x in range(0,len(thing)):
					p.extend([thing[x]])
				tags=tagdict[xthing[0]]
				p.extend([tags])
				fin.append(p)
		if tags=="":
			for x in range(0,len(thing)):
				p.extend([thing[x]])
			p.extend([tags])
			fin.append(p)

	pw=sorted(fin, key=operator.itemgetter(7,8))
	
	stmt="SELECT ti.eid, tt.type, SUM(o.qty), SUM(ti.price*o.qty) from Owns_Tickets_Has_For o, Tick_Info ti, Tick_Type tt where o.eid=ti.eid and o.typeid=ti.typeid and tt.typeid=ti.typeid and tt.typeid=o.typeid and o.uid = %s and o.eid = %s group by ti.eid, tt.type"
	cursor=g.conn.execute(stmt, (uid, gev,))
	ev=[]
	for result in cursor:
		ev.append(result)
	nev=[]
	vals=[]
	for thing in ev:
		vals.append(thing[0])
	v=list(set(vals))
	for thing in v:
		p=[]
		if not isinstance(thing, int) and not isinstance(thing, float) and thing:
			thing=thing.encode('ascii', 'ignore')
		p.extend([str(thing)])
		tdic={}
		cost=0
		for i in ev:
			if i[0]==thing:
				if i[1] in tdic.keys():
					tdic[i[1]]+=int(i[2])
				else:
					tdic[i[1]]=int(i[2])
				cost+=i[3]
		typestr=""
		typeitr=0
		for key, value in tdic.iteritems():
			if not isinstance(key, int) and not isinstance(key, float) and key:
				key=key.encode('ascii', 'ignore')
			if not isinstance(value, int) and not isinstance(value, float) and value:
				value=value.encode('ascii', 'ignore')
			if typeitr==0:
				typestr=str(key)+": "+str(value)
			else:
				typestr+=", "+str(key)+": "+str(value)
			typeitr+=1
		p.extend([typestr])
		if isinstance(cost, str) and cost:
				cost=cost.encode('ascii', 'ignore')
		p.extend([str(cost)])
		nev.append(p)
	
	stmt="SELECT tt.type, ti.price FROM Tick_Info ti, Tick_Type tt where ti.eid = %s  and ti.typeid = tt.typeid"
	cursor=g.conn.execute(stmt, (gev,))
	tpr=[]
	for result in cursor:
		tpr.append(result)
	ap=0.0
	ch=0.0
	stu=0.0
	sr=0.0
	for thing in tpr:
		if thing[0]=="adult":
			ap=thing[1]
		if thing[0]=="child":
			ch=thing[1]
		if thing[0]=="student":
			stu=thing[1]
		if thing[0]=="senior":
			sr=thing[1]
	
	return render_template('buytickets.html', lis=pw, lis2=nev, ap=ap, ch=ch, stu=stu, sr=sr, error=er)

@app.route('/buying', methods=['POST'])
def buying():
	if hid:
		return redirect('/hhome')
	global gev
	global er
	er=None
	ad=request.form['adprice']
	ch=request.form['chprice']
	stu=request.form['stprice']
	sr=request.form['srprice']
	if ad:
		try:
			ad=int(ad)
		except:
			er="Quantity must be an integer"
			return redirect('/buytick')
	if ch:
		try:
			ch=int(ch)
		except:
			er="Quantity must be an integer"
			return redirect('/buytick')
	if sr:
		try:
			sr=int(sr)
		except:
			er="Quantity must be an integer"
			return redirect('/buytick')
	if stu:
		try:
			stu=int(stu)
		except:
			er="Quantity must be an integer"
			return redirect('/buytick')
	if not ad and not ch and not sr and not stu:
		er="No value entered"
		return redirect('/buytick')
	stmt="SELECT MAX(tid) FROM Owns_Tickets_Has_For"
	cursor=g.conn.execute(stmt)
	t=[]
	for thing in cursor:
		for xt in thing:
			t.append(xt)
	tid=int(t[0])+1
	if ad:
		stmt="SELECT typeid from Tick_Type where type = 'adult'"
		cursor=g.conn.execute(stmt)
		pr=[]
		for thing in cursor:
			for pri in thing:
				pr.append(pri)
		typ=int(pr[0])
		stmt="INSERT INTO Owns_Tickets_Has_For VALUES(%s, %s, %s, %s, %s)"
		cursor=g.conn.execute(stmt, (tid, uid, gev, ad, typ,))
		tid+=1
	if ch:
		stmt="SELECT typeid from Tick_Type where type = 'child'"
		cursor=g.conn.execute(stmt)
		pr=[]
		for thing in cursor:
			for pri in thing:
				pr.append(pri)
		typ=int(pr[0])
		stmt="INSERT INTO Owns_Tickets_Has_For VALUES(%s, %s, %s, %s, %s)"
		cursor=g.conn.execute(stmt, (tid, uid, gev, ch, typ,))
		tid+=1
	if stu:
		stmt="SELECT typeid from Tick_Type where type = 'student'"
		cursor=g.conn.execute(stmt)
		pr=[]
		for thing in cursor:
			for pri in thing:
				pr.append(pri)
		typ=int(pr[0])
		stmt="INSERT INTO Owns_Tickets_Has_For VALUES(%s, %s, %s, %s, %s)"
		cursor=g.conn.execute(stmt, (tid, uid, gev, st, typ,))
		tid+=1
	if sr:
		stmt="SELECT typeid from Tick_Type where type = 'senior'"
		cursor=g.conn.execute(stmt)
		pr=[]
		for thing in cursor:
			for pri in thing:
				pr.append(pri)
		typ=int(pr[0])
		stmt="INSERT INTO Owns_Tickets_Has_For VALUES(%s, %s, %s, %s, %s)"
		cursor=g.conn.execute(stmt, (tid, uid, gev, sr, typ,))
		tid+=1
	return redirect('/buytick')
	
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
