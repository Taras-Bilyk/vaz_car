from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock
import threading
import socket
import time
import pygame

class serverApp(App):
    def build(self):
        pygame.init()
        pygame.joystick.init()
        try:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print('j connected')
        except Exception:
            print('j not connected')
        Clock.schedule_interval(self.check_j, 0.1)
        self.is_avar = 0
        self.is_blink_left = 0
        self.is_blink_right = 0
        self.left = 0
        self.right = 0
        self.streight = 0
        Window.bind(on_key_down=self.click_envent)
        Window.bind(on_key_up=self.release_event)
        #====== interface ======
        self.main_layout = FloatLayout()
        self.label_with_ip_of_connected_device = Label(text = 'server listening...',
                                                        color = (1, 1, 1, 1),
                                                        font_size=20,
                                                        size_hint=(.3, .1),
                                                        pos_hint={'x': 0, 'y': .9})
        self.main_layout.add_widget(self.label_with_ip_of_connected_device)
        #======================
        self.host = '0.0.0.0'
        self.port = 14888
        self.is_server_listening = 0
        self.listen_process = threading.Thread(target = self.listen)
        self.listen_process.daemon = True
        self.listen_process.start()
        self.get_data_from_client = threading.Thread(target = self.listen_connected_device)
        self.get_data_from_client.daemon = True
        self.get_data_from_client.start()
        return self.main_layout

    def listen(self):
        while 1:
            if self.is_server_listening == 0:
                self.label_with_ip_of_connected_device.text = 'server listening...'
                self.s = socket.socket()
                self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.s.bind((self.host, self.port))
                self.s.listen(1)
                self.conn, self.addr = self.s.accept()
                self.conn.settimeout(10)
                self.label_with_ip_of_connected_device.text = str(self.addr)
                self.is_server_listening = 1
                self.get_data_from_client = threading.Thread(target=self.listen_connected_device)
                self.get_data_from_client.daemon = True
                self.get_data_from_client.start()
            time.sleep(0.5)
    def send_message_to_connected_device(self, data):
        if self.is_server_listening == 1:
            self.conn.send((str(data)+'\n').encode())
    def listen_connected_device(self):
        while 1:
            if self.is_server_listening == 1:
                try:
                    self.data_from_client_in_bites = self.conn.recv(1024)
                    if not self.data_from_client_in_bites:
                        self.label_with_ip_of_connected_device.text = 'server listening...'
                        self.is_server_listening = 0
                        try:
                            self.conn.close()
                        except:
                            pass
                        self.conn = None
                        self.addr = None
                        continue
                    self.data_from_connected_device = self.data_from_client_in_bites.decode()
                    self.label_with_ip_of_connected_device.text = str(self.addr)
                    self.is_server_listening = 1
                except socket.timeout:
                    self.label_with_ip_of_connected_device.text = 'server listening...'
                    self.is_server_listening = 0
                    try:
                        self.conn.close()
                    except:
                        pass
                    self.conn = None
                    self.addr = None
                except:
                    pass
            time.sleep(0.5)
