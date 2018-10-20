## Project: Perception Pick & Place
---
[image1]: cf_matrix.png
[image2]: test1_result.png
[image3]: test2_result.png
[image4]: test3_result.png

### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  

You're reading it!

### Exercise 1, 2 and 3 pipeline implemented
#### 1. Complete Exercise 1 steps. Pipeline for filtering and RANSAC plane fitting implemented.
I implement the pipeline by following the hints in the file and the implementation is shown as follows:
1. Convert ROS msg to PCL data

```Python
# Convert ROS msg to PCL data
cloud = ros_to_pcl(pcl_msg)
```

2. Apply statistical outlier Filtering

```python
# Statistical Outlier Filtering
outlier_filter = cloud.make_statistical_outlier_filter()

# Set the number of neighboring points to analyze for any given point
outlier_filter.set_mean_k(8)

# Any point with a mean distance larger than global
# (mean_distance + 0.3 *std_dev) will be considered outlier
outlier_filter.set_std_dev_mul_thresh(0.3)
cloud = outlier_filter.filter()
```

3. Apply voxel grid down sample Filtering

```python
# Voxel Grid filter
vox = cloud.make_voxel_grid_filter()

# Define leaf size
LEAF_SIZE = 0.005

# Set the voxel (or leaf) size
vox.set_leaf_size(LEAF_SIZE, LEAF_SIZE, LEAF_SIZE)

# Call the filter function to obtain the resultant downsampled point cloud
cloud_filtered = vox.filter()
```

4. Apply passthrought filter

```python
# PassThrough filter 0.6 < z < 1.1
pz = cloud_filtered.make_passthrough_filter()
pz.set_filter_field_name('z')
pz.set_filter_limits(0.6, 1.1)
cloud_filtered = pz.filter()

# PassThrough filter 0.34 < x < 1.0
px = cloud_filtered.make_passthrough_filter()
px.set_filter_field_name('x')
px.set_filter_limits(0.34, 1.0)
cloud_filtered = px.filter()
```

5. Apply RANSAC to get table and all the rest objects

```python
# RANSAC plane segmentation
seg = cloud_filtered.make_segmenter()
seg.set_model_type(pcl.SACMODEL_PLANE)
seg.set_method_type(pcl.SAC_RANSAC)

# Max distance for a point to be considered fitting the model
max_distance = 0.01
seg.set_distance_threshold(max_distance)

# Obtain set of inlier indices and model coefficients
inliers, coefficients = seg.segment()

# Extract inliers
cloud_table = cloud_filtered.extract(inliers, negative=False)

# Extract outliers
cloud_objects = cloud_filtered.extract(inliers, negative=True)
```

#### 2. Complete Exercise 2 steps: Pipeline including clustering for segmentation implemented.  
1. Apply clustering for segmentation

```python
# Euclidean Clustering
white_cloud = XYZRGB_to_XYZ(cloud_objects)
tree = white_cloud.make_kdtree()

# Create a cluster extraction object
ec = white_cloud.make_EuclideanClusterExtraction()

# Set tolerances for distance threshold
# as well as minimum and maximum cluster size (in points)
ec.set_ClusterTolerance(0.02)
ec.set_MinClusterSize(40)
ec.set_MaxClusterSize(4000)

# Search the k-d tree for clusters
ec.set_SearchMethod(tree)

# Extract indices for each of the discovered clusters
cluster_indices = ec.Extract()
```
#### 2. Complete Exercise 3 Steps.  Features extracted and SVM trained.  Object recognition implemented.
1. Calculate the color histogram and normal histogram

I use nbins = 32 for both color histogram and normal histogram. I use [0, 255] for color histogram range and [-1, 1] for normal histogram range.

2. Run the script to extract the features

3. train the SVM model

The confusion matrix that I get is shown as follows, I use 50 number of images per object.
![alt text][image1]


### Pick and Place Setup

#### 1. For all three tabletop setups (`test*.world`), perform object recognition, then read in respective pick list (`pick_list_*.yaml`). Next construct the messages that would comprise a valid `PickPlace` request output them to `.yaml` format.

1. test1.world

Detect 3 out of 3 object
![alt text][image2]
The corresponding yaml file is zip in the same folder.

2. test2.world
Detect 5 out of 5 objects
![alt text][image3]
The corresponding yaml file is zip in the same folder.

3. test3.world
Detect 8 out of 8 objects
![alt text][image4]
The corresponding yaml file is zip in the same folder.
