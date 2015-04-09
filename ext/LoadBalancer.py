# !/usr/bin/python
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
     Authors : Akhilesh Thayagaturu
               Rajesh Jalisatgi
    This component is for use with the OpenFlow PoX .
    This POX controller handles PacketIn by installing TCP flows 
    and allocate a thread to collect data from HTTP server of h2 and h3 and 
    shift load to alternate paths when the packets in queue is more than 
    threshold 
""" 

from pox.core import core
from DataAgg import DynamicUpdate, FlowEventA, FlowEventB
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr, EthAddr
import pox.lib.packet as pkt
from twisted.internet import task, reactor
from time import time
import pox.lib.revent
import subprocess 
import os
import threading
from pox.lib.revent import EventMixin
from sets import Set
from pox.lib.revent import Event

log = core.getLogger()
 
port = 2

#IP address of dest h4
dest_subnet = "192.168.1.6"

#IP address of source h1
source_subnet = "192.168.1.1"
myevent=0
d = 0
# stores the tcp src and dst port entries of path 1(h1 ---> h2 ---> Aggregator)
pathA = [[0, 0]]

# stores the tcp src and dst port entries of path B(h1 ---> h3 --> Aggregator)
pathB = [[0, 0]]

#Data Collection Thread Executing 
def DataCollection_function():
    global d
    d()
          
def flowA(event):
    
    global dest_subnet
    global source_subnet
    
    inport = 1
    outport = 2
    global pathA
    global pathB
    global myevent
    
    print " Flow A Event execution"
    
    #pass IP on subnet 1 through one path
    if len(pathB) > 1 :
        tcp_src_port,tcp_dst_port =  pathB.pop()
        pathA.append([tcp_src_port, tcp_dst_port])
        print("Shifting TCP load from path A ",[tcp_src_port, tcp_dst_port])  
        msg_ip_subnet1_inport = of.ofp_flow_mod()
        msg_ip_subnet1_inport.match.dl_type = pkt.ethernet.IP_TYPE
        msg_ip_subnet1_inport.match.nw_proto = 0x06
        msg_ip_subnet1_inport.match.nw_dst = dest_subnet
        msg_ip_subnet1_inport.match.nw_src = source_subnet 
        msg_ip_subnet1_inport.match.in_port = inport
        msg_ip_subnet1_inport.match.tp_dst =  tcp_dst_port
        msg_ip_subnet1_inport.match.tp_src =  tcp_src_port
        msg_ip_subnet1_inport.idle_timeout = 6000
        msg_ip_subnet1_inport.hard_timeout = 6000
        msg_ip_subnet1_inport.actions.append(of.ofp_action_output(port = outport))
        myevent.connection.send (msg_ip_subnet1_inport)
             
        msg_ip_subnet1_outport = of.ofp_flow_mod()
        msg_ip_subnet1_outport.match.dl_type = pkt.ethernet.IP_TYPE
        msg_ip_subnet1_outport.match.nw_proto = 0x06
        msg_ip_subnet1_outport.match.nw_dst = source_subnet
        msg_ip_subnet1_outport.match.nw_src = dest_subnet
        msg_ip_subnet1_outport.match.tp_dst =  tcp_src_port
        msg_ip_subnet1_outport.match.tp_src =  tcp_dst_port
        msg_ip_subnet1_outport.idle_timeout = 6000
        msg_ip_subnet1_outport.hard_timeout = 6000
        msg_ip_subnet1_outport.actions.append(of.ofp_action_output(port = inport))
        myevent.connection.send(msg_ip_subnet1_outport)
        
        
def flowB(event):
    inport = 1
    outport = 3
    
    global dest_subnet
    global source_subnet
    global myevent
    global pathA
    global pathB
    print( "Flow B Event execution")

    if len(pathA) > 1 :
        
        tcp_src_port,tcp_dst_port =  pathA.pop()
        pathB.append([tcp_src_port, tcp_dst_port])
        print ("Shifting load from path B ",[tcp_src_port, tcp_dst_port])  
        #pass IP on subnet 1 through one path
        msg_ip_subnet1_inport = of.ofp_flow_mod()
        msg_ip_subnet1_inport.match.dl_type = pkt.ethernet.IP_TYPE
        msg_ip_subnet1_inport.match.nw_proto = 0x06
        msg_ip_subnet1_inport.match.nw_dst = dest_subnet
        msg_ip_subnet1_inport.match.nw_src = source_subnet 
        msg_ip_subnet1_inport.match.in_port = inport
        msg_ip_subnet1_inport.match.tp_dst =  tcp_dst_port
        msg_ip_subnet1_inport.match.tp_src =  tcp_src_port
        msg_ip_subnet1_inport.idle_timeout = 6000
        msg_ip_subnet1_inport.hard_timeout = 6000
        msg_ip_subnet1_inport.actions.append(of.ofp_action_output(port = outport))
        myevent.connection.send (msg_ip_subnet1_inport)
        
        msg_ip_subnet1_outport = of.ofp_flow_mod()
        msg_ip_subnet1_outport.match.dl_type = pkt.ethernet.IP_TYPE
        msg_ip_subnet1_outport.match.nw_proto = 0x06
        msg_ip_subnet1_outport.match.nw_dst = source_subnet
        msg_ip_subnet1_outport.match.nw_src = dest_subnet
        #msg_ip_subnet1_outport.match.in_port = outport
        msg_ip_subnet1_outport.match.tp_dst = tcp_src_port
        msg_ip_subnet1_outport.match.tp_src =  tcp_dst_port
        msg_ip_subnet1_outport.idle_timeout = 6000
        msg_ip_subnet1_outport.hard_timeout = 6000
        msg_ip_subnet1_outport.actions.append(of.ofp_action_output(port = inport))
        myevent.connection.send(msg_ip_subnet1_outport)
        
class MyController (object):
  def __init__ (self, connection):
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection
 
    # This binds our PacketIn event listener
    connection.addListeners(self)
 
    # Use this table to keep track of which ethernet address is on
    # which switch port (keys are MACs, values are ports).
    self.mac_to_port = {}
 
  def resend_packet (self, packet_in, out_port):
    """
    Instructs the switch to resend a packet that it had sent to us.
    "packet_in" is the ofp_packet_in object the switch had sent to the
    controller due to a table-miss.
    """
    msg = of.ofp_packet_out()
    msg.data = packet_in
 
    # Add an action to send to the specified port
    action = of.ofp_action_output(port = out_port)
    msg.actions.append(action)
 
    # Send message to switch
    self.connection.send(msg)
 
  def forward (self, packet, dpid, packet_in):
    """
    Forward on to a different port.
    """
 
    # Learn the port for the source MAC
    self.mac_to_port[packet.src] = packet_in.in_port
    
 
    if packet.dst in self.mac_to_port:
      # Send packet out the associated port
      #self.resend_packet(packet_in, self.mac_to_port[packet.dst])
 
      # Once you have the above working, try pushing a flow entry
      # instead of resending the packet (comment out the above and
      # uncomment and complete the below.)
 
      print("Installing flow...")
      # Maybe the log statement should have source/destination/port?
 
      msg = of.ofp_flow_mod()
      #
      ## Set fields to match received packet
      msg.match = of.ofp_match.from_packet(packet)
      
      #< Set other fields of flow_mod (timeouts? buffer_id?) >
      msg.idle_timeout = 60
      msg.hard_timeout = 60
      msg.buffer_id = packet_in.buffer_id
      
      #< Add an output action, and send -- similar to resend_packet() >
      msg.actions.append(of.ofp_action_output(port = self.mac_to_port[packet.dst]))
      
      self.connection.send(msg)
 
    else:
      # Flood the packet out everything but the input port
      # This part looks familiar, right?
      self.resend_packet(packet_in, of.OFPP_FLOOD)
 
 
      
  def _handle_PacketIn (self, event):
    """
    Handles packet in messages from the switch.inport
    Initailly flow will be added to path A(h1->h2>h4)
    upon high backlog on pathA flow shifted to PathB 
    """
    inport = 1
    outport = 2

    global dest_subnet
    global source_subnet
    global myevent
    
    print "PacketIn Handling"
    packet = event.parsed # This is the parsed packet data.
    myevent = event
    inport_test = event.port
    
    
    if packet.find("tcp"):
        tcp_src_port=packet.find("tcp").srcport
        tcp_dst_port=packet.find("tcp").dstport
        
        # debug if any tcp packet not configured
        if inport != inport_test :
            print ("inport=",inport,"in_test=",inport_test)
            print "Error_inport_mismatch"
            print dir(packet)
            
        test=[tcp_src_port, tcp_dst_port]    
        if pathB.count(test) != 0 :
            pathB.remove(test)
            print "Handling Timeout"
        if pathA.count(test) != 0 :
            pathA.remove(test)
            print "Handling Timeout"    
                    
        pathA.append([tcp_src_port,tcp_dst_port])
        print "Handling TCP_PacketIn_Event"
        """
        TCP_PROTO=0x06
        ICMP_PROTO = 0x01
        """
        #pass IP on subnet 1 through one path
        msg_ip_subnet1_inport = of.ofp_flow_mod()
        msg_ip_subnet1_inport.match.dl_type = pkt.ethernet.IP_TYPE
        msg_ip_subnet1_inport.match.nw_proto = 0x06
        msg_ip_subnet1_inport.match.nw_dst = dest_subnet
        msg_ip_subnet1_inport.match.nw_src = source_subnet
        msg_ip_subnet1_inport.match.in_port = inport
        msg_ip_subnet1_inport.match.tp_dst = tcp_dst_port
        msg_ip_subnet1_inport.match.tp_src = tcp_src_port
        msg_ip_subnet1_inport.actions.append(of.ofp_action_output(port = outport))
        msg_ip_subnet1_inport.idle_timeout = 6000
        msg_ip_subnet1_inport.hard_timeout = 6000
        event.connection.send (msg_ip_subnet1_inport)
        
        msg_ip_subnet1_outport = of.ofp_flow_mod()
        msg_ip_subnet1_outport.match.dl_type = pkt.ethernet.IP_TYPE
        msg_ip_subnet1_outport.match.nw_proto = 0x06
        msg_ip_subnet1_outport.match.nw_dst = source_subnet
        msg_ip_subnet1_outport.match.nw_src = dest_subnet
        #msg_ip_subnet1_outport.match.in_port = outport
        msg_ip_subnet1_outport.match.tp_dst = tcp_src_port
        msg_ip_subnet1_outport.match.tp_src = tcp_dst_port
        msg_ip_subnet1_outport.idle_timeout = 6000
        msg_ip_subnet1_outport.hard_timeout = 6000
        msg_ip_subnet1_outport.actions.append(of.ofp_action_output(port = inport))
        event.connection.send(msg_ip_subnet1_outport)
        
        
    elif packet.find("icmp"):
        print "ICMP packet handling"
        msg_ip_icmp_inport = of.ofp_flow_mod()
        msg_ip_icmp_inport.match.nw_proto = 1
        msg_ip_icmp_inport.match.dl_type = pkt.ethernet.IP_TYPE
        msg_ip_icmp_inport.match.nw_dst = source_subnet
        msg_ip_icmp_inport.match.nw_src = dest_subnet
        msg_ip_icmp_inport.match.in_port = outport
        msg_ip_icmp_inport.idle_timeout = 6000
        msg_ip_icmp_inport.hard_timeout = 6000
        msg_ip_icmp_inport.actions.append(of.ofp_action_output(port = inport))
        event.connection.send (msg_ip_icmp_inport)
        
        msg_ip_icmp_outport = of.ofp_flow_mod()
        msg_ip_icmp_outport.match.nw_proto = 1
        msg_ip_icmp_outport.match.dl_type = pkt.ethernet.IP_TYPE
        msg_ip_icmp_outport.match.in_port = inport
        msg_ip_icmp_outport.match.nw_src = source_subnet
        msg_ip_icmp_outport.match.nw_dst = dest_subnet
        msg_ip_icmp_outport.idle_timeout = 6000
        msg_ip_icmp_outport.hard_timeout = 6000
        msg_ip_icmp_outport.actions.append(of.ofp_action_output(port = outport))
        event.connection.send (msg_ip_icmp_outport)
    else :
         print "Ignoring Packet"    
        

def launch ():
  """core.openflow.
  Starts the component
  """
  def start_switch (event):
    
    global myevent
    global d
    inport = 1
    outport1 = 2
    print ("Installing ARP Paths")
    # Installing ARP both ways
    msg_arp_inport = of.ofp_flow_mod()
    msg_arp_inport.match.dl_type = pkt.ethernet.ARP_TYPE
    msg_arp_inport.match.in_port = inport
    msg_arp_inport.idle_timeout = 6000
    msg_arp_inport.hard_timeout = 6000
    msg_arp_inport.actions.append(of.ofp_action_output(port = outport1))
    event.connection.send (msg_arp_inport)
    
    msg_arp_outport = of.ofp_flow_mod()
    msg_arp_outport.match.dl_type = pkt.ethernet.ARP_TYPE
    msg_arp_outport.match.in_port = outport1
    msg_arp_outport.idle_timeout = 6000
    msg_arp_outport.hard_timeout = 6000
    msg_arp_outport.actions.append(of.ofp_action_output(port = inport))
    event.connection.send(msg_arp_outport)
    
    #storing the event for future handling
    myevent = event
    MyController(event.connection)
        
    # Add event handlers
    d = DynamicUpdate()
    d.addListenerByName("FlowEventB", flowB) 
    d.addListenerByName("FlowEventA", flowA)
    
    # Starting data collector thread b
    b = threading.Thread(target=DataCollection_function,args=[])
    b.daemon = True
    b.start() 

        
  #Registering ConnectionUp event   
  core.openflow.addListenerByName("ConnectionUp", start_switch)
  
