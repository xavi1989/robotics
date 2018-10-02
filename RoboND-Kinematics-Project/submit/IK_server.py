#!/usr/bin/env python

# Copyright (C) 2017 Udacity Inc.
#
# This file is part of Robotic Arm: Pick and Place project for Udacity
# Robotics nano-degree program
#
# All Rights Reserved.

# Author: Harsh Pandya

# import modules
import rospy
import tf
from kuka_arm.srv import *
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from geometry_msgs.msg import Pose
from mpmath import *
from sympy import *


def handle_calculate_IK(req):
    rospy.loginfo("Received %s eef-poses from the plan" % len(req.poses))
    if len(req.poses) < 1:
        print "No valid poses received"
        return -1
    else:

        ### Your FK code here
        # Create symbols
	    #
	    #
	    # Create Modified DH parameters
	    #
	    #
	    # Define Modified DH Transformation matrix
	    #
	    #
	    # Create individual transformation matrices
	    #
	    #
	    # Extract rotation matrices from the transformation matrices
	    #
	    #
        ###
        d1, d2, d3, d4, d5, d6, d7 = symbols('d1:8') # link offset
        a0, a1, a2, a3, a4, a5, a6 = symbols('a0:7') # link length
        alpha0, alpha1, alpha2, alpha3, alpha4, alpha5, alpha6 = symbols('alpha0:7')# twist angle	
        # Define Joint angle symbols
        q1, q2, q3, q4, q5, q6, q7 = symbols('q1:8')

        # Create Modified DH parameters
        DH_table = {
                alpha0:        0, a0:      0, d1:  0.75, q1: q1,
	            alpha1: rad(-90), a1:   0.35, d2:     0, q2: q2-rad(90),
	            alpha2:        0, a2:   1.25, d3:     0, q3: q3,
	            alpha3: rad(-90), a3: -0.054, d4:  1.50, q4: q4,
	            alpha4:  rad(90), a4:      0, d5:     0, q5: q5,
	            alpha5: rad(-90), a5:      0, d6:     0, q6: q6,
	            alpha6:        0, a6:      0, d7: 0.303, q7: 0}


        # Define Modified DH Transformation matrix
        def TF_matrix(alpha, a, d, q):
            T = Matrix([[            cos(q),           -sin(q),           0,             a],
	                [ sin(q)*cos(alpha), cos(q)*cos(alpha), -sin(alpha), -sin(alpha)*d],
	                [ sin(q)*sin(alpha), cos(q)*sin(alpha),  cos(alpha),  cos(alpha)*d],
	                [                 0,                 0,           0,             1]])
            return T

        # Create individual transformation matrices
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

        # Initialize service response
        joint_trajectory_list = []
        for x in xrange(0, len(req.poses)):
            # IK code starts here
            joint_trajectory_point = JointTrajectoryPoint()

	        # Extract end-effector position and orientation from request
	        # px,py,pz = end-effector position
	        # roll, pitch, yaw = end-effector orientation
            px = req.poses[x].position.x
            py = req.poses[x].position.y
            pz = req.poses[x].position.z

            (roll, pitch, yaw) = tf.transformations.euler_from_quaternion(
                [req.poses[x].orientation.x, req.poses[x].orientation.y,
                    req.poses[x].orientation.z, req.poses[x].orientation.w])

            ### Your IK code here
	        # Compensate for rotation discrepancy between DH parameters and Gazebo
	        #
	        #
	        # Calculate joint angles using Geometric IK method
	        #
	        #
            ###

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

            # Populate response for the IK request
            # In the next line replace theta1,theta2...,theta6 by your joint angle variables
	    joint_trajectory_point.positions = [theta1, theta2, theta3, theta4, theta5, theta6]
	    joint_trajectory_list.append(joint_trajectory_point)

        rospy.loginfo("length of Joint Trajectory List: %s" % len(joint_trajectory_list))
        return CalculateIKResponse(joint_trajectory_list)


def IK_server():
    # initialize node and declare calculate_ik service
    rospy.init_node('IK_server')
    s = rospy.Service('calculate_ik', CalculateIK, handle_calculate_IK)
    print "Ready to receive an IK request"
    rospy.spin()

if __name__ == "__main__":
    IK_server()
