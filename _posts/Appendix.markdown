---
layout: post
title: "Appendix"
date: 2024-08-3 12:00:00 -0700
categories: chapter
---

# Appendix

## Sample Team Contract

### Team Name: _______________________

### Team Members:
1. _______________________
2. _______________________
3. _______________________
4. _______________________
5. _______________________
6. _______________________

### Coach/Mentor: _______________________

### Purpose
This contract outlines the expectations and responsibilities of each team member to ensure a productive and enjoyable experience in the FIRST LEGO League (FLL) program.

### Responsibilities
1. **Attendance**: Attend all team meetings and practices, unless excused by the coach or mentor.
2. **Participation**: Actively participate in all team activities, including brainstorming sessions, building, programming, and presentations.
3. **Respect**: Treat all team members, coaches, mentors, and competitors with respect and courtesy.
4. **Teamwork**: Collaborate effectively with team members, valuing each person's contributions and working towards common goals.
5. **Core Values**: Uphold the FLL Core Values of discovery, innovation, impact, inclusion, teamwork, and fun.
6. **Commitment**: Dedicate the necessary time and effort to complete tasks and meet team goals.

### Agreement
By signing this contract, each team member agrees to abide by the responsibilities outlined above.

**Team Member Signatures:**
- _______________________
- _______________________
- _______________________
- _______________________
- _______________________
- _______________________

**Coach/Mentor Signature:**
- _______________________

## Grant Proposal Template

### Title: Request for Funding for FIRST LEGO League Team

### Introduction
Our team, [Team Name], is a dedicated group of students participating in the FIRST LEGO League (FLL) program. We are seeking funding to support our efforts in building a robot, conducting research for our Innovation Project, and participating in competitions.

### Team Overview
- **Team Name**: [Team Name]
- **Number of Members**: [Number of Members]
- **School/Organization**: [School/Organization Name]
- **Coach/Mentor**: [Coach/Mentor Name]

### Project Description
- **Robot Game**: We will design, build, and program a robot to complete specific missions on a themed playing field.
- **Innovation Project**: We will identify a real-world problem, research and develop an innovative solution, and present our findings.

### Budget
| Item                      | Cost          |
|---------------------------|---------------|
| LEGO Mindstorms Kit       | $[Amount]     |
| Competition Registration  | $[Amount]     |
| Field Setup Kit           | $[Amount]     |
| Travel Expenses           | $[Amount]     |
| Miscellaneous Supplies    | $[Amount]     |
| Total                     | $[Total Amount]|

### Request
We respectfully request funding in the amount of $[Amount] to support our team's participation in the FLL program. Your contribution will help us cover the costs outlined above and ensure a successful and enriching experience for our team members.

### Conclusion
Thank you for considering our request. Your support will make a significant impact on our team's ability to learn, innovate, and compete in the FIRST LEGO League.

### Contact Information
- **Team Name**: [Team Name]
- **Coach/Mentor**: [Coach/Mentor Name]
- **Email**: [Email Address]
- **Phone**: [Phone Number]

## Sample Robot Design and Code

### Robot Design

**Robot Name**: [Robot Name]

**Design Overview**:
- **Chassis**: Built using LEGO Technic beams for a sturdy base.
- **Wheels**: Equipped with large wheels for better traction and maneuverability.
- **Sensors**: Includes ultrasonic, color, and touch sensors for navigation and task completion.
- **Motors**: Two large motors for driving and one medium motor for operating attachments.

**Attachments**:
- **Arm**: A modular arm designed to lift and move objects.
- **Gripper**: A gripper mechanism for picking up and releasing items.

### Sample Code (EV3)

```python
import ev3dev.ev3 as ev3
from time import sleep

# Initialize motors and sensors
left_motor = ev3.LargeMotor('outB')
right_motor = ev3.LargeMotor('outC')
arm_motor = ev3.MediumMotor('outA')
ultrasonic_sensor = ev3.UltrasonicSensor()
color_sensor = ev3.ColorSensor()

# Function to move forward
def move_forward(seconds):
    left_motor.run_timed(time_sp=seconds * 1000, speed_sp=500)
    right_motor.run_timed(time_sp=seconds * 1000, speed_sp=500)
    left_motor.wait_while('running')
    right_motor.wait_while('running')

# Function to stop
def stop():
    left_motor.stop(stop_action="brake")
    right_motor.stop(stop_action="brake")

# Main program
move_forward(2)
stop()

====================================== Sample Code (Spike Prime) ===============
import hub
import motor
from utime import sleep

# Initialize motors
left_motor = motor.Motor('A')
right_motor = motor.Motor('B')
arm_motor = motor.Motor('C')

# Function to move forward
def move_forward(seconds):
    left_motor.run_for_seconds(seconds, 50)
    right_motor.run_for_seconds(seconds, 50)

# Function to stop
def stop():
    left_motor.stop()
    right_motor.stop()

# Main program
move_forward(2)
stop()
