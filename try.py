import cv2 
import numpy as np

model_points = [[  0.  ,  0.,    0. ],
 [  0. , -63.6 ,-12.5],
 [-43.3 , 32.7 ,-26. ],
 [ 43.3 , 32.7 ,-26. ],
 [-28.9 ,-28.9 ,-24.1],
 [ 28.9 ,-28.9, -24.1]] 

image_points = [[444. ,180.],
 [450., 295.],
 [507., 142.],
 [388., 148.],
 [487., 236.],
 [409., 238.]] 

camera_matrix = [[960. ,  0., 480.],
 [  0. ,960. ,270.],
 [  0. ,  0. ,  1.]]

dist_coeffs = np.zeros((4, 1))  # Assuming no lens distortion
(success, rotation_vector, translation_vector) = cv2.solvePnP(model_points, image_points, camera_matrix,
                                                                dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)