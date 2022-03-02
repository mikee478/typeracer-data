import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from bs4 import BeautifulSoup as bs
import requests
import time
import datetime as dt
from dateutil import parser
import pytz

def send_update_request(username):
	url = 'https://typeracerdata.com/import?username=' + username
	response = requests.get(url)
	return response.ok

def get_page_text(username):
	url = 'https://typeracerdata.com/profile?username=' + username
	response = requests.get(url)
	return response.text if response.ok else None

def parse_page_text(text):
	soup = bs(text, 'html.parser')

	table_tag = soup.find('th', text='Month').parent.parent
	tr_tags = table_tag.findChildren('tr', recursive=False)

	data = []
	for tr_tag in tr_tags[1:]: # skip header
		row_text = tr_tag.get_text().strip().split('\n')
		data.append(tuple(row_text))

	return np.array(data, dtype=[('Date', 'U32'), ('Average WPM', float), ('Best WPM', float), ('Races', int), ('Wins', int), ('Win %', float)])	

def get_updated_text(username, max_sec_since_update=30, max_wait_time=10, sleep_time=1):
	if not send_update_request(username): return None

	n_seconds = dt.timedelta(seconds=max_sec_since_update)

	start_time = time.time()

	while time.time() - start_time <= max_wait_time:
		page_text = get_page_text(username)
		if page_text is not None:
			last_imp_ind1 = page_text.find('(Last import: ')
			last_imp_ind2 = page_text.find(')', last_imp_ind1)

			date_str = page_text[last_imp_ind1+14:last_imp_ind2]
			last_update = parser.parse(date_str)

			now = dt.datetime.now(pytz.utc)

			if now - last_update < n_seconds:
				return page_text, last_update

		time.sleep(sleep_time)

	return None

def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=dt.timezone.utc).astimezone(tz=None)

def plot_data(data, last_update):
	fig, ax = plt.subplots()

	x = [dt.datetime.strptime(d,'%B %Y').date() for d in data['Date']]
	y = data['Average WPM']
	ax.plot(x,y,'-ob', label='Average WPM')
	y = data['Best WPM']
	ax.plot(x,y,'-or', label='Best WPM')

	fig.canvas.manager.set_window_title('TypeRacer Data')
	ax.set_title(f'User Data For {username} (Last Updated {utc_to_local(last_update).strftime("%x %-I:%M:%S %p")})')
	ax.legend()
	ax.xaxis.set_major_formatter(mdates.DateFormatter('%B %Y'))
	ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
	ax.set_ylabel('WPM')
	fig.autofmt_xdate()

	plt.show()

if __name__ == '__main__':
	username = 'mikee478'
	page_text, last_update = get_updated_text(username)
	data = parse_page_text(page_text)
	plot_data(data, last_update)