#!/usr/bin/env python3

from ev3dev2.motor import (
    LargeMotor,
    MediumMotor,
    OUTPUT_A,
    OUTPUT_C,
    OUTPUT_D,
    MoveDifferential,
    SpeedRPM,
    SpeedNativeUnits,
)
from ev3dev2.wheel import Wheel
from ev3dev2.sound import Sound
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_4
from ev3dev2.sensor.lego import TouchSensor, ColorSensor

import os
import sys
import math


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
        differential = self.Kd * (error - self.error_prev)
        self.error_prev = error

        return proportional + self.integral + differential


class Kolo(Wheel):
    def __init__(self):
        Wheel.__init__(self, 54, 26)


class Vehicle:
    def __init__(self):
        self.wheel_separation = 178.5
        self.sensor_offset = 88.0
        self.speed = 50
        self.default_speed = 50
        self.forklift_motor = MediumMotor(OUTPUT_C)
        self.forklift_sensor = TouchSensor(INPUT_2)

        self.color_sensor_right = ColorSensor(INPUT_1)
        self.color_sensor_left = ColorSensor(INPUT_4)

        (
            self.color_sensor_right.red_max,
            self.color_sensor_right.green_max,
            self.color_sensor_right.blue_max,
        ) = (158, 234, 281)
        (
            self.color_sensor_left.red_max,
            self.color_sensor_left.green_max,
            self.color_sensor_left.blue_max,
        ) = (132, 224, 145)

        self.controller = MoveDifferential(
            OUTPUT_A,
            OUTPUT_D,
            Kolo,
            self.wheel_separation,
            desc=None,
            motor_class=LargeMotor,
        )

        self.sound = Sound()

    def set_state(self, new_state):
        self.state = new_state
        self.state.context = self
        self.state.setup()

    def sense_line(self):
        right_val = self.color_sensor_right.reflected_light_intensity
        left_val = self.color_sensor_left.reflected_light_intensity
        diff = right_val - left_val

        return diff, right_val, left_val

    def sense_colour(self):
        color_right = self.color_sensor_right.rgb
        color_left = self.color_sensor_left.rgb
        colorfullness_right = -color_right[0] + (color_right[1] + color_right[2]) // 2
        colorfullness_left = -color_left[0] + (color_left[1] + color_left[2]) // 2

        return colorfullness_right, colorfullness_left

    def set_speed(self, speed, steering):
        speed = self.controller.left_motor._speed_native_units(SpeedRPM(speed))
        left_speed = speed
        right_speed = speed
        speed_factor = (50 - abs(float(steering))) / 50

        if steering >= 0:
            right_speed *= speed_factor
        else:
            left_speed *= speed_factor

        self.controller.on(SpeedNativeUnits(left_speed), SpeedNativeUnits(right_speed))

    def run(self):
        self.branch_right = None
        self.holding_package = False

        self.set_state(StateFollowing())

        os.system("clear")
        os.system("clear")

        self.sound.tone([(523, 100, 100), (587, 100, 100), (659, 100, 100)])

        # zerowanie odometrii
        self.controller.odometry_start()
        self.controller.x_pos_mm = 0.0
        self.controller.y_pos_mm = 0.0
        self.controller.theta = math.pi / 2

        # zbazowanie wideł
        while self.forklift_sensor.is_released:
            self.forklift_motor.on(SpeedRPM(40))

        self.forklift_motor.off()
        self.forklift_motor.on_for_rotations(SpeedRPM(40), -1)

        print("Type start to start following")
        while True:
            command = input().split(" ")
            cmd = command[0]
            if cmd == "start":
                break

        while True:
            self.state.step()



class LineFollower:
    def __init__(self, context: Vehicle):
        self.pid = PID(2.5, 0.18, 0)
        self.context = context

    def step(self, diff):
        steering = self.pid.step(0, diff)
        steering = min(100, max(-100, steering))

        self.context.set_speed(self.context.speed, steering)


class State:
    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, context: Vehicle):
        self._context = context

    def setup(self):
        pass

    def step(self):
        pass


class StateIdle(State):
    def setup(self):
        print("exiting")
        sys.exit(0)


class StateFollowing(State):
    def setup(self, tick_limit=0):
        print("Following")
        self.follower = LineFollower(self._context)
        self.tick_limit = tick_limit

    def step(self):
        diff, right_val, left_val = self.context.sense_line()

        self.follower.step(diff)


if __name__ == "__main__":
    vehicle = Vehicle()
    vehicle.run()
