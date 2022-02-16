from datetime import datetime, timedelta
from calendar import HTMLCalendar

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
		events_per_day = list(filter(lambda x: datetime.strptime(x['start']['date'], '%Y-%m-%d').day == day, events))
		print("Formatting day")
		print(events_per_day)
		d = ''
		for event in events_per_day:
			d += f"<li> {event['summary']} </li>"

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

		cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
		cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
		cal += f'{self.formatweekheader()}\n'
		for week in self.monthdays2calendar(self.year, self.month):
			cal += f'{self.formatweek(week,events)}\n'
		cal+=f'</table>\n'
		return cal