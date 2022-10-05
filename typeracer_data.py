import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from bs4 import BeautifulSoup as bs
import requests
import time
import datetime as dt
from dateutil import parser
import pytz

def send_update_request(username):
	url = f'https://typeracerdata.com/import?username={username}'
	response = requests.get(url)
	return response.text if response.ok else None

def get_page_text(username):
	url = f'https://typeracerdata.com/profile?username={username}'
	response = requests.get(url)
	return response.text if response.ok else None

def parse_page_text(text):
	soup = bs(text, 'html.parser')

	table_tag = soup.find('th', text='Month').parent.parent
	tr_tags = table_tag.findChildren('tr', recursive=False)

	data = []
	for tr_tag in tr_tags[1:]: # skip header
		row_text = tr_tag.get_text().strip().replace(',','').split('\n')
		data.append(tuple(row_text))

	return np.array(data, dtype=[('Date', 'U32'), ('Average WPM', float), ('Best WPM', float), ('Races', int), ('Wins', int), ('Win %', float)])	

def account_not_found(page_text):
	return 'Account not found' in page_text

def get_updated_text(username, max_sec_since_update=60, max_wait_time=30, sleep_time=2):
	ret = send_update_request(username)
	if ret is None:
		print('ERROR: Update request could not be sent')
	elif account_not_found(ret):
		print(f'ERROR: User "{username}" could not be found')
	else:
		n_seconds = dt.timedelta(seconds=max_sec_since_update)
		start_time = time.time()

		while time.time() - start_time <= max_wait_time:
			print('Retrieving updated user data...')
			if page_text := get_page_text(username):
				last_imp_ind1 = page_text.find('(Last import: ')
				last_imp_ind2 = page_text.find(')', last_imp_ind1)

				date_str = page_text[last_imp_ind1+14:last_imp_ind2]
				last_update = parser.parse(date_str)

				now = dt.datetime.now(pytz.utc)

				if now - last_update < n_seconds:
					return page_text, last_update

			time.sleep(sleep_time)

		print('ERROR: Timed out retrieving updated user data')

def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=dt.timezone.utc).astimezone(tz=None)

def plot_data(data, last_update):
	fig, ax = plt.subplots(figsize=(10,6))

	x = [dt.datetime.strptime(d,'%B %Y').date() for d in data['Date']]
	y = data['Average WPM']
	ax.plot(x,y,'-ob', label='Average WPM')
	y = data['Best WPM']
	ax.plot(x,y,'-or', label='Best WPM')

	fig.canvas.manager.set_window_title('TypeRacer Data')
	ax.set_title(f'User Data For {username} (Last Updated {utc_to_local(last_update).strftime("%x %-I:%M:%S %p")})')

	ax.xaxis.set_major_formatter(mdates.DateFormatter('%B %Y'))
	ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
	ax.xaxis.set_minor_locator(mdates.MonthLocator(interval=1))
	ax.yaxis.set_major_locator(ticker.MultipleLocator(5))
	ax.set_ylabel('WPM')
	fig.autofmt_xdate()
	ax.set_xlim(left=x[-1])
	plt.grid(b=True, which='major', axis='both')
	plt.grid(b=True, which='minor', axis='both', linestyle=':')
	ax.legend()

	plt.show()

if __name__ == '__main__':
	print('Enter TypeRacer username: ', end='')
	username = input().strip()

	if ret := get_updated_text(username):
		text, last_update = ret
		data = parse_page_text(text)
		plot_data(data, last_update)
