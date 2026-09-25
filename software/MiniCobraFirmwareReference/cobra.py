from MotorDriver import MotorInterface
from constants import motor_constants
import threading
import time
import os
from datetime import datetime

class COBRA:
	def __init__(self, status_rate=10, logging=True):
		self.motor_interface = MotorInterface([10, 11], "/dev/ttyUSB0", cobra_mini=False)
		self.motor_interface.start()
		
		self.status = None
		self.status_address = {
			"q": motor_constants.ADDR_PRESENT_POSITION,
            "q_dot": motor_constants.ADDR_PRESENT_VELOCITY, 
			"v": motor_constants.ADDR_PRESENT_INPUT_VOLTAGE,
			"i": motor_constants.ADDR_PRESENT_CURRENT, 
            "T": motor_constants.ADDR_PRESENT_TEMPERATURE
			}

		self.status_thread = threading.Thread(target=self.get_status, kwargs={'rate':status_rate})
		self.status_thread.start()

		if logging:
			self.log_thread = threading.Thread(target=self.log_status, kwargs={'filepath':"./Logs/" + str(datetime.now())})
			self.log_thread.start()


	def get_status(self, rate=10):
		try:
			while True:
				self.status = self.motor_interface.get_status(self.status_address)
				time.sleep(1/rate)

		except KeyboardInterrupt:
			pass

		except Exception as e:
			print(e)

	def log_status(self, filepath):
		os.mkdir(filepath)
		print("Logging to:", os.getcwd() + filepath)
		last_status = None
		keys = self.status_address.keys()

		try:
			while True:
				if self.status != last_status:
					for key in keys:
						with open(filepath + key + ".csv", 'w') as f:
							f.write(self.status[key])

		except KeyboardInterrupt:
			pass

		except Exception as e:
			print(e)

	def __del__(self):
		self.motor_interface.stop()

if __name__ == '__main__':
	cobra = COBRA(logging=False)
	print(cobra.status)