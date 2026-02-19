import time
import sys
import struct
import math

from unitree_sdk2py.core.channel import ChannelSubscriber, ChannelFactoryInitialize
# Uncomment the following two lines when using Go2、Go2-W、B2、B2-W、H1 robot
from unitree_sdk2py.idl.default import unitree_go_msg_dds__LowState_, unitree_go_msg_dds__SportModeState_
from unitree_sdk2py.idl.unitree_go.msg.dds_ import LowState_
from unitree_sdk2py.go2.sport.sport_client import (
    SportClient,
    PathPoint,
    SPORT_PATH_POINT_SIZE,
)
from dataclasses import dataclass

import evdev
from evdev import ecodes, InputDevice, categorize

@dataclass
class Actions:
    name: str
    key: str
    id: int     #Remplacer par un str pour les touches de la manette ou changer les numéro par ceux correspondant aux touches

action_list = [
    Actions(name="damp", key='L1', id=310),      # emergency stop
    Actions(name="recovery_stand", key='R1', id=311),   # restore standing
    # Actions(name="stop_move", id=2),
    Actions(name="standUp/standDown", key='CIRCLE', id=305),  
    Actions(name='Sit/Rise sit', key='Triangle', id=307),
    Actions(name='Euler front', key='Y', id=17),
    Actions(name='Euler side', key='X', id=16),    
    # Actions(name="free walk", id=5),
    # Actions(name="free avoid", id=6),
    # Actions(name="pose", id=7),
    # Actions(name="unlock", id=8),   #balance stand (after pose ?)
    # Actions(name="economic", id=9),
    Actions(name="move forward", key='L_J_Y', id=1),         
    Actions(name="move lateral", key='L_J_X', id=0),    
    # # Actions(name="move rotate", id=5),
    # Actions(name="hand stand", id=12),
    # Actions(name="sit", id=13),
    # Actions(name="rise sit", id=14),
    # Actions(name="front jump", id=15),  
    # Actions(name="walk upright", id=17),
    # Actions(name="switch avoid", id=18),
    # Actions(name="speedLevel", id=19),
    # Actions(name="classic walk", id=20),  
    # Actions(name="trot run", id=21),
    # Actions(name="walk back", id=22)
]

class UserInterface:
    def __init__(self):
        self.action_list_ = None
        self.device = evdev.InputDevice('/dev/input/by-id/usb-Sony_Interactive_Entertainment_Wireless_Controller-if03-event-joystick')
        self.robot_state_standing = True
        self.robot_state_siting = False

    def convert_to_int(self, input_str):
        try:
            return int(input_str)
        except ValueError:
            return None

    def terminal_handle(self):
        #input_str = input("Enter id or name: \n")

        # if input_str == "list":
        #     self.action_list_.name = None
        #     self.action_list_.id = None
        #     for option in action_list:
        #         print(f"{option.name}, id: {option.id}")
        #     return
        

        if event.type == ecodes.EV_KEY :
            print(event.code)
            for option in  action_list:
                if event.value == 1 and event.code == option.id :
                #if input_str == option.name or self.convert_to_int(input_str) == option.id:
                    self.action_list_.name = option.name
                    self.action_list_.key = option.key
                    self.action_list_.id = option.id
                    #print(f"Action: {self.action_list_.name}, action_key: {self.action_list_.key}, action_id: {self.action_list_.id}")
                    return   
        elif event.type == ecodes.EV_ABS:
            for option in action_list:
                if event.code == option.id :
                    self.action_list_.name = option.name
                    self.action_list_.key = option.key
                    self.action_list_.id = option.id
                    #print(f"Action: {self.action_list_.name}, action_key: {self.action_list_.key}, action_id: {self.action_list_.id}")
                    return     

        #print("No matching action found.")

