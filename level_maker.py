# ========================================================
# gameboy resolution is 160 x 144 with 16 x 16 tiles
# ========================================================
import pygame, sys, random, os, math, json
clock = pygame.time.Clock()
from pygame.locals import *

pygame.init()
WIN_WIDTH = 160 + 48
WIN_HEIGHT = 144
WIN_SCALE = 3

BASE_PATH = './'

display_window = pygame.display.set_mode((WIN_WIDTH * WIN_SCALE, WIN_HEIGHT * WIN_SCALE), 0, 32)
raw_window = pygame.Surface((WIN_WIDTH,WIN_HEIGHT))

canvas_rect = pygame.Rect(0,0, 160 * WIN_SCALE, 144 * WIN_SCALE)
subsurf = display_window.subsurface(canvas_rect)

playing = True

draw_grid = False

x_offset = 0
y_offset = 0


def load_image(path):
    img = pygame.image.load(BASE_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img

def load_dir(path) :
    images = []
    for img_name in sorted(os.listdir(BASE_PATH + path)):
        images.append(load_image(path + '/' + img_name))
    return images

frame_start = 0
frame_end = pygame.time.get_ticks()
dt = frame_end - frame_start
# ========================================
tile_palette = load_dir("tiles")
curr_brush = None
curr_brush_value = -1
canvas = {
    # tile coordinates : tile type in coord
}
painting = False
erasing = False
canvas_buffer = {}
# ========================================
while playing:
    frame_start = frame_end
    raw_window.fill((0,0,0))

    mouse_pos = pygame.mouse.get_pos()
    adjusted_mouse_pos = (
        math.floor( (mouse_pos[0]) / (16 * WIN_SCALE) ), 
        math.floor( (mouse_pos[1]) / (16 * WIN_SCALE) )
        )

    for event in pygame.event.get() :
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN : 
            if event.key == K_ESCAPE:
                playing = False
            if event.key == K_g :
                # toggle grid drawing
                draw_grid = not draw_grid
            if event.key == K_e :
                # export current canvas to json
                # Python types that map to JSON keys must be str, int, float, bool or None, only need to figure out how to map to one of those types
                # https://stackoverflow.com/questions/56403013/how-to-save-the-dictionary-that-have-tuple-keys
                # ISSUE WITH TUPLE KEYS ^^
                # better: https://stackoverflow.com/questions/12337583/saving-dictionary-whose-keys-are-tuples-with-json-python/12337657#12337657 
                draw_grid = False
                pygame.image.save(subsurf, "export.png")
                push_dict = {str(k): v for (k,v) in canvas.items()}
                with open("map.json", "w") as outfile:
                    json.dump(push_dict, outfile)
                print("MAP EXPORTED")
                # with open("map.json", "w") as outfile:
                #     json.dump(str(canvas), outfile)
            # we wanna think of holding one of the wasd keys as constantly adding an offset
            # if event.key == K_w : # up
            #     y_offset -= 4
            # if event.key == K_a : # left
            #     x_offset -= 4
            # if event.key == K_s : # down 
            #     y_offset += 4
            # if event.key == K_d : # right
            #     x_offset += 4
        if event.type == pygame.MOUSEBUTTONDOWN :
            click_coords = pygame.mouse.get_pos()
            # PALETTE CLICK
            if click_coords[0] > 160 * WIN_SCALE :
                # print("PALETTE CLICK")
                if event.button == 1:
                    # turn mouse click coords into tile array index
                    index = math.floor(((click_coords[0] / (WIN_SCALE *16)) - 1) % 3) + 3 * math.floor((click_coords[1] / (WIN_SCALE * 16)))
                    if index < len(tile_palette) :
                        curr_brush = tile_palette[index]
                        curr_brush_value = index
                    else :
                        curr_brush = None
            # CANVAS CLICK
            else :
                if event.button == 1 : 
                    painting = True
                    # take currently selected brush and place it at coords
                    # if curr_brush == None :
                    #     if adjusted_mouse_pos in canvas.keys() :
                    #         canvas.pop(adjusted_mouse_pos)
                    # else :
                    #     canvas[adjusted_mouse_pos] = curr_brush_value
                    
                    # print("click at " + str(adjusted_mouse_pos) + " with value " + str(curr_brush_value))
                    # print("New full canvas: ", canvas)
                if event.button == 3 :
                    erasing = True
        if event.type == pygame.MOUSEBUTTONUP :
            if painting :
                painting = False
                for key in canvas_buffer.keys() :
                    if canvas_buffer[key] != -1:
                        canvas[key] = canvas_buffer[key]
                canvas_buffer = {}
            elif erasing :
                erasing = False
                for key in canvas_buffer.keys() :
                    if key in canvas.keys() :
                        canvas.pop(key)

    if painting and adjusted_mouse_pos not in canvas.keys():
        if curr_brush == None : 
            pass
        else :
            canvas_buffer[adjusted_mouse_pos] = curr_brush_value
    elif erasing :
        canvas_buffer[adjusted_mouse_pos] = -1


    # PALETTE =========================================
    draw_pos = [0,0]
    for i in range(len(tile_palette)) :
        draw_pos[0] = 16 * 10 + (16 * (i % 3))
        if i % 3 == 0 and i != 0:
            draw_pos[1] += 16
        raw_window.blit(tile_palette[i], pygame.Rect(draw_pos, (16, 16)))
    # CANVAS ==========================================
    if draw_grid :
        # draw grid lines
        # NOTE: we don't need to adjust for win_scale because we're drawing directly onto the raw surface, which then gets scaled
        for i in range(0, WIN_WIDTH - 48) :
            if i % 16 == 0:
                pygame.draw.line(raw_window, (255, 0, 0), (i + x_offset, 0), (i + x_offset, WIN_HEIGHT))
        for i in range(0, WIN_HEIGHT) :
            if i % 16 == 0 :
                pygame.draw.line(raw_window, (255, 0, 0), (0, i + y_offset), (WIN_WIDTH - 48, i + y_offset))

        # get mouse position, normalize it to 16x16 grid, account for offset
        
        # print(adjusted_mouse_pos)
        if curr_brush != None :
            raw_window.blit(curr_brush, (adjusted_mouse_pos[0] * 16, adjusted_mouse_pos[1] * 16) )
                
    # RECALL: idx of this dict is the raw tile coords, capping at (9,8)
    for idx in canvas.keys() :
        draw_coords : tuple = tuple(16 * x for x in idx)
        # print(canvas, draw_coords)
        # WIN_SCALE comes later (I think)
        tile = canvas[idx]
        # print(tile)
        raw_window.blit(tile_palette[tile], draw_coords)
    

    # ========
    scaled_window = pygame.transform.scale(raw_window, display_window.get_size())
    display_window.blit(scaled_window, (0,0))
    pygame.display.update()

    # ========
    frame_end = pygame.time.get_ticks()
    dt = frame_end - frame_start
    clock.tick(60)

pygame.quit()
sys.exit()
