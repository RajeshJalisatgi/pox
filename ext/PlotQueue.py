# !/usr/bin/python
#
# Authors : Akhilesh Thayagaturu
#           Rajesh Jalisatgi
# Comments: 
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
    This component handles plotting backlog data from Ts1 and Ts2
""" 
import subprocess 
from six import string_types
import matplotlib.pyplot as plt

plt.ion()


class DynamicUpdate():
    #Suppose we know the x range
    min_y = 0
    max_y = 140

    def on_launch(self):
        #Set up plot
        self.figure, self.ax = plt.subplots()
        self.lines,  = self.ax.plot([],[],'-r',label="#Instantaneous usage at TS2")
        self.lines2, = self.ax.plot([],[],'--r',label="#Average usage at TS2")
        self.lines3, = self.ax.plot([],[],'-b',label="#Instantaneous usage at TS1")
        self.lines4, = self.ax.plot([],[],'--b',label="#Average usage at TS1")
        
        
        #Autoscale on unknown axis and known lims on the other
        self.ax.set_autoscaley_on(True)
        self.ax.set_ylim(self.min_y, self.max_y)
        #Other stuff
        self.ax.set_ylabel(' % Use of Que ')
        self.ax.set_xlabel('Time in seconds interval')
        self.ax.grid()
        self.handles, self.labels = self.ax.get_legend_handles_labels() 
        self.ax.legend(self.handles,self.labels)
        
        self.figure.suptitle('Plot of Queue Status at TS2')
        

    def on_running(self, xdata, ydata, ydata_avg, ydata2, ydata2_avg):
        #Update data (with the new _and_ the old points)
        self.lines.set_xdata(xdata)
        self.lines.set_ydata(ydata)
        #Need both of these in order to rescale
        
        self.lines2.set_xdata(xdata)
        self.lines2.set_ydata(ydata_avg)
        
        self.lines3.set_xdata(xdata)
        self.lines3.set_ydata(ydata2)
        
        self.lines4.set_xdata(xdata)
        self.lines4.set_ydata(ydata2_avg)
        
        self.ax.relim()
        self.ax.autoscale_view()
        #We need to draw *and* flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    #Example
    def __call__(self):
        import numpy as np
        import time
        self.on_launch()
        xdata = []
        ydata = []
        ydata2 = []
        ydata_avg = [0]
        ydata2_avg = [0]
        flag = 1
        flag2 = 1
        
        alpha = .1
        max_que_len = 2000
        """  
        config_file=os.path.join(SCRIPT_PATH, "buffer.config")     
        log.debug("Read Configuration " + config_file)
        config = readConfigFile(config_file, log)
        con = config["general"]
        #print ("config=",config["general"])
        print int (con['queue_length'])
        max_que_len = int(con['queue_length'])
        alpha = float(config["general"]['alpha'])
        #lamda = int (config["general"]['lambda'])
        """ 
        while True:
            #return_var = os.system('sudo ifconfig c0-eth0 10.0.0.1 netmask 255.255.255.0')
            #print subprocess.Popen("ifconfig c0-eth1 10.0.0.3 netmask 255.255.255.0", shell=True, stdout=subprocess.PIPE).stdout.read()
            #--------------------------- For plot od TS2
            proc = subprocess.Popen(["curl","-s", "http://10.0.0.3:8000/qinfo/0"], stdout=subprocess.PIPE)
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
            
            proc.wait()
            
            proc2 = subprocess.Popen(["curl","-s", "http://10.0.0.2:8000/qinfo/0"], stdout=subprocess.PIPE)
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
            
            print temp2
            
            
            #print out2.split(" ")[-1]
            #print (float(out2.split(" ")[-1])/max_que_len)*100
            ydata2.append((float(out2.split(" ")[-1])/max_que_len)*100)
            #xlen = len(ydata)
            #xdata = np.arange(xlen)
            
            #print (len(xdata), len(ydata),len(ydata_avg), len(ydata2_avg)) 
           
            self.on_running(xdata, ydata, ydata_avg, ydata2, ydata2_avg) 
            proc.wait()       
            time.sleep(1)
            
                      
        return xdata, ydata, ydata_avg, ydata2_avg

d = DynamicUpdate()
d()


