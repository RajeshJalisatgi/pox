import subprocess 
from six import string_types
#import matplotlib.pyplot as plt
from  pox.lib.revent import Event
from pox.lib.revent import EventMixin

#plt.ion()

class FlowEventA(Event):
        
    def __init__ (self, port):
        Event.__init__(self)
        self.port = port
        print "Flow A event created"
 
    # @property
    """def genuine (self):
        # If it's not Hormel, it's just canned spiced ham!
        return self.brand == Hormel"""

class FlowEventB(Event):
        
    def __init__ (self, port):
        Event.__init__(self)
        self.port = port
        print "Flow B event is created"
 
    # @property
    """def genuine (self):
        # If it's not Hormel, it's just canned spiced ham!
        return self.brand == Hormel"""


class DynamicUpdate(EventMixin):
    
    _eventMixin_events = set([
        FlowEventA,
        FlowEventB,
        ])
    
    def __call__(self):
        import numpy as np
        import time
#        self.on_launch()
        xdata = []
        ydata = []
        ydata2 = []
        ydata_avg = [0]
        ydata2_avg = [0]
        flag = 1
        flag2 = 1
             
        alpha = 0.08
        max_que_len = 2000
        lamda = 40
        
        #starting firtst time
        self.raiseEvent(FlowEventA, 2)
        
        
        while True:
            #return_var = os.system('sudo ifconfig c0-eth0 10.0.0.1 netmask 255.255.255.0')
            #print subprocess.Popen("ifconfig c0-eth1 10.0.0.3 netmask 255.255.255.0", shell=True, stdout=subprocess.PIPE).stdout.read()
            proc = subprocess.Popen(["curl","-s", "http://10.0.0.2:8000/qinfo/0"], stdout=subprocess.PIPE)
            (out, err) = proc.communicate()
            if ((isinstance(out.split(" ")[-1], (int, long, float, complex, string_types))==False) or not out.split(" ")[-1]):
                print "Start Netinfo_h3.py at h3"
                proc.wait()
                time.sleep(1)
                continue
            temp = (alpha*((float(out.split(" ")[-1])/max_que_len)*100))+(1-alpha)*ydata_avg[-1]
            ydata_avg.append(temp)
            if flag==1:
                print('Deleting first element of TS2 Avg') 
                del ydata_avg[-1]
                flag = 0
            
            #print temp
            #print out.split(" ")[-1]
                      
            ydata.append((float(out.split(" ")[-1])/max_que_len)*100)
            xlen = len(ydata)
            xdata = np.arange(xlen)
  # ------------------------------- Collecting from TS3          
            proc.wait()
            
            proc2 = subprocess.Popen(["curl","-s", "http://10.0.0.3:8000/qinfo/0"], stdout=subprocess.PIPE)
            (out2, err2) = proc2.communicate()
            if ((isinstance(out2.split(" ")[-1], (int, long, float, complex, string_types))==False) or not out2.split(" ")[-1]):
                print "Start Netinfo.py at h2"
                proc2.wait()
                time.sleep(1)
                continue
            
            temp2 = (alpha*((float(out2.split(" ")[-1])/max_que_len)*100))+(1-alpha)*ydata2_avg[-1]
            ydata2_avg.append(temp2)
            if flag2==1:
                print('Deleting first element of TS1 Avg') 
                del ydata2_avg[-1]
                flag2 = 0
            
            #print temp2          
            #print out2.split(" ")[-1]
                                  
            #print (float(out2.split(" ")[-1])/max_que_len)*100
            ydata2.append((float(out2.split(" ")[-1])/max_que_len)*100)
            #xlen = len(ydata)
            #xdata = np.arange(xlen)
            
            #print (len(xdata), len(ydata),len(ydata_avg), len(ydata2_avg)) 
            
            
            #self.on_running(xdata, ydata, ydata_avg, ydata2, ydata2_avg) 
            proc.wait()       
            time.sleep(1)          
            
            if temp > lamda and temp2 < lamda:
               print " Activate Flow B" 
               #print temp
               self.raiseEvent(FlowEventB, 3)
               time.sleep(30)
            print (temp, temp2)
            if temp2 > lamda and temp < lamda:
               print " Activate Flow A" 
               #print temp2
               self.raiseEvent(FlowEventA, 2)
               time.sleep(30)
            #print temp2
               
            
        return xdata, ydata, ydata_avg, ydata2_avg



