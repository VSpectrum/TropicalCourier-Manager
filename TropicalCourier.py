import mechanize
from bs4 import BeautifulSoup

#run once when the app starts to acquire amazon order details:
#import amazon_interface

from Tkinter import *

from config import account_number, amazon_login_email, amazon_login_password

class TropicalCourier:
    def __init__(self, master):
        master.minsize(width=300, height=300)
        master.maxsize(width=300, height=300)

        frame = Frame(master)
        frame.pack()

        self.gdButton = Button(frame, text="Get Data", command=self.get_data)
        self.gdButton.pack(side=TOP)

        self.showData = Label(frame, text="")
        self.showData.pack(side=BOTTOM)

    def get_data(self):
        br = mechanize.Browser()
        br.set_handle_robots(False)
        br.set_handle_refresh(False)  # can sometimes hang without this

        url = r"http://track.shiptropical.com/"
        br.open(url)
        br.select_form(nr=0)  # to select the first form

        br['TextBox1'] = account_number
        br.find_control("Button2").readonly = False
        search_response = br.submit("Button2")

        response = search_response.read()
        soup = BeautifulSoup(response, "html.parser")

        td_elements = soup.find_all('td', {'align': 'right'})
        costs = [float(td.renderContents()[1::]) for td in td_elements]
        total_cost = '{0:.2f}'.format(sum(costs))
        total_string = 'Total Sum to pick up everything: $' + total_cost
        self.showData['text'] = total_string

        td_elements = soup.find_all('td', {'align': 'left'})
        packages = [td.renderContents() for td in td_elements if '\xc2\xa0' not in td.renderContents()]
        #packages = [package for package in packages if '\\xc2' not in package]

        print packages


root = Tk()
TC = TropicalCourier(root)
root.mainloop()
