import requests
import multiprocessing
import time
from datetime import datetime
import logging


class Connection(object):
	def __init__(self):
		self.xml_list = []
		self.table_meta_list = []
		self.table_list = []
		self.table_dict_of_list = {}
		#TODO Read from config file (Service Now + Remedy)
		self.table_conf_file = 'serveice_now_table_list.conf'

		#TODO Read from config file
		self.limit = 1000
		self.source = 'https://dev57608.service-now.com'
		self.table = 'sys_db_object'
		self.user = 'admin'							
		self.pwd = 'ILikeFriday@1'
		self.headers = {"Content-Type":"application/json","Accept":"application/json"}

		self.log_file = Connection.logger_file_name()
		logging.basicConfig(filename=self.log_file, format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',datefmt="%Y-%m-%d %H:%M:%S", level=logging.DEBUG)
		logging.info("Service now import process is started")

	@staticmethod
	def logger_file_name():
		now = datetime.now()
		file_name = "Service_now_parser_" + now.strftime("%Y-%m-%d_%H.%M.%S") + ".log"
		return file_name

	def populate_table_file(self):
		#Re-write the file (No need to check if exits)
		with open(self.table_conf_file, 'w') as fp:
			fp.write("#Service now table configuration file, please mark (T/F) to import the tables.\n")
			fp.write("\n")
			for x in self.table_list:
				fp.write(x + '\tF\n')

	def get_response(self, table_name):
		#Construct URL and request. Return the response
		#url = source+'/api/now/v2/table/'+table+'?sysparm_display_value=all&sysparm_exclude_reference_link=true&sysparm_limit={}'.format(limit)
		url = self.source+'/api/now/v2/table/'+table_name+'?sysparm_display_value=all&sysparm_exclude_reference_link=true&sysparm_limit={}'.format(self.limit)
		try:
			response = requests.get(url, auth=(self.user, self.pwd), headers=self.headers)
		except Exception as Ereq:
			print "Exception:", Ereq
			logging.error("Response status Exception: {}".format(Ereq))
		return response

	def validate_response_code(self, response):
		if response.status_code != 200:		
			logging.error("Response status: {}".format(response.status_code))
			logging.error("Response headers: {}".format(response.headers))
			logging.error("Response error: {}".format(response.json()))
			return True
		else:
			return False

	'''
	Request ->Response -> pagination -> table list
	'''
	def get_table_name(self):
		response = self.get_response(self.table)
		
		# Check for HTTP codes other than 200		
		if self.validate_response_code(response):
			exit()
		
		self.xml_list.append(response.content)

		while (response.links.get('next', False)):
			response = requests.get(response.links['next']['url'],auth=(self.user, self.pwd), headers=self.headers)
			self.table_meta_list.append(response.json())
		
		for table in self.table_meta_list:
			for x in table['result']:
				self.table_list.append((x['name']['value']))

		self.populate_table_file()

	def get_table_details(self):
		for table in self.table_list[2:]:
			print "table:", table
			response = self.get_response(table)

			# Check for HTTP codes other than 200
			if self.validate_response_code(response):
				print "inside validate_response_code"
				exit()
			
			self.table_dict_of_list[table]=response.content


start = time.time()
c = Connection()
c.get_table_name()
c.get_table_details()
end = time.time()
print "table_dict_of_list:", c.table_dict_of_list
print "serial time:", end - start