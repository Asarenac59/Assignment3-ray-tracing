"""
    File name: tessel.py
    Author: Alex Sarenac
    Date created: 03/14/2022
    Date last modified: 03/18/2022
    Python Version: 3.8

    Class tessel.py creates convex polygons from the graphical scene, and calculates the color shade to fill the polygons in the plane. tessel.py implements
    getter methods from lightSource.py  to find the light intensity, object color values, and position of lightSource.py objects to aid in computation
"""

import numpy as np
from matrix import matrix


class tessel:

    def __init__(self, objectList, camera, light):
        EPSILON = 0.001
        self.__faceList = []                    # Create an empty list of faces. This is an instance variable for this class
        pointList = []                          # List of points for a face

        Lv = camera.worldToViewingCoordinates(light.getPosition())          # Transform the position of the light into viewing coordinates (use method worldToViewingCoordinates from class cameraMatrix)
        lightIntensity = light.getIntensity()                                           # Get light intensity values, via getter method

        for object in objectList:                                           # loop thru each object
            c = object.getColor()                                           # Get the object color
            u = object.getURange()[0]                                       # u becomes the start value of the u-parameter range for the object

            while u + object.getUVDelta()[0] < object.getURange()[1] + EPSILON:         # While u + the delta u of the object is smaller than the final value of the u-parameter range + EPSILON:
                v = object.getVRange()[0]                                               # v become the start value of the v-parameter range for the object
                while v + object.getUVDelta()[1] < object.getVRange()[1] + EPSILON:     # While v + the delta v of the object is smaller than the final value of the v-parameter range + EPSILON:

                    # surface points into viewing coordinates:
                    # Gets object point at (u,v), (u, v + delta v), (u + delta u, v + delta v), and (u + delta u, v)
                    p1 = object.getT() * object.getPoint(u, v)
                    p2 = object.getT() * object.getPoint(u, v + object.getUVDelta()[1])
                    p3 = object.getT() * object.getPoint(u + object.getUVDelta()[0], v + object.getUVDelta()[1])
                    p4 = object.getT() * object.getPoint(u + object.getUVDelta()[0], v)

                    # Append these points (respecting the order) to the list of face points
                    pointList.append(camera.worldToViewingCoordinates(p1))
                    pointList.append(camera.worldToViewingCoordinates(p2))
                    pointList.append(camera.worldToViewingCoordinates(p3))
                    pointList.append(camera.worldToViewingCoordinates(p4))

                    # Make sure we don't render any face with one or more points behind the near plane in the following way:
                    # Compute the minimum Z-coordinate from the face points

                    if not self.__minCoordinate(pointList, 2) > -camera.getNp():                                        # If this minimum Z-value is not greater than -(Near Plane) (so the face is not behind the near plane):
                        C = self.__centroid(pointList)                                                                  # Compute the centroid point of the face points
                        N = self.__vectorNormal(pointList)                                                              # Compute the normal vector of the face, normalized

                        if not self.__backFace(C, N):                                                                   # Compute face shading, excluding back faces (normal vector pointing away from camera) in the following way:
                            S = self.__vectorToLightSource(Lv,C)                                            # Find vector from centroid to light source, S is the vector from face centroid to light source, normalized
                            R = self.__vectorSpecular(S,N)                                                  # Find specular reflection vector#R is the vector of specular reflection
                            V = self.__vectorToEye(C)                                                       # Find vector from origin of viewing coordinates to surface centroid#V is the vector from the face centroid to the origin of viewing coordinates

                            colorIndex = self.__colorIndex(object, N, S, R, V)               # Compute color index
                            faceColor = (int(c[0] * lightIntensity[0] * colorIndex), int(c[1] * lightIntensity[1] * colorIndex), int(c[2] * lightIntensity[2] * colorIndex))            # Obtain face color (in the RGB 3-color channels, integer values) as a tuple:

                            pixelfaceList = []

                            for point in pointList:  # For each face point:
                                pixelfaceList.append(camera.viewingToPixelCoordinates(point))                                       #Transform point into 2D pixel coordinates and append to a pixel face point list
                            self.__faceList.append((camera.viewingToPixelCoordinates(C).get(2, 0), pixelfaceList, faceColor))       # Add face attributes to faceList with pseudo-depth

                    pointList = []                                                                                                  # Re-initialize the list of face points to empty
                    v += object.getUVDelta()[1]      # v become v + delta v
                u += object.getUVDelta()[0]          # u becomes u + delta u

    def __minCoordinate(self, facePoints, coord):
        # Computes the minimum X, Y, or Z coordinate from a list of 3D points
        # Coord = 0 indicates minimum X coord, 1 indicates minimum Y coord, 2 indicates minimum Z coord.
        min = facePoints[0].get(coord, 0)
        for point in facePoints:
            if point.get(coord, 0) < min:
                min = point.get(coord, 0)
        return min

    def __backFace(self, C, N):
        # Computes if a face is a back face with using the dot product of the face centroid with the face normal vector
        return C.dotProduct(N) > 0.0

    def __centroid(self, pointList):
        # Computes the centroid point of a face by averaging the points of the face
        sum = matrix(np.zeros((4, 1)))
        for point in pointList:
            sum += point
        return sum.scalarMultiply(1.0 / float(len(pointList)))

    def __vectorNormal(self, pointList):
        # Computes the normalized vector normal to a face with the cross product
        U = (pointList[3] - pointList[1]).removeRow(3).normalize()
        V = (pointList[2] - pointList[0]).removeRow(3).normalize()
        return U.crossProduct(V).normalize().insertRow(3, 0.0)

    def __vectorToLightSource(self, L, C):
        return (L.removeRow(3) - C.removeRow(3)).normalize().insertRow(3, 0.0)

    def __vectorSpecular(self, S, N):
        return S.scalarMultiply(-1.0) + N.scalarMultiply(2.0 * (S.dotProduct(N)))

    def __vectorToEye(self, C):
        return C.removeRow(3).scalarMultiply(-1.0).normalize().insertRow(3, 0.0)

    def __colorIndex(self, object, N, S, R, V):
        # Computes local components of shading
        Id = max(N.dotProduct(S), 0.0)
        Is = max(R.dotProduct(V), 0.0)
        r = object.getReflectance()
        index = r[0] + r[1] * Id + r[2] * Is ** r[3]
        return index

    def getFaceList(self):
        return self.__faceList
