from turtle import distance
import numpy as np
from scipy.optimize import quadratic_assignment

distance_matrix = np.array([[0,1,0,0],
                   [1,0,0,0],
                   [0,0,0,1],
                   [0,0,1,0]])
print(distance_matrix)


familiarity_matrix = np.array([[0,100,10,0],
                      [100,0,25,0],
                      [10,25,0,1],
                      [0,0,1,0]])

res = quadratic_assignment(distance_matrix,familiarity_matrix,method = '2opt')
print(type(res.col_ind))


