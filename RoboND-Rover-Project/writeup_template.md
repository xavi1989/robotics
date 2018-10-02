## Project: Search and Sample Return
### Writeup Template: You can use this file as a template for your writeup if you want to submit it as a markdown file, but feel free to use some other method and submit a pdf if you prefer.

---


**The goals / steps of this project are the following:**  

**Training / Calibration**  

* Download the simulator and take data in "Training Mode"
* Test out the functions in the Jupyter Notebook provided
* Add functions to detect obstacles and samples of interest (golden rocks)
* Fill in the `process_image()` function with the appropriate image processing steps (perspective transform, color threshold etc.) to get from raw images to a map.  The `output_image` you create in this step should demonstrate that your mapping pipeline works.
* Use `moviepy` to process the images in your saved dataset with the `process_image()` function.  Include the video you produce as part of your submission.

**Autonomous Navigation / Mapping**

* Fill in the `perception_step()` function within the `perception.py` script with the appropriate image processing functions to create a map and update `Rover()` data (similar to what you did with `process_image()` in the notebook).
* Fill in the `decision_step()` function within the `decision.py` script with conditional statements that take into consideration the outputs of the `perception_step()` in deciding how to issue throttle, brake and steering commands.
* Iterate on your perception and decision function until your rover does a reasonable (need to define metric) job of navigating and mapping.  

[//]: # (Image References)

[image1]: ./output/rock_map.png

## [Rubric](https://review.udacity.com/#!/rubrics/916/view) Points
### Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---
### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  

You're reading it!

### Notebook Analysis
#### 1. Run the functions provided in the notebook on test images (first with the test data provided, next on data you have recorded). Add/modify functions to allow for color selection of obstacles and rock samples.

I refer to the demo video https://www.youtube.com/watch?v=oJA6QHDPdQw for some basic ideas.

Obstacles is the reverse map of terrain, which means where the area is not for terrain, then these areas are for obstacles. In order to make it more accurate, I introduce the field of view map, which is the maximum view that the camera can see. Here is the sample code
```python
warped, fov_mask = perspect_transform(img, source, destination)
threshed = color_thresh(warped) #terrain map
o_map = np.absolute(np.float32(threshed) - 1) * fov_mask
```

Rock map is generated based on the color of the rock, here we choose color (110, 110, 50) as threshold.

```python
def find_rocks(img, levels = (110, 110, 50)):
    rockpix = (img[:,:,0] > levels[0]) \
                & (img[:,:,1] > levels[1]) \
                & (img[:,:,2] < levels[2])

    color_select = np.zeros_like(img[:, :, 0])
    color_select[rockpix] = 1

    return color_select
```

Here is an example of the rock map:

![alt text][image1]

#### 1. Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result.
I will explain the code in process_image() based on the processing steps.
1. Define source and destination points for perspective transform
The source and destination points have already been defined in the above section in the notebook.

2. Apply perspective transform
apply perspective transform to the input image. It will convert the source 4 points to 4 points of a square.
```python
warped, fov_mask = perspect_transform(img, source, destination)
```
3. Apply color threshold
terrain map
```python
threshed = color_thresh(warped)
```
obstacle map
```python
o_map = np.absolute(np.float32(threshed) - 1) * fov_mask
```
rock map
```python
rock_map = find_rocks(warped, levels=(110, 110, 50))
```

4. Convert image pixel values to rover-centric coords
rover coords for terrain pixels
```python
xpix, ypix = rover_coords(threshed)
```
rover coords for obstacle pixels
```python
xpix_obstacle, ypix_obstacle = rover_coords(o_map)
```
rover coords for rock pixels
```python
xpix_rock, ypix_rock = rover_coords(rock_map)
```
5. Convert rover-centric pixel values to world coords
Use rover coords of terrain as example
```python
  world_size = data.worldmap.shape[0]
  scale = 2 * dst_size
  xpos = data.xpos[data.count]
  ypos = data.ypos[data.count]
  yaw = data.yaw[data.count]
  x_world, y_world = pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale)
```
6. Update worldmap
Update the obstacle pixels in the red channel, update the terrain in the blue channel and update rock to be white color.

```python
# terrain
data.worldmap[y_world, x_world, 2] = 255

#obstacle
data.worldmap[y_world_obstacle, x_world_obstacle, 0] = 255

#rock
data.worldmap[y_world_rock, x_world_rock, :] = 255
```

### Autonomous Navigation and Mapping

#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.
`perception_step()` is almost the same steps as in the `process_image` except for the following two items:
1. Instead of updating to the data.worldmap, here updates to Rover.worldmap
```python
Rover.worldmap[y_world, x_world, 2] += 10
Rover.worldmap[y_world_obstacle, x_world_obstacle, 0] += 1
Rover.worldmap[rock_ycen, rock_xcen, 1] = 255
```
2. Calculate the steer angles
```python
dist, angles = to_polar_coords(xpix, ypix)
Rover.nav_angles = angles
```

#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  

**Note: running the simulator with different choices of resolution and graphics quality may produce different results, particularly on different machines!  Make a note of your simulator settings (resolution and graphics quality set on launch) and frames per second (FPS output to terminal by `drive_rover.py`) in your writeup when you submit the project so your reviewer can reproduce your results.**

I run the simulation with 640x480 with good graphic quality.
When I launch the simulation, I notice that:
1. The Rover may go circle in the map and not cover the whole map.
2. If there is obstacles in front of the Rover and terrain in the right and left, the Rover may just hit the obstacles and stuck there.
In order to tackle these two items, I introduce some parameters
```python
 right_space = np.sum(Rover.nav_angles <= 0)
 left_space = np.sum(Rover.nav_angles > 0)
 front_space = np.sum(Rover.nav_angles < 0.5) + np.sum(Rover.nav_angles > -0.5)
```
Right_space means the number of terrain in the Rover's right hand. Left_space means the number of terrain in the Rover's left hand. Front_space means the number of terrain in the Rover's front hand.
In order to solve the first item, I set a condition on the right_space. If the right_space is smaller to some threshold, the Rover will turn left, which will set the Rover perfer to turn left than right, here is the example code
```python
steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
if right_space <= Rover.stop_forward / 3:
    Rover.steer = np.clip(steer, 0, 15)
else:
    Rover.steer = np.clip(steer, -15, 0)
```

In order to cover the second item, I set condition on the front_space, if the front space is smaller than a threshold, then I set the Rover state from 'forward' to 'stop'.

In the furture, if I have more time to spend on this project, we can try to improve the techniques to identify the terrain, obstacle and rock.
