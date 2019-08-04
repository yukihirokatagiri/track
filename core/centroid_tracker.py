# original : https://www.pyimagesearch.com/2018/07/23/simple-object-tracking-with-opencv/

# import the necessary packages
from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np
from detection_graph import DetectionObject
import config
from enum import Enum
import copy

class Region(Enum):
	Init = 0
	Left = 1
	Middle = 2
	Right = 3

class PersonState(Enum):
	Init = 0			# initial state
	Left = 1			# the centroid is on the left region
	Right = 2			# the centroid is on the middle region
	LeftToMiddle = 3	# the centroid moved from left region to the middle region
	RightToMiddle = 4	# the centroid moved from right region to the middle region
	Pass = 5			# the centroid passed from right to left or from left to right

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
			PersonState.Init : {
				Region.Left : PersonState.Left,
				Region.Right : PersonState.Right,
			},
			PersonState.Left : {
				Region.Middle : PersonState.LeftToMiddle,
				Region.Right : PersonState.Right,
			},
			PersonState.Right : {
				Region.Left : PersonState.Left,
				Region.Middle : PersonState.RightToMiddle,
			},
			PersonState.LeftToMiddle : {
				Region.Left : PersonState.Left,
				Region.Right : PersonState.Pass,
			},
			PersonState.RightToMiddle : {
				Region.Left : PersonState.Pass,
				Region.Right : PersonState.Right,
			},
			PersonState.Pass : {
				Region.Left : PersonState.Left,
				Region.Right : PersonState.Right,
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
	def __init__(self, maxDisappeared=config.LOST_COUNT):
		# initialize the next unique object ID along with two ordered
		# dictionaries used to keep track of mapping a given object
		# ID to its centroid and number of consecutive frames it has
		# been marked as "disappeared", respectively
		self.nextObjectID = 1
		self.tracking_objects = OrderedDict()

		# store the number of maximum consecutive frames a given
		# object is allowed to be marked as "disappeared" until we
		# need to deregister the object from tracking
		self.maxDisappeared = maxDisappeared

	def __update_centroid(self, objectID, centroid):
		if objectID in self.tracking_objects:
			self.tracking_objects[objectID].update_centroid(centroid)
		else:
			self.tracking_objects[objectID] = TrackingObject(centroid)

	def __register(self, centroid):
		# when registering an object we use the next available object
		# ID to store the centroid
		self.__update_centroid(self.nextObjectID, centroid)
		self.nextObjectID += 1

	def __register_all(self, centroids):
		for c in centroids:
			self.__register(c)

	# def __deregister(self, objectID):
	# 	# to deregister an object ID we delete the object ID from
	# 	# both of our respective dictionaries
	# 	del self.tracking_objects[objectID] # here

	def __ageing(self, objectID):
		if objectID in self.tracking_objects:
			self.tracking_objects[objectID].lost_frame_count += 1
			self.tracking_objects[objectID].is_lost = True

			# check to see if the number of consecutive
			# frames the object has been marked "disappeared"
			# for warrants deregistering the object
			if self.tracking_objects[objectID].lost_frame_count > self.maxDisappeared:
				del self.tracking_objects[objectID]

	def __ageing_all(self):
		IDs = self.tracking_objects.keys()
		for objectID in IDs:
			self.__ageing(objectID)

		# Note : Deleting dictionary member during iteration may cause an error, so do not call like the code below
		# for objectID in self.tracking_objects.keys():
		# 	self.ageing(objectID)

	def __convert_rects_to_centroids(self, rects):
		centroids = []
		for rect in rects:
			centroids.append(Point(
				int((rect.left + rect.right) / 2.0),
				int((rect.top + rect.bottom) / 2.0)
			))
		return centroids

	def update(self, object_bounds_in_the_latest_frame):
		# If we got no new objects in the frame, just run ageing.
		if len(object_bounds_in_the_latest_frame) == 0:
			self.__ageing_all()
		else:
			input_centroids = self.__convert_rects_to_centroids(object_bounds_in_the_latest_frame)

			# if we are currently not tracking any objects take the input
			# centroids and register each of them
			if len(self.tracking_objects) == 0:
				self.__register_all(input_centroids)
			else:
				# grab the set of object IDs and corresponding centroids
				objectIDs = list(self.tracking_objects.keys())

				tracking_centroids_tupple = []
				for obj in self.tracking_objects.values():
					tracking_centroids_tupple.append((obj.centroid.x, obj.centroid.y))

				input_centroids_tupple = []
				for c in input_centroids:
					input_centroids_tupple.append((c.x, c.y))

				# compute the distance between each pair of object
				# centroids and input centroids, respectively -- our
				# goal will be to match an input centroid to an existing
				# object centroid
				dist_matrix = dist.cdist(np.array(tracking_centroids_tupple), input_centroids_tupple)

				# in order to perform this matching, we must (1) find the
				# smallest value in each row and then (2) sort the row
				# indexes based on their minimum values so that the row
				# with the smallest value as at the *front* of the index
				# list
				rows = dist_matrix.min(axis=1).argsort()

				# next, we perform a similar process on the columns by
				# finding the smallest value in each column and then
				# sorting using the previously computed row index list
				cols = dist_matrix.argmin(axis=1)[rows]

				# in order to determine if we need to update, register,
				# or deregister an object we need to keep track of which
				# of the rows and column indexes we have already examined
				usedRows = set()
				usedCols = set()

				# loop over the combination of the (row, column) index
				# tuples
				for (row, col) in zip(rows, cols):
					# if we have already examined either the row or
					# column value before, ignore it
					if row in usedRows or col in usedCols:
						continue

					# otherwise, grab the object ID for the current row,
					# set its new centroid, and reset the disappeared
					# counter
					objectID = objectIDs[row]
					self.__update_centroid(objectID, input_centroids[col])

					# indicate that we have examined each of the row and
					# column indexes, respectively
					usedRows.add(row)
					usedCols.add(col)

				# compute both the row and column index we have NOT yet
				# examined
				unusedRows = set(range(0, dist_matrix.shape[0])).difference(usedRows)
				unusedCols = set(range(0, dist_matrix.shape[1])).difference(usedCols)

				# in the event that the number of object centroids is
				# equal or greater than the number of input centroids
				# we need to check and see if some of these objects have
				# potentially disappeared
				if dist_matrix.shape[0] >= dist_matrix.shape[1]:
					# loop over the unused row indexes
					for row in unusedRows:
						# grab the object ID for the corresponding and ageing
						self.__ageing(objectIDs[row])

				# otherwise, if the number of input centroids is greater
				# than the number of existing object centroids we need to
				# register each new input centroid as a trackable object
				else:
					for col in unusedCols:
						self.__register(input_centroids[col])

		# return the set of trackable objects
		return self.tracking_objects
