import mechanize
from bs4 import BeautifulSoup

br = mechanize.Browser()
br.set_handle_robots(False)  # ignore robots
br.set_handle_refresh(False)  # can sometimes hang without this

url = r"http://track.shiptropical.com/"
response = br.open(url)
br.select_form(nr=0)  # to select the first form

br['TextBox1'] = '2466'
br.find_control("Button2").readonly = False
search_response = br.submit("Button2")

response = search_response.read()
soup = BeautifulSoup(response, "html.parser")

td_elements = soup.find_all('td', {'align': 'right'})
costs = [float(td.renderContents()[1::]) for td in td_elements]
print costs
print 'Total Sum to pick up everything: '
print sum(costs)
