"""Code for network implementations of data transfer. Only handles the publisher
and the subscribers

 ..moduleauthors:: Christian Gould <christian.d.gould@gmail.com>
                   Mohammad Shafi <ma.shafi99@gmail.com>
"""

import socket

class publisher(object):
	"""Publisher class. Creates methods and means to publish data over UDP
	"""

	def __init__(self, ip_router):
		"""Initializes the publisher, uses the ip dictionary to access all the
		necessary functions, like the address and sockets

		:param ip_router: dictionary that holds sockets, addresses, etc for UDP
		:type ip_router: dictionary
		"""
		self.ip_router=ip_router

	def publish(self, msg, register):
		"""Sends the message over udp. Address, publisher socket, and subscriber
		socket are all nested in the dictionary. This is how it accesses them

		:param msg: The message to send over UDP
		:type msg: bytes
		:param register: key to access all the publisher info
		:type register: object
		"""
		address  = self.ip_router[register]['address']
		pub_sock = self.ip_router[register]['sockets'][0]
		sub_sock = self.ip_router[register]['sockets'][1] #sub_sock for reference

		return 	pub_sock.sendto(msg, address)


class subscriber(object):
	"""Subscriber class. Creates methods and means to subscribe to data over UDP
	"""

	def __init__(self, ip_router):
		"""Initializes the subscriber, uses the ip dictionary to access all the
		necessary functions, like the address and sockets

		:param ip_router: dictionary that holds sockets, addresses, etc for UDP
		:type ip_router: dictionary
		"""
		#TODO double check format for json:

		#self.UDP_socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		#self.TCP_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.ip_router=ip_router
		#self.type=type


	def subscribe(self, register):
		"""Recieves the message via udp. Address, publisher socket, and
		subscriber socket are all nested in the dictionary. This is how it
		accesses them

		:param register: key to access all the publisher info
		:type register: object
		"""

		#TODO double check format for json:
		if self.ip_router[register]['type']=='TCP':
			pass

		else:
			address  = self.ip_router[register]['address']
			pub_sock = self.ip_router[register]['sockets'][0]
			sub_sock = self.ip_router[register]['sockets'][1] #sub_sock for reference

			address  = self.ip_router[register]['address']
			pub_sock = self.ip_router[register]['sockets'][0]
			sub_sock = self.ip_router[register]['sockets'][1]

			data, addr = sub_sock.recvfrom(4096)

			return data
