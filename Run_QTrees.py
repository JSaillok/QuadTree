import time
import QTree
from Local_QTree import LocalQuadTree
import re #Regular expression operations
import pandas as pd
import names

dim = 2


def put_into_list(file, start, end):

    latitude = []
    longtitude = []
    scientists_list = []

    firstline = file.readline()

    for line in file:

        if firstline == line:continue

        line = line.split(",")

        filt_line = names.name_filter(line, start, end)
        if (filt_line != []):
            latitude.append(int(filt_line[0]))
            longtitude.append(int(filt_line[1]))
            scientists_list.append(filt_line[3].strip())
        
        

    return latitude, longtitude, scientists_list



def get_points(latitude, longtitude): # Takes the list of scientists as an instance.
    points = [] # Initializing an empty list.

    for i in range(len(latitude)): # Iterating through the whole list,
        temp_list = [0, 0] # we initialize an empty list with two elements.
        temp_list[0] = latitude[i] # First, we insert the latitude
        temp_list[1] = longtitude[i]# and secondly the longtitude
        points.append(temp_list) # Finally we append our temporary list to our list of points

    return points # and we return our list of points


def range_search(points, range_min, range_max):
    result = []
    index = 0
    for i in points: # For every point in our tree

        if (i[0] >= range_min[0]) and (i[0] <= range_max[0]) and (i[1] >= range_min[1]) and (i[1] <= range_max[1]):
            #print("I am " + str(i[0]) + " and i am bigger than " + str(range_min[0]) + " and smaller than " + str(range_max[0]) + "\n")
            #print("I am " + str(i[1]) + " and i am bigger than " + str(range_min[1]) + " and smaller than " + str(range_max[1]) + "\n")
            result.append(index) # If the point is within the range we append it to the result list

        index = index + 1

    return result

# It takes as input the name of the scientist and the data that is preprocessed in the main_scientists function
# and creates the quadtree builds a point according to the latt and long given by the user and according to
# the user parses the whole dataset of scientists and runs knn
def run_scientists(scientist_name, k: int, lat, lon, name):

    #Tree creation
    tree = LocalQuadTree((0, 0), 10000, 10000)
    # print(len(name))
    for i in range(len(lat)):
        #print(str(round(lat[i]/1000000, 4)) +  "  ---   " + str(round(lon[i]/1000000, 4)))
        node = QTree.Point(lat[i], lon[i], data=name[i])
        tree.insert(node, node.data)

    #Index of searching point
    idx = [i for i, item in enumerate(name) if re.search(scientist_name, item)]
    searching_point = QTree.Point(lat[idx[0]], lon[idx[0]], data=scientist_name)

    #Execution times
    ts = time.time()
    list3 = tree.get_knn(searching_point, k)
    te = time.time()
    dt = te - ts

    print(20*"*")
    print("The algorithm run for :")
    print("%f%s" % (dt, "sec"))
    print(20*"*")
    print(20*"*")
    print("%s%i%s" % ("The ", k-1, " nearest neighbors are :"))
    print("\n")
    count = 0
    for i in list3:
        if i==list3[0]:continue
        print(str(count) + "  ====> "+i.data + "with coordinates (" + str(i.x) + "," + str(i.y) + ")")
        count = count + 1
    print("_________________")


# User friendly Menu to choose 1. Range Search or KNN
def main_scientists():

    #Read file

    file = open("demo_file.csv", "r")
    start = input("Give the 1st letter of list: ")
    end = input("Give the last letter of list: ")
    lat, lon, name = put_into_list(file, start, end)
    if len(name) == 0:
        print("There is no scientist in this range of letters")

    else:
        print("Data successfully read.\n")
        points = get_points(lat, lon)

        print("\n MENU :\n")
        choice = int(input("1: kNN \n2: Range Search \n"))

        if choice == 1:

            scientist = input("Give the name of the scientist you want to search his neighbors: ")
            k_neighbors = int(input("How many nearby scientists do you want to show: "))
            # n = name.index(scientist)
            # name.remove(scientist)
            # lat.remove(lat[n])
            # lon.remove(lon[n])
            run_scientists(scientist, k_neighbors + 1, lat, lon, name)

        elif choice == 2:

            search_min = [0, 0]
            search_max = [0, 0]
            search_min[0] = float(input("Please give the minimum cord: "))
            search_min[1] = float(input("Please give the minimum award: "))
            search_max[0] = float(input("Please give the maximum cord: "))
            search_max[1] = float(input("Please give the maximum award: "))

            result = range_search(points, search_min, search_max)
            # print(result)
            for i in result:
                print(name[i] + "[" + str(lat[i]) + ", " + str(lon[i]) + "]")

if __name__ == '__main__':

    print("Reading scientists data...\n")
    main_scientists()