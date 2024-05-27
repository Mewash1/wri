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
    SpeedNativeUnits,
)
from ev3dev2.wheel import Wheel
from ev3dev2.sound import Sound
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4
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
        self.speed = 20
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
        # self.state.step()

    def sense_line(self):
        right_val = self.color_sensor_right.reflected_light_intensity
        left_val = self.color_sensor_left.reflected_light_intensity
        diff = right_val - left_val

        return diff, right_val, left_val

    def sense_colour(self):
        color_right = self.color_sensor_right.rgb
        color_left = self.color_sensor_left.rgb

        """
        colorfullness_right = max(color_right) - min(color_right)
        colorfullness_left = max(color_left) - min(color_left)

        if sum(color_right) > 240:
            colorfullness_right = 0

        if sum(color_left) > 240:
            colorfullness_left = 0
        """
        colorfullness_right = -color_right[0] + (color_right[1] + color_right[2]) // 2
        colorfullness_left = -color_left[0] + (color_left[1] + color_left[2]) // 2

        print(
            color_right,
            -color_right[0] + color_right[1] + color_right[2],
            color_left,
            -color_left[0] + color_left[1] + color_left[2],
        )

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

        # print("i,x,y,theta,diff,steering,right_val,left_val")  # column titles
        while True:
            self.state.step()

            """
            print(
                ",".join(
                    [
                        str(x)
                        for x in [
                            i,
                            x,
                            y,
                            theta,
                            diff,
                            steering,
                            right_val,
                            left_val,
                        ]
                    ]
                )
            )"""


class LineFollower:
    def __init__(self, context: Vehicle):
        self.pid = PID(2.5, 0.2, 0)
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

        if right_val < 15 and left_val < 15:
            self.context.speed = 10
            self.follower.step(diff)
            color_right, color_left = self.context.sense_colour()
        else:
            self.context.speed = 20
            self.follower.step(diff)
            color_right = 0
            color_left = 0

        print(right_val, " ", left_val, " ", color_right, " ", color_left)

        if (
            abs(color_right - color_left) > 10
            and max(color_right, color_left) > 50
            and self.tick_limit == 0
        ):
            self.context.set_state(StateEnterBranch())
            if color_right > color_left:
                self.context.branch_right = True
            else:
                self.context.branch_right = False

        if self.tick_limit > 0:
            self.tick_limit -= 1


class StateEnterBranch(State):
    def setup(self):
        print("Entering branch")
        """
        if self.context.branch_right:
            self.context.controller.turn_degrees(SpeedRPM(self.context.speed), -35)
        else:
            self.context.controller.turn_degrees(SpeedRPM(self.context.speed), 35)
        """

    def step(self):
        diff, _, _ = self.context.sense_line()
        if self.context.branch_right:
            self.context.set_speed(self.context.speed, 80)
        else:
            self.context.set_speed(self.context.speed, -80)

        if diff > 20:
            self.context.set_state(StateSearchTarget())
        # self.context.set_state(StateSearchTarget())


class StateSearchTarget(State):
    def setup(self):
        print("Searching for target")
        self.follower = LineFollower(self._context)
        self.step_count = 0

    def step(self):
        diff, right_val, left_val = self.context.sense_line()
        self.follower.step(diff)

        if right_val < 20 and left_val < 20 and self.step_count > 100:
            color_right, color_left = self.context.sense_colour()

            print(color_left, " ", color_right)
            if color_left > 50 and color_right > 50:  # TODO: calibration
                if self.context.holding_package:
                    self.context.set_state(StateDropPackage())
                else:
                    self.context.set_state(StatePickupPackage())

        self.step_count += 1

    pass


class StatePickupPackage(State):
    def setup(self):
        print("Picking up package")

    def step(self):
        self.context.controller.on_for_distance(
            SpeedRPM(self.context.speed), 0
        )  # TODO: calibrate

        while self.context.forklift_sensor.is_released:
            self.context.forklift_motor.on(SpeedRPM(40))

        self.context.forklift_motor.off()
        self.context.set_state(StateReturnToLine())

        self.context.holding_package = True


class StateReturnToLine(State):
    def setup(self):
        print("Returning to line")

    def step(self):
        self.context.controller.on_for_distance(
            SpeedRPM(self.context.speed), 100
        )  # TODO: calibrate
        self.context.controller.turn_degrees(SpeedRPM(self.context.speed), 180)

        self.context.set_state(StateReturnToIntersection())


class StateReturnToIntersection(State):
    def setup(self):
        print("Returning to intersection")
        # self.follower = LineFollower(self._context)

    def step(self):
        diff, right_val, left_val = self.context.sense_line()
        self.follower.step(diff)

        if right_val < 15 and left_val < 15:
            self.context.set_state(StateExitIntersection())


"""
class StateReturnToIntersection(State):
    def setup(self):
        print("Returning to intersection (odometry)")

    def step(self):
        self.context.controller.on_to_coordinates(
            SpeedRPM(self.context.speed), 0, 200 # TODO: calibrate
        )
        self.context.controller.turn_to_angle(
            SpeedRPM(self.context.speed), 90 # TODO: calibrate
        )
        self.context.set_state(StateFollowing())
"""


class StateExitIntersection(State):
    def setup(self):
        print("Exiting intersection")

    def step(self):
        """
        diff, _, _ = self.context.sense_line()

        if self.context.branch_right:
            self.context.set_speed(self.context.speed, 100)
        else:
            self.context.set_speed(self.context.speed, -100)

        if diff > 20:
            self.context.set_state(StateFollowing())
        """
        self.context.controller.on_for_distance(
            SpeedRPM(self.context.speed), self.context.sensor_offset
        )
        if self.context.branch_right:
            self.context.controller.turn_degrees(SpeedRPM(self.context.speed), 90)
        else:
            self.context.controller.turn_degrees(SpeedRPM(self.context.speed), -90)

        self.context.set_state(StateFollowing(100))


class StateDropPackage(State):
    def setup(self):
        print("Dropping package")

    def step(self):
        self.context.controller.on_for_distance(
            SpeedRPM(self.context.speed), 10
        )  # TODO: calibrate

        self.context.forklift_motor.on_for_rotations(SpeedRPM(40), -1)
        self.context.set_state(StateFinish())


class StateFinish(State):
    def setup(self):
        print("Finished!")

    def step(self):
        self.context.controller.on_for_distance(
            SpeedRPM(self.context.speed), -100
        )  # TODO: calibrate

        self.context.controller.turn_degrees(SpeedRPM(self.context.speed), 180)

        self.context.sound.tone([(659, 100, 100), (659, 100, 100), (659, 100, 100)])

        for i in range(3):
            self.context.forklift_motor.on_for_rotations(SpeedRPM(40), 1)
            self.context.forklift_motor.on_for_rotations(SpeedRPM(40), -1)

        self.context.set_state(StateIdle())


if __name__ == "__main__":
    vehicle = Vehicle()
    vehicle.run()
