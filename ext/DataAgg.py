# !/usr/bin/python
#
# Authors : Akhilesh Thayagaturu
#           Rajesh Jalisatgi
# 
#            
# POX is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# POX is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with POX.  If not, see <ht tp://www.gnu.org/licenses/>.
 
"""
    This component is for use with the OpenFlow PoX .
    This component constantly queries buffer length from h2 and h3 HTTP servers   
    and raises event to shift flow upon exceeding threshold on backlog.
""" 

import subprocess 
from six import string_types
from pox.lib.revent import Event
from pox.lib.revent import EventMixin
from pox.core import core
from utils import *
from multiprocessing import Pool, Process

log = core.getLogger()
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))

class FlowEventA(Event):
        
    def __init__ (self, port):
        Event.__init__(self)
        self.port = port
        print "Flow A event created"  

class FlowEventB(Event):
        
    def __init__ (self, port):
        Event.__init__(self)
        self.port = port
        print("Flow B event is created")
 

# function_plot executed as a process to plot the queue lengths.
# PlotQueue.py plots after fetching the data 
def function_Plot() :
    SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
    plot_file=os.path.join(SCRIPT_PATH, "PlotQueue.py")
    proc3 = subprocess.Popen(["sudo","python", plot_file, "&"], stdout=subprocess.PIPE)
    (out3, err3) = proc3.communicate()

class DynamicUpdate(EventMixin):
    
    _eventMixin_events = set([
        FlowEventA,
        FlowEventB,
        ])
    
    def __call__(self):
        import numpy as np
        import time
        xdata = []
        ydata = []
        ydata2 = []
        ydata_avg = [0]
        ydata2_avg = [0]
        flag = 1
        flag2 = 1
        
        # Config Values
        alpha = 0.1
        # max queue length defined in Topology
        max_que_len = 4000
        # Threshold
        lamda = 40
        
        #Used in case of using .config file
        """
        config_file=os.path.join(SCRIPT_PATH, "buffer.config")     
        log.debug("Read Configuration " + config_file)
        config = readConfigFile(config_file, log)
        con = config["general"]
        print ("config=",config["general"])
        print int (con['queue_length'])
        max_que_len = int(con['queue_length'])
        alpha = float(config["general"]['alpha'])
        lamda = int (config["general"]['lambda'])
        """
        
        # flag to start subprocess for plotting
        flag_plot=0
        
        while True:
        #--------------------------------Collecting from TS2(h)------------------------    
            proc = subprocess.Popen(["curl","-s", "http://10.0.0.2:8000/qinfo/0"], stdout=subprocess.PIPE)
            (out, err) = proc.communicate()
            
            if ((isinstance(out.split(" ")[-1], (int, long, float, complex, string_types))==False) or not out.split(" ")[-1]):
                print( "Start netinfo_h3.py at h3")
                proc.wait()
                time.sleep(1)
                continue
            
            temp = (alpha*((float(out.split(" ")[-1])/max_que_len)*100))+(1-alpha)*ydata_avg[-1]
            ydata_avg.append(temp)
            
            if flag == 1:
                print('Deleting first element of TS2 Avg') 
                del ydata_avg[-1]
                flag = 0
                      
            ydata.append((float(out.split(" ")[-1])/max_que_len)*100)
            xlen = len(ydata)
            xdata = np.arange(xlen)
  # ------------------------------- Collecting from TS1(h2)-----------------------------------------------          
            proc.wait()
            
            proc2 = subprocess.Popen(["curl","-s", "http://10.0.0.3:8000/qinfo/0"], stdout=subprocess.PIPE)
            (out2, err2) = proc2.communicate()
            if ((isinstance(out2.split(" ")[-1], (int, long, float, complex, string_types))==False) or not out2.split(" ")[-1]):
                print( "Start netinfo.py at h2")
                proc2.wait()
                time.sleep(1)
                continue
            
            temp2 = (alpha*((float(out2.split(" ")[-1])/max_que_len)*100))+(1-alpha)*ydata2_avg[-1]
            ydata2_avg.append(temp2)
            if flag2==1:
                print("Deleting first element of TS1 Avg") 
                del ydata2_avg[-1]
                flag2 = 0
            
            ydata2.append((float(out2.split(" ")[-1])/max_que_len)*100)
         
            proc.wait()       
            time.sleep(1)          
            
            if flag_plot == 0 and ( temp > 0 or temp2 > 0) :
                flag_plot=1
                p = Process(target=function_Plot, args=())
                p.start()     
                    
            if temp > lamda and temp2 < lamda:
               print (" Activate Flow B") 
               #raising Event B to shift load to A
               self.raiseEvent(FlowEventB, 3)
               time.sleep(30)
               
            #print (temp, temp2)
            #log = core.getLogger()
            
            if temp2 > lamda and temp < lamda:
               print( " Activate Flow A") 
               #print temp2
               #raising Event A to shift load to B
               self.raiseEvent(FlowEventA, 2)
               time.sleep(30)
            #print temp2
               
            
        return xdata, ydata, ydata_avg, ydata2_avg



