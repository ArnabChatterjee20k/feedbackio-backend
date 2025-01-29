### Analytics jist and my main thinking

* Event driven rather than session driven
* Event driven means for every event a http request will be made
* Session driven means a recording of a session would be done by constant http updates 
or during feedback submission will be sending a request when form opened and when submission completed another http request leading to knowing people opening and actually completing
* Heat maps or click maps can be tracked using the session driven only. To validate a single session cookies can be used.
* Here only calculations and logs need to be generated thats why event driven method is chose as no constant tracking is required

space -> feedback, poll, form

### space(for numerical data)
type = feedback, poll, form
metadata = {}

### feedback components
landing page
wall of fame
feedback submission

page visit(space_id) -> landing, wall of fame
-> graph
date range = last 7 days, 24 hours, 30 days
data show - number of visit with time for specific one hour
others -> country, browser, os

feedback submission
-> numerical data(metadata for the space)
avg sentiment
total submission
-> logging type
submission log with ip, country, creation time, sentiment[if userid then logged in otherwise not loggedin]