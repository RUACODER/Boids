import numpy
import cv2
import random

from __init__ import *


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Boid:
    def __init__(self, points):
        self.points = points

        x_total = 0
        y_total = 0
        for point in self.points:
            x_total += point.x
            y_total += point.y

        self.center = Point(x_total / 3, y_total / 3)
        self.theta = self.find_alignment(self.points[0])
        #self.indent = Point((points[1].x + points[2].x) / 2, (points[1].y + points[2].y) / 2)

    def update(self):
        x_total = 0
        y_total = 0
        for point in self.points:
            x_total += point.x
            y_total += point.y

        self.center = Point(x_total / 3, y_total / 3)
        self.theta = self.find_alignment(self.points[0])
        #self.indent = Point((points[1].x + points[2].x) / 2, (points[1].y + points[2].y) / 2)

    def move(self, direc):
        for point in self.points:
            point.x += MOVE_SPEED * numpy.cos(direc)
            point.y += MOVE_SPEED * numpy.sin(direc)

    def rotate(self, angle):
        for point in self.points:
            x = point.x - self.center.x
            y = point.y - self.center.y
            angle_rad = angle * numpy.pi / 180
            point.x = (x * numpy.cos(angle_rad)) - (y * numpy.sin(angle_rad)) + self.center.x
            point.y = (x * numpy.sin(angle_rad)) + (y * numpy.cos(angle_rad)) + self.center.y

    def search_area(self, boids, search_radius):
        boids_in_your_area = []
        for boid in boids:
            boid.center.x = int(boid.center.x)
            boid.center.y = int(boid.center.y)
            self_center_x = int(self.center.x)
            self_center_y = int(self.center.y)

            if boid.center.x in range(self_center_x - search_radius, self_center_x + search_radius) and \
                    boid.center.y in range(self_center_y - search_radius, self_center_y + search_radius):
                boids_in_your_area.append(boid)

        return boids_in_your_area

########################################################################################################################

    def controller(self):
        com = self.find_com(all_boids, VISION_RADIUS)
        closest_boid = self.find_closest_boid(all_boids, VISION_RADIUS)
        alignment = self.alignment(all_boids, VISION_RADIUS)

        pivot_com = self.turn_to_face(com)
        pivot_sep = self.turn_to_face(closest_boid) * -1
        self.rotate(1 * 1 * alignment)

        self.move(self.theta)

########################################################################################################################

    def is_facing(self):
        is_facing = False
        multiplier = 100
        fov = 120
        fov_rad = (fov * numpy.pi / 180) / 2
        #target_theta = int(self.find_alignment(target) * multiplier)

        upper_bound = int((self.theta + fov_rad) * multiplier)
        lower_bound = int((self.theta - fov_rad) * multiplier)

        #if target_theta in range(lower_bound, upper_bound):
            #is_facing = True

        return [upper_bound, lower_bound]

    def turn_to_face(self, target):
        pivot = 0
        if target != None:
            target_theta = self.find_alignment(target)
            delta = target_theta - self.theta

            # normalizing data
            if delta > numpy.pi:
                delta -= 2 * numpy.pi
            elif delta < -numpy.pi:
                delta += 2 * numpy.pi

            if delta > 0:
                pivot = 1
            elif delta < 0:
                pivot = -1

        return pivot

    def find_com(self, boids, search_radius):
        total_mass = [0, 0]
        area = self.search_area(boids, search_radius)
        for boid in area:
            total_mass[0] += boid.center.x
            total_mass[1] += boid.center.y

        center_of_mass = Point(total_mass[0], total_mass[1])
        center_of_mass.x /= len(area)
        center_of_mass.y /= len(area)

        return center_of_mass

    def find_closest_boid(self, boids, search_radius):
        shortest_dist = search_radius
        closest_boid = None
        area = self.search_area(boids, search_radius)
        for boid in area:
            dist = abs(self.center.x - boid.center.x) + abs(self.center.y - boid.center.y)
            if dist != 0:
                if dist < shortest_dist:
                    shortest_dist = dist
                    closest_boid = boid.center

        return closest_boid

    def find_alignment(self, point):
        return numpy.arctan2((point.y - self.center.y), point.x - self.center.x)

    def alignment(self, boids, search_radius):
        total_theta = 0
        pivot = -1
        in_area = self.search_area(boids, search_radius)
        for boid in in_area:
            total_theta += boid.theta

        avg_alignment = total_theta / len(in_area)

        delta = avg_alignment - self.theta
        print(avg_alignment)
        '''
        if delta > numpy.pi:
            delta -= 2 * numpy.pi
        elif delta < -numpy.pi:
            delta += 2 * numpy.pi
        '''
        if delta > 0:
            pivot = 1
        elif delta < 0:
            pivot = -1

        return pivot

    def magic_wall(self):
        # right wall
        if self.center.x > CANVAS_WIDTH:
            for point in self.points:
                point.x -= (CANVAS_WIDTH - 5)
        # left wall
        elif self.center.x < 0:
            for point in self.points:
                point.x += (CANVAS_WIDTH - 5)
        # bottom wall
        if self.center.y > CANVAS_HEIGHT:
            for point in self.points:
                point.y -= (CANVAS_HEIGHT - 5)
        # top wall
        elif self.center.y < 0:
            for point in self.points:
                point.y += (CANVAS_HEIGHT - 5)


