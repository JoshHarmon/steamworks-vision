"""
2017 Steamworks vision code for Team 2811 (StormBots)
"""

import cv2
import numpy as np
from grip import GripPipeline
from networktables import NetworkTables
import logging

import time
import sys


def main():

    bad_data = False

    cam = cv2.VideoCapture(0)
    grip = GripPipeline()

    ##NetworkTables.initialize(server='roboRIO-2811-FRC.local')

    ##table = NetworkTables.getTable("contourData")

    while True:
        start_time = time.time()
        ret_val, img = cam.read()
        contours = False

        if ret_val:
            grip.process(img)
            bad_data = False

            contours = grip.filter_contours_output

            dArr = []

            for i in range(len(contours)):

                moments1 = cv2.moments(contours[i])

                cx = int(moments1['m10']/moments1['m00'])
                cy = int(moments1['m01']/moments1['m00'])

                area = cv2.contourArea(contours[i])

                dArr.append([i, cx, cy, area])

            dArr.sort(key=lambda x: x[3], reverse=True)

            ## dArr = [[1, 419, 140, 11317.0], [0, 215, 142, 10963.0], [2, 550, 300, 12000.0], [4, 650, 200, 8491.0], [5, 200, 100, 7540.0]]

            ##print(dArr)
            
            ## Traits: Group Height, dTop, LEdge, Width ratio, Height ratio

            traitAnalysisArr = []

            for i in range(len(dArr) - 1): ## range stops before the length, so this stays in bounds
                ##print('outer idx is', i, ' with list length of', len(dArr))
                for j in range(i + 1, len(dArr)):
                    ##print('inner idx is', j, ' with list length of', len(dArr))

                    ## The non-2 values should represent the top target (as we sort dArr by area and the top target is bigger)
                    ## The -2 values, logically, represent the bottom target rect values
                    ##print('getting rect i for idx', dArr[i][0], 'of contours list with max idx of', (len(contours) - 1))
                    x,y,w,h = cv2.boundingRect(contours[dArr[i][0]])  ## dArr[i][0] represents the true i-value of the contour
                    ##print('getting rect j for idx', dArr[j][0], 'of contours list with max idx of', (len(contours) - 1))
                    x2,y2,w2,h2 = cv2.boundingRect(contours[dArr[j][0]])

                    ##groupHeightTestValue = (h/((y2+h2-y)*.4)) ## Top target ~ 40% total cluster height

                    ##dTopTestValue = abs((y2 - y)/(((y2 + h2) - y)*0.6)) ## Top of bot to top of top ~ 60% total cluster height

                    ## See how well the left edges of the targets line up
                    lEdgeTestValue = abs((((x - x2) / w) + 1))

                    ## Note that these ratios are not safe until we've
                    ## iterated based on greatest-least area... this may
                    ## involve getting i from (sorted) dArr and fetching that i from
                    ## the contours list
                    widthCompareTestValue = abs((w / w2)) ## Widths should be about the same
                    heightCompareTestValue = abs((h / (2*h2))) ## Top should be about twice as tall as bottom

                    areaCompareValue = abs(((w * h) / (w2 * h2)) - 2) ## .5 or (2) (need to force one later)

                    totalTestScore = lEdgeTestValue + widthCompareTestValue + heightCompareTestValue + areaCompareValue

                    traitAnalysisArr.append([i, j, totalTestScore])
            
            ## end traits loop
            bestIdx = 0
            bestScore = sys.maxsize

            for i in range(len(traitAnalysisArr)):
                if (traitAnalysisArr[i][2] < bestScore):
                    bestIdx = i
                    bestScore = traitAnalysisArr[i][2]
            print('Best score: pair', traitAnalysisArr[i], 'with a score of', traitAnalysisArr[i][2])

            ##table.putNumberArray("coordinates", dArr[0][1:]) ## cx and cy pushed to NT
        else:
            bad_data = True
        end_time = time.time()

        ##print((end_time - start_time) * 1000)

'''
Conditions for boiler targeting
len(contours) >= 2
two targets_vertically_stacked


'''

'''
Conditions for gear peg targeting
len(contours) >= 2    (3 if one is split by the peg)

if split, targets_vertically_stacked for one of the physical targets ( two contours )


'''


def targets_horizontally_stacked(contour1, contour2):
    moments1 = cv2.moments(contour1)
    moments2 = cv2.moments(contour2)

    cy1 = int(moments1['m01']/moments1['m00'])
    cy2 = int(moments2['m01']/moments2['m00'])

    return abs(cy1 - cy2) < 12

def targets_vertically_stacked(contour1, contour2):
    moments1 = cv2.moments(contour1)
    moments2 = cv2.moments(contour2)

    cx1 = int(moments1['m10']/moments1['m00'])
    cx2 = int(moments2['m10']/moments2['m00'])

    return abs(cx1 - cx2) < 12



'''
def get_cx(contour):
    moments = cv2.moments(contour)
    return int(moments['m10']/moments['m00'])

def get_cy(contour):
    moments = cv2.moments(contour2)
    return int(moments['m01']/moments['m00'])

def filter_cy(contour):
    cy = get_cy(contour)
    return cy > (0.9 * 640) || cy < (0.1 * 640)

def filter_cx(contour):
    cx = get_cx(contour)
    return cx > (0.9 * 360) || cx < (0.1 * 360)

def center_score(contour):
    cx = get_cx(contour)
    cy = get_cy(contour)

    # TODO: May sqrt this (max value then would be ~367 -- currently ~134000)
    return 100000 - ((cx - 320) ** 2 + (cy - 180) ** 2)

def proximity_score(idx, contours):
    length = len(contours)
    contour = contours[idx]
    scores_array = np.zeros(length, length)

    for (i = 0; i < length; i++):
        for (j = i + 1; j < length; j++):
            scores_array[i][j] = sqrt(
'''
if __name__ == '__main__':
	main()
