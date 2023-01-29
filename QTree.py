import math

# Function that creates an object which represents x,y coordinates on 2D
# Every object has one point

class Point(object):

    def __init__(self, x, y, data=None):
        
        self.x = x  # X axis
        self.y = y  # Y axis
        self.data = data # The possibility of characterising each point is given


# Quad tree each node has 4 children
# In the representation in 2D space, this is divided by rectangular parallelograms
# Which shows us if we 've passed the 4-child limit
class BoundingBox(object):

    def __init__(self, min_x, min_y, max_x, max_y):
        
        # We define the minimum and maximum frame in which to include a point
        # and take the middle frame to place it

        self.min_x = min_x  
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y
        self.width = self.max_x - self.min_x
        self.height = self.max_y - self.min_y
        self.half_width = self.width / 2
        self.half_height = self.height / 2
        self.center = Point(self.half_width, self.half_height)

    # Boolean function that returns if a point belongs into a frame

    def contains(self, point):

        return (
                self.min_x <= point.x <= self.max_x
                and self.min_y <= point.y <= self.max_y
        )


# In the Quadtree structure we are interested not only in the content of the node
# its location and its capacity
# Capacity helps when to subdivide

class QuadNode(object):

    POINT_CAPACITY = 4
    point_class = Point
    bb_class = BoundingBox

    # Constructs a `QuadNode` object
    def __init__(self, center, width, height, capacity=None):

        # capacity by default is 4  "POINT_CAPACITY = 4"

        self.center = center #center of quadtree
        self.width = width   #width of node
        self.height = height #height of node
        self.points = []    


        self.ul = None
        self.ur = None
        self.ll = None
        self.lr = None

        if capacity is None:
            capacity = self.POINT_CAPACITY

        self.capacity = capacity
        self.bounding_box = self.calc_bounding_box()

    #Boolean function that returns if contains a point
    def __contains__(self, point):

        return self.find(point) is not None

    # Returns all point objects
    # Creates generators for each point in whichever quadrant it is
    # And then it does iterable (for inside of it)
    def __iter__(self):

        # Breaks to all points and after focus on each one
        for pnt in self.points[:]:
            yield pnt

        if self.ul is not None:
            yield from self.ul

        if self.ur is not None:
            yield from self.ur

        if self.ll is not None:
            yield from self.ll

        if self.lr is not None:
            yield from self.lr

    #calculate bb for every node created
    def calc_bounding_box(self):

        half_width = self.width / 2
        half_height = self.height / 2

        min_x = self.center.x - half_width
        min_y = self.center.y - half_height
        max_x = self.center.x + half_width
        max_y = self.center.y + half_height

        return self.bb_class(
            min_x=min_x, min_y=min_y, max_x=max_x, max_y=max_y
        )

    # Examine if a point exists inside a node (Boolean)
    def contains_point(self, point):

        bb = self.bounding_box

        if bb.min_x <= point.x <= bb.max_x:
            if bb.min_y <= point.y <= bb.max_y:
                return True

        return False

    # We calculate if the point is North East from the point we are looking at (Boolean)
    def is_ul(self, point):

        return point.x < self.center.x and point.y >= self.center.y

    # North West
    def is_ur(self, point):

        return point.x >= self.center.x and point.y >= self.center.y

    # South East
    def is_ll(self, point):

        return point.x < self.center.x and point.y < self.center.y

    # South West
    def is_lr(self, point):

        return point.x >= self.center.x and point.y < self.center.y

    # Subdivide node with its children when capacity>4
    def subdivide(self):

        half_width = self.width / 2
        half_height = self.height / 2
        quarter_width = half_width / 2
        quarter_height = half_height / 2

        ul_center = self.point_class(
            self.center.x - quarter_width, self.center.y + quarter_height
        )
        self.ul = self.__class__(
            ul_center, half_width, half_height, capacity=self.capacity
        )

        ur_center = self.point_class(
            self.center.x + quarter_width, self.center.y + quarter_height
        )
        self.ur = self.__class__(
            ur_center, half_width, half_height, capacity=self.capacity
        )

        ll_center = self.point_class(
            self.center.x - quarter_width, self.center.y - quarter_height
        )
        self.ll = self.__class__(
            ll_center, half_width, half_height, capacity=self.capacity
        )

        lr_center = self.point_class(
            self.center.x + quarter_width, self.center.y - quarter_height
        )
        self.lr = self.__class__(
            lr_center, half_width, half_height, capacity=self.capacity
        )

        # Implemented retrograde for the repositioning of the nodes in the quad
        # after break

        for pnt in self.points:
            if self.is_ul(pnt):
                self.ul.points.append(pnt)
            elif self.is_ur(pnt):
                self.ur.points.append(pnt)
            elif self.is_ll(pnt):
                self.ll.points.append(pnt)
            else:
                self.lr.points.append(pnt)

        #Return list to null after redivined
        self.points = []

    
    def insert(self, point):

        # We check if the point he's trying to get to doesn't exist
        if not self.contains_point(point):
            raise ValueError(
                "Point {} is not within this node ({} - {}).".format(
                    point.data, self.center, self.points[0].data
                )
            )

        # We check if the capacity at the node where we're going to put it is exceeded
        if (len(self.points) + 1) > self.capacity:
            # If this is exceeded then subdivide() is called
            self.subdivide()
        # If not, check which quadrant to put it in
        if self.ul is not None:
            if self.is_ul(point):
                return self.ul.insert(point) # North East
            elif self.is_ur(point):
                return self.ur.insert(point) # North West
            elif self.is_ll(point):
                return self.ll.insert(point) # South East
            elif self.is_lr(point):
                return self.lr.insert(point) # South West

        # We put the point in the hub after we see
        # that there are no more children and it fits
        self.points.append(point)
        return True # insert succesfully

    # it takes as its input the node we're looking for
    # returns its data
    def find(self, point):

        found_node, _ = self.find_node(point)

        if found_node is None:
            return None

        # Try the points on this node first.
        for pnt in found_node.points:
            if pnt.x == point.x and pnt.y == point.y:
                return pnt

        return None

    # Search for node. 
    # Takes as input the node and a list with nodes that have been searched.
    # Returns a tuple with node we 're looking for and the final list.
    def find_node(self, point, searched=None):

        if searched is None:
            searched = []

        if not self.contains_point(point):
            return None, searched

        searched.append(self)

        # Elegxei ta paidia
        if self.is_ul(point):
            if self.ul is not None:
                return self.ul.find_node(point, searched)
        elif self.is_ur(point):
            if self.ur is not None:
                return self.ur.find_node(point, searched)
        elif self.is_ll(point):
            if self.ll is not None:
                return self.ll.find_node(point, searched)
        elif self.is_lr(point):
            if self.lr is not None:
                return self.lr.find_node(point, searched)

        # Not found in any children. Return this node.
        return self, searched

    # List with all points that has a node and all of its children
    def all_points(self):

        return list(iter(self))

    #We check if a rectangle is contained within the rectangle we are looking for.
    #So it will help us to look in which direction to move
    def within_bb(self, bb):

        points = []

        # Check every point that node contains
        # and they are inside of boundary box
        for pnt in self.points:
            if bb.contains(pnt):
                points.append(pnt)

        if self.ul is not None:
            points += self.ul.within_bb(bb)

        if self.ur is not None:
            points += self.ur.within_bb(bb)

        if self.ll is not None:
            points += self.ll.within_bb(bb)

        if self.lr is not None:
            points += self.lr.within_bb(bb)

        return points


