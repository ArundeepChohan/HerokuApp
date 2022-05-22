# HerokuApp
This is a medical site hosted on Herokuapp using Django

Medical website that allows users to get quality healthcare services from reliable professionals at the comfort of their own home.

• Dashboard that displays the last unread message along with the count, the latest event in the month, and the last medication added.

• Edit profile section that uses an AWS S3 bucket to store their avatar pics along with a custom Abstractuser model schema to store their bio, gender, age, and phone number, 

• Allows users to add and track their medications by name, quantity, type and etc.

• Messaging and Inboxes between users/doctors/admins with a reply section and removing the message temporarily from one's view or deleting the message if both don't want the message.

• Allows users to check their own calendars via Google Calendar Api and displays valid times to book an appointment for each doctor.

• Uses Django form wizard to separate a health care professional sign up that stores an additional image to verify by admins and the user sign up.

• Signs up using Google's Oauth2 via Python Social Auth to connect to a user associated with that email or create a temp user to access their access tokens for their primary calendar.

• Removes users along with disabling all their messages and removing their files from AWS after 30 days using Celery.

• Messages self using AWS SES for contact.

Prerequisites: Able to run Python + Django + Setup Google .

Installing: Download all files and set up an .env file, with all the necessary variables.

Useful Links:

• https://blog.benhammond.tech/connecting-google-cal-api-and-django

• https://simpleisbetterthancomplex.com/tutorial/2017/08/01/how-to-setup-amazon-s3-in-a-django-project.html

Built With: AWS (SES, S3), Google (Calendar API), OAuth2, Django, Heroku, Python, SQLite, PostgreSQL, Celery, Redis

Authors: Arundeep Chohan

