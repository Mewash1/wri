#!/usr/bin/env python3

from ev3dev2.motor import (
    LargeMotor,
    MediumMotor,
    OUTPUT_A,
    OUTPUT_B,
    OUTPUT_C,
    OUTPUT_D,
    MoveDifferential,
    SpeedRPM,
)
from ev3dev2.button import Button
from ev3dev2.wheel import Wheel
from ev3dev2.sound import Sound
from ev3dev2.sensor import INPUT_1
from ev3dev2.sensor.lego import TouchSensor

import math


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
        self.speed = 40

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
        self.controller.theta = 0.0
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
                self.controller.theta = 0.0
            if cmd == "stop":
                sound.tone([(659, 100, 100), (587, 100, 100), (523, 100, 100)])
                break
            if cmd == "help":
                self.print_help()

            print("Done.")

        self.controller.odometry_stop()


if __name__ == "__main__":
    vehicle = Vehicle()
    vehicle.run()
