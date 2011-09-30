#!/usr/bin/env python
#
# GAE_RateMyName
#
import wsgiref.handlers
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

class rateableName(db.Model):
	firstname = db.StringProperty()
	lastname = db.StringProperty()
	when = db.DateTimeProperty(auto_now_add=True)
	upvotes = db.IntegerProperty(default=-1)
	downvotes = db.IntegerProperty(default=-1)

class MyHandler(webapp.RequestHandler):
	global detectRegisteredUsers
	def get(self):
		self.response.out.write("hmmmm interesting")
		
		self.response.out.write("""
          <html>
            <body>
              <form action="/sign" method="post">
                <div><br />operation: <input type="text" name="operation" /></div>

				<div>First Name: <input type="text" name="firstname" /> </div>
				
				<div>Last Name: <input type="text" name="lastname" /> </div>

                <input type="submit" value="submit"></div>
              </form>
            </body>
          </html>""")

	def post(self):
		#button press or a name addition?
		cmd = self.request.get('operation')
		
		if(cmd == "BUTTONPRESS"):
			votedFor = int(self.request.get('votedFor'))
			n = getCurrentNameToBeRated()
			if votedFor:
				for t in n:
					ups = t.upvotes
					downs = t.downvotes
					
					if ups + downs >= 100:
						#change current to non-current .... UPDATE
						name = n.get()
						name.current = 0
						name.put()
					else:
						#since this is the votedFor = true branch....
						name = n.get()
						name.upvotes = name.upvotes + 1
						name.put()
			else:
				name = n.get() # note sure if this syntax works (as opposed to the for loop with single-item array)
				name.downvotes = name.downvotes + 1
				name.put()

		elif cmd == "ADDMYNAME":
			fn = self.request.get('firstname')
			ln = self.request.get('lastname')
			
			if len(fn) <= 0 or len(ln) <= 0:
				self.response.out.write("ERROR found a zero length name...")
				return
				

			#to do: LANGUAGE FILTERING#

			insertableName = rateableName(firstname= fn, lastname=ln)
			insertableName.put()
			self.response.out.write('put name into db')
		
			# return all results... limited to a certain number  
			results = db.GqlQuery('SELECT * FROM rateableName ORDER BY when DESC LIMIT 50')
			for r in results:
				self.response.out.write("name: " + r.firstname + " " + r.lastname)
		else:
			self.response.out.write("unrecognized command -- " + cmd)
		
		
	def getCurrentNameToBeRated(self):
		responseString = ""
		name = db.GqlQuery("SELECT * FROM rateableName WHERE current = '1'")
		return name

def main():
	app = webapp.WSGIApplication([(r'.*', MyHandler)], debug=True)
	wsgiref.handlers.CGIHandler().run(app)	
if __name__ == "__main__":
	main()
