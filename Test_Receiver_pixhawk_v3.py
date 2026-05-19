from pymavlink import mavutil
import sys
import socket 
import time
import cv2
import os
from datetime import datetime
import pickle
import struct
import threading

####################################################################################################Socket

# Create a socket object 
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
 
# Get the hostname of the machine 
host = '169.254.175.117'
 
# Define the port to listen on 
port = 12345 
 
# Bind the socket to the host and port 
server_socket.bind((host, port)) 
 
# Listen for incoming connections (max 5 connections in the queue) 
server_socket.listen(1) 
 
print(f"Server is listening on {host}:{port}") 

# Establish connection with the client 
client_socket, addr = server_socket.accept() 
####################################################################################################Socket

####################################################################################################Pixhawk Connection
# Hedef sistemi ve bileşeni ayarla
target_system = 0  # Su altı aracının sistem ID'si
target_component = 0  # Su altı aracının bileşen ID'si


# Pixhawk'a bağlan
master = mavutil.mavlink_connection("COM13", baud=115200)
master.wait_heartbeat()

####################################################################################################Pixhawk Connection


def rc_ch_pwm(channel_id, pwm=1500):
    """ Set RC channel pwm value
    Args:
        channel_id (TYPE): Channel ID
        pwm (int, optional): Channel pwm value 1100-1900
    """
    #if channel_id < 1 or channel_id > 18:
        #print("Channel does not exist.")
        #return

    # Mavlink 2 supports up to 18 channels:
    # https://mavlink.io/en/messages/common.html#RC_CHANNELS_OVERRIDE
    rc_channel_values = [65535 for _ in range(18)]
    rc_channel_values[channel_id - 1] = pwm
    master.mav.rc_channels_override_send(master.target_system, master.target_component,*rc_channel_values)                 

    

def ileri():
    master.mav.manual_control_send(
    master.target_system,
    900,                              # -1000 ile 1000                        x: 1000 ileri, -1000 geri         'pitch'
    0,                              # -1000 ile 1000                        y: 1000 sag, -1000 sol            'yaw'
    500,                            # 0 ile 1000            500 orta        z: yukarı asagi heral
    0,                              # 1000 saat yonunde, -1000 saat yonu tersine
    0) 

def geri():
    master.mav.manual_control_send(
    master.target_system,
    -900,                             
    0,                              
    500,                            
    0,                              
    0) 

def yukari():
    master.mav.manual_control_send(
    master.target_system,
    0,                             
    0,                              
    750,                        
    0,                              
    0) 

def asagi():
    master.mav.manual_control_send(
    master.target_system,
    0,                             
    0,                              
    250,                            
    0,                              
    0) 

def sag():
    master.mav.manual_control_send(
    master.target_system,
    0,                              
    900,                              
    900,                           
    0,                             
    0) 

def sol():
    master.mav.manual_control_send(
    master.target_system,
    0,                              
    -900,                             
    900,                           
    0,                             
    0) 

def stop():
    master.mav.manual_control_send(
    master.target_system,
    0,                            
    0,                              
    500,                          
    0,                             
    0) 
    
    
def saat_yonu():
    master.mav.manual_control_send(
    master.target_system,
    0,                              
    0,                             
    500,                           
    900,                             
    0) 
    
def saat_tersi():
    master.mav.manual_control_send(
    master.target_system,
    0,                              
    0,                             
    500,                           
    -900,                             
    0) 

def goruntu_durdur():
    
    global running
    running = False

def joystick_kontrol():
    while(1):

        data1 = int(client_socket.recv(4).decode())
        #print(f"###Eksen 1:\n {data1}\n")

        data2 = int(client_socket.recv(4).decode())
        #print(f"###Eksen 2:\n {data2}\n")
        
        data3 = int(client_socket.recv(4).decode())
        #print(f"###Eksen 3:\n {data3}\n")

        data4 = int(client_socket.recv(4).decode())
        #print(f"###Eksen 4:\n {data4}\n")
        
        data5 = int(client_socket.recv(1).decode())
        #print(f"###Eksen 5:\n {data5}\n")
        

        if (data5 == 1):
            stop()
            break

        rc_ch_pwm(4, data1)
        rc_ch_pwm(3, data2)
        rc_ch_pwm(2, data3)
        rc_ch_pwm(1, data4)
              

def goruntu_al():
            
####################################################################
            cap = cv2.VideoCapture(0)  # 0, birincil kamera demektir. Daha fazla kamera varsa, 1, 2, vb. kullanılabilir.

            if not cap.isOpened():
                print("Kamera açılamadı!")
                #return

            # Kaydedilecek klasörü oluştur
            ###save_folder = "kayit"
            ###os.makedirs(save_folder, exist_ok=True)

            # Görüntü kaydetme sayaçı
            ###image_counter = 0 

            # İlk kayıt zamanı
            ###last_save_time = time.time()

            # Görüntü alımı ve işleme döngüsüq
            while True:
                # Görüntüyü yakala
                ret, frame = cap.read()
                
