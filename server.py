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
eev=0
rendedit=False
utoadd=0


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
	global er
	er=None
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

	pw=sorted(fin, key=operator.itemgetter(8,9))
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
			val=thing[0]
			if not isinstance(val, int):
				val=val.encode('ascii','ignore')
			val=str(val).lower()
			if sval in val:
				res.append(thing)
		if dval=='hname':
			val=thing[1]
			if not isinstance(val, int):
				val=val.encode('ascii','ignore')
			val=str(val).lower()
			if sval in val:
				res.append(thing)
		if dval=='city':
			val=thing[3]
			if not isinstance(val, int):
				val=val.encode('ascii','ignore')
			val=str(val).lower()
			if sval in val:
				res.append(thing)
		if dval=='zip':
			val=thing[4]
			if not isinstance(val, int):
				val=val.encode('ascii','ignore')
			val=str(val).lower()
			if sval in val:
				res.append(thing)
		if dval=='state':
			val=thing[5]
			if not isinstance(val, int):
				val=val.encode('ascii','ignore')
			val=str(val).lower()
			if sval in val:
				res.append(thing)
		if dval=='loc_name':
			val=thing[6]
			if not isinstance(val, int):
				val=val.encode('ascii','ignore')
			val=str(val).lower()
			if sval in val:
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
	fin=sorted(fin, key=operator.itemgetter(8,9))
	if hid:
		return render_template("heventsearch.html", lis=fin)
	else:
		return render_template("eventsearch.html", lis=fin)

@app.route('/hhome')
def hhome():
	if uid:
		return redirect('/uhome')
	print hid
	global eev
	global er
	global rendedit
	rendedit=False
	er=None
	eev=0
	stmt = "SELECT e.ename, h.hname, t.tname, l.city, l.zip, l.state, l.loc_name, e.edate, e.time, e.photo, e.eid FROM Event_Create_Where e, Host h, Tags t, Marked m, Location l where e.lid=l.lid and e.uid=h.uid and t.tag_id=m.tag_id and e.eid=m.eid and e.uid = %s"
	cursor = g.conn.execute(stmt, (hid,))
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

	pw=sorted(fin, key=operator.itemgetter(8,9))

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

@app.route('/addfriend', methods=['GET', 'POST'])
def addfr():
	if hid:
		return redirect('/hhome')
	error=None
	today="2016-03-27"
	stmt= "SELECT * from Friend f where f.uid1=%s and f.uid2=%s UNION SELECT * from FRIEND f where f.uid1=%s and f.uid2=%s"
	cursor=g.conn.execute(stmt, (uid, utoadd, utoadd, uid))
	pw=[]
	for result in cursor:
		pw.append(result)
	friends=False
	if len(pw)>=1:
		friends=True
	print friends
	if not friends:
		stmt="INSERT into Friend VALUES (%s, %s, %s)"
		cursor=g.conn.execute(stmt, (uid, utoadd, today,))
	return redirect('/friends')
	

@app.route('/viewprof', methods=['GET', 'POST'])
def viewprof():
	if hid:
		return redirect('/hhome')
	user=request.form['drop']
	global utoadd
	print user
	utoadd=user
	stmt="SELECT name, loc FROM Reg_User WHERE uid = %s"
	cursor=g.conn.execute(stmt, (user,))
	uinfo=[]
	for result in cursor:
		uinfo.append(result)
	print uid
	print user
	user=int(user)
	stmt= "SELECT * from Friend f where f.uid1=%s and f.uid2=%s UNION SELECT * from FRIEND f where f.uid1=%s and f.uid2=%s"
	cursor=g.conn.execute(stmt, (uid, user, user, uid))
	fs="Not friends with this user"
	pw=[]
	for result in cursor:
		pw.append(result)
	notfriend=True
	if len(pw)>=1:
		notfriend=False
		for thing in pw:
			fs=thing[2]
	stmt = "SELECT e.ename, h.hname, t.tname, l.city, l.zip, l.state, l.loc_name, e.edate, e.time, e.photo FROM Event_Create_Where e, Host h, Tags t, Marked m, Location l, Going g where e.lid=l.lid and e.uid=h.uid and t.tag_id=m.tag_id and e.eid=m.eid and e.eid = g.eid and g.uid = %s"
	cursor = g.conn.execute(stmt, (user,))
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

	pw=sorted(fin, key=operator.itemgetter(8,9))

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
	
	return render_template('userpage.html', lis=uinfo, fs=fs, lis2=pw, inters=inters, notfriend=notfriend)

