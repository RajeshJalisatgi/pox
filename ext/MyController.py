#!/usr/bin/python
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
This component is for use with the OpenFlow tutorial.

It acts as a simple hub, but can be modified to act like an L2
learning switch.

It's quite similar to the one for NOX.  Credit where credit due. :)
""" 


from pox.core import core
from CollectData import DynamicUpdate, FlowEventA, FlowEventB
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

from  pox.lib.revent import Event

log = core.getLogger()
 
port = 2
dest_subnet = "192.168.1.6"
source_subnet = "192.168.1.1"
myevent=0
d = 0

def parallel_function():
    global d
    d()

          
def flowA(event):
    
    global dest_subnet
    global source_subnet
    
    inport = 1
    outport = 2
    
    print "Installing Flow A"
    # pass ARP both ways
    msg_arp_inport = of.ofp_flow_mod()
    msg_arp_inport.match.dl_type = pkt.ethernet.ARP_TYPE
    msg_arp_inport.match.in_port = inport
    msg_arp_inport.actions.append(of.ofp_action_output(port = outport))
    myevent.connection.send (msg_arp_inport)
    
    msg_arp_outport = of.ofp_flow_mod()
    msg_arp_outport.match.dl_type = pkt.ethernet.ARP_TYPE
    msg_arp_outport.match.in_port = outport
    msg_arp_outport.actions.append(of.ofp_action_output(port = inport))
    myevent.connection.send(msg_arp_outport)
    
    #pass IP on subnet 1 through one path
    msg_ip_subnet1_inport = of.ofp_flow_mod()
    msg_ip_subnet1_inport.match.dl_type = pkt.ethernet.IP_TYPE
    msg_ip_subnet1_inport.match.nw_dst = dest_subnet
    msg_ip_subnet1_inport.match.nw_src = source_subnet 
    msg_ip_subnet1_inport.match.in_port = inport
    msg_ip_subnet1_inport.actions.append(of.ofp_action_output(port = outport))
    myevent.connection.send (msg_ip_subnet1_inport)
    
    msg_ip_subnet1_outport = of.ofp_flow_mod()
    msg_ip_subnet1_outport.match.dl_type = pkt.ethernet.IP_TYPE
    msg_ip_subnet1_outport.match.nw_dst = source_subnet
    msg_ip_subnet1_outport.match.nw_src = dest_subnet
    msg_ip_subnet1_outport.match.in_port = outport
    msg_ip_subnet1_outport.actions.append(of.ofp_action_output(port = inport))
    myevent.connection.send(msg_ip_subnet1_outport)
        
        
def flowB(event):
    inport = 1
    outport = 3
    
    global dest_subnet
    global source_subnet
    global myevent
    
    print "Installing Flow B"
     # pass ARP both ways
    msg_arp_inport = of.ofp_flow_mod()
    msg_arp_inport.match.dl_type = pkt.ethernet.ARP_TYPE
    msg_arp_inport.match.in_port = inport
    msg_arp_inport.actions.append(of.ofp_action_output(port = outport))
    myevent.connection.send (msg_arp_inport)
    
    msg_arp_outport = of.ofp_flow_mod()
    msg_arp_outport.match.dl_type = pkt.ethernet.ARP_TYPE
    msg_arp_outport.match.in_port = outport
    msg_arp_outport.actions.append(of.ofp_action_output(port = inport))
    myevent.connection.send(msg_arp_outport)
    
    #pass IP on subnet 1 through one path
    msg_ip_subnet1_inport = of.ofp_flow_mod()
    msg_ip_subnet1_inport.match.dl_type = pkt.ethernet.IP_TYPE
    msg_ip_subnet1_inport.match.nw_dst = dest_subnet
    msg_ip_subnet1_inport.match.nw_src = source_subnet 
    msg_ip_subnet1_inport.match.in_port = inport
    msg_ip_subnet1_inport.actions.append(of.ofp_action_output(port = outport))
    myevent.connection.send (msg_ip_subnet1_inport)
    
    msg_ip_subnet1_outport = of.ofp_flow_mod()
    msg_ip_subnet1_outport.match.dl_type = pkt.ethernet.IP_TYPE
    msg_ip_subnet1_outport.match.nw_dst = source_subnet
    msg_ip_subnet1_outport.match.nw_src = dest_subnet
    msg_ip_subnet1_outport.match.in_port = outport
    msg_ip_subnet1_outport.actions.append(of.ofp_action_output(port = inport))
    myevent.connection.send(msg_ip_subnet1_outport)
        
"""def update_stats(event):
    print "Executing update_stats"
    t = int(time())
    lam1 = 200 
    global port
    if port == 2
        print subprocess.Popen("ifconfig c0-eth0 10.0.0.1 netmask 255.255.255.0", shell=True, stdout=subprocess.PIPE).stdout.read()
        proc = subprocess.Popen(["curl","-s", "http://10.0.0.2:8000/qinfo/0"], stdout=subprocess.PIPE)
        (out, err) = proc.communicate()
        print dir(event)
        print x =out.split(" ")[-1]
        if x > lam1
            port = 3
            print "Switching flow through h3"
            flowB(event)
    elif port == 3
        print subprocess.Popen("ifconfig c0-eth0 10.0.0.1 netmask 255.255.255.0", shell=True, stdout=subprocess.PIPE).stdout.read()
        proc = subprocess.Popen(["curl","-s", "http://10.0.0.2:8000/qinfo/0"], stdout=subprocess.PIPE)
        (out, err) = proc.communicate()
        print x =out.split(" ")[-1]
        if x > lam1
            log.debug("Switching flow through h2") 
            port = 2
            flowA(event) """
 
class MyController (object):
  def __init__ (self, connection):
    # Keep tsplittthreadinging_tablerack of the connection to the switch so that we can
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
 
      log.debug("Installing flow...")
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
    """
    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return
 
    packet_in = event.ofp # The actual ofp_packet_in message.
    print "Packet arrived for testing" 
    self.forward(packet, event.dpid, packet_in)
 
