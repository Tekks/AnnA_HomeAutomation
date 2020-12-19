import smbus
from time import *

class i2c_device:
   def __init__(self, addr, port=1):
      self.addr = addr
      self.bus = smbus.SMBus(port)

   def write_cmd(self, cmd):
      self.bus.write_byte(self.addr, cmd)
      sleep(0.0001)

   def write_cmd_arg(self, cmd, data):
      self.bus.write_byte_data(self.addr, cmd, data)
      sleep(0.0001)

   def write_block_data(self, cmd, data):
      self.bus.write_block_data(self.addr, cmd, data)
      sleep(0.0001)

   def read(self):
      return self.bus.read_byte(self.addr)

   def read_data(self, cmd):
      return self.bus.read_byte_data(self.addr, cmd)

   def read_block_data(self, cmd):
      return self.bus.read_block_data(self.addr, cmd)
      