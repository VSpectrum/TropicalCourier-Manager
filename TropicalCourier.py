import mechanize
from bs4 import BeautifulSoup

from amazon_interface import get_amazon_data

from Tkinter import *
import webbrowser
from config import account_number, amazon_login_email, amazon_login_password

class TropicalCourier:
    def __init__(self, master):
        master.minsize(width=300, height=300)
        master.maxsize(width=300, height=300)

        frame = Frame(master)
        frame.pack()

        midframe = Frame(root)
        midframe.pack(side=TOP)

        bottomframe = Frame(root)
        bottomframe.pack(side=BOTTOM)

        self.gdButton = Button(frame, text="Get Amazon Data", command=self.amazon_data)
        self.gdButton.pack(side=LEFT)

        self.gdButton = Button(frame, text="Get Courier Data", command=self.get_data)
        self.gdButton.pack(side=LEFT)


        self.scrollbar = Scrollbar(midframe, orient=VERTICAL)
        self.scrollbar.config(command=self.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox = Listbox(midframe, height=15, width=30, yscrollcommand=self.scrollbar.set)
        self.listbox.bind('<Double-Button-1>', self.selection)
        self.listbox.pack(side=TOP, fill=BOTH, expand=1)

        self.showData = Label(bottomframe, text="")
        self.showData.pack(side=BOTTOM)

    def yview(self, *args):
        apply(self.listbox.yview, args)

    def selection(self, event):
        widget = event.widget
        selection = widget.curselection()
        value = widget.get(selection[0])

        ordersdict = {}

        with open("amazon_orders.txt", 'r') as amazonorders:
            for line in amazonorders:
                stringsplit = line.split('|')
                ordersdict[stringsplit[0]]=stringsplit[1]

        webbrowser.open(ordersdict[[item for item in ordersdict.keys() if item in value][0]])

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
        packages = [td.renderContents().replace('# ','').upper() for td in td_elements if '\xc2\xa0' not in td.renderContents()]

        for package in packages:
            self.listbox.insert(END, package)

        print packages

    def amazon_data(self):
        while(get_amazon_data()=='Could not automatically solve captcha.'): pass

root = Tk()
TC = TropicalCourier(root)
root.mainloop()
