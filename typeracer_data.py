import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
from bs4 import BeautifulSoup as bs
import requests

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

if __name__ == '__main__':
	
	username = 'mikee478'
	if send_update_request(username):
		page_text = get_page_text(username)
		if page_text:
			data = parse_page_text(page_text)

			fig, ax = plt.subplots()

			x = [dt.datetime.strptime(d,'%B %Y').date() for d in data['Date']]
			y = data['Average WPM']
			ax.plot(x,y,'-ob', label='Average WPM')
			y = data['Best WPM']
			ax.plot(x,y,'-or', label='Best WPM')

			fig.canvas.manager.set_window_title('TypeRacer Data')
			ax.set_title(f'User Data For {username}')
			ax.legend()
			ax.xaxis.set_major_formatter(mdates.DateFormatter('%B %Y'))
			ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
			ax.set_ylabel('WPM')
			fig.autofmt_xdate()

			plt.show()