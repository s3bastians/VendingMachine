from tkinter import *
import socket
import pickle
import sys
import tkinter.messagebox as msgbox
from dataclasses import dataclass
import threading
import time


@dataclass  # indicate that Ticket class is a data class
class Ticket:  # create ticket data class
    id: str
    route: str
    price: float
    stock: int

    # create string method for ticket class
    def __str__(self):
        return f'{self.id},{self.route},{self.price},{self.stock}'


# create Client Class which inherits from TK class
class Client(Tk):
    inserted_cash = 0  # create variable to store inserted cash
    transaction_received = dict()  # save received database in a dictionary
    transaction_to_send = dict()  # create dictionary for object to be send
    # define width and height
    width = 1000
    height = 600
    ticket_labels = []  # create list of tickets' labels
    total_value = 0  # define total value for the receipt and set it to 0

    def __init__(self):
        super().__init__()
        self.title('Train Tickets')  # set title for root window
        self.geometry(f'{Client.width}x{Client.height}')  # set the size of the root window
        self.protocol("WM_DELETE_WINDOW", self.close)  # specify action for window close button
        self.resizable(width=False, height=False)  # prevent user from resizing the window
        # create header frame
        self.header_frame = Frame(self, bg='orange', bd=10, relief='raised')
        # pack header_frame fill horizontally
        self.header_frame.pack(fill='both', side=TOP)
        # create and pack title label
        self.title_label = Label(self.header_frame, text='TICKETS', fg='red', font=('Caster', 48, 'bold'), bg='orange')
        self.title_label.pack()
        # create left body frame
        self.body_frame_left = Frame(self, bg='blue')
        self.body_frame_left.pack(side=LEFT, fill=BOTH, expand=True)
        # create tickets frame and use pack geometry manager to set its position
        self.tickets_frame = Frame(self.body_frame_left, bg='black', bd=10, relief='groove')
        self.tickets_frame.pack(expand=TRUE, anchor='center')
        # connect to the server
        self.s = self.connect()
        # get tickets from db
        self.get_tickets()
        # create image object for ticket
        self.ticket_image = PhotoImage(file='images/ticket.png')
        # show tickets
        """shows tickets in the main window"""
        col, row = 0, 0  # start griding in col 0, row 0
        for ticket in Client.transaction_received.keys():  # for every ticket from database
            # assign string variable
            self.text = StringVar()
            self.ticket_labels.append(self.text)  # add string variable to ticket_labels list
            # set value of self.text variable to value in dictionary Customer.transaction_received
            self.text.set(f'ID: {Client.transaction_received[ticket].id}\n\
{Client.transaction_received[ticket].route}\n\
Price: £ {Client.transaction_received[ticket].price:5.2f}\n\
Stock Level: {Client.transaction_received[ticket].stock}')  # set string variable for every label
            # create and grid label for every ticket
            self.label = Label(self.tickets_frame, bd=5, relief='raised', bg='moccasin', fg='black',
                               font=('Courier', 10, 'bold'), textvariable=self.text, image=self.ticket_image,
                               compound=TOP)
            self.label.grid(column=col, row=row, sticky='nsew')
            # increase column and row accordingly to create table of ticket labels
            col += 1
            if col > 3:
                col = 0
                row += 1
        # create tickets & change dispenser
        self.label_tickets_dispenser = Label(self.body_frame_left, bg='black', fg='white', width=30,
                                             text='Collect your tickets and change here')
        # use pack geometry manager to display tickets & change dispenser
        self.label_tickets_dispenser.pack(expand=True)
        # create right body frame and display using pack geometry manager
        self.body_frame_right = Frame(self, bg='black')
        # bind function to clear thank you screen after collecting tickets
        self.label_tickets_dispenser.bind('<ButtonPress>', self.clear_bottom_screen)
        # create right body frame
        self.body_frame_right.pack(side=LEFT, fill=BOTH)
        # create frame for selection & payment widgets
        self.selection_payment_widgets = Frame(self.body_frame_right, bg='black')
        self.selection_payment_widgets.pack(expand='True')
        # create screen welcome screen
        self.screen_label = Label(self.selection_payment_widgets, font=('Courier', 10, 'bold'),
                                  text='Welcome! Please input ID of the product followed by the quantity',
                                  bg='black', fg='lime', bd=5, relief='raised', wraplength=Client.width / 3,
                                  padx=5, pady=5)
        # utilize grid geometry manager to display screen_label
        self.screen_label.grid(row=0, column=0, columnspan=2)
        # create frame for payment widgets
        self.payment_widgets = Frame(self.selection_payment_widgets, bg='black', padx=10, pady=10)
        self.payment_widgets.grid(row=1, column=0)
        # create and grid entry to store the current choice
        self.item = Entry(self.payment_widgets, bg='black', fg='lime', width=6, font=('courier', 12, 'bold'))
        self.item.grid(row=0, column=0, columnspan=6)
        self.letters_buttons = ['A', 'B']  # create the list of the letters for buttons
        self.numbers_buttons = [str(x) for x in range(10)]  # create the list of the numbers for buttons
        self.letters_numbers_buttons = self.letters_buttons + self.numbers_buttons  # merge both lists in one
        self.choice_buttons = []  # create list of button
        # create buttons and append them to choice_buttons list, use lambda function to link self.item.insert
        # with relevant button, use grid geometry manager to organize the buttons within payment_widget
        i = 0
        for row in range(1, 3):
            for col in range(6):
                self.choice_buttons.append(Button(self.payment_widgets, font=('Courier', 12, 'bold'),
                                                  text=self.letters_numbers_buttons[i],
                                                  command=lambda x=self.letters_numbers_buttons[i]:
                                                  self.item.insert('end', str(x))))
                if self.letters_numbers_buttons[i].isdigit():
                    self.choice_buttons[i].config(bg='aquamarine')
                else:
                    self.choice_buttons[i].config(bg='palegreen')
                self.choice_buttons[i].grid(column=col, row=row, sticky='nsew')
                i += 1
        # create function buttons
        self.enter_button = Button(self.payment_widgets, font=('Courier', 10, 'bold'), text='ENTER', bg='red',
                                   fg='white', command=lambda: self.enter_product(self.item.get()))
        self.enter_button.grid(column=0, row=3, columnspan=6, sticky='nsew')
        self.add_another_button = Button(self.payment_widgets, font=('Courier', 10, 'bold'), text='Add another',
                                         bg='orchid1', command=self.add_another)
        self.add_another_button.grid(column=0, row=4, columnspan=6, sticky='nsew')
        self.cancel_button = Button(self.payment_widgets, font=('Courier', 10, 'bold'), text='Cancel',
                                    bg='orchid1', command=self.cancel_transaction)
        self.cancel_button.grid(column=0, row=5, columnspan=6, sticky='nsew')
        self.pay_button = Button(self.payment_widgets, font=('Courier', 10, 'bold'), text='Finish and Pay',
                                 bg='orchid1', command=self.finish_and_pay)
        self.pay_button.grid(column=0, row=6, columnspan=6, sticky='nsew')
        # create and grid payment frame
        self.payment_frame = Frame(self.selection_payment_widgets, bg='black', padx=10)
        self.payment_frame.grid(row=1, column=1)
        # create and grid label for inserted money
        self.inserted_money = Entry(self.payment_frame, bg='black', fg='lime', width=20,
                                    justify=CENTER, font=('courier', 12, 'bold'))
        self.inserted_money.grid(row=0, column=0, columnspan=3)
        # create list of nominal
        self.nominal = [50, 20, 10, 5, 2, 1, 0.50, 0.20, 0.10, 0.05, 0.02, 0.01]
        # create list of money buttons
        self.money_buttons = []
        i = 0
        for row in range(1, 5):
            for col in range(3):
                # create button objects for each nominal and append it to money_buttons list
                self.money_buttons.append(
                    Button(self.payment_frame, bg='deep sky blue', font=('Courier', 10, 'bold'),
                           text=f'£{self.nominal[i]:4.2f}'))
                # grid each button
                self.money_buttons[i].grid(row=row, column=col, sticky='nsew')
                # set the command for each button so it triggers self.add_money method and passes tha arguments of
                # the value of nominal and cash as a payment type
                self.money_buttons[i]['command'] = lambda x=self.nominal[i], y='cash': self.add_money(x, y)
                i += 1
        # create card_payment button object and set command which triggers add_money method
        self.card_payment = Button(self.payment_frame, bg='gray55', fg='white', font=('Courier', 24, 'bold'),
                                   text=f'CARD HERE', command=self.add_money)
        # grid card_payment button
        self.card_payment.grid(row=5, column=0, columnspan=3, sticky='nsew')
        # create and grid bottom_screen widget
        self.bottom_screen = Text(self.selection_payment_widgets, width=43, height=18,
                                  bg='black', fg='lime', wrap='word')
        self.bottom_screen.grid(row=2, column=0, columnspan=2)
        # create deamon thread which updates stock level
        self.thread = threading.Thread(target=self.update_every10, daemon=True)
        self.thread.start()

    @staticmethod
    def connect():
        """Connects to the server"""
        result = True
        while result:  # reattempt setting up connection as many times as user wants to or connection successful
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create socket object
            host = '192.168.0.223'  # define server ip address
            port = 65255  # define port ip
            result = s.connect_ex((host, port))  # attempt to connect to the server, connect_ex returns 0 if connected
            if result:  # if not connected ask user if they want to reattempt connecting
                msgbox.showerror(title='No connection', message='There is no connection with the server. \n\
Please check your internet connection and try again. \nIf the problem persist the server may be down.')
                if not msgbox.askyesno('Connection Error', 'Would you like to try to connect again?'):
                    sys.exit()  # terminate if they don't
        return s

    def get_tickets(self):
        """retrieves tickets from the database
                and returns its value to dict transaction_received"""
        self.s.send(bytes('request', 'utf-8'))  # send request command to the server
        database = pickle.loads(self.s.recv(1024))  # receive database from the server
        for record in database:  # for every record in database assign relevant field to variables
            ticket_id = record[0]
            ticket_route = record[1]
            ticket_price = record[2]
            ticket_stock = record[3]
            # create Ticket object and save it to variable ticket
            ticket = Ticket(ticket_id, ticket_route, float(ticket_price), int(ticket_stock))
            # append ticket object to the dictionary Customer transaction received
            Client.transaction_received[ticket_id] = ticket

    def clear_fields(self):
        """clear fields and display goodbye message"""

        self.bottom_screen.delete('1.0', 'end')  # clear the bottom screen
        self.inserted_money.delete(0, 'end')  # clear inserted money screen
        # create goodbye message
        text_do_display = 'Your tickets are dispensed under the tickets screen\n\n'
        # if there is any change add change message to goodbye message
        if Client.total_value:
            text_do_display += f'Please do not forget to collect your change: £ {abs(Client.total_value):3.2f}\n'
        text_do_display += f'Thank you. Goodbye!'  # add final goodbye
        self.bottom_screen.insert('end', text_do_display)  # display goodbye message in the bottom screen
        Client.transaction_to_send.clear()  # clear content of Customer.transaction_to_send list
        Client.total_value = 0  # reset balance

    def clear_bottom_screen(self, event):
        """clears bottom screen if the message starting with Your is present"""
        if self.bottom_screen.get('1.0', '1.4') == 'Your':
            self.bottom_screen.delete('1.0', 'end')

    def send_transaction(self):
        """send current transaction to the server"""
        self.s.send(bytes('transaction', 'utf-8'))
        with open('transaction.csv', 'r') as transaction:
            data = transaction.read()
            self.s.send(pickle.dumps(data))

    def update_tickets(self):
        """updates value of text variable to display correct stock information"""
        for i, ticket in enumerate(Client.transaction_received.values()):
            text = f'ID: {ticket.id}\n{ticket.route}\nPrice: £ {ticket.price:5.2f}\nStock Level: {ticket.stock}'
            self.ticket_labels[i].set(text)

    def update_every10(self):
        """updates stock level every 10 s"""
        while True:
            self.get_tickets()
            self.update_tickets()
            time.sleep(10)

    def paid(self):
        """sends paid confirmation to the server and updates gui"""
        self.s.send(bytes('paid', 'utf-8'))
        self.clear_fields()
        self.get_tickets()
        self.update_tickets()

    def add_money(self, amount='full', payment_type='card'):
        """processes payment"""

        # check if there is any outstanding balance to pay
        if Client.total_value:
            # if customer is old fashioned and payment type is cash...
            if payment_type == 'cash':
                # decrease total_value by inserted money
                Client.total_value -= float(amount)
                # set text variable to show what is left to pay
                text = f'£{Client.total_value:6.2f} is due'
                self.inserted_money.delete(0, 'end')  # clear inserted_money entry widget
                self.inserted_money.insert('end', f'{text}')  # show updated value in inert_money entry widget
                if Client.total_value <= 0:  # call paid method if total_value field reaches or goes below 0
                    self.paid()
            else:  # if paid with card
                self.inserted_money.delete(0, 'end')  # clear inserted money entry widget
                Client.total_value = 0  # set balance to pay to 0
                self.paid()

    def enter_product(self, value):
        """show customer their choice refuse if they added more than in stock"""

        # clear bottom screen if it is not a list of tickets
        if self.bottom_screen.get('1.0', '1.1').isalpha():
            self.bottom_screen.delete('1.0', 'end')
        choice = value[0:2]  # extract choice from self.item entry
        quantity = value[2:]  # extract quantity from self.item entry
        # check if choice available in transaction_received, quantity is a digit different to 0
        if choice in Client.transaction_received.keys() and quantity.isdigit() and quantity != '0':
            record = Client.transaction_received[choice]  # save object in record variable
            quantity = int(quantity)
            ticket = Ticket(record.id, record.route, record.price, quantity)  # create ticket object to be added
            if ticket.id not in Client.transaction_to_send.keys():  # if ticket id not in transaction to send
                Client.transaction_to_send[choice] = ticket  # add ticket.id to to dictionary transaction to send
            else:
                Client.transaction_to_send[choice].stock += quantity  # otherwise increase quantity of the tickets
            # add product info to the bottom screen
            self.bottom_screen.insert('end', f'{quantity} x {record.route} @ £{record.price} \
                            \t\t\t= £{record.price*quantity:6.2f}\n')
        else:
            # display feedback that user selected invalid id or quantity
            self.bottom_screen.insert('end', 'Incorrect ID or quantity\n')
            # call add_another method to let user to select another product/quantity
            self.add_another()

    def add_another(self):
        """clears screen above selection tool allowing adding more items"""

        self.item.delete(0, 'end')  # clear self.item entry

    def cancel_transaction(self):
        """voids current transaction"""

        Client.transaction_to_send.clear()  # clear the list transaction_to_send
        self.item.delete(0, 'end')  # clear self.item entry
        self.bottom_screen.delete('1.0', 'end')  # clear the bottom screen
        self.inserted_money.delete(0, 'end')  # clear inserted money screen
        self.bottom_screen.insert('end', 'Sorry, we could not provide you with your \nchoice today.\
 We hope to see you soon \nagain. Have a great day\n')  # display the message in the bottom screen

    @staticmethod
    def generate_csv():
        """generates csv file from products added by the customer"""

        with open('transaction.csv', 'w') as transaction_csv:  # open transaction.csv to write
            for key in Client.transaction_to_send.keys():  # for every object in Customer.transaction_to_send
                # assign value of the current key to the variable ticket
                ticket = Client.transaction_to_send[key]
                record = f'{ticket}\n'  # create text variable record
                transaction_csv.write(record)  # and append the record to the transaction_csv file

    def generate_receipt(self):
        """generates receipt"""


        available_tickets = pickle.loads(self.s.recv(1024))  # retrieve available tickets
        self.bottom_screen.insert('end', 'RECEIPT\n')  # give receipt title
        Client.total_value = 0  # set total value of transaction
        for ticket in available_tickets:
            if not ticket.stock:
                # create text variable to add on the bottom screen
                text = f'{ticket.route} was not available today\n'
            else:
                text = ''  # create variable text to display message on the receipt
                # check if value of order greater than value available in stock and add relevant message to the receipt
                if Client.transaction_to_send[ticket.id].stock > ticket.stock:
                    text += 'Quantity for the following ticket was reduced due to insufficient stock level\n'
                record_value = ticket.stock * ticket.price  # calculate value of the record
                # create text variable to add on the bottom screen
                text += f'{ticket.stock} x {ticket.route} @ £{ticket.price:5.2f} = £{record_value:5.2f} \n'
                Client.total_value += record_value  # increase total value of transaction by record value
            self.bottom_screen.insert('end', text)  # add print value of the text variable on the bottom screen
        # display total amount to pay & scalp the customer
        self.bottom_screen.insert('end', f'\n\n\t\tTotal to pay: £{Client.total_value:5.2f}\n\n')
        self.bottom_screen.insert('end', 'Insert cash or pay with card')
        self.inserted_money.insert('end', f'£{Client.total_value:5.2f} is due')

    def finish_and_pay(self):
        """guides user towards payment"""

        self.get_tickets()  # update the tickets objects
        self.update_tickets()  # update the information on the gui
        self.bottom_screen.delete('1.0', 'end')  # clear bottom screen
        self.item.delete(0, 'end')  # clear self.item entry
        if Client.transaction_to_send:  # if there is data in Customer.transaction_to_send
            self.generate_csv()
            self.send_transaction()
            self.generate_receipt()
        else:
            self.bottom_screen.insert('end', 'Select your products first')

    def close(self):
        """ensures closing the socket before closing the app"""

        self.s.close()
        self.destroy()


if __name__ == '__main__':
    root = Client()  # create Customer object
    root.mainloop()  # prevent root window from being garbage collected