def euclidean_distance(ref_point, check_point):

    dx = max(ref_point.x, check_point.x) - min(ref_point.x, check_point.x)
    dy = max(ref_point.y, check_point.y) - min(ref_point.y, check_point.y)

    return math.sqrt(dx ** 2 + dy ** 2)



class QuadTree(object):

    node_class = QuadNode
    point_class = Point

    def __init__(self, center, width, height, capacity=None):

        self.width = width
        self.height = height
        self.center = self.convert_to_point(center)
        self._root = self.node_class(
            self.center, self.width, self.height, capacity=capacity
        )

    # converts input to point for correct insert
    def convert_to_point(self, val):

        if isinstance(val, self.point_class):
            return val
        elif isinstance(val, (tuple, list)):
            return self.point_class(val[0], val[1])
        elif val is None:
            return self.point_class(0, 0)
        else:
            raise ValueError(
                "The input is not correctly given, the input must be of the type: "
                "Point | tuple | list | None"
            )
    
    # contains a point
    def __contains__(self, point):

        pnt = self.convert_to_point(point)
        return self.find(pnt) is not None

    # number of points
    def __len__(self):

        return len(self._root)

    def __iter__(self):

        return iter(self._root)

    # convert data to point
    # and insert the data that describe it if they are exist
    def insert(self, point, data):

        pnt = self.convert_to_point(point)

        pnt.data = data
        #print(pnt.data)
        return self._root.insert(pnt)

    # convert to point and returns true if it will find it
    def find(self, point):

        pnt = self.convert_to_point(point)
        return self._root.find(pnt)
