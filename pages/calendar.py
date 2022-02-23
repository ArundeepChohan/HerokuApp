from calendar import HTMLCalendar
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pytz
class Calendar(HTMLCalendar):
	def __init__(self, year=None, month=None):
		self.year = year
		self.month = month
		super(Calendar, self).__init__()

	# formats a day as a td
	def formatday(self, day, events,is_book_appointment=False):
		print("day: "+str(day))
		print("Formatting day")
		d = ''
		if day !=0:
			# list(filter(lambda x: datetime.strptime(x['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z').day == day, events))
			# list(filter(lambda x: datetime.strptime(x['start']['date'], '%Y-%m-%d').day == day , events))
			events_per_day = list(filter(lambda x: datetime.strptime(x['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z').day == day, events))
			print(self.year,self.month,day)
			start = datetime(self.year,self.month,day)
			tz = 'America/Vancouver'
			time_zone = pytz.timezone(tz)
			start = time_zone.localize(start)
			# Modify this to get user's time slots later on
			# Starts at 7 am  then goes for the next 10 hours
			start+=relativedelta(hours=7)
			end = start+relativedelta(hours=10)
			min_gap = 30
			# Compute datetime interval of 30 mins for a day
			time_slots = [(start + timedelta(hours=min_gap*i/60)).strftime('%Y-%m-%dT%H:%M:%S%z')for i in range(int((end-start).total_seconds() / 60.0 / min_gap))]
			print(time_slots)
			# Hide other's information from the user
		
			if is_book_appointment:
				print("Book appointments",is_book_appointment)
				for time in time_slots:
					# Just check if there's an event in time slots
					am_format = datetime.strptime(time[:-8].split('T')[1].split('-')[0], '%H:%M').strftime('%I:%M %p').lstrip('0')
					print(am_format)
					time_occupied = False
					for event in events_per_day:
						print(credits,datetime.strptime(event['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z'))
						if datetime.strptime(time, '%Y-%m-%dT%H:%M:%S%z')==datetime.strptime(event['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z'):
							time_occupied = True
							d += f"<li> {'Booked'} {am_format}</li>"
							break
					# I need to pass the current user, the doctor it clicked(pass from front end or context?), start time(not occupied time)
					if not time_occupied:
						#form="<form action='addAppointment/' method='POST' enctype='multipart/form-data'><button type='submit'>Book now</button></form>"
	
						form="<button onclick="+ 'location.href="'+"/addAppointment/manjit/2022-02-28T07:00:00-0800"+ '"'+">Book now</button>"
						#form ="<button>"+'<a href="'+'/addAppointment"' +"> Book Now"+"</a>"+"</button>"
						d += f'<li>'+form+am_format+'</li>'

			else:
				for event in events_per_day:
					if 'summary' in event:
						d += f"<li> {event['summary']} {am_format}</li>"
					else:
						d += f"<li> {'No title'}{am_format} </li>"

		if day != 0:
			return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"
		return '<td></td>'

	# formats a week as a tr 
	def formatweek(self, theweek,events,is_book_appointment=False):
		print("Formatting week")
		week = ''
		for d, weekday in theweek:
			week += self.formatday(d,events,is_book_appointment)
		return f'<tr> {week} </tr>'

	# formats a month as a table
	# filter events by year and month
	def formatmonth(self, events, withyear=True,is_book_appointment=False):
		print("Formatting month")
		#print(events)
		cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
		cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
		cal += f'{self.formatweekheader()}\n'
		for week in self.monthdays2calendar(self.year, self.month):
			cal += f'{self.formatweek(week,events,is_book_appointment)}\n'
		cal += f'</table>\n'
		return cal