if __name__ == "__main__":


    print("WARNING: Please ensure that the robot is standing at the start and there are no obstacles around it.")
    input("Press Enter to continue...")

    if len(sys.argv)>1:
        ChannelFactoryInitialize(0, sys.argv[1])
    else:
        ChannelFactoryInitialize(0)

    action_option = Actions(name=None, key=None, id=None) 
    user_interface = UserInterface()
    user_interface.action_list_ = action_option

    sport_client = SportClient()  
    sport_client.SetTimeout(10.0)
    sport_client.Init()

    for event in user_interface.device.read_loop() :
        #print('starting loop...')
        user_interface.terminal_handle()

        #print(f"Updated Action: Name = {action_option.name}, Key = {action_option.key}, ID = {action_option.id}\n")

        if action_option.key == 'L1':
            print('damp')
            sport_client.Damp()
            user_interface.robot_state_standing = False
            action_option.key = None
        elif action_option.key == 'R1':
            print('Recovery stand')
            sport_client.RecoveryStand()
            user_interface.robot_state_standing = True
            action_option.key = None
        elif action_option.key == 'CIRCLE':
            if user_interface.robot_state_standing == True :
                print('Stand Down')
                sport_client.StandDown()
                time.sleep(5)
                user_interface.robot_state_standing = False
            else :
                print('Stand Up')
                sport_client.StandUp()
                time.sleep(5)
                user_interface.robot_state_standing = True
            action_option.key = None
        elif action_option.key == 'Triangle':
            if user_interface.robot_state_siting == False :
                sport_client.Sit()
                time.sleep(5)
                user_interface.robot_state_siting = True
            else :
                sport_client.RiseSit()
                time.sleep(5)
                user_interface.robot_state_siting = False
            action_option.key = None


        elif event.type == ecodes.EV_SYN:
            pass
        elif action_option.key == 'L_J_Y':
            # if not (100 <= event.value <= 150):
            #     print(categorize(event), 'value :' , event.value)

            if event.value < 110 :
                print('move forward: ', event.value)
                sport_client.Move(0.5, 0, 0)
            elif event.value > 140 :
                print('Move back: ', event.value)
                sport_client.Move(-0.5, 0, 0)
            else : 
                sport_client.StopMove()
                print('STOP: ',event.value)
            action_option.key = None

        # elif action_option.key == 'L_J_X':
        #     if event.value < 100:
        #         print('Move to LEFT: ', event.value)
        #         sport_client.Move(0, -0.5, 0)
        #     if event.value > 150 :
        #         print('Move to RIGHT: ', event.value)
        #     else :
        #         sport_client.StopMove()
        #     action_option.key = None

        elif action_option.key == 'Y': 
            orientation = True
            pitch = 0.0   # valeur actuelle maintenue

            while orientation:
                for event in user_interface.device.read_loop():
                    sport_client.BalanceStand()
                    user_interface.terminal_handle()
                    print('Execution: ', pitch)
                    sport_client.Euler(0, pitch, 0)
                    if event.type == ecodes.EV_ABS:
                        if event.value == -1:
                            print("Inclinaison vers l'avant")
                            pitch = 0.5

                        elif event.value == 1:
                            print("Inclinaison vers l'arrière")
                            pitch = -0.5
                    elif event.type == ecodes.EV_KEY:
                        if action_option.key == 'R1':
                            pitch = 0.0
                            sport_client.Euler(0, 0, 0)
                            orientation = False
                            break
        


                # if action_option.key == 'Y': 
                #     if event.value == -1 :
                #         print("Inclinaison vers l'avant")
                #         #sport_client.Pose()
                #         sport_client.Euler(0, 0.5, 0)
                #     elif event.value == 1:
                #         sport_client.Euler(0, -0.5, 0)
                # elif action_option.key == 'R1':
                #     sport_client.Euler(0, 0, 0)
                #     orientation = False
                #     action_option.key = None
                
        
            
        
               
        
        
        
        
    



# import rclpy
# from rclpy.node import Node
# from sensor_msgs.msg import Joy

# class JoyControl(Node):

#     def __init__(self):
#         super().__init__('joy_control')

#         self.subscription = self.create_subscription(
#             Joy,
#             '/joy',
#             self.joy_callback,
#             10)

#     def joy_callback(self, msg):

#         # bouton A
#         if msg.buttons[0] == 1:
#             self.get_logger().info("Bouton A pressé")

#         # bouton B
#         if msg.buttons[1] == 1:
#             self.get_logger().info("Bouton B pressé")

#         # joystick gauche horizontal
#         x = msg.axes[0]

#         if x > 0.5:
#             self.get_logger().info("Joystick droite")

#         elif x < -0.5:
#             self.get_logger().info("Joystick gauche")

# def main(args=None):

#     rclpy.init(args=args)

#     node = JoyControl()

#     rclpy.spin(node)

#     node.destroy_node()
#     rclpy.shutdown()
