#  lsof -i :8000
#  sudo kill -9 id

import socket
import threading
import sys
from PyQt5 import QtCore, QtGui , QtWidgets
from PyQt5.QtWidgets import QMessageBox
import time
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog, QLineEdit
from PyQt5.uic import loadUi


# Initial setup
global s
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 5000
IP = input('Enter the IP address of the sever: ')
s.connect((IP, port))
global client_running
client_running = True

#--------------------------------------------------------#
#					GUI FOR CHATTING
# 
# 
#--------------------------------------------------------#
class chat_gui(QDialog):
	def __init__(self):
		super(chat_gui, self).__init__()
		loadUi('chat.ui', self)
		self.setWindowTitle('Net Chating Chat')
		self.SendButton.clicked.connect(self.SendButton_clicked)
		self.ClearButton.clicked.connect(self.ClearButton_clicked)
		self.QuitButton.clicked.connect(self.QuitButton_clicked)
		#timer
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.timerEvent)
		self.timer.start(100)
		self.timerchatlist = QtCore.QTimer()
		self.timerchatlist.timeout.connect(self.timerEventchatlist)
		self.timerchatlist.start(100)
	@pyqtSlot()
	def SendButton_clicked(self):
		message = self.SendLineEdit.text()
		s.send(message.encode('ascii'))
		message = 'Me>> ' + message
		self.StatusListWidget.addItem(message)
		self.SendLineEdit.clear()
	def ClearButton_clicked(self):
		self.SendLineEdit.clear()
	def QuitButton_clicked(self, event):
		global client_running
		exitmessage = 'Do you want to exit?'
		resp = QMessageBox.question(self, 'Exit', exitmessage, QMessageBox.Yes, QMessageBox.No)
		if resp == QMessageBox.Yes: 
			# event.accept()
			s.send('**quit'.encode('ascii'))
			client_running = False
			self.close()
		else: pass
	def timerEvent(self):
		global message
		global printmessagecontrol
		if printmessagecontrol:
			printmessagecontrol = False
			self.StatusListWidget.addItem(message)
	def timerEventchatlist(self):
		global listchat
		global printchatlistcontrol
		if printchatlistcontrol:
			printchatlistcontrol = False
			self.ChatlistListWidget.clear()
			self.ChatlistListWidget.addItem(listchat)

#--------------------------------------------------------#
#					GUI FOR LOGGING
# 
# 
#--------------------------------------------------------#
class Login_Signup_gui(QDialog):
	def __init__(self):
		super(Login_Signup_gui, self).__init__()
		loadUi('login_signup.ui', self)
		self.setWindowTitle('Net Chating Login or Signup')
		self.LoginPasswordLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
		self.SignupPasswordLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
		self.LoginLoginButton.clicked.connect(self.LoginLoginButton_clicked)
		self.LoginClearButton.clicked.connect(self.LoginClearButton_clicked)
		self.SignupSignupButton.clicked.connect(self.SignupSignupButton_clicked)
		self.SignupClearButton.clicked.connect(self.SignupClearButton_clicked)
	@pyqtSlot()
	def LoginLoginButton_clicked(self):
		global message
		global logincontrol
		global sendcontrol
		sendcontrol = False
		logincontrol = False
		username = self.LoginUsernameLineEdit.text()
		password = self.LoginPasswordLineEdit.text()
		message = 'login' + '\n' + username + '\n' + password
		self.LoginUsernameLineEdit.clear()
		self.LoginPasswordLineEdit.clear()
		time.sleep(1)
		sendcontrol = True

		# wait a little
		timewait = 0
		while (not logincontrol):
			timewait += 1
			time.sleep(1)
			if timewait == 5:
				break

		if logincontrol:
			self.chatui = chat_gui()
			loginui.hide()
			self.chatui.show()
		else:
			QMessageBox.critical(loginui, 'Error', 'Log in fail!!!')

	def LoginClearButton_clicked(self):
		self.LoginUsernameLineEdit.clear()
		self.LoginPasswordLineEdit.clear()
	def SignupSignupButton_clicked(self):
		global message
		global signupcontrol
		global sendcontrol
		sendcontrol = False
		signupcontrol = False
		username = self.SignupUsernameLineEdit.text()
		password = self.SignupPasswordLineEdit.text()
		name = self.SignupNameLineEdit.text()
		message = 'signup' + '\n' + username + '\n' + password + '\n' + name
		time.sleep(1)
		self.SignupUsernameLineEdit.clear()
		self.SignupPasswordLineEdit.clear()
		self.SignupNameLineEdit.clear()
		sendcontrol = True
		# wait a little
		timewait = 0
		while (not signupcontrol):
			timewait += 1
			time.sleep(1)
			if timewait == 5:
				break

		if signupcontrol:
			QMessageBox.critical(loginui, 'Signup Success', 'You can log in now!!!')
		else:
			QMessageBox.critical(loginui, 'Error', 'Sign up fail!!!')

	def SignupClearButton_clicked(self):
		self.SignupUsernameLineEdit.clear()
		self.SignupPasswordLineEdit.clear()
		self.SignupNameLineEdit.clear()

#--------------------------------------------------------#
#					RECEIVE
# 
# 
#--------------------------------------------------------#
def receive_message(sk):
	global printmessagecontrol
	global logincontrol
	global client_running
	global message
	global printchatlistcontrol
	global listchat
	global signupcontrol
	printchatlistcontrol = False
	printmessagecontrol = False
	logincontrol = False
	client_running = True
	server_down = False
	signupcontrol = False
	num = 0
	while (not logincontrol) and (not server_down):
		try:
			message = sk.recv(1024).decode('ascii')
			if '**LoginSuccess' in message:
				logincontrol = True
			elif '**SignupSuccess' in message:
				signupcontrol = True
		except:
			message = 'Server down. Press Enter to exit...'
			printmessagecontrol = True
			server_down = True
	while client_running and (not server_down):
		try:
			message = sk.recv(1024).decode('ascii')
			if '**chatlist' in message:
				printchatlistcontrol = True
				listchat = message.replace('**chatlist' + '\n', '')
			else:
				printmessagecontrol = True
		except:
			message = 'Server down. Press Enter to exit...'
			printmessagecontrol = True
			server_down = True

#--------------------------------------------------------#
#					SEND
# 
# 
#--------------------------------------------------------#
def send_message(sk):
	global sendcontrol
	sendcontrol = False
	global message
	global client_running
	client_running = True
	server_down = False
	while client_running and (not server_down):
		try:
			if sendcontrol:
				sk.send(message.encode('ascii'))
				sendcontrol = False
		except:
			message = 'Server down. Press Enter to exit...'
			printmessagecontrol = True
			server_down = True

#--------------------------------------------------------#
#					THREAT AND INITIAL GUI
# 
# 
#--------------------------------------------------------#
threading.Thread(target = send_message, args = (s,)).start()
threading.Thread(target = receive_message, args = (s,)).start()
app = QApplication(sys.argv)
loginui = Login_Signup_gui()
loginui.show()
sys.exit(app.exec_())
