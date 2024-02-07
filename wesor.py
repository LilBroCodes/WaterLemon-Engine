import random
import time

import pygame
from pygame.locals import *
import sys
import math


def rand_grey():
    shade = random.randint(155, 255)
    return (shade, ) * 3


def load_obj(file):
    vertices = []
    faces = []

    with open(file, 'r') as obj_file:
        for line in obj_file:
            if line.startswith('v '):
                # Split line by whitespace and take elements from index 1 onward, then convert to float
                vertex_data = line.strip()
                vertex_data = vertex_data.split()
                vertex_data = vertex_data[1:]
                vertex = list(map(float, vertex_data))
                vertices.append(vertex)

            elif line.startswith('f '):
                # Split line by whitespace, take elements from index 1 onward,
                # split each element by '/' and take the first part, then convert to int
                face_data = line.strip().split()[1:]
                face = [int(vertex.split('/')[0]) - 1 for vertex in face_data]
                faces.append(face)

    colored_faces = []
    for face in faces:
        colored_faces.append((face, rand_grey()))

    return vertices, colored_faces


def render_obj(screen, vertices, faces, scale, offset):
    polygons = []
    for face, color in faces:
        points = []
        for vertex_index in face:
            x, y, z = vertices[vertex_index]
            y -= 2
            # Rotate around x-axis
            y_rotated_x = y * math.cos(angle_x) - z * math.sin(angle_x)
            z_rotated_x = y * math.sin(angle_x) + z * math.cos(angle_x)
            # Rotate around y-axis
            x_rotated_y = x * math.cos(angle_y) + z_rotated_x * math.sin(angle_y)
            z_rotated_y = -x * math.sin(angle_y) + z_rotated_x * math.cos(angle_y)
            # Flip vertically
            x_projected = x_rotated_y * scale + offset[0]
            y_projected = -y_rotated_x * scale + offset[1]
            z_projected = z_rotated_y * scale + offset[2]
            points.append((x_projected, y_projected, z_projected))
            polygons.append(points)
    poslist = []
    depthmap = []
    depthmap_gen = time.time()
    for polygon in polygons:
        out_poly = []
        z_l = []
        for point in polygon:
            x, y, z = point
            out_poly.append((x, y))
            z_l.append(z)
        poslist.append(out_poly)
        az = 0
        for _ in range(len(z_l)):
            az += z_l[_]
        depthmap.append(az / len(z_l))
    print(f"Finished generating depthmap in {str(time.time() - depthmap_gen)[:4]}s")
    drawable = []
    dml = len(depthmap)
    process_start_time = time.time()
    for _ in range(len(depthmap)):
        current_polygon = min(depthmap)
        pos_index = depthmap.index(current_polygon)
        pos = poslist[pos_index]
        depthmap.remove(current_polygon)
        poslist.remove(pos)
        drawable.append([pos, rand_grey()])
    print(f"Finished processing polygons in {str(time.time() - process_start_time)[:4]}s")
    draw_start = time.time()
    for i in drawable:
        polygon = i[0]
        color = i[1]
        pygame.draw.polygon(screen, color, polygon, 0)
    print(f"   Finished drawing polygons in {str(time.time() - draw_start)[:4]}s")


def main(obj_file):
    global angle_x, angle_y, angle_z, angle_w
    angle_x, angle_y, angle_z, angle_w = 0.0, 0.0, 0.0, 0.0

    pygame.init()
    width, height = 800, 600
    scale = 100
    offset = (width / 2, height / 2, 0)
    bg_color = (41, 41, 41)

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('WaterLemon Engine SO Render')

    vertices, faces = load_obj(obj_file)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[K_LEFT] or keys[K_a]:
            angle_y -= 0.01
        if keys[K_RIGHT] or keys[K_d]:
            angle_y += 0.01
        if keys[K_UP] or keys[K_w]:
            angle_x -= 0.01
        if keys[K_DOWN] or keys[K_s]:
            angle_x += 0.01
        if keys[K_j]:
            angle_z -= 0.01
        if keys[K_u]:
            angle_z += 0.01
        if keys[K_h]:
            angle_w -= 0.01
        if keys[K_k]:
            angle_w += 0.01
        if keys[K_q]:
            scale -= 1
        if keys[K_e]:
            scale += 1

        screen.fill(bg_color)
        render_obj(screen, vertices, faces, scale, offset)
        pygame.display.flip()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: wesor.py <path_to_obj_file>")
        sys.exit(1)
    main(sys.argv[1])
