import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
import moderngl
import pytest

from pygame_easy_menu import (
    AlertBox, InputBox, Menu, Menu_Manager, ModernGLBackend, ScrollableBox,
    SurfaceBackend, Vector2, sprite,
)


def setup_module():
    pygame.init()
    pygame.display.set_mode((64, 64))


def teardown_module():
    pygame.quit()


def create_gl33_context():
    try:
        return moderngl.create_standalone_context(require=330)
    except Exception as error:
        pytest.skip(f"OpenGL 3.3 context unavailable on this runner: {error}")


def test_surface_backend_keeps_existing_menu_flow(tmp_path):
    image_path = tmp_path / "button.bmp"
    pygame.image.save(pygame.Surface((8, 8), pygame.SRCALPHA), str(image_path))
    target = pygame.Surface((64, 64), pygame.SRCALPHA)
    manager = Menu_Manager(window=target, auto_present=False)
    manager.running = True
    menu = Menu("main", manager)
    item = sprite("item", image_path, manager)
    item.set_position(Vector2(32, 32))
    menu.add(item)
    manager.actual_menu = menu

    manager.frame([])

    assert isinstance(manager.backend, SurfaceBackend)
    assert target.get_at((32, 32)).a == 255


def test_sprite_revision_tracks_assignment_and_in_place_changes(tmp_path):
    image_path = tmp_path / "sprite.bmp"
    pygame.image.save(pygame.Surface((4, 4), pygame.SRCALPHA), str(image_path))
    manager = Menu_Manager(window=pygame.Surface((16, 16)), auto_present=False)
    item = sprite("item", image_path, manager)
    initial = item.render_revision
    item.image.fill("red")
    item.mark_dirty(pygame.Rect(0, 0, 2, 2))
    assert item.render_revision == initial + 1
    item.set_image(item.image.copy())
    assert item.render_revision == initial + 2
    unchanged = item.render_revision
    item.image = item.image
    assert item.render_revision == unchanged


def test_backend_coordinate_conversion_is_stable():
    backend = SurfaceBackend(pygame.Surface((320, 180)))
    assert backend.window_to_logical((17.9, 22.1)) == (17, 22)


def test_moderngl_backend_draws_and_updates_a_texture_region():
    context = create_gl33_context()
    framebuffer = context.simple_framebuffer((8, 8), components=4)
    framebuffer.use()
    backend = ModernGLBackend.from_context(context, (8, 8), (8, 8))
    image = pygame.Surface((2, 2), pygame.SRCALPHA)
    image.fill("red")

    context.clear(0, 0, 0, 0)
    backend.begin()
    backend.draw_surface(image, pygame.Rect(0, 0, 8, 8), revision=0)
    backend.end()
    assert backend.texture_uploads == 1
    assert framebuffer.read(components=4)[0:4] == bytes((255, 0, 0, 255))

    image.set_at((0, 0), pygame.Color("green"))
    backend.update_surface_region(image, pygame.Rect(0, 0, 1, 1), revision=1)
    assert backend.texture_uploads == 1
    assert backend.region_uploads == 1
    context.clear(0, 0, 0, 0)
    backend.begin()
    backend.draw_surface(image, pygame.Rect(0, 0, 8, 8), revision=1)
    backend.end()
    assert backend.texture_uploads == 1
    assert framebuffer.read(
        viewport=(0, 7, 1, 1), components=4
    ) == bytes((0, 255, 0, 255))
    assert framebuffer.read(
        viewport=(0, 0, 1, 1), components=4
    ) == bytes((255, 0, 0, 255))
    backend.release()
    framebuffer.release()
    context.release()


def test_all_composite_widgets_render_with_moderngl(tmp_path):
    image_path = tmp_path / "widget.bmp"
    base = pygame.Surface((40, 20), pygame.SRCALPHA)
    base.fill("navy")
    pygame.image.save(base, str(image_path))
    context = create_gl33_context()
    framebuffer = context.simple_framebuffer((160, 90), components=4)
    framebuffer.use()
    backend = ModernGLBackend.from_context(context, (160, 90), (160, 90))
    manager = Menu_Manager(
        size=Vector2(160, 90), backend=backend, auto_present=False
    )
    manager.running = True
    menu = Menu("widgets", manager)

    input_box = InputBox("input", image_path, manager)
    input_box.set_position(Vector2(40, 15))
    alert = AlertBox("alert", image_path, manager)
    alert.set_position(Vector2(100, 15))
    alert.set_text("OpenGL alert text", align_center=True)
    scroll = ScrollableBox("scroll", (120, 45), manager)
    scroll.rect.topleft = (20, 40)
    child = sprite("child", image_path, manager)
    child.set_position(Vector2(50, 55))
    scroll.add_sprite(lambda: child)
    menu.add(input_box, alert, scroll)
    manager.actual_menu = menu

    manager.frame([
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (40, 15), "button": 1}),
        pygame.event.Event(pygame.TEXTINPUT, {"text": "A"}),
    ])

    assert input_box.text == "A"
    assert backend.texture_uploads >= 4
    child.image.set_at((0, 0), pygame.Color("green"))
    child.mark_dirty(pygame.Rect(0, 0, 1, 1))
    manager.render()
    assert backend.region_uploads == 1
    manager.release()
    framebuffer.release()
    context.release()
