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
# along with POX.  If not, see <http://www.gnu.org/licenses/>.
 
"""
This component is for use with the OpenFlow tutorial.

It acts as a simple hub, but can be modified to act like an L2
learning switch.

It's quite similar to the one for NOX.  Credit where credit due. :)
"""
 
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr, EthAddr
import pox.lib.packet as pkt
 
log = core.getLogger()
 
 
 
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
    Handles packet in messages from the switch.
    """
 
    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return
 
    packet_in = event.ofp # The actual ofp_packet_in message.
 
    self.forward(packet, event.dpid, packet_in)
 
def launch ():
  """append
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    
    # dpid =>switch ID 
    splitting_table = { \
        0x0000000000000007: (1,2,3), \  
        0x0000000000000008: (3,1,2) \
    }
    subnet1 = "10.0.0.0/255.255.255.128"
    subnet2 = "10.0.0.128/255.255.255.128"
    
    if event.dpid in splitting_table:
        inport, outport1, outport2 = splitting_table[event.dpid]
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
        msg_ip_subnet1_inport.match.nw_dst = subnet1
        msg_ip_subnet1_inport.match.nw_src = subnet1
        msg_ip_subnet1_inport.match.in_port = inport
        msg_ip_subnet1_inport.actions.append(of.ofp_action_output(port = outport1))
        event.connection.send (msg_ip_subnet1_inport)
        
        msg_ip_subnet1_outport = of.ofp_flow_mod()
        msg_ip_subnet1_outport.match.dl_type = pkt.ethernet.IP_TYPE
        msg_ip_subnet1_outport.match.nw_dst = subnet1
        msg_ip_subnet1_outport.match.nw_src = subnet1
        msg_ip_subnet1_outport.match.in_port = outport1
        msg_ip_subnet1_outport.actions.append(of.ofp_action_output(port = inport))
        event.connection.send(msg_ip_subnet1_outport)
        
        # pass IP on subnet 2 through the other path
        msg_ip_subnet2_inport = of.ofp_flow_mod()
        msg_ip_subnet2_inport.match.dl_type = pkt.ethernet.IP_TYPE
        msg_ip_subnet2_inport.match.nw_dst = subnet2
        msg_ip_subnet2_inport.match.nw_src = subnet2
        msg_ip_subnet2_inport.match.in_port = inport
        msg_ip_subnet2_inport.actions.append(of.ofp_action_output(port = outport2))
        event.connection.send (msg_ip_subnet2_inport)
        
        msg_ip_subnet2_outport = of.ofp_flow_mod()
        msg_ip_subnet2_outport.match.dl_type = pkt.ethernet.IP_TYPE
        msg_ip_subnet2_outport.match.nw_dst = subnet2
        msg_ip_subnet2_outport.match.nw_src = subnet2
        msg_ip_subnet2_outport.match.in_port = outport2
        msg_ip_subnet2_outport.actions.append(of.ofp_action_output(port = inport))
        event.connection.send(msg_ip_subnet2_outport)
    else:
        MyController(event.connection)
    
    
  core.openflow.addListenerByName("ConnectionUp", start_switch)