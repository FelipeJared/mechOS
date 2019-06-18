"""Code for local implementations of data transfer. Only handles the reader and
the writer

 ..moduleauthors:: Christian Gould <christian.d.gould@gmail.com>
                   Mohammad Shafi <ma.shafi99@gmail.com>
"""
class reader(object):

	"""Reader class. Allows the user to pull data locally from memory. Prevents
	the need to publish or subscribe unecessarily when local data transfer would
	be faster
	"""

	def __init__(self, volatile_memory):
		"""Initializes the reader. Accepts a dictionary and lets the reader
		retrieve any data user wishes, so long as the key is stored within the
		dictionary.

		:param volatile_memory: dictionary holding all the values we wish to
								read from
		:type volatile_memory: dictionary
		"""
		self.MEM=volatile_memory

	def read(self, register):
		"""Takes in the key for the data we want to read, returns value.

		:param register: the key for the message we wish to read
		:type register: object
		:returns: the value associated with the key register
		:raises: KeyError
		"""
		return self.MEM[register]

class writer(object):

	"""Initializes the writer. Accepts a dictionary, writes whatever values we
	need to whatever key the user wants
	"""

	def __init__(self, volatile_memory):
		"""Initializes the writer

		:param volatile_memory: dictionary where we want to store our data in
		:type volatile_memory: dictionary
		"""
		self.MEM=volatile_memory

	def write(self, msg, register):
		"""Writes the message desired to the key desired within the dictionary.
		Automatically creates the key if not found

		:param msg: message we want to store, value in (key, value) pair
		:type msg: object
		:param register: location to store message, key in (key, value) pair
		:type register: object
		"""
		self.MEM[register]=msg
