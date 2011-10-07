#!/usr/bin/env python
#
# GAE_ratemyname
#
import wsgiref.handlers
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import re
THRESHHOLD = 7

class rateableName(db.Model):
	firstname = db.StringProperty()
	lastname = db.StringProperty()
	when = db.DateTimeProperty(auto_now_add=True)
	upvotes = db.IntegerProperty(default=-1)
	downvotes = db.IntegerProperty(default=-1)
	current = db.BooleanProperty(default=False)

class MyHandler(webapp.RequestHandler):
	global getCurrentNameToBeRated
	global isContentSafe
	global incrementCurrentNameToBeRated
	global decrementCurrentNameToBeRated
	global deThroneCurrentName
	def get(self):
		self.response.out.write("<title>demo</title>")
		
		self.response.out.write("""
          <html>
            <body>
              <form action="/index.html" method="post">
                <div><br />operation: <input type="text" name="operation" /></div>
				<div>votedFor: <input type="text" name="votedFor" /> </div>
				<div>First Name: <input type="text" name="firstname" /> </div>
				<div>Last Name: <input type="text" name="lastname" /> 
                <input type="submit" value="submit"></div>
              </form>
            </body>
          </html>""")
	
	# run_in_transaction calls
	def deThroneCurrentName(key):
		thisEntry = db.get(key)
		thisEntry.current = False
		db.put(thisEntry)
	
	def incrementCurrentNameToBeRated(key, amount=1):
		thisEntry = db.get(key)
		if thisEntry.upvotes < 0:
			thisEntry.upvotes = 0
		thisEntry.upvotes = thisEntry.upvotes + 1
		db.put(thisEntry)
		
	def decrementCurrentNameToBeRated(key, amount=1):
		thisEntry = db.get(key)
		if thisEntry.downvotes < 0:
			thisEntry.downvotes = 0
		thisEntry.downvotes = thisEntry.downvotes + 1
		db.put(thisEntry)
	
	def post(self):
		#button press or a name addition?
		cmd = self.request.get('operation')
		
		if(cmd == "BUTTONPRESS"):
			votedFor = int(self.request.get('votedFor'))
			n = getCurrentNameToBeRated(self)
			voteShouldBeCounted = True
			
			
			#call a run_in_transaction for the below items
			
			for t in n:
				ups = t.upvotes
				downs = t.downvotes
				if ups == -1:
					ups = 0
				if downs == -1:
					downs = 0
				if ups + downs >= THRESHHOLD:  #THRESHOLD
					#change current to non-current .... UPDATE
					#name = n.get()
					#name.current = False
					#name.put()
					thisEntry = n.get()
					db.run_in_transaction(deThroneCurrentName, thisEntry.key())
					voteShouldBeCounted = False
				break
			if votedFor and voteShouldBeCounted:
				#since this is the votedFor = true branch....  UPDATE
				thisEntry = n.get()
				db.run_in_transaction(incrementCurrentNameToBeRated, thisEntry.key(), amount=1)
				self.response.out("vote was counted (incremented)")
				#name.put()
			elif not votedFor and voteShouldBeCounted:
				
				#UPDATE
				name = n.get() # note sure if this syntax works (as opposed to the for loop with single-item array)
				if name.downvotes < 0:
					name.downvotes = 0
				name.downvotes = name.downvotes + 1
				name.put()
				self.response.out("vote was counted (decremented)")
				
				
			if not voteShouldBeCounted:
				self.response.out("vote was not counted")

		elif cmd == "ADDMYNAME":
			fn = self.request.get('firstname')
			ln = self.request.get('lastname')
			
			if len(fn) <= 0 or len(ln) <= 0:
				self.response.out.write("ERROR found a zero length name...")
				return
			
			#basic language filter#
			langsafe = isContentSafe(self, fn, ln)
			if not langsafe:
				self.response.out.write("--  ERROR bad word  -- ")
				return
			
			c = getCurrentNameToBeRated(self) #if there is no entry that is false, this name is THE name to be rated
			cnt = c.count() #inefficient
			
			if cnt <= 0:
				insertableName = rateableName(firstname=fn, lastname=ln, current=True)
				insertableName.put()
				self.response.out.write('put name into db AS CURRENT')
			else:
				insertableName = rateableName(firstname= fn, lastname=ln)
				insertableName.put()
				self.response.out.write('put name into db as NOT CURRENT')
			
			# return all results... limited to a certain number  
			results = db.GqlQuery('SELECT * FROM rateableName ORDER BY when DESC LIMIT 100')
			for r in results:
				self.response.out.write("<br />name: " + r.firstname + " " + r.lastname)
		else:
			self.response.out.write("unrecognized command -- " + cmd)
	def getCurrentNameToBeRated(self):
		name = db.GqlQuery("SELECT * FROM rateableName WHERE current = True")
		return name
	def isContentSafe(self, fn, ln):
		bad_words = ["fuck", "shit", "piss", "cunt", "bitch", "dick", "ass", "pussy", "vagina", "penis", "fag", "nigger", "niga", "nigga"]
		for word in bad_words:
			matchf = re.search(word, fn, re.IGNORECASE)
			matchl = re.search(word, ln, re.IGNORECASE)
			if matchf or matchl:
				return False
		return True
def main():
	app = webapp.WSGIApplication([(r'.*', MyHandler)], debug=True)
	wsgiref.handlers.CGIHandler().run(app)	
if __name__ == "__main__":
	main()