@app.route('/editevent', methods=['GET', 'POST'])
def editevent():
	print 'in editevent'
	if uid:
		return redirect('/uhome')
	global eev
	print rendedit
	if rendedit:
		eid=eev
	else:
		eid=request.form['drop']
		eev=eid
	print 'eid is '+str(eid)
	global er
	global renedit
	renedit=False
	stmt="SELECT * FROM Event_Create_Where e, Location l WHERE e.lid = l.lid and eid = %s"
	cursor=g.conn.execute(stmt, (eid,))
	pw=[]
	for result in cursor:
		pw.append(result)
	print pw
	name=pw[0][3]
	time=pw[0][4]
	date=pw[0][5]
	qty=pw[0][6]
	photo=pw[0][7]
	roomno=""
	if pw[0][11]:
		roomno=" "+str(pw[0][11])
	loc=str(pw[0][9])+roomno+" "+str(pw[0][10])+" "+str(pw[0][13])+" "+str(pw[0][12])+", "+str(pw[0][14])+" "+str(pw[0][15])
	stmt="SELECT o.eid, tt.type, ti.price FROM Owns_Tickets_Has_For o, Tick_Info ti, Tick_Type tt where o.eid = %s and o.eid=ti.eid and ti.typeid = tt.typeid"
	cursor=g.conn.execute(stmt, (eid,))
	tpr=[]
	for result in cursor:
		tpr.append(result)
	for thing in tpr:
		print thing
	print 'things'
	stmt = "SELECT e.ename, t.tname  FROM Event_Create_Where e, Tags t, Marked m where t.tag_id=m.tag_id and e.eid=m.eid and e.eid = %s"
	cursor = g.conn.execute(stmt, (eid,))
	pw=[]
	enames=[]
	tagdict={}
	for result in cursor:
		if result[0] in enames:
			l=len(pw)
			for i in range(0,l):
				if str(pw[i][0])==str(result[0]):
					dictval= tagdict[result[0]]
					newdictval = dictval+", "+str(result[1])
					tagdict[result[0]]=newdictval
		else:
			enames.append(result[0])
			tagdict[result[0]]=result[1]
			pw.append(result)
	fin=[]	
	for thing in pw:
		p=[]
		for x in range(0,len(thing)):
			p.extend([thing[x]])
			tags=tagdict[thing[0]]
		p.extend([tags])
		fin.append(p)
	tags= fin[0][2]

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
	stmt = "SELECT tname from Tags EXCEPT SELECT t.tname from Tags t, Marked m, Event_Create_Where e where t.tag_id = m.tag_id and m.eid=e.eid and e.eid= %s"
	cursor=g.conn.execute(stmt, (eid,))
	tg=[]
	for thing in cursor:
		for t in thing:
			tg.append(t)
	stmt="SELECT * from Location"
	cursor=g.conn.execute(stmt)
	locs=[]
	for thing in cursor:
		locs.append(thing)
	print locs
	return render_template("editevent.html", name=name, time=time, date=date, qty=qty, photo=photo, loc=loc, tags=tags, at=sold, going=going, seltags=seltags, useltags=tg, lis=locs, error=er)

@app.route('/delev', methods=['POST', 'GET'])
def delev():
	global eev
	stmt="DELETE FROM Event_Create_Where WHERE eid = %s"
	cursor=g.conn.execute(stmt, (eev,))
	return redirect('/hhome')

@app.route('/eec', methods=['POST', 'GET'])
def eec():
	global er
	er=None
	print eev
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
	print 'hi'
	print l
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
	stmt = "SELECT tname from Tags INTERSECT SELECT t.tname from Tags t, Marked m where t.tag_id = m.tag_id and m.eid= %s"
	cursor=g.conn.execute(stmt, (eev,))
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
			stmt="INSERT INTO Marked VALUES (%s, %s)"
			cursor=g.conn.execute(stmt, (var, eev))
			change=True
		elif x==False and thing in yw:
			var=0
			stmt= "SELECT * from Tags"
			cursor=g.conn.execute(stmt)
			alltags=[]
			for result in cursor:
				if result[1]==thing:
					var= int(result[0])
			stmt="DELETE FROM Marked WHERE tag_id=%s and eid=%s"
			cursor=g.conn.execute(stmt, (var, eev))
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

	newloc=False
	if lname!="" and bnum!="" and st!="" and city!="" and state!="" and zipc!="":
		newloc=True
		stmt="SELECT COUNT(lid) FROM Location"
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
	 
	if name=="" and time=="" and date=="" and qty=="" and photo =="" and ntag=="" and change==False and newloc==False and l==0:
		er= "No new data entered"
		return redirect("/editevent")

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
		stmt="SELECT COUNT(tag_id) FROM Tags"
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
	print locs
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
	l=request.form['drop']
	l=int(l)
	print 'hi'
	print l
	stmt= "SELECT COUNT(*) From Event_Create_Where"
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
		
	if name=="" or time=="" or date=="" or qty=="" or photo =="" or (ntag=="" and change==False) or (newloc==False and l==0):
		er= "All data not entered"
		return redirect("/evcr")
	
	lnum=0
	if l!=0:
		lnum=l
	if l==0 and newloc==True:
		stmt="SELECT COUNT(lid) FROM Location"
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
		stmt="SELECT COUNT(tag_id) FROM Tags"
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
	print uid
	global er
	er=None
	stmt = "SELECT e.ename, h.hname, t.tname, l.city, l.zip, l.state, l.loc_name, e.edate, e.time, e.photo FROM Event_Create_Where e, Host h, Tags t, Marked m, Reg_User r1, Reg_User r2, Friend f, Location l, Going g where e.lid=l.lid and e.uid=h.uid and t.tag_id=m.tag_id and e.eid=m.eid and e.eid = g.eid and g.uid = r2.uid and r1.uid!=r2.uid and r1.uid=f.uid1 and r2.uid=f.uid2 and r1.uid = %s UNION SELECT e.ename, h.hname, t.tname, l.city, l.zip, l.state, l.loc_name, e.edate, e.time, e.photo FROM Event_Create_Where e, Host h, Tags t, Marked m, Reg_User r1, Reg_User r2, Friend f, Location l, Going g where e.lid=l.lid and e.uid=h.uid and t.tag_id=m.tag_id and e.eid=m.eid and e.eid = g.eid and g.uid = r1.uid and r1.uid!=r2.uid and r1.uid=f.uid1 and r2.uid=f.uid2 and r2.uid = %s"
	cursor = g.conn.execute(stmt, (uid, uid,))
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

	pw=sorted(fin, key=operator.itemgetter(8,9))
	return render_template("friendevents.html", lis=pw)


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