#=======================================


    def release_event(self, window, key, scancode):
        if key == 119 or key == 115:
            self.send_message_to_connected_device('off_m_motor')
        if key == 97 or key == 100:
            self.send_message_to_connected_device('off_t_motor')
        if key == 120:
            self.send_message_to_connected_device('stop_braking')

    def click_envent(self, window, key, scancode, codepoint, modifier):
        self.command_to_push = ''
        if codepoint == 'w':
            self.command_to_push = 'forward'
        if codepoint == 's':
            self.command_to_push = 'reverse'
        if codepoint == 'a':
            self.command_to_push = 't_left'
        if codepoint == 'd':
            self.command_to_push = 't_right'
        if codepoint == '1':
            self.command_to_push = 'off_light_f'
        if codepoint == '2':
            self.command_to_push = 'on_light_f'
        if codepoint == '3':
            self.command_to_push = 'front_far'
        if codepoint == '4':
            self.command_to_push = 'off_light_r'
        if codepoint == '5':
            self.command_to_push = 'on_light_r'
        if codepoint == 'q':
            self.command_to_push = 'off_bl'
            if self.is_blink_left == 0:
                self.command_to_push = 'on_bl_l'
                self.is_blink_left = 1
            else:
                self.command_to_push = 'off_bl'
                self.is_blink_left = 0
        if codepoint == 'e':
            self.command_to_push = 'off_bl'
            if self.is_blink_right == 0:
                self.command_to_push = 'on_bl_r'
                self.is_blink_right = 1
            else:
                self.command_to_push = 'off_bl'
                self.is_blink_right = 0
        if codepoint == 'z':
            self.command_to_push = 'off_bl'
        if codepoint == 't':
            self.command_to_push = 'off_bl'
            if self.is_avar == 0:
                self.command_to_push = 'blink_avar'
                self.is_avar = 1
            else:
                self.command_to_push = 'off_bl'
                self.is_avar = 0
        if codepoint == 'x':
            self.command_to_push = 'start_braking'
        if self.command_to_push != '':
            self.send_message_to_connected_device(self.command_to_push)

    def check_j(self, instance):
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                l = []
                for x in range(0, self.joystick.get_numaxes()):
                    l.append(self.joystick.get_axis(x))
                if float(l[2]) < 0:
                    if self.left == 0:
                        print('left')
                        self.send_message_to_connected_device('t_left')
                        self.left = 1
                        self.streight = 0
                if float(l[2]) > 0:
                    if self.right == 0:
                        print('right')
                        self.send_message_to_connected_device('t_right')
                        self.right = 1
                        self.streight = 0
                if float(l[2]) == 0:
                    self.left = 0
                    self.right = 0
                    if self.streight == 0:
                        print('streight')
                        self.send_message_to_connected_device('off_t_motor')
                        self.streight = 1
            if event.type == pygame.JOYBUTTONDOWN:
                if int(event.button) == 1:
                    print('right_blinker_on')
                    self.send_message_to_connected_device('off_bl')
                    if self.is_blink_right == 0:
                        self.send_message_to_connected_device('on_bl_r')
                        self.is_blink_right = 1
                    else:
                        self.send_message_to_connected_device('off_bl')
                        self.is_blink_right = 0
                if int(event.button) == 3:
                    print('left_blinker_on')
                    self.send_message_to_connected_device('off_bl')
                    if self.is_blink_left == 0:
                        self.send_message_to_connected_device('on_bl_l')
                        self.is_blink_left = 1
                    else:
                        self.send_message_to_connected_device('off_bl')
                        self.is_blink_left = 0
                if int(event.button) == 4:
                    print('on_light_f')
                    self.send_message_to_connected_device('on_light_f')
                if int(event.button) == 0:
                    print('on_light_r')
                    self.send_message_to_connected_device('on_light_r')
                if int(event.button) == 9:
                    print('forward')
                    self.send_message_to_connected_device('forward')
                if int(event.button) == 8:
                    print('start_braking')
                    self.send_message_to_connected_device('start_braking')
                if int(event.button) == 6 or int(event.button) == 7:
                    print('reverse')
                    self.send_message_to_connected_device('reverse')
                if int(event.button) == 10:
                    print('off_blinkers')
                    self.send_message_to_connected_device('off_bl')
                if int(event.button) == 11:
                    print('front_far')
                    self.send_message_to_connected_device('front_far')
                if int(event.button) == 12:
                    print('avar')
                    self.send_message_to_connected_device('off_bl')
                    if self.is_avar == 0:
                        self.send_message_to_connected_device('blink_avar')
                        self.is_avar = 1
                    else:
                        self.send_message_to_connected_device('off_bl')
                        self.is_avar = 0
            elif event.type == pygame.JOYBUTTONUP:
                if int(event.button) == 9:
                    print('off_m_motor')
                    self.send_message_to_connected_device('off_m_motor')
                if int(event.button) == 8:
                    print('stop_braking')
                    self.send_message_to_connected_device('stop_braking')
                if int(event.button) == 6 or int(event.button) == 7:
                    print('off_m_motor')
                    self.send_message_to_connected_device('off_m_motor')
            elif event.type == pygame.JOYHATMOTION:
                if str(event.value) == '(0, 1)':
                    print('off_light_f')
                    self.send_message_to_connected_device('off_light_f')
                if str(event.value) == '(0, -1)':
                    print('off_light_r')
                    self.send_message_to_connected_device('off_light_r')

serverApp().run()





