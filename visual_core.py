"""The helper functions for the visuals are defined here.
These functions provide textures or modify pygame Surfaces or Rects in ways which
are convenient to use for multiple scenes."""
import pygame

# This dict contains references to all textures which are loaded with get_texture(),
# and functions as a cache. With this technique, textures are not loaded multiple
# times, but are also not all loaded at startup, making startup faster.
loaded_textures = {}
standard_font = None


def get_texture(name: str):
    """Returns a texture from loaded_textures if it exists, else it loads the texture from memory.
    The file format of the texture is assumed to be png."""
    try:
        return loaded_textures[name]
    except KeyError:
        loaded_textures[name] = pygame.image.load(f"textures\\{name}.png").convert_alpha()
        return loaded_textures[name]


def crop_whitespace(surf: pygame.Surface):
    rect = surf.get_bounding_rect()
    new_surf = pygame.Surface(rect.size, pygame.SRCALPHA)
    new_surf.blit(surf, (0,0), rect)
    return new_surf, surf.get_rect()


def render_text(text: str):
    """Returns a surface containing the rendered text with standard settings
    and the standard pokémon font."""
    global standard_font
    if not standard_font:
        # The font does not scale; the size is therefore arbitrary
        standard_font = pygame.font.Font("PKMNRSEU.FON", 1)
    return standard_font.render(text, False, (0,0,0))


def render_number(num: int):
    assert type(num) is int, f"The type of num should be int, its value is '{num}'."
    digit_height = 7
    digit_x_pos = [0, 9, 17, 26, 35, 44, 53, 62, 71, 80, 89]
    digit_width = [digit_x_pos[i]-digit_x_pos[i-1] for i in range(1, len(digit_x_pos))]
    text = str(num)
    total_width = sum(digit_width[int(x)] for x in text)
    surf = pygame.Surface((total_width, digit_height), pygame.SRCALPHA)
    current_pos = 0
    for digit in text:
        surf.blit(
            get_texture("hpbars"),
            (current_pos, 0),
            pygame.Rect(digit_x_pos[int(digit)], 110, digit_width[int(digit)], digit_height)
        )
        current_pos += digit_width[int(digit)]
    return surf
