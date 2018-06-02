import os
import subprocess
from subprocess import call
import RPi.GPIO as GPIO
from time import sleep

#Setting buttons to GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(4 ,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(22,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(25,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
buttonPressedTime = None

Pass = True

while Pass:
        sleep (3)

        #Reads files in SD card
        path ='/home/pi/Music'
        f =[os.path.join(dirpath,fn)
            for dirpath,dirnames,files in os.walk(path)
            for fn in files if fn.endswith('mp3')]

        #Reads files in USB
        path2 ='/media/pi/'
        g =[os.path.join(dirpath,fn)
            for dirpath,dirnames,files in os.walk(path2)
            for fn in files if fn.endswith('mp3')]

        #Checks if there are any songs in SD card if not, checks if there are any in USB, if not it will loop continuously 
        if (len(f) == 0 and len(g) > 0):
                #Copy files from USB
                os.system("cp /media/pi/**/*.mp3 /home/pi/Music")
        else:
                #Limits number of songs played.
                if (len(f) < 15 and len(f) > 0):
                        h = len (f)
                        Pass = False
                        print Pass
                elif (len(f) >= 15):
                        h = 15
                        Pass = False
                        print  Pass
        print Pass
        
print "# Of Songs"
print h
flag = 1
pointer = 0 # pointer for which audio file
sFlag = 0 # stop flag when music command is used

start = 0
volume = 0
tempVolume = 0
btnDown = 0
playing = False

print "Start Music Player"
while True:
        try:
                #Initiates music player
                if (flag == 1):
                        player = subprocess.Popen(["omxplayer",f[pointer]],stdin =subprocess.PIPE)
                        sleep (1)
                        fi = player.poll() 
                        flag=0
                        sFlag = 0
                        
                        if (start == 0): #Stops music from playing before Play button is pressed
                                player.stdin.write("p")
                        elif (volume !=0): #Pauses music temporarily if volume needs to be reset
                                player.stdin.write("p")

                        tempVolume = volume
                        if (volume > 0): #Increment volume up again
                                while (tempVolume != 0):
                                        tempVolume -= 1
                                        sleep (0.8)
                                        player.stdin.write("+")
                                        print tempVolume
                                sleep(0.2)
                                player.stdin.write("p") #Resumes volume
                                playing = True
                        elif (volume < 0): #Decrement volume down again
                                while (tempVolume != 0):
                                        tempVolume += 1
                                        sleep (0.8)
                                        player.stdin.write("-")
                                        print tempVolume
                                sleep (0.2)        
                                player.stdin.write("p") #Resumes volume
                                playing = True
                        start = 1
                        
                #Play/Pause
                if (GPIO.input(4) == 1):
                        sleep (0.2)
                        fi = player.poll() #Play
                        if fi!=0:        
                                player.stdin.write("p")
                                if (playing == True):
                                        playing = False
                                else:
                                        playing = True

                        #Long Press button
                        for count in range(10000):
                                if (GPIO.input(4) == 1):
                                        btnDown +=1
                                        print btnDown

                                #Prevents music from playing while user is trying to overwrite songs
                                if (btnDown == 2000):
                                        if (playing == True):
                                                player.stdin.write("p")
                                                playing = False
                                        
                                #If button is held down for ~10 seconds overwrites music in SD card 
                                if (btnDown == 10000):
                                        btnDown = 0

                                        #Check if there are files in the USB
                                        path2 ='/media/pi/'
                                        g =[os.path.join(dirpath,fn)
                                        for dirpath,dirnames,files in os.walk(path2)
                                        for fn in files if fn.endswith('mp3')]

                                        print len(g)
                                        if (len(g) > 0):
                                                #Quit player
                                                player.stdin.write("q")
                                                playing = False
                                                sleep(1)
                                                
                                                #Deletes ALL mp3 files from Music directory
                                                os.system("rm -r /home/pi/Music/*.mp3")
                                                sleep(4)

                                                #Copy files from USB
                                                os.system("cp /media/pi/**/*.mp3 /home/pi/Music")
                                                sleep(1)

                                                #Restarts player with newly imported songs
                                                player = subprocess.Popen(["omxplayer",f[pointer]],stdin =subprocess.PIPE)
                                                sleep(1)
                                                fi=player.poll() 
                                                flag=0
                                                sFlag = 0
                                                player.stdin.write("p") #Play
                                                playing = True
                                                
                #Volume Down
                if (GPIO.input(22) == 1):
                        if volume > -10 :
                                volume -= 1
                                sleep(0.8)
                                player.stdin.write("-")
                                print "volume down"
                                
                #Volume Up
                if (GPIO.input(25) == 1):
                        if volume < 3 :
                                volume += 1
                                sleep(0.8)
                                player.stdin.write("+") 
                                print "volume up"
                                
                #Moves to next song
                else:
                        fi = player.poll()
                        if(fi == 0 and sFlag == 0):
                                flag = 1
                                pointer += 1
                        if(pointer > h - 1):
                                pointer = 0
                        
        except KeyboardInterrupt:
                GPIO.cleanup()
