"""Rendering backends for pygame-easy-menu.

The default backend keeps the historical pygame Surface behaviour.  The
ModernGL backend renders the same widget tree directly into an OpenGL 3.3
context and only uploads a Surface when its revision changes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol, Sequence

import pygame


Color = tuple[float, float, float, float]


class RenderBackend(Protocol):
    """Small interface consumed by :class:`Menu_Manager`."""

    logical_size: tuple[int, int]

    def begin(self) -> None: ...

    def draw_surface(
        self,
        surface: pygame.Surface,
        destination: pygame.Rect | Sequence[float],
        *,
        source_rect: pygame.Rect | None = None,
        tint: Color = (1.0, 1.0, 1.0, 1.0),
        opacity: float = 1.0,
        angle: float = 0.0,
        flip_x: bool = False,
        flip_y: bool = False,
        revision: int = 0,
    ) -> None: ...

    def draw_widget(self, widget, destination: pygame.Rect | None = None) -> None: ...

    def push_clip(self, rect: pygame.Rect) -> None: ...

    def pop_clip(self) -> None: ...

    def end(self) -> None: ...

    def present(self) -> None: ...

    def window_to_logical(self, position: Sequence[float]) -> tuple[int, int]: ...

    def release(self) -> None: ...


class SurfaceBackend:
    """Historical pygame Surface renderer."""

    def __init__(self, surface: pygame.Surface):
        self.surface = surface
        self.logical_size = surface.get_size()
        self._clips: list[pygame.Rect | None] = []

    def begin(self) -> None:
        return None

    def draw_surface(
        self,
        surface: pygame.Surface,
        destination: pygame.Rect | Sequence[float],
        *,
        source_rect: pygame.Rect | None = None,
        tint: Color = (1.0, 1.0, 1.0, 1.0),
        opacity: float = 1.0,
        angle: float = 0.0,
        flip_x: bool = False,
        flip_y: bool = False,
        revision: int = 0,
    ) -> None:
        rect = pygame.Rect(destination)
        image = surface if source_rect is None else surface.subsurface(source_rect)
        if image.get_size() != rect.size:
            image = pygame.transform.scale(image, rect.size)
        if flip_x or flip_y:
            image = pygame.transform.flip(image, flip_x, flip_y)
        if angle:
            image = pygame.transform.rotate(image, angle)
            rect = image.get_rect(center=rect.center)
        if tint != (1.0, 1.0, 1.0, 1.0) or opacity != 1.0:
            image = image.copy()
            rgba = tuple(max(0, min(255, round(value * 255))) for value in tint)
            image.fill(rgba, special_flags=pygame.BLEND_RGBA_MULT)
            image.set_alpha(max(0, min(255, round(opacity * 255))))
        self.surface.blit(image, rect)

    def draw_widget(self, widget, destination: pygame.Rect | None = None) -> None:
        if not getattr(widget, "isactive", True):
            return
        rect = destination or widget.rect
        self.draw_surface(
            widget.image,
            rect,
            source_rect=getattr(widget, "source_rect", None),
            tint=getattr(widget, "tint", (1.0, 1.0, 1.0, 1.0)),
            opacity=getattr(widget, "opacity", 1.0),
            angle=getattr(widget, "angle", 0.0),
            flip_x=getattr(widget, "flip_x", False),
            flip_y=getattr(widget, "flip_y", False),
            revision=getattr(widget, "render_revision", 0),
        )
        text_surface = getattr(widget, "txt_surface", None)
        if text_surface is not None:
            text_rect = (
                text_surface.get_rect(center=rect.center)
                if getattr(widget, "text_centered", False)
                else text_surface.get_rect(
                    midleft=(rect.left + int(rect.width * 0.05), rect.centery)
                )
            )
            self.draw_surface(
                text_surface, text_rect,
                revision=getattr(widget, "text_revision", 0),
            )
            if getattr(widget, "active", False) and pygame.time.get_ticks() % 1000 > 500:
                pygame.draw.rect(
                    self.surface,
                    getattr(widget, "text_color", "white"),
                    pygame.Rect(text_rect.right, text_rect.top, 3, text_rect.height),
                )

    def push_clip(self, rect: pygame.Rect) -> None:
        self._clips.append(self.surface.get_clip())
        self.surface.set_clip(rect)

    def pop_clip(self) -> None:
        if self._clips:
            self.surface.set_clip(self._clips.pop())

    def end(self) -> None:
        return None

    @staticmethod
    def present() -> None:
        pygame.display.update()

    def window_to_logical(self, position: Sequence[float]) -> tuple[int, int]:
        return int(position[0]), int(position[1])

    def release(self) -> None:
        self._clips.clear()


@dataclass
class _TextureEntry:
    texture: object
    size: tuple[int, int]
    revision: int


@dataclass
class _Command:
    texture: object
    instance: tuple[float, ...]
    clip: Optional[tuple[int, int, int, int]]


class ModernGLBackend:
    """OpenGL 3.3 renderer for pygame menu trees.

    Importing this module does not require ModernGL.  It is imported lazily
    when this backend is constructed, which keeps the default Surface backend
    usable without the optional ``opengl`` dependency.
    """

    _VERTEX_SHADER = """
        #version 330
        in vec2 in_position;
        in vec4 in_destination;
        in vec4 in_uv;
        in vec4 in_tint;
        in float in_angle;
        in vec2 in_origin;

        uniform vec2 logical_size;

        out vec2 uv;
        out vec4 tint;

        void main() {
            vec2 local = (in_position - in_origin) * in_destination.zw;
            float angle = radians(in_angle);
            mat2 rotation = mat2(cos(angle), sin(angle), -sin(angle), cos(angle));
            vec2 pixel = rotation * local + in_destination.xy + in_origin * in_destination.zw;
            vec2 ndc = vec2(pixel.x / logical_size.x * 2.0 - 1.0,
                            1.0 - pixel.y / logical_size.y * 2.0);
            gl_Position = vec4(ndc, 0.0, 1.0);
            uv = mix(in_uv.xy, in_uv.zw, in_position);
            tint = in_tint;
        }
    """

    _FRAGMENT_SHADER = """
        #version 330
        uniform sampler2D image_texture;
        in vec2 uv;
        in vec4 tint;
        out vec4 fragment_color;

        void main() {
            fragment_color = texture(image_texture, uv) * tint;
        }
    """

    def __init__(
        self,
        context,
        logical_size: Sequence[int],
        framebuffer_size: Sequence[int],
        *,
        owns_context: bool = False,
    ):
        import moderngl

        self.moderngl = moderngl
        self.context = context
        self.logical_size = (int(logical_size[0]), int(logical_size[1]))
        self.framebuffer_size = (int(framebuffer_size[0]), int(framebuffer_size[1]))
        self.owns_context = owns_context
        self._textures: dict[int, _TextureEntry] = {}
        self.texture_uploads = 0
        self.region_uploads = 0
        self._commands: list[_Command] = []
        self._clips: list[pygame.Rect] = []
        self._program = context.program(
            vertex_shader=self._VERTEX_SHADER,
            fragment_shader=self._FRAGMENT_SHADER,
        )
        self._program["logical_size"].value = self.logical_size
        self._program["image_texture"].value = 0
        vertices = __import__("struct").pack(
            "12f", 0.0, 0.0, 1.0, 0.0, 0.0, 1.0,
            0.0, 1.0, 1.0, 0.0, 1.0, 1.0,
        )
        self._quad_buffer = context.buffer(vertices)
        self._instance_buffer = context.buffer(reserve=15 * 4 * 256, dynamic=True)
        self._vao = context.vertex_array(
            self._program,
            [
                (self._quad_buffer, "2f", "in_position"),
                (
                    self._instance_buffer,
                    "4f 4f 4f 1f 2f /i",
                    "in_destination",
                    "in_uv",
                    "in_tint",
                    "in_angle",
                    "in_origin",
                ),
            ],
        )
        context.enable(moderngl.BLEND)
        context.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        self._white_surface = pygame.Surface((1, 1), pygame.SRCALPHA)
        self._white_surface.fill("white")

    @classmethod
    def create_window(
        cls,
        size: Sequence[int],
        *,
        logical_size: Sequence[int] | None = None,
        caption: str | None = None,
        fullscreen: bool = False,
        vsync: bool = True,
    ) -> "ModernGLBackend":
        import moderngl

        pygame.init()
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(
            pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE
        )
        flags = pygame.OPENGL | pygame.DOUBLEBUF
        if fullscreen:
            flags |= pygame.FULLSCREEN
        pygame.display.set_mode(tuple(size), flags, vsync=1 if vsync else 0)
        if caption:
            pygame.display.set_caption(caption)
        context = moderngl.create_context(require=330)
        return cls(
            context,
            logical_size or size,
            pygame.display.get_window_size(),
            owns_context=True,
        )

    @classmethod
    def from_context(
        cls,
        context,
        logical_size: Sequence[int],
        framebuffer_size: Sequence[int],
    ) -> "ModernGLBackend":
        return cls(context, logical_size, framebuffer_size, owns_context=False)

    def resize(self, framebuffer_size: Sequence[int]) -> None:
        self.framebuffer_size = (int(framebuffer_size[0]), int(framebuffer_size[1]))

    def configure_view(
        self,
        logical_size: Sequence[int],
        framebuffer_size: Sequence[int] | None = None,
    ) -> None:
        self.logical_size = (int(logical_size[0]), int(logical_size[1]))
        if framebuffer_size is not None:
            self.resize(framebuffer_size)
        self._program["logical_size"].value = self.logical_size

    @property
    def texture_count(self) -> int:
        return len(self._textures)

    def begin(self) -> None:
        self._commands.clear()
        self._clips.clear()
        self.context.viewport = (0, 0, *self.framebuffer_size)

    def _texture_for(self, surface: pygame.Surface, revision: int):
        key = id(surface)
        size = surface.get_size()
        entry = self._textures.get(key)
        if entry is None or entry.size != size:
            if entry is not None:
                entry.texture.release()
            texture = self.context.texture(size, 4)
            texture.filter = (self.moderngl.NEAREST, self.moderngl.NEAREST)
            texture.repeat_x = False
            texture.repeat_y = False
            texture.write(pygame.image.tobytes(surface, "RGBA", True))
            self.texture_uploads += 1
            entry = _TextureEntry(texture, size, revision)
            self._textures[key] = entry
        elif entry.revision != revision:
            entry.texture.write(pygame.image.tobytes(surface, "RGBA", True))
            self.texture_uploads += 1
            entry.revision = revision
        return entry.texture

    def update_surface_region(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        *,
        revision: int,
    ) -> None:
        rect = pygame.Rect(rect).clip(surface.get_rect())
        if rect.width <= 0 or rect.height <= 0:
            return
        texture = self._texture_for(surface, revision - 1)
        pixels = pygame.image.tobytes(surface.subsurface(rect), "RGBA", True)
        texture.write(
            pixels,
            viewport=(rect.x, surface.get_height() - rect.bottom, rect.width, rect.height),
        )
        self.region_uploads += 1
        self._textures[id(surface)].revision = revision

    def _current_clip(self) -> Optional[tuple[int, int, int, int]]:
        if not self._clips:
            return None
        clip = self._clips[-1]
        sx = self.framebuffer_size[0] / self.logical_size[0]
        sy = self.framebuffer_size[1] / self.logical_size[1]
        return (
            round(clip.x * sx),
            round((self.logical_size[1] - clip.bottom) * sy),
            round(clip.width * sx),
            round(clip.height * sy),
        )

    def draw_surface(
        self,
        surface: pygame.Surface,
        destination: pygame.Rect | Sequence[float],
        *,
        source_rect: pygame.Rect | None = None,
        tint: Color = (1.0, 1.0, 1.0, 1.0),
        opacity: float = 1.0,
        angle: float = 0.0,
        flip_x: bool = False,
        flip_y: bool = False,
        revision: int = 0,
    ) -> None:
        if surface is None:
            return
        destination = pygame.Rect(destination)
        source = pygame.Rect(source_rect or surface.get_rect())
        width, height = surface.get_size()
        left = source.left / width
        right = source.right / width
        top = 1.0 - source.top / height
        bottom = 1.0 - source.bottom / height
        if flip_x:
            left, right = right, left
        if flip_y:
            top, bottom = bottom, top
        alpha = max(0.0, min(1.0, opacity))
        color = tuple(float(value) for value in tint)
        instance = (
            float(destination.x), float(destination.y),
            float(destination.width), float(destination.height),
            left, top, right, bottom,
            color[0], color[1], color[2], color[3] * alpha,
            float(angle), 0.5, 0.5,
        )
        self._commands.append(
            _Command(self._texture_for(surface, revision), instance, self._current_clip())
        )

    def draw_widget(self, widget, destination: pygame.Rect | None = None) -> None:
        if not getattr(widget, "isactive", True):
            return
        rect = pygame.Rect(destination or widget.rect)
        # ScrollableBox is rendered recursively; asking for its image would
        # rebuild two large CPU surfaces every frame.
        if hasattr(widget, "sprites") and hasattr(widget, "offset"):
            self.push_clip(rect)
            offset_y = int(widget.offset.y)
            for child in widget.sprites:
                child_rect = child.rect.move(0, -offset_y)
                self.draw_widget(child, child_rect)
            self.pop_clip()
            cursor = getattr(widget, "cursor", None)
            if cursor is not None:
                maximum = max(0, widget.get_max())
                factor = rect.height / (rect.height + maximum) if maximum else 1.0
                cursor_rect = cursor.get_rect(
                    topright=(rect.right, rect.top + round(widget.offset.y * factor))
                )
                self.draw_surface(cursor, cursor_rect, revision=getattr(widget, "render_revision", 0))
            return
        dirty_rect = getattr(widget, "_dirty_rect", None)
        if isinstance(dirty_rect, pygame.Rect):
            self.update_surface_region(
                widget.image,
                dirty_rect,
                revision=getattr(widget, "render_revision", 0),
            )
            widget._dirty_rect = None
        self.draw_surface(
            widget.image,
            rect,
            source_rect=getattr(widget, "source_rect", None),
            tint=getattr(widget, "tint", (1.0, 1.0, 1.0, 1.0)),
            opacity=getattr(widget, "opacity", 1.0),
            angle=getattr(widget, "angle", 0.0),
            flip_x=getattr(widget, "flip_x", False),
            flip_y=getattr(widget, "flip_y", False),
            revision=getattr(widget, "render_revision", 0),
        )
        text_surface = getattr(widget, "txt_surface", None)
        if text_surface is not None:
            text_rect = (
                text_surface.get_rect(center=rect.center)
                if getattr(widget, "text_centered", False)
                else text_surface.get_rect(
                    midleft=(rect.left + int(rect.width * 0.05), rect.centery)
                )
            )
            self.draw_surface(
                text_surface, text_rect,
                revision=getattr(widget, "text_revision", 0),
            )
            if getattr(widget, "active", False) and pygame.time.get_ticks() % 1000 > 500:
                color = pygame.Color(getattr(widget, "text_color", "white"))
                self.draw_surface(
                    self._white_surface,
                    pygame.Rect(text_rect.right, text_rect.top, 3, text_rect.height),
                    tint=(color.r / 255, color.g / 255, color.b / 255, color.a / 255),
                )
        for child in getattr(widget, "childs", ()) or ():
            if not isinstance(child, str):
                self.draw_widget(child)

    def push_clip(self, rect: pygame.Rect) -> None:
        clip = pygame.Rect(rect)
        if self._clips:
            clip.clip_ip(self._clips[-1])
        self._clips.append(clip)

    def pop_clip(self) -> None:
        if self._clips:
            self._clips.pop()

    def end(self) -> None:
        import struct

        index = 0
        while index < len(self._commands):
            first = self._commands[index]
            instances = [first.instance]
            index += 1
            while index < len(self._commands):
                command = self._commands[index]
                if command.texture is not first.texture or command.clip != first.clip:
                    break
                instances.append(command.instance)
                index += 1
            payload = struct.pack(f"{len(instances) * 15}f", *(v for row in instances for v in row))
            if len(payload) > self._instance_buffer.size:
                self._instance_buffer.orphan(len(payload))
            self._instance_buffer.write(payload)
            self.context.scissor = first.clip
            first.texture.use(0)
            self._vao.render(self.moderngl.TRIANGLES, instances=len(instances))
        self.context.scissor = None

    @staticmethod
    def present() -> None:
        pygame.display.flip()

    def window_to_logical(self, position: Sequence[float]) -> tuple[int, int]:
        x = int(position[0] * self.logical_size[0] / self.framebuffer_size[0])
        y = int(position[1] * self.logical_size[1] / self.framebuffer_size[1])
        return x, y

    def release(self) -> None:
        for entry in self._textures.values():
            entry.texture.release()
        self._textures.clear()
        self._vao.release()
        self._instance_buffer.release()
        self._quad_buffer.release()
        self._program.release()
        if self.owns_context:
            self.context.release()
