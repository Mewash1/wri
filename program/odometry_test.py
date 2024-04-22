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
)
from ev3dev2.button import Button
from ev3dev2.wheel import Wheel
from ev3dev2.sound import Sound
from ev3dev2.sensor import INPUT_1
from ev3dev2.sensor.lego import TouchSensor


class Kolo(Wheel):
    """
    part number XXXXX
    """

    def __init__(self):
        Wheel.__init__(self, X, Y)  # do zmierzenia


class Vehicle:
    def __init__(self):
        self.wheel_separation = 0.0  # do sprawdzenia
        self.sensor_offset = 0.0
        self.speed = 40

        self.controller = MoveDifferential(
            OUTPUT_A,
            OUTPUT_D,
            Kolo,
            self.wheel_separation,
            desc=None,
            motor_class=LargeMotor,
        )

    def run(self):
        print("Program started")
        sound = Sound()
        sound.tone([(523, 350, 100), (587, 350, 100), (659, 350, 100)])

        self.controller.odometry_start()

        while True:
            command = input().split(" ")
            cmd = command[0]
            args = command[1:]
            if cmd == "goto":  # w mm
                self.controller.on_to_coordinates(
                    SpeedRPM(self.speed), int(args[0]), int(args[1])
                )
            if cmd == "rotate":  # w stopniach
                self.controller.turn_to_angle(SpeedRPM(self.speed), int(args[0]))
            if cmd == "reset":
                self.x = 0.0
                self.y = 0.0
                self.theta = 0.0
            if cmd == "stop":
                break

            print("done")

        self.controller.odometry_stop()


if __name__ == "__main__":
    vehicle = Vehicle(0)
    vehicle.run()