def create_boid(size):
    points = []
    x_offset = random.randrange(50, CANVAS_WIDTH - 50 - (4 * size))
    y_offset = random.randrange(50, CANVAS_HEIGHT - 50 - (2 * size))
    points.append(Point((4 * size) + x_offset, (1 * size) + y_offset))
    points.append(Point(0 + x_offset, (2 * size) + y_offset))
    points.append(Point(0 + x_offset, 0 + y_offset))

    return points


# vector initialization
all_boids = []
for i in range(NUM_BOIDS):
    all_boids.append(Boid(create_boid(BOID_SCALE)))
for i in all_boids:
    rand_rotation = random.randrange(0, 361)
    i.rotate(rand_rotation)

# game loop
while True:
    # Create canvas
    background = numpy.zeros((CANVAS_HEIGHT, CANVAS_WIDTH, 3), numpy.uint8)
    background.fill(0)

    # changes for each individual boid
    counter = 0
    for each_boid in all_boids:
        points_list = []
        counter += 1

        # translations
        each_boid.controller()

        # create magic walls
        each_boid.magic_wall()




        # turn boid object into format for cv2
        for pt in each_boid.points:
            points_list.append([pt.x, pt.y])
        boid_list32 = numpy.array(points_list, numpy.int32)
        # update boid with new info
        each_boid.update()

        # plot boid
        if each_boid == all_boids[0]:
            cv2.fillPoly(background, [boid_list32], (97, 105, 255))
            # plot dist to center of mass

        else:
            cv2.fillPoly(background, [boid_list32], BOID_COLOR)

        # plot center point
        cv2.circle(background, [round(each_boid.center.x), round(each_boid.center.y)], 3, CENTER_COLOR_DOT, -1)
        # plot alignment line
        cv2.line(background, (round(each_boid.points[0].x), round(each_boid.points[0].y)),
                 (round(each_boid.center.x), round(each_boid.center.y)), ALIGNMENT_LINE_COLOR, 1)
        # plot vision circle
        cv2.circle(background, [round(all_boids[0].center.x), round(all_boids[0].center.y)], VISION_RADIUS, VISION_COLOR)
        # find closest boid
        apple = each_boid.find_closest_boid(all_boids, VISION_RADIUS)
        if apple != None:
            cv2.line(background, (round(each_boid.center.x), round(each_boid.center.y)),
            (round(apple.x), round(apple.y)), ALIGNMENT_LINE_COLOR, 1)
        center_of_mass = each_boid.find_com(all_boids, VISION_RADIUS)
        cv2.line(background, [round(each_boid.center.x), round(each_boid.center.y)],
        [round(center_of_mass.x), round(center_of_mass.y)], CENTER_OF_MASS_LINE_COLOR, 1)


    # display drawings
    cv2.imshow('Boids', background)
    cv2.waitKey(SLEEP_TIME)
