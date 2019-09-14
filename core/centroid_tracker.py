# import the necessary packages
from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np
import config
from enum import Enum
import copy


class Region(Enum):
    Init = 0
    Left = 1
    Middle = 2
    Right = 3


class PersonState(Enum):
    Init = 0            # initial state
    Left = 1            # the centroid is on the left region
    Right = 2           # the centroid is on the middle region
    LeftToMiddle = 3    # the centroid moved from left region to the middle region
    RightToMiddle = 4   # the centroid moved from right region to the middle region
    Pass = 5            # the centroid passed from right to left or from left to right


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class TrackingObject:
    def __init__(self, centroid):
        self.tracking_frame_count = 0
        self.lost_frame_count = 0
        self.class_id = -1
        self.footprints = [centroid]
        self.centroid = centroid
        self.is_lost = False
        self.counted = False
        self.region = Region.Init

        self.state = PersonState.Init
        self.state_trans = {
            PersonState.Init: {
                Region.Left: PersonState.Left,
                Region.Right: PersonState.Right,
            },
            PersonState.Left: {
                Region.Middle: PersonState.LeftToMiddle,
                Region.Right: PersonState.Right,
            },
            PersonState.Right: {
                Region.Left: PersonState.Left,
                Region.Middle: PersonState.RightToMiddle,
            },
            PersonState.LeftToMiddle: {
                Region.Left: PersonState.Left,
                Region.Right: PersonState.Pass,
            },
            PersonState.RightToMiddle: {
                Region.Left: PersonState.Pass,
                Region.Right: PersonState.Right,
            },
            PersonState.Pass: {
                Region.Left: PersonState.Left,
                Region.Right: PersonState.Right,
            },
        }

    def update_centroid(self, centroid):
        self.centroid = centroid
        self.tracking_frame_count += 1
        self.lost_frame_count = 0
        self.is_lost = False
        self.footprints.append(centroid)
        if len(self.footprints) > config.TRACKING_HISTORY:
            self.footprints.pop(0)

        if not self.counted:
            current_resion = Region.Middle
            if centroid.x < config.PASS_COUNT_LEFT_BORDER:
                current_resion = Region.Left
            elif centroid.x > config.PASS_COUNT_RIGHT_BORDER:
                current_resion = Region.Right

            # state transition
            if self.region != current_resion:
                if current_resion in self.state_trans[self.state]:
                    self.state = self.state_trans[self.state][current_resion]
                self.region = current_resion

    def mark_as_counted(self):
        self.counted = True

    def was_counted(self):
        return self.counted

    def passed(self):
        return self.state == PersonState.Pass


class CentroidTracker():
    def __init__(self, lost_count=config.LOST_COUNT):
        # initialize the next unique object ID along with two ordered
        # dictionaries used to keep track of mapping a given object
        # ID to its centroid and number of consecutive frames it has
        # been marked as "disappeared", respectively
        self.nextObjectID = 1
        self.objs = OrderedDict()

        # store the number of maximum consecutive frames a given
        # object is allowed to be marked as "disappeared" until we
        # need to deregister the object from tracking
        self.lost_count = lost_count

    def __update_centroid(self, objectID, centroid):
        if objectID in self.objs:
            self.objs[objectID].update_centroid(centroid)
        else:
            self.objs[objectID] = TrackingObject(centroid)

    def __register(self, centroid):
        # when registering an object we use the next available object
        # ID to store the centroid
        self.__update_centroid(self.nextObjectID, centroid)
        self.nextObjectID += 1

    def __register_all(self, centroids):
        for c in centroids:
            self.__register(c)

    def __ageing(self, objectID):
        if objectID in self.objs:
            self.objs[objectID].lost_frame_count += 1
            self.objs[objectID].is_lost = True

            # check to see if the number of consecutive
            # frames the object has been marked "disappeared"
            # for warrants deregistering the object
            if self.objs[objectID].lost_frame_count > self.lost_count:
                del self.objs[objectID]

    def __ageing_all(self):
        dict_copy = copy.deepcopy(self.objs)
        IDs = dict_copy.keys()

        for objectID in IDs:
            self.__ageing(objectID)

    def ___rects_to_centroids(self, rects):
        centroids = []
        for rect in rects:
            centroids.append(Point(
                int((rect.left + rect.right) / 2.0),
                int((rect.top + rect.bottom) / 2.0)
            ))
        return centroids

    def update(self, rects):
        # If we got no new objects in the frame, just run ageing.
        if len(rects) == 0:
            self.__ageing_all()
        else:
            input_centroids = self.___rects_to_centroids(rects)

            # if we have no tracking objects, register all
            if len(self.objs) == 0:
                self.__register_all(input_centroids)
            else:
                tracking_ids = list(self.objs.keys())

                tracking_centroids = []
                for obj in self.objs.values():
                    tracking_centroids.append(
                        (obj.centroid.x, obj.centroid.y)
                    )

                input_centroids_tupple = []
                for c in input_centroids:
                    input_centroids_tupple.append(
                        (c.x, c.y)
                    )

                dist_matrix = dist.cdist(
                    np.array(tracking_centroids),
                    input_centroids_tupple
                )

                tracking_ids_by_dist = dist_matrix.min(axis=1).argsort()
                input_ids_by_dist = dist_matrix.argmin(axis=1)[tracking_ids_by_dist]
                tracking_ids_checked = set()
                input_ids_checked = set()

                for (tracking_id, in_id) in zip(tracking_ids_by_dist,
                                                input_ids_by_dist):
                    if tracking_id in tracking_ids_checked or in_id in input_ids_checked:
                        continue

                    objectID = tracking_ids[tracking_id]
                    self.__update_centroid(objectID, input_centroids[in_id])

                    tracking_ids_checked.add(tracking_id)
                    input_ids_checked.add(in_id)

                to_age = set(
                    range(0, dist_matrix.shape[0])
                ).difference(tracking_ids_checked)

                for row in to_age:
                    self.__ageing(tracking_ids[row])

                to_register = set(
                    range(0, dist_matrix.shape[1])
                ).difference(input_ids_checked)

                for col in to_register:
                    self.__register(input_centroids[col])

        return self.objs
