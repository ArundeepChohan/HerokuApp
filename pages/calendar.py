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
			events_per_day = list(filter(lambda x: datetime.strptime(x['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z').day == day, events))
			print(self.year,self.month,day)
			start = datetime(self.year,self.month,day)
			tz='America/Vancouver'
			time_zone = pytz.timezone(tz)
			start = time_zone.localize(start)
			start+=relativedelta(hours=7)
			# Starts at 7 am  then goes for the next 8 hours
			end = start+relativedelta(hours=8)
			min_gap = 30

			# compute datetime interval
			time_slots = [(start + timedelta(hours=min_gap*i/60)).strftime('%Y-%m-%dT%H:%M:%S%z')for i in range(int((end-start).total_seconds() / 60.0 / min_gap))]
			print(time_slots)
			if is_book_appointment:
				print("Book appointments",is_book_appointment)
				for time in time_slots:
					# Just check if there's an event in time slots
					time_occupied=False
					for event in events_per_day:
						print(datetime.strptime(time, '%Y-%m-%dT%H:%M:%S%z'),datetime.strptime(event['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z'))
						if datetime.strptime(time, '%Y-%m-%dT%H:%M:%S%z')==datetime.strptime(event['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z'):
							time_occupied=True
							if 'summary' in event:
								d += f"<li> {event['summary']} </li>"
							else:
								d += f"<li> {'No title'} </li>"
							break
					if not time_occupied:
						d += f"<li><button type='button' data-bs-toggle='modal' data-bs-target='#calendarBook'>Book Now</button> </li>"

			else:
				for event in events_per_day:
					if 'summary' in event:
						d += f"<li> {event['summary']} </li>"
					else:
						d += f"<li> {'No title'} </li>"

		if day != 0:
			return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"
		return '<td></td>'

	# formats a week as a tr 
	def formatweek(self, theweek,events,is_book_appointment=False):
		print("Formatting week")
		week = ''
		for d, weekday in theweek:
			# list(filter(lambda x: datetime.strptime(x['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z').day == day, events))
			# list(filter(lambda x: datetime.strptime(x['start']['date'], '%Y-%m-%d').day == day , events))
			
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