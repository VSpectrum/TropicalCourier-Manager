from config import secret_key
from simplecrypt import encrypt, decrypt
from Tkinter import *
from amazon_interface import get_amazon_data
import base64

def encrypted(raw):
    return base64.b64encode(encrypt(secret_key, raw))

def decrypted(enc):
    return base64.b64decode(decrypt(secret_key, enc))

class AmazonInitialLogin():
    def __init__(self, master):
        master.minsize(width=500, height=190)
        master.maxsize(width=500, height=190)

        master.title("Amazon Login Handler")
        img = Image("photo", file="TC.gif")
        master.tk.call('wm','iconphoto',master._w,img)

        frame = Frame(master)
        frame.pack()


        midframe = Frame(master)
        midframe.pack(side=TOP)

        midframe2 = Frame(master)
        midframe2.pack(side=TOP)

        bottomframe = Frame(master)
        bottomframe.pack(side=TOP)

        bottomframe2 = Frame(master)
        bottomframe2.pack(side=TOP)


        self.labelText=StringVar()
        self.labelText.set("Amazon Username/Email: ")
        self.labelDir=Label(frame, textvariable=self.labelText, height=2)
        self.labelDir.pack(side="left")

        self.email = Entry(frame)
        self.email.insert(0, '')
        self.email.pack(side="left")

        self.labelText_p=StringVar()
        self.labelText_p.set(" Amazon Login Password: ")
        self.labelDir_p=Label(midframe, textvariable=self.labelText_p, height=2)
        self.labelDir_p.pack(side="left")

        self.password = Entry(midframe)
        self.password.insert(0, '')
        self.password.pack(side="left")

        self.labelText_T=StringVar()
        self.labelText_T.set(" Tropical Courier Account #: ")
        self.labelDir_T=Label(midframe2, textvariable=self.labelText_T, height=2)
        self.labelDir_T.pack(side="left")

        self.accountnum = Entry(midframe2)
        self.accountnum.insert(0, '')
        self.accountnum.pack(side="left")


        self.labelDir_placeholder=Label(bottomframe, textvariable="", height=3)
        self.labelDir_placeholder.pack(side="left")

        self.gdButton = Button(bottomframe, text="Login", command=self.check_login_success)
        self.gdButton.pack(side=LEFT)

        self.ErrorMsg=Label(bottomframe2, textvariable="", height=3)
        self.ErrorMsg.pack(side="top")

    def check_login_success(self):
        email = self.email.get()
        passwd = self.password.get()
        accountnum = self.accountnum.get()
        if email=='' or passwd=='' or accountnum=='':
            self.ErrorMsg['text'] = "No field should be blank."

        else:
            if '@' in email:
                amazon_fetch_result = get_amazon_data(email, passwd)
                if amazon_fetch_result != "Login Error" and amazon_fetch_result != "There was a problem":
                    with open('login', 'wb+') as loginfile:
                        loginfile.write('login:'+email+'\n')
                        loginfile.write('passwd:'+encrypted(passwd)+'\n')
                        loginfile.write('account:'+accountnum)
                    quit(self)
                else:
                    self.ErrorMsg['text'] = "Error Logging in! Username/Password may be incorrect."
            else:
                self.ErrorMsg['text'] = "Incorrectly formatted email supplied."

    def quit(self):
        self.root.destroy()

# root = Tk()
# TC = AmazonInitialLogin(root)
# root.mainloop()
