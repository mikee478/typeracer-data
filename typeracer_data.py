import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
from bs4 import BeautifulSoup as bs
import requests

if __name__ == '__main__':
	url = 'https://typeracerdata.com/profile?username=mikee478'
	response = requests.get(url)
	soup = bs(response.text, 'html.parser')

	table_tag = soup.find('th', text='Month').parent.parent
	tr_tags = table_tag.findChildren('tr',recursive=False)

	data = []
	for i,tr_tag in enumerate(tr_tags):
		if i != 0: #ignore header
			txt = tr_tag.get_text().strip()
			data.append(tuple(txt.split('\n')))

	data = np.array(data, dtype=[('Date', 'U32'), ('Average', float), ('Best', float), ('Races', int), ('Wins', int), ('Win %', float)])	

	fig, ax = plt.subplots()

	x = [dt.datetime.strptime(d,'%B %Y').date() for d in data['Date']]
	y = data['Average']

	ax.plot(x,y)

	ax.xaxis.set_major_formatter(mdates.DateFormatter('%B %Y'))
	ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
	ax.set_ylabel("WPM")
	fig.autofmt_xdate()

	plt.show()


