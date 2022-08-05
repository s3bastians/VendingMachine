import mysql.connector as mysql
import socket
import pickle
import threading
from dataclasses import dataclass


@dataclass  # indicate that Ticket class is data class
class Ticket:  # create ticket data class
    id: str
    route: str
    price: float
    stock: int

    # create string method for ticket class
    def __str__(self):
        return f'{self.id},{self.route},{self.price},{self.stock}'


class Server:

    def __init__(self):
        self.db = self.connect_db()  # create mysql connector object, connect to database vending
        self.cursor = self.db.cursor()  # create cursor object in mysql connector object self.db
        self.s = self.set_up_connection()  # set up socket object
        self.wait_for_connection()   # wait for clients to connect

    @staticmethod
    def connect_db():
        """returns mysql connector object linked to database VENDING"""

        return mysql.connect(
            host='localhost',
            user='vending',
            password='vending90?',
            database='VENDING'
            )

    def current_db(self):
        """returns current data stored in the table TICKETS"""

        self.cursor.execute('SELECT * FROM TICKETS')  # query the VENDING database
        return self.cursor.fetchall()  # return all tickets from database

    @staticmethod
    def receive_transaction(client_socket):
        """receives data from the client and store in csv file"""

        received_transaction = pickle.loads(client_socket.recv(1024))  # get transaction from client
        with open('transaction.csv', 'w') as transaction:  # open transaction.csv file
            for line in received_transaction:
                transaction.write(line)  # store data from transaction received in csv file

    def check_availability(self):
        """Compares received transaction with available stock
        and returns stock reduced to the level of stock available"""

        tickets_db = dict()  # create dictionary to store current database
        # add elements of database to dictionary
        for ticket in self.current_db():
            ticket_id = ticket[0]
            ticket_route = ticket[1]
            ticket_price = ticket[2]
            ticket_stock = ticket[3]
            tickets_db[ticket_id] = [ticket_route, ticket_price, ticket_stock]
        # create list for available tickets
        available_tickets = []
        # checks availability for each record of received transaction and adds maximum amounts to the list
        for record in open('transaction.csv', 'r'):
            current_item = record.strip().split(',')
            current_item_id = current_item[0]
            current_item_route = current_item[1]
            current_item_price = current_item[2]
            current_item_stock = current_item[3]
            available_stock = tickets_db[current_item_id][2]
            if int(current_item_stock) > int(available_stock):
                current_item_stock = available_stock
            available_tickets.append(Ticket(current_item_id, current_item_route,
                                            float(current_item_price), int(current_item_stock)))
        return available_tickets

    def update_records(self, available_tickets):
        """updates data based on the received transaction from the client"""

        for ticket in available_tickets:  # for every record in available tickets
            ticket_id = ticket.id
            stock = ticket.stock
            # decrease relevant stock values in the database
            self.cursor.execute(f'UPDATE TICKETS SET Stock = Stock - {stock} WHERE ID="{ticket_id}"')
            self.db.commit()  # commit changes to database

    @staticmethod
    def set_up_connection():
        """establishes TCP connection"""

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create socket object
        HOST = socket.gethostbyname(socket.gethostname() + ".local")  # get IP address and store to variable host
        PORT = 65255  # set the port
        s.bind((HOST, PORT))  # bind the socket
        return s

    def service_client(self, client_socket, address):
        print(f'[{address}] has been successfully connected')
        while True:
            try:
                command = client_socket.recv(12).decode('utf-8')  # accept command from the client
                if command == 'transaction':
                    self.receive_transaction(client_socket)  # receive transaction form client save to csv
                    available_tickets = self.check_availability()  # check if requested products in stock
                    client_socket.send(pickle.dumps(available_tickets))  # send available_tickets to client
                elif command == 'paid':
                    self.update_records(available_tickets)  # update database on the server
                else:
                    database = self.current_db()  # fetch data from the database
                    client_socket.send(pickle.dumps(database))  # send database to the client
            except:
                print(f'[{address}] has disconnected.')
                client_socket.close()  # close the client socket
                break

    def wait_for_connection(self):
        self.s.listen()  # listen for incoming connection
        while True:
            print('Waiting for someone to connect...')
            # accept incoming connection and save returned tuple to client_socket object and address
            client_socket, address = self.s.accept()
            # create new thread to service connected client
            thread = threading.Thread(target=self.service_client, args=(client_socket, address))
            thread.start()


if __name__ == '__main__':
    main = Server()
