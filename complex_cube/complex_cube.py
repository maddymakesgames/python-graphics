import pyglet
from pyglet.gl import *

import pyshaders

import numpy as np

from math import tan, sin, cos, radians
import timeit
from timeit import default_timer

CUBE_VERTS = (
    # Front face
    -0.5, 0.5, 0.5,
    0.5, 0.5, 0.5,
    0.5, -0.5, 0.5,
    -0.5, -0.5, 0.5,

    # Left Face
    0.5, 0.5, 0.5,
    0.5, 0.5, -0.5,
    0.5, -0.5, -0.5,
    0.5, -0.5, 0.5,

    # Back Face
    -0.5, 0.5, -0.5,
    0.5, 0.5, -0.5,
    0.5, -0.5, -0.5,
    -0.5, -0.5, -0.5,

    # Right Face
    -0.5, 0.5, 0.5,
    -0.5, 0.5, -0.5,
    -0.5, -0.5, -0.5,
    -0.5, -0.5, 0.5,

    # Top Face
    -0.5, 0.5, 0.5,
    -0.5, 0.5, -0.5,
    0.5, 0.5, -0.5,
    0.5, 0.5, 0.5,

    # Bottom Face
    -0.5, -0.5, 0.5,
    -0.5, -0.5, -0.5,
    0.5, -0.5, -0.5,
    0.5, -0.5, 0.5,
)

CUBE_COLORS = (
    # Front Face
    1., 0., 0.,
    1., 0., 0.,
    1., 0., 0.,
    1., 0., 0.,

    # Left Face
    0., 1., 0.,
    0., 1., 0.,
    0., 1., 0.,
    0., 1., 0.,

    # Back Face
    1., 0., 1.,
    1., 0., 1.,
    1., 0., 1.,
    1., 0., 1.,

    # Right Face
    0., 0., 1.,
    0., 0., 1.,
    0., 0., 1.,
    0., 0., 1.,

    # Top Face
    1., 1., 0.,
    1., 1., 0.,
    1., 1., 0.,
    1., 1., 0.,

    # Bottom Face
    0., 1., 1.,
    0., 1., 1.,
    0., 1., 1.,
    0., 1., 1.,
)

CUBE_INDECIES = [
    0, 1, 2, 2, 3, 0,
    4, 5, 6, 6, 7, 4,
    8, 9, 10, 10, 11, 8,
    12, 13, 14, 14, 15, 12,
    16, 17, 18, 18, 19, 16,
    20, 21, 22, 22, 23, 20
]

# UVS should be 0-1 but for some reason its sampling the image to be larger
# so we have to shrink the uvs
CUBE_UVS = (
    0., 0.,
    2., 0.,
    2., 2.,
    0., 2.,

    0., 0.,
    1., 0.,
    1., 1.,
    0., 1.,

    0., 0.,
    1., 0.,
    1., 1.,
    0., 1.,

    0., 0.,
    1., 0.,
    1., 1.,
    0., 1.,

    0., 0.,
    1., 0.,
    1., 1.,
    0., 1.,

    0., 0.,
    1., 0.,
    1., 1.,
    0., 1.,
)

CUBE_POSITION = np.array([0., 0., -3.])
CAMERA_POSITION = np.array([0., 0., 0.])
CAMERA_FOV = 45.
CAMERA_FAR_PLANE = 1000.
CAMERA_NEAR_PLANE = 0.1
CAMERA_UP_VECTOR = np.array([0., 1., 0.])


