from machine import Pin, PWM # type: ignore
import network # type: ignore
import _thread
import socket
import time

# motor speed ( max duty 1023 )
steering_motor_1 = PWM(Pin(15), freq = 50)
steering_motor_2 = PWM(Pin(13), freq = 50)
pwm_move_motor_1_speed = PWM(Pin(4), freq = 1000)
pwm_move_motor_2_speed = PWM(Pin(27), freq = 1000)
pwm_move_motor_1_speed.duty(1023)
pwm_move_motor_2_speed.duty(1023)

# motor direction pins
motor_1_dir_pin_0 = Pin(16, Pin.OUT)
motor_1_dir_pin_1 = Pin(17, Pin.OUT)
motor_2_dir_pin_0 = Pin(14, Pin.OUT)
motor_2_dir_pin_1 = Pin(12, Pin.OUT)

# set start main motors direction
motor_1_dir_pin_0.value(0)
motor_1_dir_pin_1.value(0)
motor_2_dir_pin_0.value(0)
motor_2_dir_pin_1.value(0)

# lights turns
light_front_left_yellow = PWM(Pin(0), freq = 1000)
light_front_right_yellow = PWM(Pin(2), freq = 1000)
light_back_left_yellow = PWM(Pin(5), freq = 1000)
light_back_right_yellow = PWM(Pin(18), freq = 1000)
light_front_left_yellow.duty(0)
light_front_right_yellow.duty(0)
light_back_left_yellow.duty(0)
light_back_right_yellow.duty(0)

# back white
light_back_left_white = PWM(Pin(22), freq = 1000)
light_back_right_white = PWM(Pin(23), freq = 1000)
light_back_left_white.duty(0)
light_back_right_white.duty(0)

# for main lights
light_front_pin_0 = Pin(19, Pin.OUT)
light_front_pin_1 = Pin(21, Pin.OUT)
light_back_pin_0= Pin(32, Pin.OUT)
light_back_pin_1 = Pin(33, Pin.OUT)
light_front_pin_0.value(0)
light_front_pin_1.value(0)
light_back_pin_0.value(0)
light_back_pin_1.value(0)

# main lights
light_front_white_main = PWM(Pin(26), freq = 1000)
light_back_red_main = PWM(Pin(25), freq = 1000)
light_front_white_main.duty(50)
light_back_red_main.duty(50)

# connect to server
wifi_module = network.WLAN(network.STA_IF)
wifi_module.active(True)
wifi_module.connect('YOUR_WIFI_SSID', 'YOUR_WIFI_PWD')
ip_of_computer = 'YOUR_IP_OF_PC_WHERE_SERVER_IS_RUNNING'
port = 14888
connected_to_server = 0
s = None

def connection_to_server():
    global connected_to_server, s
    if connected_to_server == 0:
        try:
            if s:
                s.close()
            s = socket.socket()
            s.connect((ip_of_computer, port))
            connected_to_server = 1
        except:
            connected_to_server = 0
            if s:
                s.close()
            s = None
def ping_sending():
    global s
    global connected_to_server
    try:
        s.send(b'ping')
    except:
        connected_to_server = 0
        if s != None:
            s.close()
        s = None
#================================================================

def set_angle(angle):
    min_pulse = 0.5
    max_pulse = 2.5
    period = 20
    pulse_width = min_pulse + (max_pulse - min_pulse) * (angle / 180)
    duty = int((pulse_width / period) * 1023)
    steering_motor_1.duty(duty)
    steering_motor_2.duty(duty)

blinking_avar = 0
time_counter = 0
blink_left = 0
blink_right = 0
light_r_now = 0

def start_avar():
    global blinking_avar
    if blinking_avar == 1:
        if time_counter % 2 == 0:
            light_front_left_yellow.duty(1023)
            light_front_right_yellow.duty(1023)
            light_back_left_yellow.duty(1023)
            light_back_right_yellow.duty(1023)
        else:
            light_front_left_yellow.duty(0)
            light_front_right_yellow.duty(0)
            light_back_left_yellow.duty(0)
            light_back_right_yellow.duty(0)
def stop_blink():
    global blinking_avar, blink_left, blink_right
    blinking_avar = 0
    blink_left = 0
    blink_right = 0
    light_front_left_yellow.duty(0)
    light_front_right_yellow.duty(0)
    light_back_left_yellow.duty(0)
    light_back_right_yellow.duty(0)