def launch ():
  """core.openflow.
  Starts the component
  """
  def start_switch (event):
    
    global myevent
    myevent = event
    global d
    d = DynamicUpdate()
    d.addListenerByName("FlowEventB", flowB) 
    d.addListenerByName("FlowEventA", flowA)
    #d.add(FlowEventB, flowB, True)
    #d.add(FlowEventA, flowA, True)
    print "D has been updated"
    #log.debug("Controlling %s" % (event.connection,))
    flowA(event)
    b = threading.Thread(target=parallel_function,args=[])
    b.daemon = True
    b.start() 
  
    
    """splitting_table = { 
        # 0x0000000000000007: (1,2,3) \
     }"""
    
    # port_to_name = { 1: } 
    # dest_subnet = "192.168.1.6"
    # source_subnet = "192.168.1.1"start_switch
    
    """splitting_table[event.dpid] = (1,2,3)
    if event.dpid in splitting_table:
        inport, outport1, outport2 = splitting_table[event.dpid]
        print splitting_table[event.dpid]
        
        # pass ARP both ways
        msg_arp_inport = of.ofp_flow_mod()
        msg_arp_inport.match.dl_type = pkt.ethernet.ARP_TYPE
        msg_arp_inport.match.in_port = inport
        msg_arp_inport.actions.append(of.ofp_action_output(port = outport1))
        event.connection.send (msg_arp_inport)
        
        msg_arp_outport = of.ofp_flow_mod()
        msg_arp_outport.match.dl_type = pkt.ethernet.ARP_TYPE
        msg_arp_outport.match.in_port = outport1
        msg_arp_outport.actions.append(of.ofp_action_output(port = inport))
        event.connection.send(msg_arp_outport)
        
        #pass IP on subnet 1 through one path
        msg_ip_subnet1_inport = of.ofp_flow_mod()
        msg_ip_subnet1_inport.match.dl_type = pkt.ethernet.IP_TYPE
        msg_ip_subnet1_inport.match.nw_dst = dest_subnet
        msg_ip_subnet1_inport.match.nw_src = source_subnet 
        msg_ip_subnet1_inport.match.in_port = inport
        msg_ip_subnet1_inport.actions.append(of.ofp_action_output(port = outport1))
        event.connection.send (msg_ip_subnet1_inport)
        
        msg_ip_subnet1_outport = of.ofp_flow_mod()
        msg_ip_subnet1_outport.match.dl_type = pkt.ethernet.IP_TYPE
        msg_ip_subnet1_outport.match.nw_dst = source_subnet
        msg_ip_subnet1_outport.match.nw_src = dest_subnet
        msg_ip_subnet1_outport.match.in_port = outport1
        msg_ip_subnetflowA1_outport.actions.append(of.ofp_action_output(port = inport))
        event.connection.send(msg_ip_subnet1_outport)"""   
        
        
    """ else:
        MyController(event.connection)"""
    
    
  core.openflow.addListenerByName("ConnectionUp", start_switch)
  
