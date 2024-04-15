#!/usr/bin/env python3

from time import sleep

from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, MoveSteering
from ev3dev2.button import Button
from ev3dev2.sensor import INPUT_1
from ev3dev2.sensor.lego import TouchSensor


class Vehicle:
	def __init__(self, speed):
		self.speed = speed
		self.rotation = 0
		self.left_wheel = LargeMotor(OUTPUT_A)
		self.right_wheel = LargeMotor(OUTPUT_D)
		self.steer_pair = MoveSteering(OUTPUT_A, OUTPUT_D, motor_class=LargeMotor)
		self.btn = Button()

	def up(self):
		if (self.speed > -100):
			self.speed -= 1

	def down(self):
		if (self.speed < 100):
			self.speed += 1

	def right(self):
		if (self.rotation < 100):
			self.rotation += 1

	def left(self):
		if (self.rotation > -100):
			self.rotation -= 1

	def enter(self):
		self.steer_pair.on(self.rotation, 0)
		print("Paused")
		while not self.btn.enter:
			continue
		self.steer_pair.on(self.rotation, self.speed)
		print("Unpaused")
	
	def backspace(self):
		self.steer_pair.on(self.rotation, 0)
		print("Exited program")
		exit()
	
	def run(self):
		print("Program started")

		while True:
			if self.btn.up:
				self.up()
			elif self.btn.down:
				self.down()
			elif self.btn.right:
				self.right()
			elif self.btn.left:
				self.left()
			elif self.btn.enter:
				self.enter()
			elif self.btn.backspace:
				self.backspace()
			self.steer_pair.on(self.rotation, self.speed)

			print("Current speed: ", str(self.speed))
			print("Current rotation: ", str(self.rotation))
			sleep(0.01)

    

if __name__ == "__main__":
	vehicle = Vehicle(0)
	vehicle.run()