def main():
    window = pyglet.window.Window(
        visible=True, width=300, height=300, resizable=True)

    shader = pyshaders.from_files_names(
        './complex_cube_vert.glsl', './complex_cube_frag.glsl')
    shader.use()

    texture_image = pyglet.image.load('./texture.png')
    width, height = texture_image.width, texture_image.height

    shader.uniforms.image_dims = [width, height]

    texture = texture_image.get_texture(rectangle=True, force_rectangle=True)

    glEnable(texture.target)
    glBindTexture(texture.target, texture.id)

    vertex_list = pyglet.graphics.vertex_list_indexed(24, CUBE_INDECIES,
                                                      ('v3f', CUBE_VERTS),
                                                      ('1g3f', CUBE_COLORS),
                                                      ('2g2f', CUBE_UVS))
    print(shader.uniforms)
    start = default_timer()
    glEnable(GL_DEPTH_TEST)

    @ window.event
    def on_draw():
        draw(default_timer() - start)

    def draw(elapsed):
        window.clear()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        (win_x, win_y) = window.get_size()
        set_uniforms(shader, elapsed*50., win_x / win_y)
        vertex_list.draw(GL_TRIANGLES)
        # texture_image.blit(0, 0)

    pyglet.clock.schedule_interval(draw, 1/600.0)
    pyglet.app.run()


def perspective(aspect_ratio: float):
    """
    creates a perspective matrix from the camera settings and the aspect ratio
    """
    n = CAMERA_NEAR_PLANE
    f = CAMERA_FAR_PLANE

    t = n * tan(radians(CAMERA_FOV/2.))
    b = -t
    r = t * aspect_ratio
    l = -t

    x = 2 * n / (r - l)
    y = 2 * n / (t - b)
    w = (r + l) / (r - l)
    z = (t + b) / (t - b)
    a = -(f+n)/(f-n)
    b = -2 * (f*n)/(f-n)
    return np.array([
        [x, 0., w, 0.],
        [0., y, z, 0.],
        [0., 0., a, b],
        [0., 0., -1., 0.]
    ])


def set_uniforms(shader: pyshaders.ShaderProgram, elapsed, aspect_ratio):
    model = np.matmul(matrix4_from_angle_x(radians(elapsed)),
                      matrix4_from_angle_y(radians(elapsed)))
    view = direct_view()
    proj = perspective(aspect_ratio)

    # projection matrix is fucked so we just use the mv matrix instead
    mv = np.matmul(view, model)
    # mvp = np.matmul(mv, proj)
    shader.uniforms.mvp = mv.tolist()


def direct_view():

    dir = norm(CUBE_POSITION - CAMERA_POSITION)
    dir = np.nan_to_num(dir, nan=0)

    u = norm(cross(CAMERA_UP_VECTOR, dir))
    u = np.nan_to_num(u, nan=0)
    v = cross(u, dir)

    return np.array([
        [u[0], u[1], u[2], 0.],
        [v[0], v[1], v[2], 0.],
        [-dir[0], -dir[1], -dir[2], 0.],
        [0., 0., 0., 1.]
    ])


def norm(a):
    return np.array([a[0] / abs(a[0]), a[1] / abs(a[1]), a[2] / abs(a[2])])


def cross(a, b):
    return np.array([
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0]
    ])


def matrix4_from_angle_y(theta: float):
    """
    creates a rotation matrix around the y axis
    """
    s = sin(theta)
    c = cos(theta)
    return np.array([
        [c, 0., -s, 0.],
        [0., 1., 0., 0.],
        [s, 0., c, 0.],
        [0., 0., 0., 1.]
    ])


def matrix4_from_angle_x(theta: float):
    """
    creates a rotation matrix around the x axis
    """
    s = sin(theta)
    c = cos(theta)
    return np.array([
        [1., 0., 0., 0.],
        [0., c, s, 0.],
        [0., -s, c, 0.],
        [0., 0., 0., 1.]
    ])


def matrix4_from_angle_z(theta: float):
    """
    creates a rotation matrix around the z axis
    """
    s = sin(theta)
    c = cos(theta)
    return np.array([
        [c, s, 0., 0.],
        [-s, c, 0., 0.],
        [0., 0., 1., 0.],
        [0., 0., 0., 1.]
    ])


if __name__ == '__main__':
    main()
