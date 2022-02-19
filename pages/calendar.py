from datetime import datetime, timedelta
from calendar import HTMLCalendar
from datetime import date
from datetime import datetime
import pytz

class Calendar(HTMLCalendar):
	def __init__(self, year=None, month=None):
		self.year = year
		self.month = month
		super(Calendar, self).__init__()

	# formats a day as a td
	# filter events by day
	def formatday(self, day, events):
		print("day: "+str(day))
		# list(filter(lambda x: datetime.strptime(x['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z').day == day, events))
		# list(filter(lambda x: datetime.strptime(x['start']['date'], '%Y-%m-%d').day == day , events))

		events_per_day = list(filter(lambda x: datetime.strptime(x['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z').day == day, events))
		print("Formatting day")
		print(events_per_day)
		d = ''
		for event in events_per_day:
			if "summary" in event:
				d += f"<li> {event['summary']} </li>"
			else:
				d += f"<li> {'No title'} </li>"

		if day != 0:
			return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"
		return '<td></td>'

	# formats a week as a tr 
	def formatweek(self, theweek,events):
		print("Formatting week")
		print(events)
		week = ''
		for d, weekday in theweek:
			week += self.formatday(d,events)
		return f'<tr> {week} </tr>'

	# formats a month as a table
	# filter events by year and month
	def formatmonth(self, events, withyear=True):
		print("Formatting month")
		print(events)

		# This is the most important function in my project it has to chunk events in the month into 30 min intervals.
		# Move to the backend when done
		startDates = [x for x in events if ("date" in x['start'])] 
		print(startDates)
		events = [x for x in events if ("date" not in x['start'])]      
		print(events)

		timeZone = pytz.timezone('America/Vancouver')
		# Compare end - start date and make 48 * day datetimes
		for event in startDates:
			newStartDateTime = datetime.strptime(event['start']['date'], '%Y-%m-%d' )
			print(newStartDateTime)
			vancouverTime = timeZone.localize(newStartDateTime)
			print(vancouverTime)
			#Loop through each day still missing
			
			for delta in range(0, 30 * 48, 30):
				offsetted_ist = vancouverTime + timedelta(minutes=delta)
				print("Date & Time in :", offsetted_ist.strftime('%Y-%m-%dT%H:%M:%S%z'))
		# Make multiple hour datetimes into 30 min chunks

		cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
		cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
		cal += f'{self.formatweekheader()}\n'
		for week in self.monthdays2calendar(self.year, self.month):
			cal += f'{self.formatweek(week,events)}\n'
		cal += f'</table>\n'
		return cal