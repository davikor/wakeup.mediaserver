'''
    Cache service for XBMC
    Copyright (C) 2010-2011 Tobias Ussing And Henrik Mosgaard Jensen

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    Version 0.8
'''

import struct, socket, telnetlib, time
import sys
import xbmc
import xbmcaddon

settings = xbmcaddon.Addon(id='script.wakeup.mediaserver')
language = settings.getLocalizedString

# The builtin method does not always work
# Code taken from Wake-On-Lan Script by AT (aturlov)
# see http://wiki.xbmc.org/index.php?title=Add-on:Wake_On_Lan
# and http://sourceforge.net/projects/xbmc-script-wol/
def CustomWakeOnLan(mac_address):
    addr_bytes = mac_address.split(':')
    if len(addr_bytes)==1:
        addr_bytes = mac_address.split('-')

    addr = struct.pack('BBBBBB', int(addr_bytes[0], 16),
        int(addr_bytes[1], 16),
        int(addr_bytes[2], 16),
        int(addr_bytes[3], 16),
        int(addr_bytes[4], 16),
        int(addr_bytes[5], 16))

    packet = '\xff' * 6 + addr * 16

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto(packet, ('<broadcast>', 9))
    s.close()

def wakeup():
    mac = settings.getSetting("mac")

    print "WUMS: Waking up server " + mac + "..."
    xbmc.executebuiltin('WakeOnLan(' + mac + ')')
    CustomWakeOnLan(mac)

    if settings.getSetting("showmessage") == "true":
        xbmc.executebuiltin("Notification(" + language(35000) + "," + language(35001) + " " + mac + " " + language(35002) +")")

def shutdown():
    debug = settings.getSetting("debug") == "true"
    timeout = int(settings.getSetting("timeout"))
    linebreak = settings.getSetting("linebreaks")
    host = settings.getSetting("host")
    lb='\r\n'
    if linebreak == "UNIX":
        lb='\n'

    tn = telnetlib.Telnet()
    try:
        tn.open(host, int(settings.getSetting("port")), timeout)
        result = tn.read_until(settings.getSetting("loginresponse"),timeout)
        if debug:
            print result

        tn.write(settings.getSetting("user")+lb)

        result = tn.read_until(settings.getSetting("passwordresponse"),timeout)
        if debug:
            print result

        tn.write(settings.getSetting("pass")+lb)

        result = tn.read_until(settings.getSetting("prompt"),timeout)
        if debug:
            print result

        tn.write(settings.getSetting("shutdowncmd")+lb)

        time.sleep(1)

        tn.close() 

        print 'WUMS: Shutdown of host ' + host + ' successfully initiated...'
    except:
        print 'WUMS: Connecting to ' + host + ' via telnet failed. Media server could not be shut down...'

def doNothing():
    x = 0

if __name__ == "__main__":
    # try to wake up media server
    wakeup()
    
    # do nothing while XBMC is running...
    while (not xbmc.abortRequested):
        doNothing()

    # shutdown media server when turning off XBMC...
    shutdown()
