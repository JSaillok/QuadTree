from collections import deque
import QTree

#Template class for Quadtree, so we apply KNN
class LocalQuadTree(QTree.QuadTree):

    # Search within a QuadTree to find all the neighbouring points at a specific point.
    # These points were passed in a stack
    # Starts from root till will find the point in 2D space.
    # A list is returned with the points that the node we are looking for may contain
    # and also contains the nodes that it examined
    def query(self, point: QTree.Point):

        # The deque method was used to put data from both the left and right side
        # The goal is to place the contents of the node on the left 
        # and the nodes we passed until we found it on the right
        nodes_visited = deque()
        current_node = self._root
        nodes_visited.append(current_node)


        while current_node is not None and not LocalQuadTree.nodeIsLeaf(current_node):

            if current_node.ll.contains_point(point):

                current_node = current_node.ll
                nodes_visited.append(current_node)

            elif current_node.lr.contains_point(point):

                current_node = current_node.lr
                nodes_visited.append(current_node)

            elif current_node.ul.contains_point(point):

                current_node = current_node.ul
                nodes_visited.append(current_node)

            elif current_node.ur.contains_point(point):

                current_node = current_node.ur
                nodes_visited.append(current_node)

            else:

                current_node = None

        if LocalQuadTree.nodeIsLeaf(current_node):

            points = current_node.all_points()

        else:

            points = []

        return points, nodes_visited


    # KNN takes as attributes the point we are looking for and the number of NN
    # Returns a list with nn. Runs the query function to return the stack
    # So we can see the points inside the sub-rectangle
    # We pop every item till we reach the goal of neighbors
    # Calculate the euclidean distance and sort. Returns k items.
    def get_knn(self, point: QTree.Point, k: int):

        print(20*"*")
        print("For " + point.data + " with coordinates " + str(point.x) + ", " + str(point.y) + "\n")

        points, nodes_visited = self.query(point)

        while len(nodes_visited) != 0 and len(points) < k:

            node = nodes_visited.pop()
            contained_points = node.all_points()

            for current_point in contained_points:
                if current_point not in points:

                    points.append(current_point)

        points.sort(key=lambda point_in_list: QTree.euclidean_distance(point, point_in_list))

        points = points[0:k]

        radius = QTree.euclidean_distance(point, points[k - 1])

        bb = QTree.BoundingBox(point.x - radius, point.y - radius, point.x + radius, point.y + radius)

        points = self._root.within_bb(bb)

        points.sort(key=lambda point_in_list: QTree.euclidean_distance(point, point_in_list))

        return points[0:k]

    #Checks if node is a leaf
    @staticmethod
    def nodeIsLeaf(node: QTree.QuadNode):

        return node.ll is None and node.ul is None and node.lr is None and node.ur is None