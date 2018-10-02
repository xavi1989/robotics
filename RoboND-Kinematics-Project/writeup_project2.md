## Project: Kinematics Pick & Place
### Writeup Template: You can use this file as a template for your writeup if you want to submit it as a markdown file, but feel free to use some other method and submit a pdf if you prefer.

---


**Steps to complete the project:**  


1. Set up your ROS Workspace.
2. Download or clone the [project repository](https://github.com/udacity/RoboND-Kinematics-Project) into the ***src*** directory of your ROS Workspace.  
3. Experiment with the forward_kinematics environment and get familiar with the robot.
4. Launch in [demo mode](https://classroom.udacity.com/nanodegrees/nd209/parts/7b2fd2d7-e181-401e-977a-6158c77bf816/modules/8855de3f-2897-46c3-a805-628b5ecf045b/lessons/91d017b1-4493-4522-ad52-04a74a01094c/concepts/ae64bb91-e8c4-44c9-adbe-798e8f688193).
5. Perform Kinematic Analysis for the robot following the [project rubric](https://review.udacity.com/#!/rubrics/972/view).
6. Fill in the `IK_server.py` with your Inverse Kinematics code.


[//]: # (Image References)

[image1]: ./misc_images/misc1.png
[image2]: ./misc_images/misc3.png
[image3]: ./misc_images/misc2.png
[image4]: ./misc_images/p2_1.png
[image5]: ./misc_images/P2_2.png
[image6]: ./misc_images/p2_3.png

## [Rubric](https://review.udacity.com/#!/rubrics/972/view) Points
### Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---
### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  

You're reading it!

### Kinematic Analysis
#### 1. Run the forward_kinematics demo and evaluate the kr210.urdf.xacro file to perform kinematic analysis of Kuka KR210 robot and derive its DH parameters.

Run command roslaunch kuka_arm forward_kinematics.launch and here is the screenshot:
![alt text][image1]

From the file kr210.urdf.xacro one can get the following information:

Joint | X | Y | Z | Roll | Pitch | Yaw
--- | --- | ---| --- | --- | --- |---
1  | 0  | 0  | 0.33  | 0  | 0  | 0
2  | 0.35  | 0  | 0.42  | 0  | 0  | 0
3  | 0  | 0  | 1.25  | 0  | 0  | 0
4  | 0.96  | 0  | -0.054  | 0  | 0  | 0
5  | 0.54  | 0  | 0.33  | 0  | 0  | 0
6  | 0.193  | 0  | 0.33  | 0  | 0  | 0
G  | 0.11  | 0  | 0.33  | 0  | 0  | 0

Based on the above information, one can derive the DH table as:

Links | alpha(i-1) | a(i-1) | d(i) | theta(i)
--- | --- | --- | --- | ---
0->1 | 0 | 0 | 0.75 | q1
1->2 | - pi/2 | 0.35 | 0 | -pi/2 + q2
2->3 | 0 | 1.25 | 0 | q3
3->4 |  - pi/2 | -0.054 | 1.5 | q4
4->5 | pi/2 | 0 | 0 | q5
5->6 | - pi/2 | 0 | 0 | q6
6->G | 0 | 0 | 0.303 | 0

#### 2. Using the DH parameter table you derived earlier, create individual transformation matrices about each joint. In addition, also generate a generalized homogeneous transform between base_link and gripper_link using only end-effector(gripper) pose.

The transformation from frame i-1 to i by using the DH parameter is given as:
```python
  T = [[cos(theta) ,             -sin(theta),              0,          a],
       [sin(theta) * cos(alpha), cos(theta) * cos(alpha), -sin(alpha), -sin(alpha) * d],
       [sin(theta) * sin(alpha), cos(theta) * sin(alpha),   cos(alpha), cos(alpha) * d],
       [0, 0, 0, 1]]
```
Substitue with the value in DH table,
```python
  T0_1 = [[cos(q1), -sin(q1), 0, 0],
          [sin(q1),  cos(q1), 0, 0],
          [0,        0,       1, 0.75],
          [0,        0,       0, 1]]

  T1_2 = [[sin(q2),  cos(q2),  0, 0.35],
          [0,        0,        1, 0],
          [cos(q2),  -sin(q2), 0, 0],
          [0,        0,        0, 1]]

  T2_3 = [[cos(q3), -sin(q3), 0, 1.25],
          [sin(q3),  cos(q3), 0, 0],
          [0,        0,       1, 0],
          [0,        0,       0, 1]]

  T3_4 = [[cos(q4), -sin(q4),  0, -0.054],
          [0,        0,        1, 1.5],
          [-sin(q4), -cos(q4), 0, 0],
          [0,        0,        0, 1]]

  T4_5 = [[cos(q5), -sin(q5),  0, 0],
          [0,       0,        -1, 0],
          [sin(q5), cos(q5),   0, 0],
          [0,        0,        0, 1]]

  T5_6 = [[cos(q6), -sin(q6),  0, 0],
          [0,        0,        1, 0],
          [-sin(q6), -cos(q6), 0, 0],
          [0,        0,        0, 1]]

  T6_G = [[1, 0, 0, 0],
          [0, 1, 0, 0],
          [0, 0, 1, 0.303],
          [0, 0, 0, 1]]
```
The frame G and the frame gripper_link, there is one extra rotation which is achieved by rotate around Z axis for 180 degrees and then rotate around Y axis for -90 degrees:
```python
  TG_g = Ry(-pi/2) * Rz(pi)
       = [[0, 0, 1],
          [0, -1, 0],
          [1, 0, 0]]  
```
So the homogeneous transform between base_link and gripper_link is given as
```python
  T0_g = T0_1 * T1_2 * T2_3 * T3_4 * T4_5 * T5_6 * T6_G * TG_g
```

#### 3. Decouple Inverse Kinematics problem into Inverse Position Kinematics and inverse Orientation Kinematics; doing so derive the equations to calculate all individual joint angles.

And here's where you can draw out and show your math for the derivation of your theta angles.

![alt text][image4]

As shown in the following figure, view the arm from the top and we can get the projection view on the x-y plane.
```python
  q1 = atan2(Py, Px)
```

Next we will try to calculate q2 and q3 by projecting the view to the x1-z1 plane in the frame 1.

![alt text][image5]

```python
  angle(q3) = angle(O2_O3_WC) - angle(P0_O3_WC)
  cos(angle(O2_O3_WC)) = (d(O2_O3)^2 + d(O3_WC)^2 - d(O2_WC)^2) / 2*d(O2_O3)*d(O3_WC)
  where d(O2_O3) = a2
        d(O3_WC) = sqrt(d4^2 + a3^2)
        d(O2_WC) = sqrt(((Px1 - a1)^2 + Pz1^2))

  angle(q2) = pi/2 - angle(O3_O2_WC) - angle(WC_O2_X1)
  cos(angle(O3_O2_WC)) = (d(O2_O3)^2 + d(O2_WC)^2 - d(O3_WC)^2) / 2 * d(O2_O3) * d(O2_WC)

  q21 = atan2(Pz1, Px1 - a1)
```
Next we calculate q4, q5, q6
```python
  T3_6 = inv(T0_3) * T0_6 = [[r11, r12, r13, k1],
                             [r21, r22, r23, k2],
                             [r31, r32, r33, k3],
                             [0,   0,   0,   1]]
  T3_6 = T3_4 * T4_5 * T5_6
  by comparing the two equations, we can have:
  q6 = atan2(-r22, r21)
  q4 = atan2(r33, -r13)
  q5 = atan2(sqrt(r21^2 + r22^2), r23)
```

### Project Implementation

#### 1. Fill in the `IK_server.py` file with properly commented python code for calculating Inverse Kinematics based on previously performed Kinematic Analysis. Your code must guide the robot to successfully complete 8/10 pick and place cycles. Briefly discuss the code you implemented and your results.


Here I'll talk about the code, what techniques I used, what worked and why, where the implementation might fail and how I might improve it if I were going to pursue this project further.  

I follow the hints in the IK_server.py.
1. Create symbols
```python
d1, d2, d3, d4, d5, d6, d7 = symbols('d1:8') # link offset
a0, a1, a2, a3, a4, a5, a6 = symbols('a0:7') # link length
alpha0, alpha1, alpha2, alpha3, alpha4, alpha5, alpha6 = symbols('alpha0:7')# twist angle
# Define Joint angle symbols
q1, q2, q3, q4, q5, q6, q7 = symbols('q1:8')
```

2. Create Modified DH parameters
```python
DH_table = {
        alpha0:        0, a0:      0, d1:  0.75, q1: q1,
      alpha1: rad(-90), a1:   0.35, d2:     0, q2: q2-rad(90),
      alpha2:        0, a2:   1.25, d3:     0, q3: q3,
      alpha3: rad(-90), a3: -0.054, d4:  1.50, q4: q4,
      alpha4:  rad(90), a4:      0, d5:     0, q5: q5,
      alpha5: rad(-90), a5:      0, d6:     0, q6: q6,
      alpha6:        0, a6:      0, d7: 0.303, q7: 0}
```

3. Define Modified DH Transformation matrix
```python
def TF_matrix(alpha, a, d, q):
    T = Matrix([[            cos(q),           -sin(q),           0,             a],
          [ sin(q)*cos(alpha), cos(q)*cos(alpha), -sin(alpha), -sin(alpha)*d],
          [ sin(q)*sin(alpha), cos(q)*sin(alpha),  cos(alpha),  cos(alpha)*d],
          [                 0,                 0,           0,             1]])
    return T
```

4. Create individual transformation matrices
```python
T0_1 =  TF_matrix(alpha0, a0, d1, q1).subs(DH_table)
T1_2 =  TF_matrix(alpha1, a1, d2, q2).subs(DH_table)
T2_3 =  TF_matrix(alpha2, a2, d3, q3).subs(DH_table)
T3_4 =  TF_matrix(alpha3, a3, d4, q4).subs(DH_table)
T4_5 =  TF_matrix(alpha4, a4, d5, q5).subs(DH_table)
T5_6 =  TF_matrix(alpha5, a5, d6, q6).subs(DH_table)
T6_G = TF_matrix(alpha6, a6, d7, q7).subs(DH_table)

T0_G = T0_1 * T1_2 * T2_3 * T3_4 * T4_5 * T5_6 * T6_G
# G->g
r, p, y = symbols('r p y')

ROT_x = Matrix([[ 1,            0,       0],
              [ 0,       cos(r), -sin(r)],
              [ 0,       sin(r),  cos(r)]]) # Roll

ROT_y = Matrix([[ cos(p),       0,  sin(p)],
              [      0,       1,       0],
              [-sin(p),       0,  cos(p)]]) # Pitch

ROT_z = Matrix([[ cos(y), -sin(y),       0],
              [ sin(y),  cos(y),       0],
              [      0,       0,       1]]) # Yaw

ROT_gg = ROT_z * ROT_y * ROT_x

# Compensate for rotation discrepancy between DH parameters and Gazebo (URDF)
# More information can be found in KR210 Forward Kinematics section
Rot_Correct = ROT_z.subs(y, radians(180)) * ROT_y.subs(p, radians(-90))

ROT_gg = ROT_gg * Rot_Correct
```

5. For the IK part
```python
ROT_gg = ROT_gg.subs({'r': roll, 'p': pitch, 'y': yaw})

gg = Matrix([[px], [py], [pz]])

WC = gg - 0.303 * ROT_gg[:,2]
# Calculate joint angles using Geometric IK method
theta1 = atan2(WC[1], WC[0])

# theta3
side_O2_O3 = DH_table[a2]
side_O3_WC = sqrt(DH_table[d4] * DH_table[d4] + DH_table[a3] * DH_table[a3])
size_O2_WC = sqrt(pow((sqrt(WC[0] * WC[0] + WC[1] * WC[1]) - DH_table[a1]), 2) + pow(WC[2] - DH_table[d1], 2))

cos_angle_O2_O3_WC = ((side_O2_O3 * side_O2_O3 + side_O3_WC * side_O3_WC - size_O2_WC * size_O2_WC) / (2 * side_O2_O3 * side_O3_WC))
angle_O2_O3_WC = atan2(sqrt(1 - cos_angle_O2_O3_WC * cos_angle_O2_O3_WC), cos_angle_O2_O3_WC)

angle_p0_O3_O4 = atan2(Abs(DH_table[d4]), Abs(DH_table[a3]))

theta3 = -(angle_O2_O3_WC - angle_p0_O3_O4)

#theta2
cos_angle_O3_O2_WC = ((side_O2_O3 * side_O2_O3 + size_O2_WC * size_O2_WC - side_O3_WC * side_O3_WC) / (2 * side_O2_O3 * size_O2_WC))
angle_O3_O2_WC = atan2(sqrt(1 - cos_angle_O3_O2_WC * cos_angle_O3_O2_WC), cos_angle_O3_O2_WC)
angle_WC_O2_X1 = atan2(WC[2] - Abs(DH_table[d1]), sqrt(WC[0] * WC[0] + WC[1] * WC[1]) - Abs(DH_table[a1]))

theta2 = pi/2 - angle_O3_O2_WC - angle_WC_O2_X1

# theta4, 5, 6
R0_3 = T0_1[0:3,0:3] * T1_2[0:3,0:3] * T2_3[0:3,0:3]
R0_3 = R0_3.evalf(subs={q1:theta1, q2:theta2, q3:theta3})
R3_6 = R0_3.T * ROT_gg

# Euler angles from rotation matrix
# More information can be found in the Euler Angles from a Rotation Matrix section
theta4 = atan2(R3_6[2,2], -R3_6[0,2])
theta6 = atan2(-R3_6[1,1], R3_6[1,0])
theta5 = atan2(R3_6[1,0]/cos(theta6), R3_6[1,2])
```
Here is the image of successfully pick the target and put into the bin:
![alt text][image6]
