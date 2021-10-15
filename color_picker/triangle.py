from typing import Tuple
import pyglet
from pyglet.gl import *

import pyshaders

from math import radians

dampener = 0.5


def main():
    window = pyglet.window.Window(
        visible=True, width=300, height=300, resizable=True)

    shader = pyshaders.from_files_names(
        './circle_vert.glsl', './circle_frag.glsl')

    center, radius = gen_incircle((1., -1.), (1., 1.), (-1., 1.), (-1., -1.))
    print(center, radius)

    shader.use()

    shader.uniforms.center = center
    shader.uniforms.outer_radius = radius
    shader.uniforms.inner_radius = radius * 0.9

    # We just render onto a single quad that is the full window
    circle_vertex_list = pyglet.graphics.vertex_list(4,
                                                     ('v2f', (
                                                         1, -1,
                                                         1, 1,
                                                         -1, 1,
                                                         -1, -1)))

    mouse_coord = (0., 1.)

    shader.uniforms.mouse_coords = mouse_coord

    @window.event
    def on_draw():
        draw()

    def draw(_=None):
        window.clear()
        circle_vertex_list.draw(GL_QUADS)

    @ window.event
    def on_resize(width, height):
        pass

    @ window.event
    def on_mouse_press(x, y, button, modifiers):
        mouse_coord = remap(x, y, window.width, window.height)
        shader.uniforms.mouse_coords = mouse_coord
        draw()

    @ window.event
    def on_mouse_drag(x, y, dx, dy, button, modifiers):
        mouse_coord = remap(x, y, window.width, window.height)
        shader.uniforms.mouse_coords = mouse_coord
        draw()

    pyglet.app.run()


# Generates the center and radius of a circle who is inscribed in a square
def gen_incircle(v1: Tuple[float, float], v2: Tuple[float, float], v3: Tuple[float, float], v4: Tuple[float, float]) -> Tuple[Tuple[float, float], float]:
    length = max(abs(v1[0] - v3[0]), abs(v2[0] - v4[0]))

    center = (v2[0] - length / 2., v2[1] - length / 2.)

    return (center, length / 2.)


def remap(x: float, y: float, screen_x: float, screen_y: float) -> Tuple[float, float]:
    return ((x / screen_x) * 2 - 1, (y / screen_y) * 2 - 1)


if __name__ == '__main__':
    main()
