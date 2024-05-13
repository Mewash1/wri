#!/usr/bin/env micropython

from ev3dev2.motor import (
    LargeMotor,
    MediumMotor,
    OUTPUT_A,
    OUTPUT_B,
    OUTPUT_C,
    OUTPUT_D,
    MoveDifferential,
    SpeedRPM,
    SpeedNativeUnits,
)
from ev3dev2.button import Button
from ev3dev2.wheel import Wheel
from ev3dev2.sound import Sound
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4
from ev3dev2.sensor.lego import TouchSensor, ColorSensor

import math
import time
import os

class PID:
    def __init__(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        
        self.integral = 0.0
        self.error_prev = 0.0

    def reset(self):
        self.integral = 0.0
        self.error_prev = 0.0
        
    def step(self, setpoint, measurement):
        error = setpoint - measurement

        proportional = self.Kp * error
    
        self.integral += self.Ki * error
    
        # antiwindup by limiting the maximum and minimum integral
        # self.integral = min(self.integral, 1.0)
        # self.integral = max(self.integral, -1.0)
        differential = self.Kd * (error - self.error_prev)
    
        self.error_prev = error
    
        # return (proportional + self.integral + differential, proportional, self.integral, differential)
        return proportional + self.integral + differential

class Kolo(Wheel):
    """
    part number XXXXX
    """

    def __init__(self):
        Wheel.__init__(self, 54, 26)  # do zmierzenia


class Vehicle:
    def __init__(self):
        self.wheel_separation = 178.5  # do sprawdzenia
        self.sensor_offset = 88.0
        self.speed = 20
        self.forklift_motor = MediumMotor(OUTPUT_C)
        self.forklift_sensor = TouchSensor(INPUT_2)

        self.color_sensor_right = ColorSensor(INPUT_1)
        self.color_sensor_left = ColorSensor(INPUT_4)

        self.controller = MoveDifferential(
            OUTPUT_A,
            OUTPUT_D,
            Kolo,
            self.wheel_separation,
            desc=None,
            motor_class=LargeMotor,
        )

    def print_help(self):
        print(
        """
Wybierz komendę:
- pid - uruchom pida (x y z)
- reset - przywróć do zera pozycję oraz kąt obrotu robota
- stop - zakończ działanie programu
- help - wyświetl ponownie tę wiadomość
        """
        )

    def run(self):
        print("Program started")
        sound = Sound()
        sound.tone([(523, 100, 100), (587, 100, 100), (659, 100, 100)])

        self.controller.odometry_start()
        self.controller.x_pos_mm = 0.0
        self.controller.y_pos_mm = 0.0
        self.controller.theta = math.pi / 2
        self.print_help()

        while True:
            command = input().split(" ")
            cmd = command[0]
            args = command[1:]
            if cmd == "reset":
                self.controller.x_pos_mm = 0.0
                self.controller.y_pos_mm = 0.0
                self.controller.theta = math.pi / 2
            if cmd == "stop":
                sound.tone([(659, 100, 100), (587, 100, 100), (523, 100, 100)])
                break
            if cmd == "help":
                self.print_help()
            if cmd == "lift":
                while (self.forklift_sensor.is_released):
                    self.forklift_motor.on(SpeedRPM(40))
                
                self.forklift_motor.off()
            if cmd == "tfil":
                self.forklift_motor.on_for_rotations(SpeedRPM(40), -1)
            if cmd == "pid":
                pid = PID(float(args[0]), float(args[1]), float(args[2]))
                diff_offset = 0 # to calibrate
                line_theshold = 0 # to calibrate

                os.system('clear')
                os.system('clear')
                print("pid", float(args[0]), float(args[1]), float(args[2]))
                print("i,x,y,theta,diff,steering,right_val,left_val,colorfullness_right,colorfullness_left") # column titles

                state = "following"
                turning_steer = 0.0
                search_for_spot = False
                for i in range(200):
                    right_val = self.color_sensor_right.reflected_light_intensity
                    left_val = self.color_sensor_left.reflected_light_intensity
                    diff = right_val - left_val + diff_offset

                    x = self.controller.x_pos_mm 
                    y = self.controller.y_pos_mm 
                    theta = self.controller.theta

                    if state == "following":
                        steering = pid.step(0, diff)
                        steering = min(100, max(-100, steering))
                        speed = self.speed

                        if right_val < 15 and left_val < 15 or search_for_spot:
                            color_right = self.color_sensor_right.rgb
                            color_left = self.color_sensor_left.rgb

                            colorfullness_right = max(color_right) - min(color_right)
                            colorfullness_left = max(color_left) - min(color_left)
                        else: 
                            colorfullness_left = 0
                            colorfullness_right = 0

                        if abs(colorfullness_right - colorfullness_left) > 40:
                            state = "turning"
                            search_for_spot = True
                            if colorfullness_right > colorfullness_left:
                                turning_steer = 100
                            else:
                                turning_steer = -100
                            
                    elif state == "turning":
                        speed = 20
                        steering = turning_steer
                        if diff > 20:
                            state = "stabilize"
                    elif state == "stabilize":
                        x = pid.step(0, diff)
                        steering = -100 if x < 0 else 100
                        speed = abs(x) / 4
                        if diff < 5:
                            state = "following"

                    print(",".join([str(x) for x in [i, x, y, theta, diff, steering, right_val, left_val, colorfullness_right, colorfullness_left]]))

                    speed = self.controller.left_motor._speed_native_units(SpeedRPM(speed))
                    left_speed = speed
                    right_speed = speed
                    speed_factor = (50 - abs(float(steering))) / 50

                    if steering >= 0:
                        right_speed *= speed_factor
                    else:
                        left_speed *= speed_factor

                    self.controller.on(SpeedNativeUnits(left_speed), SpeedNativeUnits(right_speed))
            
            if cmd == "test":
                pid = PID(float(args[0]), float(args[1]), float(args[2]))
                diff_offset = 0 # to calibrate
                line_theshold = 0 # to calibrate
                print("pid", float(args[0]), float(args[1]), float(args[2]))

                os.system('clear')
                os.system('clear')
                print("diff,steering,right_val,left_val,,") # column titles
                while True:
                    right_val = self.color_sensor_right.reflected_light_intensity
                    left_val = self.color_sensor_left.reflected_light_intensity
                    diff = right_val - left_val + diff_offset
                    line_found = right_val < line_theshold
                    print(str(right_val) + "," + str(left_val) + "," + ",") # values to log

            print("Done.")
            self.controller.on(SpeedNativeUnits(0), SpeedNativeUnits(0))
        

        self.controller.odometry_stop()


if __name__ == "__main__":
    vehicle = Vehicle()
    vehicle.run()
