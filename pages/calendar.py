from calendar import HTMLCalendar
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import django
import pytz

class Calendar(HTMLCalendar):
	def __init__(self, year=None, month=None, day=None, time=None, username=None):
		self.year = year
		self.month = month
		self.day = day
		self.username = username
		self.time = time
		super(Calendar, self).__init__()

	# formats a day as a td
	def formatday(self, request, day, events,is_book_appointment=False):
		#print("day: "+str(day))
		#print("Formatting day")
		d = ''
		if day !=0:
			# list(filter(lambda x: datetime.strptime(x['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z').day == day, events))
			# list(filter(lambda x: datetime.strptime(x['start']['date'], '%Y-%m-%d').day == day , events))
			events_per_day = list(filter(lambda x: datetime.strptime(x['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z').day == day and datetime.strptime(x['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z').month == self.month and datetime.strptime(x['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z').year == self.year, events))
			start = datetime(self.year,self.month,day)
			tz = 'America/Vancouver'
			time_zone = pytz.timezone(tz)
			start = time_zone.localize(start)
			# Modify this to get user's time slots later on. Starts at 7 am then goes for the next 10 hours.
			start += relativedelta(hours=7)
			end = start + relativedelta(hours=10)
			min_gap = 30
			# Compute datetime interval of 30 mins for a day
			time_slots = [(start + timedelta(hours=min_gap*i/60)).strftime('%Y-%m-%dT%H:%M:%S%z')for i in range(int((end-start).total_seconds() / 60.0 / min_gap))]
			#print(time_slots)
			# Hide other's information from the user
			if is_book_appointment:
				print("Book appointments",is_book_appointment)
				for time in time_slots:
					am_format = datetime.strptime(time[:-8].split('T')[1].split('-')[0], '%H:%M').strftime('%I:%M %p').lstrip('0')
					#print(am_format)
					# Just check if there's an event in time slots
					time_occupied = False
					converted_time = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S%z')
					# Checks if can book the time if it's past current time.
					if converted_time>=self.time:
						for event in events_per_day:
							converted_start = datetime.strptime(event['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z')
							#print(converted_time,converted_start)
							if converted_time==converted_start:
								time_occupied = True
								d += f"<li> {'Booked'} {am_format}</li>"
								break
						
						# I need to pass the current user, the doctor it clicked(pass from front end or context?), start time(not occupied time)
						if not time_occupied:
							token = django.middleware.csrf.get_token(request)
							#print("token: ",token)
							form = '<form action="/addAppointment/'+self.username+"/"+time+ '/"'+ ' method="POST" enctype="multipart/form-data"><button type="submit">Book now</button>'+'<input name="csrfmiddlewaretoken"'+'value="'+token+'"'+ 'type="hidden">'+'</form>'
							#form="<button onclick="+ 'location.href="'+"/addAppointment/"+self.username+"/"+time+ '/"'+">Book now</button>"
							#form ="<button>"+'<a href="'+'/addAppointment"' +"> Book Now"+"</a>"+"</button>"
							d += f'<li>'+form+am_format+'</li>'
					else:
						d += f'<li> Unavailable </li>'

			else:
				for event in events_per_day:
					am_format = datetime.strptime(event['start']['dateTime'][:-9].split('T')[1].split('-')[0], '%H:%M').strftime('%I:%M %p').lstrip('0')
					#print(am_format)

					if 'summary' in event:
						d += f"<li> {event['summary']} {am_format}</li>"
					else:
						d += f"<li> {'No title'} {am_format}</li>"

		if day != 0:
			return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"
		return '<td></td>'

	# formats a week as a tr 
	def formatweek(self, request, theweek, events, is_book_appointment=False):
		#print("Formatting week")
		week = ''
		for d, weekday in theweek:
			week += self.formatday(request, d, events, is_book_appointment)
		return f'<tr> {week} </tr>'

	# formats a month as a table
	# filter events by year and month
	def formatmonth(self, request, events, withyear=True, is_book_appointment=False):
		#print("Formatting month")
		#print(events)
		cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
		cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
		cal += f'{self.formatweekheader()}\n'
		for week in self.monthdays2calendar(self.year, self.month):
			cal += f'{self.formatweek(request,week,events,is_book_appointment)}\n'
		cal += f'</table>\n'
		return cal