import serial
import serial.tools.list_ports
import time
from pycromanager import Bridge


class steper():
    def __init__(self) -> None:
        portList = list(serial.tools.list_ports.comports())
        if len(portList) < 1:
            pass
        else:
            self.name = portList[0].name
            self.bps = 19200
            self.timex = 0.01
        self.x = self.getX()
        self.y = self.getY()

    def send(self, mes):
        re = "E01"
        try:
            self.ser = serial.Serial(self.name, self.bps, timeout=self.timex)
            self.write(mes)
            re = self.read()
        except Exception as e:
            print(e)
        finally:
            try:
                self.ser.close()
            except Exception as e:
                print(e)
            return re

    def setZ(self,z):
        with Bridge() as bridge:
            core = bridge.get_core()
            core.set_position(z)
            okFlag = 0
            for i in range(200):
                if abs(core.get_position() - z) < 0.5:
                    okFlag = 1
                    break
            if not okFlag:
                return "wrong"
            else:
                return "ok"
    
    def getZ(self):
        with Bridge() as bridge:
            core = bridge.get_core()
            return core.get_position()
    
    def write(self, mes):
        pass
        # self.ser.write(str2hex(mes))
    
    def read(self):
        for i in range(10):
            count = self.ser.inWaiting()
            if count != 0:
                break
            time.sleep(0.1)
        if count != 0:
            recv = self.ser.read(count)
            self.ser.flushInput()
            return recv.decode("utf-8")
        else:
            return -1

    def initX(self):
        re = self.send("position? x")
        if re != -1 and re != "E01":
            self.x = float(re.split(",")[1])
            return float(re.split(",")[1])
        else:
            return -1

    def initY(self):
        re = self.send("position? y")
        if re != -1 and re != "E01":
            self.y = float(re.split(",")[1])
            return float(re.split(",")[1])
        else:
            return -1


    def getX(self):
        with Bridge() as bridge:
            core = bridge.get_core()
            return core.get_x_position()
        # re = self.send("position? x")
        # if re != -1 and re != "E01":
        #     before = self.x
        #     try:
        #         self.x = float(re.split(",")[1])
        #         return float(re.split(",")[1])
        #     except Exception as e:
        #         print(e)
        #         return before
        # else:
        #     return -1

    def getY(self):
        with Bridge() as bridge:
            core = bridge.get_core()
            return core.get_y_position()
        # re = self.send("position? y")
        # if re != -1 and re != "E01":
        #     before = self.y
        #     try:
        #         self.y = float(re.split(",")[1])
        #         return float(re.split(",")[1])
        #     except Exception as e:
        #         print(e)
        #         return before
        # else:
        #     return -1

    def checkPos(self, zhou, v):
        for i in range(200):
            if zhou == "x":
                if self.getX() == v:
                    break
            else:
                if self.getY() == v:
                    break
            time.sleep(0.1)
        if zhou == "x":
            if self.getX() != v:
                return "wrong"
        else:
            if self.getY() != v:
                return "wrong"
        return "ok" 
                

    def xMoveAbsolute(self, x):
        with Bridge() as bridge:
            core = bridge.get_core()
            core.set_xy_position("XYStage", x, self.getY())
            self.x = x
        # if x >= 0:
        #     dir = "p"
        # else:
        #     dir = "n"
        # if x > 10000 or x < -10000:
        #     return "wrong"
        # else:
        #     res = self.send("goposition x,o,a,%s,%f"%(dir, abs(x)))
        #     if res != -1 and res != "E01":
        #         if self.checkPos("x", x) == "ok":
        #             self.x = self.getX()
        #             return self.x
        #         else:
        #             self.x = self.getX()
        #             return "wrong"
        #     else:
        #         return "wrong"
    
    def yMoveAbsolute(self, y):
        with Bridge() as bridge:
            core = bridge.get_core()
            core.set_xy_position("XYStage", self.getX(), y)
            self.y = y
        # if y >= 0:
        #     dir = "p"
        # else:
        #     dir = "n"
        # if y > 10000 or y < -10000:
        #     return "wrong"
        # else:
        #     res = self.send("goposition y,o,a,%s,%f"%(dir, abs(y)))
        #     if res != -1 and res != "E01":
        #         if self.checkPos("y", y) == "ok":
        #             self.y = self.getY()
        #             return self.y
        #         else:
        #             self.y = self.getY()
        #             return "wrong"
        #     else:
        #         return -1
    
    def xMoveRelative(self, x):
        target = self.getX() + x
        return self.xMoveAbsolute(target)
    
    def yMoveRelative(self, y):
        target = self.getY() + y
        return self.yMoveAbsolute(target)
