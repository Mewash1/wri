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
from ev3dev2.sensor import INPUT_1, INPUT_2
from ev3dev2.sensor.lego import TouchSensor

import math
from path_math import get_dist


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
        self.speed = 80
        self.forklift_motor = MediumMotor(OUTPUT_C)
        self.forklift_sensor = TouchSensor(INPUT_2)

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
- goto x y - przesuń robota do punktu (x,y) [x,y] = mm
- rotate z - obróć robota o kąt z   
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
            if cmd == "goto":  # w mm
                if int(args[0]) == self.controller.x_pos_mm and int(args[1]) == self.controller.y_pos_mm:
                    print("You cannot move to your current position!")
                else:
                    self.controller.on_to_coordinates(
                        SpeedRPM(self.speed), int(args[0]), int(args[1])
                    )
                print("Current position: x=" + str(self.controller.x_pos_mm) + " y=" + str(self.controller.y_pos_mm) +  " angle=" + str(self.controller.theta))
            if cmd == "rotate":  # w stopniach
                self.controller.turn_to_angle(SpeedRPM(self.speed), int(args[0]))
            if cmd == "spin":
                theta = self.controller.theta
                self.controller.turn_to_angle(SpeedRPM(self.speed), theta + 90)
                self.controller.turn_to_angle(SpeedRPM(self.speed), theta + 180)
                self.controller.turn_to_angle(SpeedRPM(self.speed), theta + 270)
                self.controller.turn_to_angle(SpeedRPM(self.speed), theta)
            if cmd == "move":
                dest_x = int(args[0])
                dest_y = int(args[1])
                x = self.controller.x_pos_mm
                y = self.controller.y_pos_mm
                theta = self.controller.theta# * math.pi / 180

                heading_x = math.cos(theta) 
                heading_y = math.sin(theta) 

                delta_x = dest_x - x 
                delta_y = dest_y - y
                d = math.sqrt(delta_x ** 2 + delta_y ** 2)

                alpha = math.atan2(heading_y * delta_x - heading_x * delta_y, heading_x * delta_x + heading_y * delta_y)

                #cos_alpha = (delta_x * heading_x + delta_y * heading_y) / d
                #gamma = 2 * math.acos(cos_alpha)
                gamma = 2 * alpha
                cos_gamma = math.cos(gamma)

                r = d / math.sqrt(2 - 2 * cos_gamma)
                arc_len = r * gamma
                
                print(x, y, theta)
                print(heading_x, heading_y)
                print(delta_x, delta_y)
                print(d)
                print(alpha)
                print(r, arc_len, gamma)
                arc_len -= self.sensor_offset

                if (arc_len < 0):
                    self.controller.on_arc_left(SpeedRPM(self.speed), r, abs(arc_len))
                else:
                    self.controller.on_arc_right(SpeedRPM(self.speed), r, abs(arc_len))

                print("Current position: x=" + str(self.controller.x_pos_mm) + " y=" + str(self.controller.y_pos_mm) +  " angle=" + str(self.controller.theta))
            if cmd == "reset":
                self.controller.x_pos_mm = 0.0
                self.controller.y_pos_mm = 0.0
                self.controller.theta = math.pi / 2
            if cmd == "follow":
                while True:
                    x = self.controller.x_pos_mm
                    y = self.controller.y_pos_mm
                    theta = self.controller.theta

                    x += self.sensor_offset * math.cos(theta)
                    y += self.sensor_offset * math.sin(theta)

                    dist = get_dist(-x, y, theta)
                    print(dist)

                    steering = dist * 2
                    steering = min(100, max(-100, steering))

                    speed = self.controller.left_motor._speed_native_units(SpeedRPM(self.speed))
                    left_speed = speed
                    right_speed = speed
                    speed_factor = (50 - abs(float(steering))) / 50

                    if steering >= 0:
                        right_speed *= speed_factor
                    else:
                        left_speed *= speed_factor

                    self.controller.on(SpeedNativeUnits(left_speed), SpeedNativeUnits(right_speed))
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
            

            print("Done.")

        self.controller.odometry_stop()


if __name__ == "__main__":
    vehicle = Vehicle()
    vehicle.run()


