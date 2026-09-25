from dynamixel_sdk import *              # Uses Dynamixel SDK library
from constants import motor_constants
from threading import Lock
from data_processor import twos_comp_filter
from datetime import datetime, timezone

class MotorInterface:
    """
    Class representing all interactions between the software and the motors, restricted
    to reads and writes to the motors via the Dynamixel SDK.    
    """
    
    def __init__(self, ids, deviceName, cobra_mini=False):
        """
        Initialize all relevant private fields that represent objects that are essential for communication with the robot, such as the port and packet handler. Additionally we have groupWrite/Read for handling groups of ids that are read/written at the same time.

        Args:
            
            ids : array of motor id numbers, from 0 to n, INCLUDING the latch motor
        
            deviceName : string representing the USB serial port device name, such as COM3 for 
                windows and whatever shows up when you type "ls /dev/tty.usb*" in terminal for Mac/Linux
            
        """

        tester_list = []
        tester_list.extend(motor_constants.JOINT_IDS)
        if not cobra_mini:
            tester_list.append(motor_constants.LATCH_ID)
        self.ids = ids
        self.cobra_mini = cobra_mini
        # on init it's not started yet
        self.started = False
        if deviceName == "MOCK_DRIVER":
            pass
        else:
            # Initialize PortHandler instance
            # Set the port path
            # Get methods and members of PortHandlerLinux or PortHandlerWindows
            self._port_handler = PortHandler(deviceName)

            # Initialize PacketHandler instance
            # Set the protocol version
            # Get methods and members of Protocol1PacketHandler or Protocol2PacketHandler
            self._packet_handler = PacketHandler(motor_constants.PROTOCOL_VERSION)

            # Initialize GroupSyncWrite instances for all writable addresses
            self._group_write = {}
            for addr, size in motor_constants.WRITABLE_ADDR_LENS.items():
                self._group_write[addr] = GroupSyncWrite(self._port_handler, self._packet_handler, addr, size)

            # Initialize GroupSyncRead instances for all read-only addresses
            self._group_read = {}
            for addr, size in motor_constants.RODATA_ADDR_LENS.items():
                self._group_read[addr] = GroupSyncRead(self._port_handler, self._packet_handler, addr, size)

        # lock should help thread safety
        self.packet_lock = Lock()

    def is_cobra_mini(self):
        """
        Very simple

        Returns:
            True if Driver is initialized for COBRA mini (no latch), and false otherwise.
        """
        return self.cobra_mini

    def get_ids(self, include_latch=False):
        """
        Getter function for ids that passed by value.
        """

        # create a new list that has the same values as self.ids, but isn't
        # the same object
        if not include_latch and motor_constants.LATCH_ID in self.ids:
            # have everything except the last item
            return self.ids[:len(self.ids) - 1]
        return self.ids[::]

    def start(self):
        """
            Start driver, connect controller and motors.
        """
        if self.started:
            raise Exception("Driver already started, run driver.stop()")

        # Open Port
        if self._port_handler.openPort():
            print("Succeeded to open the port")
        else:
            raise Exception("Failed to open the port.")

        # Set port baudrate
        if self._port_handler.setBaudRate(motor_constants.BAUDRATE):
            print("Succeeded to change the baudrate.")
        else:
            self._port_handler.closePort()
            raise Exception("Failed to change the baudrate.")
        self.started = True

        # enable torque for all motors
        for i in self.ids:
            self.enable_torque(i)

    def stop(self):
        """
            Stop driver and free resources when finished running.
        """
        self.packet_lock.acquire()

        if not self.started:
            raise Exception("Driver not yet started, run driver.start()")

        # Clear syncread parameter storage for all reads and writes
        for item in self._group_read.values():
            item.clearParam()
        for item in self._group_write.values():
            item.clearParam()

        self.packet_lock.release()
        for i in self.ids:
            self.disable_torque(i)
        self.packet_lock.acquire()

        # Close port
        self._port_handler.closePort()
        self.started = False
        self.packet_lock.release()

    def get_group_rw(self, addr):
        """
            Getter method for retrieving a groupWrite/groupRead object from driver
        """
        if addr in motor_constants.WRITABLE_ADDR_LENS.keys():
            return self._group_write.get(addr)
        elif addr in motor_constants.RODATA_ADDR_LENS.keys():
            return self._group_read.get(addr)
        else:
            raise Exception("invalid address, see constants")

    def get_txrx_result(self, comm_result):
        """
            Getter for txrx result from packet handler given communication result.
        """
        if not self.started:
            raise Exception("Driver not yet started, run driver.start()")
        return self._packet_handler.getTxRxResult(comm_result)

    def enable_torque(self, id):
        """
            Enables torque for a motor given its ID, makes motor controllable and resist outside
            forces to change the position.
        """
        if not self.started:
            raise Exception("Driver not yet started, run driver.start()")
        self.packet_lock.acquire()

        dxl_comm_result, dxl_error = self._packet_handler.write1ByteTxRx(self._port_handler, id,
                                                                        motor_constants.ADDR_TORQUE_ENABLE, motor_constants.TORQUE_ENABLE)
        if dxl_comm_result != COMM_SUCCESS:
            raise Exception("ID:%d -- %s" % (id, self._packet_handler.getTxRxResult(dxl_comm_result)))
        elif dxl_error != 0:
            raise Exception("ID:%d -- %s" % (id, self._packet_handler.getRxException(dxl_error)))
        else:
            print("Dynamixel#%d has been successfully connected" % id)
        self.packet_lock.release()

    def disable_torque(self, id):
        """
        Disable torque for a motor given its ID. Makes motor "flexible".
        """
        if not self.started:
            raise Exception("Driver not yet started, run driver.start()")
        self.packet_lock.acquire()
        dxl_comm_result, dxl_error = self._packet_handler.write1ByteTxRx(self._port_handler, id,
                                                                        motor_constants.ADDR_TORQUE_ENABLE, motor_constants.TORQUE_DISABLE)
        if dxl_comm_result != COMM_SUCCESS:
            raise Exception("ID:%d -- %s" % (id, self._packet_handler.getTxRxResult(dxl_comm_result)))
        elif dxl_error != 0:
            raise Exception("ID:%d -- %s" % (id, self._packet_handler.getRxException(dxl_error)))
        self.packet_lock.release()

    def single_read(self, id, addr):
        if not self.started:
            raise Exception("Driver not yet started, run driver.start()")
        if addr not in motor_constants.RODATA_ADDR_LENS.keys():
            raise Exception("invalid address, not included under readable addresses")
        # use specific packetHandler method depending on length of data

        self.packet_lock.acquire()
        len_data = motor_constants.RODATA_ADDR_LENS[addr]
        if len_data == 1:
            result, dxl_comm_result, dxl_error = self._packet_handler.read1ByteTxRx(self._port_handler, id,
                                                                                                 addr)
        elif len_data == 2:
            result, dxl_comm_result, dxl_error = self._packet_handler.read2ByteTxRx(self._port_handler, id,
                                                                                                 addr)
        elif len_data == 4:
            result, dxl_comm_result, dxl_error = self._packet_handler.read4ByteTxRx(self._port_handler,
                                                                                                 id,
                                                                                                 addr)
        else:
            raise Exception("Invalid data size, see Dynamixel SDK packetHandler definition")
        if dxl_comm_result != COMM_SUCCESS:
            raise Exception("%s" % self._packet_handler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            raise Exception("%s" % self._packet_handler.getRxException(dxl_error))

        self.packet_lock.release()
        return twos_comp_filter(result, len_data)

    def single_write(self, id, addr, data):
        """
            Writes a single value of data to the given address for a single motor
            specified with id.

            Args:
                id: valid motor id
                addr: valid writable address
                data: information to transmit, in Dynamixel Units
        """
        if not self.started:
            raise Exception("Driver not yet started, run driver.start()")
        if addr not in motor_constants.WRITABLE_ADDR_LENS.keys():
            raise Exception("invalid address, not included under writable addresses")
        if addr == motor_constants.ADDR_GOAL_POSITION and (id != motor_constants.LATCH_ID) and ((data < motor_constants.MIN_POSITION) or (data > motor_constants.MAX_POSITION)):
            raise Exception("Invalid goal position %d, min: %d, max: %d" % (data, motor_constants.MIN_POSITION, motor_constants.MAX_POSITION))

        self.packet_lock.acquire()

        # use specific packetHandler method depending on length of data
        len_data = motor_constants.WRITABLE_ADDR_LENS[addr]
        if len_data == 1:
            dxl_comm_result, dxl_error = self._packet_handler.write1ByteTxRx(self._port_handler, id, addr, data)
        elif len_data == 2:
            dxl_comm_result, dxl_error = self._packet_handler.write2ByteTxRx(self._port_handler, id, addr, data)
        elif len_data == 4:
            dxl_comm_result, dxl_error = self._packet_handler.write4ByteTxRx(self._port_handler, id, addr, data)
        else:
            raise Exception("Invalid data size, see Dynamixel SDK packetHandler definition")
        if dxl_comm_result != COMM_SUCCESS:
            raise Exception("%s" % self._packet_handler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            raise Exception("%s" % self._packet_handler.getRxException(dxl_error))

        self.packet_lock.release()

    def sync_read(self, ids, addr):
        """
            Synchronously read from given ids for the address provided.
            Args:
                ids: array of motor ids
                addr: address to read data from, see motor_constants.py and Dynamixel EManual for details
            Returns:
                array of values of size ids, in format specified by Dynamixel EManual
        """
        if not self.started:
            raise Exception("Driver not yet started, run driver.start()")

        if addr not in self._group_read.keys():
            raise Exception("addr is not in valid read addresses")

        self.packet_lock.acquire()

        groupSyncRead = self._group_read[addr]
        groupSyncRead.clearParam()
        for i in ids:
            dxl_addparam_result = groupSyncRead.addParam(i)
            if not dxl_addparam_result:
                raise Exception("[ID:%03d] groupSyncRead addparam failed" % i)

        dxl_comm_result = groupSyncRead.txRxPacket()
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self._packet_handler.getTxRxResult(dxl_comm_result))
        for id in ids:
            dxl_getdata_result = groupSyncRead.isAvailable(id, addr, motor_constants.RODATA_ADDR_LENS[addr])
            if not dxl_getdata_result:
                raise Exception("[ID:%03d] groupSyncRead getdata failed" % id)
        results = [twos_comp_filter(
            groupSyncRead.getData(id, addr, motor_constants.RODATA_ADDR_LENS[addr]), motor_constants.RODATA_ADDR_LENS[addr])
            for id in ids]

        groupSyncRead.clearParam()

        self.packet_lock.release()

        return results

    def sync_write(self, ids, addr, data):
        """
        Synchronously write data to the given motor ids, address, and data.
        For now, only supports 4 byte data transmission.

        Args:
            ids: array of motor ids
            addr: address to write data to, see motor_constants.py and Dynamixel EManual for details
            data: instruction data for motors to execute
        """
        if motor_constants.LATCH_ID in ids and len(ids) > 0:
            raise Exception("Attempting to write to latch synchronously with joint ids, use single_write"
                                   "if attempting to move latch motor")
        if not self.started:
            raise Exception("Driver not yet started, run driver.start()")
        if len(ids) != len(data):
            raise Exception("id array doesn't match data array length")
        if addr not in self._group_write.keys():
            raise Exception("invalid address, not included under writable addresses")
        if motor_constants.WRITABLE_ADDR_LENS[addr] != 4:
            raise Exception("address is not 4 bytes, only 4 bytes supported right now")

        self.packet_lock.acquire()

        groupSyncWrite = self._group_write[addr]
        # adding params for all ids and corresponding data values
        for i in range(0, len(ids)):
            if addr == motor_constants.ADDR_GOAL_POSITION and ((data[i] < motor_constants.MIN_POSITION) or (data[i] > motor_constants.MAX_POSITION)):
                raise Exception("Invalid goal position %d, min: %d, max: %d" % (data, motor_constants.MIN_POSITION, motor_constants.MAX_POSITION))
            # byte array for the input value (data[i]) -- leaving as 4 bytes for now
            # as most addresses of interest are 4 bytes.
            param_goal_position = [DXL_LOBYTE(DXL_LOWORD(data[i])),
                                   DXL_HIBYTE(DXL_LOWORD(data[i])),
                                   DXL_LOBYTE(DXL_HIWORD(data[i])),
                                   DXL_HIBYTE(DXL_HIWORD(data[i]))]
            dxl_addparam_result = groupSyncWrite.addParam(ids[i], param_goal_position)
            if dxl_addparam_result != True:
                raise Exception("[ID:%03d] groupSyncWrite addparam failed" % ids[i])
        # transmit to motors
        dxl_comm_result = groupSyncWrite.txPacket()
        if dxl_comm_result != COMM_SUCCESS:
            raise Exception("%s" % self._packet_handler.getTxRxResult(dxl_comm_result))
        # Clear sync write parameter storage
        groupSyncWrite.clearParam()

        self.packet_lock.release()

    def reboot_motor(self, id):
        """
        Try rebooting motor.
        Args:
            id: Id of motor to reboot
        """
        self.packet_lock.acquire()

        result, error = self._packet_handler.reboot(self._port_handler, id)
        if result != COMM_SUCCESS:
            raise Exception("[ID:%03d] motor reboot failed!" % id)
        if error != 0:
            raise Exception("[ID:%03d] motor reboot failed with packet error" % id)

        self.packet_lock.release()

    def get_status(self, addr):
        for value in addr.values():
            if value not in motor_constants.RODATA_ADDR_LENS.keys():
                raise ValueError("Invalid address. need to be in RODATA_ADDR_LENS. Got:", addr, "RODATA:", motor_constants.RODATA_ADDR_LENS)
        
        status = dict()
                
        try:
            dt = datetime.now(timezone.utc)
            utc_time = dt.replace(tzinfo=timezone.utc)
            utc_timestamp = utc_time.timestamp()
            status.update({'t': utc_timestamp})
            for key, a in addr.items():
                status.update({key: self.sync_read(self.ids, a)})

        except Exception as e:
            print("Status Read -- encountered exception\n", e)
            return
        
        return status
