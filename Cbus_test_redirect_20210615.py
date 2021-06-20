import can
import operator
import time
import os

class LOG():
    def __init__(self):
        if not os.path.exists('log'):
            os.mkdir('log')
        self.log = open('log/%s.txt' % time.strftime("%Y_%m_%d_%I_%M_%S"), 'w+')
        log_fils = os.listdir('log/')
        log_fils.sort()
        if len(log_fils) > 200:
            print('log file >200,delere old file', log_fils.pop(0), file=self.log)

    def Info(self, *data):
        msg = time.strftime("%Y-%m-%d_%I:%M:%S") + "  INFO:    "
        for info in data:
            if type(info) == int:
                msg = msg + str(info)
            else:
                msg = msg + str(info)
        print(msg)
        print(msg, file=self.log)
        self.log.flush()

    def Warn(self, *data):
        msg = time.strftime("%Y-%M-%d_%I:%M:%S") + "  WARN:    "
        for info in data:
            if type(info) == int:
                msg = msg + str(info)
            else:
                msg = msg + info
        print(msg, file=self.log)
        print(msg)

    def Error(self, *data):
        msg = time.strftime("%Y-%M-%d_%I:%M:%S") + " ERROR:    "
        for info in data:
            if type(info) == int:
                msg = msg + str(info)
            else:
                msg = msg + info
        print(msg, file=self.log)
        print(msg)

# PM_can_id = 0x130904FF
# IM_can_id = 0x120984FF
# data = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]  #IM test

TESTBITRATE = 500000 # the bitrate of can speed

data = [0x01]  #PM test 20210615
PM_can_id = 0x130100DF
IM_can_id = 0x120980DE

class CanListener(can.listener.Listener):
    def __init__(self,bus):
        self._framecount = 0
        self._errorcount = 0
        self._recivecount = 0
        self.bus = bus
        self.data = data
        self.can_id = IM_can_id

    def on_message_received(self, msg):
        # print(msg.arbitration_id)
        # print(msg)
        self._recivecount += 1
        if msg.arbitration_id == IM_can_id:
            print(msg.data[0],'I am here.')
        if msg.arbitration_id == PM_can_id:
            # print('data',data[0],'msg',msg.data[0])
            self._framecount = self._framecount + 1
            if not operator.eq(data[0], msg.data[0]-1):
                self._errorcount = self._errorcount + 1
            data[0] = data[0]+1
            if data[0] == 0xff:
                data[0] = 0
            msg = can.message.Message(extended_id=True, arbitration_id=self.can_id, data=data)
            self.bus.send(msg)

    def clear(self):
        self._framecount = 0
        self._errorcount = 0

    @property
    def framecount(self):
        return self._framecount

    @property
    def errorcount(self):
        return self._errorcount

    @property
    def recivecount(self):
        return self._recivecount

def main():
    #创建需要监听的总线
    can_bus = can.interface.Bus(channel='PCAN_USBBUS1', bustype='pcan', bitrate=TESTBITRATE)
    #创建一个listener 实例
    listener = CanListener(can_bus)
    #监听消息，乒乓无线循环（自动调用listener 方法）
    can.Notifier(bus=can_bus, listeners=[listener])
    # 消息以arbitration_id 发出
    msg = can.message.Message(extended_id=True, arbitration_id=IM_can_id, data=data)
    can_bus.send(msg)
    log = LOG()

    #每10秒，打印统计结果，并清零
    while(1):
        time.sleep(10)
        log.Info("total frame= ",listener.recivecount," pingpang frame= ", listener.framecount, " error frame= ", listener.errorcount)
        listener.clear()

if __name__ == "__main__":
    main()