def is_blink_left():
    global blink_left
    if blink_left == 1:
        if time_counter % 2 == 0:
            light_front_left_yellow.duty(1023)
            light_front_right_yellow.duty(0)
            light_back_left_yellow.duty(1023)
            light_back_right_yellow.duty(0)
        else:
            light_front_left_yellow.duty(0)
            light_front_right_yellow.duty(0)
            light_back_left_yellow.duty(0)
            light_back_right_yellow.duty(0)
def is_blink_right():
    global blink_right
    if blink_right == 1:
        if time_counter % 2 == 0:
            light_front_left_yellow.duty(0)
            light_front_right_yellow.duty(1023)
            light_back_left_yellow.duty(0)
            light_back_right_yellow.duty(1023)
        else:
            light_front_left_yellow.duty(0)
            light_front_right_yellow.duty(0)
            light_back_left_yellow.duty(0)
            light_back_right_yellow.duty(0)
def action(command_paremeter):
    global blinking_avar, blink_left, blink_right, light_r_now
    if command_paremeter == 'forward':
        motor_1_dir_pin_0.value(0)
        motor_1_dir_pin_1.value(1)
        motor_2_dir_pin_0.value(1)
        motor_2_dir_pin_1.value(0)
        light_back_left_white.duty(0)
        light_back_right_white.duty(0)
    if command_paremeter == 'reverse':
        motor_1_dir_pin_0.value(1)
        motor_1_dir_pin_1.value(0)
        motor_2_dir_pin_0.value(0)
        motor_2_dir_pin_1.value(1)
        light_back_left_white.duty(1023)
        light_back_right_white.duty(1023)
    if command_paremeter == 'off_m_motor':
        motor_1_dir_pin_0.value(0)
        motor_1_dir_pin_1.value(0)
        motor_2_dir_pin_0.value(0)
        motor_2_dir_pin_1.value(0)
    if command_paremeter == 't_left':
        set_angle(60)
    if command_paremeter == 't_right':
        set_angle(120)
    if command_paremeter == 'off_t_motor':
        set_angle(90)
    if command_paremeter == 'on_light_f':
        light_front_pin_1.value(1)
        light_front_white_main.duty(50)
    if command_paremeter == 'off_light_f':
        light_front_pin_1.value(0)
    if command_paremeter == 'front_far':
        light_front_pin_1.value(1)
        light_front_white_main.duty(300)
    if command_paremeter == 'on_bl_l':
        blink_left = 1
    if command_paremeter == 'on_bl_r':
        blink_right = 1
    if command_paremeter == 'off_bl':
        stop_blink()
    if command_paremeter == 'blink_avar':
        blinking_avar = 1
    if command_paremeter == 'off_light_r':
        light_back_pin_0.value(0)
        light_back_pin_1.value(0)
        light_r_now = 0
    if command_paremeter == 'on_light_r':
        light_back_pin_0.value(0)
        light_back_pin_1.value(1)
        light_r_now = 1
    if command_paremeter == 'start_braking':
        motor_1_dir_pin_0.value(1)
        motor_1_dir_pin_1.value(1)
        motor_2_dir_pin_0.value(1)
        motor_2_dir_pin_1.value(1)
        light_back_pin_0.value(0)
        light_back_pin_1.value(1)
        light_back_red_main.duty(300)
    if command_paremeter == 'stop_braking':
        motor_1_dir_pin_0.value(0)
        motor_1_dir_pin_1.value(0)
        motor_2_dir_pin_0.value(0)
        motor_2_dir_pin_1.value(0)
        light_back_red_main.duty(50)
        if light_r_now == 0:
            light_back_pin_0.value(0)
            light_back_pin_1.value(0)
def receive_message_from_server():
    global connected_to_server, s
    while 1:
        if connected_to_server == 1:
            try:
                message_from_server_in_bites = s.recv(1024)
                if not message_from_server_in_bites:
                    connected_to_server = 0
                    s.close()
                    s = None
                    continue
                message_from_server = message_from_server_in_bites.decode()

                #====== actions ======
                commands = message_from_server.strip().split('\n')
                for command in commands:
                    action(command)
                #===================
            except:
                connected_to_server = 0
                if s:
                    s.close()
                s = None
    time.sleep(0.1)
_thread.start_new_thread(receive_message_from_server, ())
def main():
    global time_counter
    connection_to_server()
    ping_sending()
    time_counter += 1
    start_avar()
    is_blink_left()
    is_blink_right()
    time.sleep(0.5)

while 1:
    main()






