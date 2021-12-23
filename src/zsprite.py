""" 3-dimensional sprite implementation.
Allows Z-sorting.

Classes:

    ZSpriteGroup
    ZSprite
"""

import pyglet
from pyglet.gl import *

pyglet.image.Texture.default_mag_filter = pyglet.gl.GL_NEAREST
pyglet.image.Texture.default_min_filter = pyglet.gl.GL_NEAREST

def y_to_z(y: float):
    return -y / 1000

class ZSpriteGroup(pyglet.graphics.Group):

    def __init__(self, texture, blend_src, blend_dest, parent=None):
        super().__init__(parent)
        self.texture = texture
        self.blend_src = blend_src
        self.blend_dest = blend_dest

    def set_state(self):
        glEnable(self.texture.target)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(self.texture.target, self.texture.id)
        glPushAttrib(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glEnable(GL_BLEND)
        glBlendFunc(self.blend_src, self.blend_dest)

        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        glEnable(GL_ALPHA_TEST)
        glAlphaFunc(GL_GREATER, 0.01)

    def unset_state(self):
        glPopAttrib()
        glBindTexture(self.texture.target, 0)
        glDisable(self.texture.target)
        glDisable(GL_DEPTH_TEST)


    def __repr__(self):
        return '%s(%r-%d)' % (self.__class__.__name__, self.texture, self.texture.id)

    def __eq__(self, other):
        return (other.__class__ is self.__class__ and
                self.texture.target == other.texture.target and
                self.texture.id == other.texture.id and
                self.blend_src == other.blend_src and
                self.blend_dest == other.blend_dest)

    def __hash__(self):
        return hash((id(self.parent), self.texture.id, self.texture.target,
                     self.blend_src, self.blend_dest))
                     
                     

class ZSprite(pyglet.sprite.Sprite):
    """ Supports Z layer """

    def __init__(self,
             img, x=0, y=0, z=0,
             blend_src=GL_SRC_ALPHA,
             blend_dest=GL_ONE_MINUS_SRC_ALPHA,
             batch=None,
             group=None,
             usage='dynamic',
             subpixel=False):
        if batch is not None:
            self._batch = batch

        self._x = x
        self._y = y
        self._z = z

        if isinstance(img, pyglet.image.Animation):
            self._animation = img
            self._texture = img.frames[0].image.get_texture()
            self._next_dt = img.frames[0].duration
            if self._next_dt:
                pyglet.clock.schedule_once(self._animate, self._next_dt)
        else:
            self._texture = img.get_texture()

        self._group = ZSpriteGroup(self._texture, blend_src, blend_dest, group)
        self._usage = usage
        self._subpixel = subpixel
        self._create_vertex_list()

    @property
    def group(self):
        return self._group.parent

    @group.setter
    def group(self, group):
        if self._group.parent == group:
            return
        self._group = self._group.__class__(self._texture,
                                  self._group.blend_src,
                                  self._group.blend_dest,
                                  group)
        if self._batch is not None:
            self._batch.migrate(self._vertex_list, GL_QUADS, self._group,
                                self._batch)

    def _create_vertex_list(self):
        if self._subpixel:
            vertex_format = 'v3f/%s' % self._usage
        else:
            vertex_format = 'v3i/%s' % self._usage
        if self._batch is None:
            self._vertex_list = pyglet.graphics.vertex_list(4, vertex_format,
                'c4B', ('t3f', self._texture.tex_coords))
        else:
            self._vertex_list = self._batch.add(4, GL_QUADS, self._group,
                vertex_format, 'c4B', ('t3f', self._texture.tex_coords))

        self._update_position()
        self._update_color()

    def _update_position(self):
        img = self._texture
        scale_x = self._scale * self.scale_x
        scale_y = self._scale * self.scale_y
        if not self._visible:
            vertices = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif self._rotation:
            x1 = -img.anchor_x * scale_x
            y1 = -img.anchor_y * scale_y
            x2 = x1 + img.width * scale_x
            y2 = y1 + img.height * scale_y
            x = self._x
            y = self._y
            z = self._z
            r = -math.radians(self._rotation)
            cr = math.cos(r)
            sr = math.sin(r)
            ax = x1 * cr - y1 * sr + x
            ay = x1 * sr + y1 * cr + y
            bx = x2 * cr - y1 * sr + x
            by = x2 * sr + y1 * cr + y
            cx = x2 * cr - y2 * sr + x
            cy = x2 * sr + y2 * cr + y
            dx = x1 * cr - y2 * sr + x
            dy = x1 * sr + y2 * cr + y
            vertices = [ax, ay, z, bx, by, z, cx, cy, z, dx, dy, z]
        elif scale_x != 1.0 or scale_y != 1.0:
            x1 = self._x - img.anchor_x * scale_x
            y1 = self._y - img.anchor_y * scale_y
            x2 = x1 + img.width * scale_x
            y2 = y1 + img.height * scale_y
            z = self._z
            vertices = [x1, y1, z, x2, y1, z, x2, y2, z, x1, y2, z]
        else:
            x1 = self._x - img.anchor_x
            y1 = self._y - img.anchor_y
            x2 = x1 + img.width
            y2 = y1 + img.height
            z = self._z
            vertices = [x1, y1, z, x2, y1, z, x2, y2, z, x1, y2, z]
        if not self._subpixel:
            vertices = [int(v) for v in vertices]

        self._vertex_list.vertices[:] = vertices

    @property
    def z(self):
        """Z coordinate of the sprite.

        :type: int
        """
        return self._z

    @z.setter
    def z(self, z):
        self._z = z
        self._update_position()

    def update(self, x=None, y=None, z=None, rotation=None, scale=None, scale_x=None, scale_y=None):
        if x is not None:
            self._x = x
        if y is not None:
            self._y = y
        if z is not None:
            self._z = z
        if rotation is not None:
            self._rotation = rotation
        if scale is not None:
            self._scale = scale
        if scale_x is not None:
            self._scale_x = scale_x
        if scale_y is not None:
            self._scale_y = scale_y
        self._update_position()