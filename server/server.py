import socket
import threading
import sqlite3
from requests import get
import time
# import server_functions as sefu

# Get external IP
#IP = get('https://api.ipify.org').text
#port = 5000

# IP = str(socket.gethostbyname(socket.gethostname()))
# port = 5000
IP = '172.20.10.2'
port = 5000
# Available for TCP/IP connections
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', port))
s.listen()

# Inform IP and port of the server
print('Server ready!')
print('The IP address of the server: %s'%IP)
print('And Port: %s'%port)
global clients_online
global serverRunning
global chatlistcontrol
chatlistcontrol = False
clients_online = {}
serverRunning = True
#--------------------------------------------------------#
#					PROCESSING
# 
# 
#--------------------------------------------------------#
def handle_client(client, name):
	global chatlistcontrol
	connection = True
	keys = clients_online.keys()
	helps = 'There are four commands in Net chatting\n\
	1::**quit=>To cancel the connect\n\
	2::**sendall=>To send the message to all users currently online\n\
	3::**name=>To send the message to "name"'
	time.sleep(2)
	keyname = 'Hello ' + name + '! \n' + 'Welcome to Net chatting. Type **help to see all commands.\n'
	client.send(keyname.encode('ascii'))
	while connection:
		try:
			message = client.recv(1024).decode('ascii')
			if '**quit' in message:
				print('%s quit1'%str(name))
				clients_online.pop(name)
				chatlistcontrol = True
				connection = False
			elif '**sendall' in message:
				content = name + '>> ' + message.replace('**sendall','')
				for usernameinlist, address in clients_online.items():
					if (usernameinlist != name):
						address.send(content.encode('ascii'))
			elif '**help' in message:
				client.send(helps.encode('ascii'))
			else:
				violate = False
				for namerecei in keys:
					if '**' + namerecei in message:
						content = name + '>> ' + message.replace('**' + namerecei, '')
						clients_online[namerecei].send(content.encode('ascii'))
						violate = True
				if violate == False:
					client.send('Message invalid. Send again, please!!!'.encode('ascii'))
		except:
			try:
				clients_online.pop(name)
				chatlistcontrol = True
				print(name + ' quit2')
				connection = False
			except:
				pass

#--------------------------------------------------------#
#					LOG IN
# 
# 
#--------------------------------------------------------#
def check_login(user_name, password):
	try:
		with sqlite3.connect('accounts.db') as db:
			data = db.cursor()
		data.execute('SELECT * FROM accounts WHERE username = ? and password = ?', (user_name, password))
		check = data.fetchone()
		name = check[2]
		login = False
		if check != None:
			login = True
		db.commit()
		db.close()
		return login, name
	except:
		return False, False

#--------------------------------------------------------#
#						CREATE ACCOUNT
# 
# 
#--------------------------------------------------------#
def create_account(user_name, password, name):
	try:
		db = sqlite3.connect('accounts.db')
		data = db.cursor()
		data.execute('SELECT * FROM accounts WHERE username = ? and name = ?', (user_name, name))
		check = data.fetchone()
		signup = False
		if check == None:
			data.execute('INSERT INTO accounts VALUES (?, ?, ?)',(user_name, password, name))
			signup = True
		db.commit()
		db.close()
		return signup
	except:
		return False
#--------------------------------------------------------#
#					UPDATE CHATLIST
# 
# 
#--------------------------------------------------------#
def updatechatlist():
	global serverRunning
	global chatlistcontrol
	global clients_online
	while serverRunning:
		if chatlistcontrol:
			chatlistcontrol = False
			keys = clients_online.keys()
			message = '**chatlist'
			for listname in keys:
				message = message + '\n' + listname
			for listname in keys:
				clients_online[listname].send(message.encode('ascii'))
#--------------------------------------------------------#
#					MAIN LOOP
# 
# 
#--------------------------------------------------------#
while serverRunning:

	client, address = s.accept()
	connect_one = True

	while connect_one:
		try:
			first_data = client.recv(1024).decode('ascii')
			first_data = first_data.splitlines()
			mode = first_data[0]
			user_name = first_data[1]
			password = first_data[2]
			if mode == 'login':
				key, name = check_login(user_name, password)
				if key == True:
					client.send('**LoginSuccess'.encode('ascii'))
					print('%s connected to the server'%str(name))
					if(client not in clients_online):
						clients_online[name] = client
						chatlistcontrol = True
						threading.Thread(target = handle_client, args = (client, name)).start()
						threading.Thread(target = updatechatlist, args = ()).start()
						connect_one = False

			elif mode == 'signup':
				name = first_data[3]
				key = create_account(user_name, password, name)
				if key == True:
					client.send('**SignupSuccess'.encode('ascii'))
		except:
			pass

