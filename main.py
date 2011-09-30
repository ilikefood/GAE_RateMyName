#!/usr/bin/env python
#
# server
#
import wsgiref.handlers
from google.appengine.ext import db
from google.appengine.exit import webapp
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

	def post(self):
		#button press or a name addition?
		cmd = self.request.get('operation')

		if(cmd == "BUTTONPRESS"):
			votedFor = int(self.request.get('votedFor')
			curName = getCurrentNameToBeRated()
			if votedFor:
				for t in curName:
					ups = t.upvotes
					downs = t.downvotes
					
					if ups + downs >= 100:
						#change current to non-current .... UPDATE
						name = curName.get()
						name.current = 0
						name.put()
					else:
						#since this is the votedFor = true branch....
						name = curName.get()
						name.upvotes = name.upvotes + 1
						name.put()
			else:
				name = curName.get() # note sure if this syntax works (as opposed to the for loop with single-item array)
				name.downvotes = name.downvotes + 1
				name.put()

			
		elif cmd == "ADDMYNAME":
			fn = self.request.get('firstname')
			ln = self.request.get('lastname')

			#to do: LANGUAGE FILTERING#

			insertableName = rateableName(firstname= fn, lastname=ln)
			insertableName.put()
			self.response.out.write('put name into db')
		
			# return all results... limited to a certain number  
			results = db...
		
		
	def getCurrentNameToBeRated():
		responseString = ""
		name = db.GqlQuery("SELECT * FROM rateableName WHERE current = '1'")
		if len(name) > 1:
			self.response.out.write("ERROR returned gt 1 current")
		else:
			return name
	
	


def main():
	app = webapp.WSGIApplication([(r'.*', MyHandler)], debug=True)
	wsgiref.handlers.CGIHandler().run(app)	
if __name__ == "__main__":
	main()