#######################################          
                data6 = int(client_socket.recv(4).decode())
                print(f"###Eksen 6:\n {data6}\n")
                if (data6 == 1):
                    print("KAPANDI")
                    stop()
                    break
#######################################3           
                
                ###if ret:
                    # Görüntüyü ekranda göster
                    ###cv2.imshow("Goruntu", frame)

                    # Görüntüyü kaydet
                    ###current_time = time.time()
                    ###if current_time - last_save_time >= 2:  # Her 4 saniyede bir kaydet
                        ###image_counter += 1
                        ###current_datetime = datetime.now()   
                        ###timestamp = current_datetime.strftime("%d%m%Y%H%M%S")  # Tarih ve saat bilgisini al
                        ###file_path = os.path.join(save_folder, f"{image_counter}_{timestamp}.jpg")
                        ###cv2.imwrite(file_path, frame)
                        ###last_save_time = current_time
                    # Bir tuşa basıldığında döngüden çık
                    #data5 = int(client_socket.recv(1))
                    #if data5 == 1:
                        #break
                else:
                    print("Görüntü alınamadı!")
                    break

            # Kamerayı kapat
            ###cap.release()
            ###cv2.destroyAllWindows()  
running = True
####################################################################3
def videocapture():
        vid = cv2.VideoCapture(0)
        global running
        while(vid.isOpened() and running):
            img,frame = vid.read()
            a = pickle.dumps(frame)
            message = struct.pack("Q",len(a))+a
            client_socket.sendall(message)
            #cv2.imshow('Sending...',frame)
            #key=int(client_socket.recv(1024).decode())
            #print(key)
            #if key == 27:
                #break
        #vid.release()
        #cv2.destroyAllWindows() 

operasyon = 0

while True:
    #print("DENEME111")
    operasyon = int(client_socket.recv(1024).decode())
    stop()
    print(operasyon)
    if (operasyon == 1):
        # Arm mı yoksa Disarm mı ? Kontrol Blogu.
        msg0 = master.recv_match()
        if not msg0:
            continue
        # Aracın durumu
        if msg0.get_type() == 'HEARTBEAT':
            armed = (msg0.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED) != 0
            if armed:
                print("\n***Araç ARMED Durumunda.***\n")
                
            else:
                print("\n***Araç DISARMED Durumunda.***\n")
                

    elif (operasyon == 2):
        master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        # 7 parametre
        0,
        1, 0, 0, 0, 0, 0, 0)               
        print("Waiting for the vehicle to arm")
        master.motors_armed_wait()         # Eger arm etmiyorsa baglantiyi kopar tekrar bagla   - Misson planner
        print('Armed!\n')

    elif (operasyon == 3):
        master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        # 7 parametre
        0,
        0, 0, 0, 0, 0, 0, 0)               # 2. parametre 1 ise arm eder 0 ise disarm eder
        print("Waiting for the vehicle to disarm")
        master.motors_disarmed_wait()         
        print('Disarmed!\n')
    
    elif (operasyon == 4):
        while 1:
            #print("DENEME2222222222")
            received_data = client_socket.recv(1024)
            stop()
            girdi=received_data.decode()
            #print(girdi)
            
            if (girdi == 'sag'):
                sag()
            elif (girdi == 'sol'):
                sol()
            elif (girdi == 'ileri'):
                ileri()
            elif (girdi == 'geri'):
                geri()
            elif (girdi == 'yukari'):
                yukari()
            elif (girdi == 'asagi'):
                asagi()
            elif (girdi == 'stop'):
                stop()
            elif (girdi == 'stop2'):
                goruntu_durdur()
            elif (girdi == 'saat_yonu'):
                saat_yonu()
            elif (girdi == 'saat_tersi'):
                saat_tersi()
                
            elif (girdi == 'pwm'):
                channel_buffer = int(client_socket.recv(1024).decode())
                print(channel_buffer)
                pwm_buffer = int(client_socket.recv(1024).decode())
                print(pwm_buffer)
                rc_ch_pwm(channel_buffer, pwm_buffer)
                
            elif (girdi == 'joy'):
                joystick_kontrol()
            elif (girdi == 'q'):
                break

            else:
                print("Tekrar Dene!")
            print("\n")
    elif (operasyon==6):
        threading.Thread(target=videocapture).start()
        #videocapture()
    elif (operasyon ==5):
        goruntu_al()
    elif (operasyon == 100):
        sys.exit()
        print("Program Sonlandirildi!")



