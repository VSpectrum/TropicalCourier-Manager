import mechanize
from bs4 import BeautifulSoup

from amazon_interface import get_amazon_data

from Tkinter import *
import webbrowser

from login import AmazonInitialLogin, decrypted
from config import secret_key

from os.path import exists

import base64
from simplecrypt import decrypt

class TropicalCourier:
    def __init__(self, master):
        master.minsize(width=400, height=300)
        master.maxsize(width=400, height=300)

        master.title("Tropical Courier Manager")
        img = Image("photo", file="TC.gif")
        master.tk.call('wm', 'iconphoto', master._w, img)

        frame = Frame(master)
        frame.pack()


        midframe = Frame(master)
        midframe.pack(side=TOP)

        bottomframe = Frame(master)
        bottomframe.pack(side=BOTTOM)

        self.gdButton1 = Button(frame, text="Get Amazon Data", command=self.amazon_data)
        self.gdButton1.pack(side=LEFT)

        self.gdButton = Button(frame, text="Get Courier Data", command=self.get_data)
        self.gdButton.pack(side=LEFT)

        self.scrollbar = Scrollbar(midframe, orient=VERTICAL)
        self.scrollbar.config(command=self.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox = Listbox(midframe, height=15, width=50, yscrollcommand=self.scrollbar.set)
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
        if '|' in value:
            value = [x.strip() for x in value.split('|')][0]
        print value

        ordersdict = {}

        with open("amazon_orders.txt", 'r') as amazonorders:
            for line in amazonorders:
                stringsplit = line.split('|')
                ordersdict[stringsplit[0]] = stringsplit[1]

        webbrowser.open(ordersdict[[item for item in ordersdict.keys() if item in value][0]])

    def get_data(self):
        if exists('login'):
            logincred = []
            with open('login', 'r') as loginfile:
                logincred = loginfile.readlines()
            account_number = logincred[2].split(':')[1]

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
            costs = [float(td.renderContents()[1::].replace(',', '')) for td in td_elements]
            total_cost = '{0:.2f}'.format(sum(costs))
            total_string = 'Total Sum to pick up everything: $' + total_cost
            self.showData['text'] = total_string

            # td_elements = soup.find_all('td', {'align': 'left'})


            processing_miami = soup.find('div', class_="Pan3")
            processing = processing_miami.find_all('td')
            if processing_miami:
                processing = [item.renderContents().replace('# ', '').upper() for item in processing]
            else:
                processing = []

            in_transit = soup.find('div', class_="Pan4")
            transit = in_transit.select('tr > td:nth-of-type(2)')
            if in_transit:
                transit = [item.renderContents().replace('# ', '').upper() for item in transit]
            else:
                in_transit = []

            in_trinidad = soup.find('div', class_="Pan1")
            trini = in_trinidad.select('tr > td:nth-of-type(2)')
            if in_trinidad:
                trini = [item.renderContents().replace('# ', '').upper() for item in trini]
            else:
                trini = []

            ready_for_pickup = soup.find('div', class_="Pan2")
            ready = ready_for_pickup.select('tr > td:nth-of-type(2)')
            readyprice = ready_for_pickup.select('tr > td:nth-of-type(4)')
            if ready_for_pickup:
                ready = [item.renderContents().replace('# ', '').upper() + ' | ' + price.renderContents() for
                         item, price in zip(ready, readyprice)]
            else:
                ready = []

            packages = processing + transit + trini + ready

            self.listbox.delete(0, END)
            for package in packages:
                self.listbox.insert(END, package)
                if package in processing:
                    self.listbox.itemconfig(END, bg='ivory')
                elif package in transit:
                    self.listbox.itemconfig(END, bg='mintcream')
                elif package in trini:
                    self.listbox.itemconfig(END, bg='ghostwhite')
                elif package in ready:
                    self.listbox.itemconfig(END, bg='azure')

            print packages
        else:
            #Aroot.mainloop()
            window = Toplevel()
            AmaInit = AmazonInitialLogin(window)
            window.focus_set()

    def amazon_data(self):
        if exists('login'):
            with open('login', 'rb+') as loginfile:
                logincred = loginfile.readlines()
            ama_email = logincred[0].split(':')[1]
            passwd = logincred[1].split(':')[1].rstrip()
            passwd = base64.b64decode(passwd)
            print passwd
            ama_pass = decrypt(secret_key, passwd)
            print get_amazon_data(ama_email, ama_pass)
            self.gdButton1['state'] = 'disabled'
        else:
            window = Toplevel()
            AmaInit = AmazonInitialLogin(window)
            window.focus_set()

TCroot = Tk()
TC = TropicalCourier(TCroot)
TCroot.mainloop()
