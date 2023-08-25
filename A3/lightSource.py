"""
    File name: lightSource.py
    Author: Alex Sarenac
    Date created: 03/14/2022
    Date last modified: 03/18/2022
    Python Version: 3.8

   This class implements simple getter and setter methods for a light source object that is used in the tessalation of polygons in tessel.py
"""

import numpy as np
from matrix import matrix


class lightSource:
    """
      constructor sets the original position, color, and intensity values for the lightSource
      @color
      @position
      @intensity
      """
    def __init__(self, position=matrix(np.zeros((4, 1))), color=(0, 0, 0), intensity=(1.0, 1.0, 1.0)):      #RGB values are 1.0 for brightest white
        self.__position = position
        self.__color = color
        self.__intensity = intensity

    def getPosition(self):
        return self.__position

    def getColor(self):
        return self.__color

    def getIntensity(self):
        return self.__intensity

    def setPosition(self, position):
        self.__position = position

    def setColor(self, color):
        self.__color = color

    def setIntensity(self, intensity):
        self.__intensity = intensity
