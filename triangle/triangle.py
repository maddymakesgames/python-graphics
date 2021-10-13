import pyglet
from pyglet.gl import *

import pyshaders


def main():
    window = pyglet.window.Window(
        visible=True, width=300, height=300, resizable=True)

    shader = pyshaders.from_files_names(
        './triangle_vert.glsl', './triangle_frag.glsl')
    shader.use()

    vertex_list = pyglet.graphics.vertex_list(3,
                                              ('v2f', (0.5, -0.5, -
                                               0.5, -0.5, 0.0, 0.5)),
                                              ('1g3f', (1.0, 0.0, 0.0,
                                                        0.0, 1.0, 0.0,
                                                        0.0, 0.0, 1.0)))

    @window.event
    def on_draw():
        window.clear()
        vertex_list.draw(GL_TRIANGLES)

    pyglet.app.run()


if __name__ == '__main__':
    main()
