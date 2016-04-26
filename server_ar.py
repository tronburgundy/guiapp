from socket import *
import struct
import serial
from wifi import Cell, Scheme

class AServer:

    def __init__(self, serialName):
        self.wireless = False
        try:
            self.ser = serial.Serial(serialName, timeout=1)
        except serial.serialutil.SerialException:
             raise DeviceConnectionError

    def get_delay(self):
        """Take a measurement from the device using serial unless a wireless
        scheme is set up.
        """
        self.ser.write(b'm')
        if self.wireless is False:
            bin_delay = self.ser.read(16)
            bin_delay = '\0'*(4-len(bin_delay)) + bin_delay
            delay = struct.unpack('f', bin_delay)[0]
        else:
            delay = self.get_wireless_delay()
        return delay

    def get_networks(self):
        """Form a list of available Wi-Fi cells, keeping only the best quality
        Cell out of any duplicates. Return a list of SSIDs, sorted by quality.
        """
        unfiltered = Cell.all('wlan0')
        unfiltered_sorted = sorted(unfiltered, key = attrgetter('quality'),
                                   reverse=True)
        seen = set()
        self.networks = []
        for i in unfiltered_unsorted:
            if i not in seen:
                self.networks.append(i)
                seen.add(i)
        s = attrgetter('ssid')
        ssids = []
        for i in self.networks:
            ssids.append(s(i))
        return ssids

    def go_wireless(self, serverName, serverPort, ssid, passkey):
        """Switch from a serial connection to a wireless connection and set up
        a UDP socket
        """
        # serverName is the IP address of the Raspberry Pi over the network
        self.serverName = serverName
        self.serverPort = serverPort
        self.clientSocket = socket(AF_INET, SOCK_DGRAM)

        # A scheme is needed to connect to a Wi-Fi access point.
        scheme = Scheme.for_cell('wlan0', 'ruler', ssid, passkey)
        scheme.save()
        scheme.activate()
        self.wireless = True

    def get_wireless_delay(self):
        """Cue a measurement using sockets over the wireless connection.
        Returns a floating point number as the measured delay.
        """
        self.clientSocket.settimeout(1)
        try:
            cue = 'm'
            self.clientSocket.sendto(cue,(self.serverName,
                                          self.serverPort))
            delay, serverAddress = self.clientSocket.recvfrom(2048)
            return float(delay)
        except:
            raise DeviceConnectionError

    def closeSocket(self):
        """Close the UDP socket opened to request a measurement over a wireless
        connection.
        """
        self.clientSocket.close()

    def closeSerial(self):
        """Close the serial port that was opened to request a measurement over
        a serial connection.
        """
        self.ser.close()

class DeviceConnectionError(Exception):
    pass