import pygame
import sys

pygame.init()
pygame.mixer.init()

info = pygame.display.Info()
W, H = info.current_w, info.current_h
win = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
pygame.display.set_caption("Parkour Land")
clock = pygame.time.Clock()

def load_bg(path):
    return pygame.transform.scale(pygame.image.load(path).convert(), (W, H))

bg1 = load_bg("Parkour game/background.jpeg")
bg2 = load_bg("Parkour game/background-2.png")

cat     = pygame.transform.scale(pygame.image.load("Parkour game/cat.png").convert_alpha(), (120, 120))
cat_l   = pygame.transform.flip(cat, True, False)

npc_img = pygame.transform.scale(pygame.image.load("Parkour game/Gato-npc.png").convert_alpha(), (220, 220))
npc_l   = pygame.transform.flip(npc_img, True, False)

jump_sfx = pygame.mixer.Sound("Parkour game/mario-jump.mp3")

font_sm   = pygame.font.SysFont("Arial", 20)
font_hint = pygame.font.SysFont("Arial", 22, bold=True)
font_lg   = pygame.font.SysFont("Arial", 64, bold=True)

BG1_GROUND_RATIO = 0.885          


BG2_PLATFORMS_RATIOS = [
    (0.000, 0.693, 0.225),  
    (0.303, 0.650, 0.369),  
    (0.416, 0.591, 0.480), 
    (0.510, 0.534, 0.590),  
    (0.640, 0.470, 0.720),   
    (0.766, 0.408, 1.000),  
]
BG2_Y_OFFSET = 50  

def scaled_platforms():
    return [pygame.Rect(int(l*W), int(t*H) + BG2_Y_OFFSET, int((r-l)*W), 20)
            for l, t, r in BG2_PLATFORMS_RATIOS]

GRAVITY   = 0.55
JUMP_VEL  = -14
SPEED     = 5
PLAYER_W, PLAYER_H = 120, 120


def fade(from_bg, to_bg, duration_ms=600):
    
    steps   = 30
    delay   = duration_ms // steps
    overlay = pygame.Surface((W, H))
    overlay.fill((0, 0, 0))
    for i in range(steps + 1):
        win.blit(from_bg, (0, 0))
        overlay.set_alpha(int(255 * i / steps))
        win.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(delay)
    for i in range(steps + 1):
        win.blit(to_bg, (0, 0))
        overlay.set_alpha(int(255 * (1 - i / steps)))
        win.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(delay)

def draw_dialogue(lines):
    box = pygame.Rect(40, 40, 480, 30 + len(lines) * 28)
    pygame.draw.rect(win, (0, 0, 0), box, border_radius=6)
    pygame.draw.rect(win, (255, 255, 255), box, 2, border_radius=6)
    for i, line in enumerate(lines):
        win.blit(font_sm.render(line, True, (255, 255, 255)), (58, 55 + i * 28))

stage = 1
bg    = bg1

ground_y1 = int(BG1_GROUND_RATIO * H) - PLAYER_H + 50  

NPC_X = int(0.35 * W) + 200
NPC_Y_OFFSET = 150   
npc_y_draw   = ground_y1 - 220 + NPC_Y_OFFSET
npc_rect_s1  = pygame.Rect(NPC_X, npc_y_draw, 220, 220)
NPC_HINT_DIST = 280   


platforms = scaled_platforms()
spawn_platform = platforms[0]


px = 60
py = ground_y1
vx = 0.0
vy = 0.0
prev_py     = py
on_ground   = False
facing_right = True

DLG_INTRO = ["Hey traveler!", "Welcome to Parkour Land.", "Press ← → to move, ↑ to jump.", "Press E to talk."]
DLG_ASK   = ["Ready to jump to Stage 2?", "Press Y = Yes   N = No"]
DLG_NO    = ["Come back when you're ready!"]
DLG_WIN   = []   

dialogue       = DLG_INTRO[:]
dlg_stage      = 0          
show_dlg       = False
npc_visible    = True
won            = False

running = True
while running:
    dt = clock.tick(60)

    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            
            if stage == 1 and npc_visible and event.key == pygame.K_e:
                p_rect = pygame.Rect(px, py, PLAYER_W, PLAYER_H)
                if p_rect.colliderect(npc_rect_s1):
                    if dlg_stage == 0:
                        show_dlg  = True
                        dlg_stage = 1
                        dialogue  = DLG_INTRO[:]
                    elif dlg_stage == 1:
                        dialogue  = DLG_ASK[:]
                        dlg_stage = 2

            if dlg_stage == 2:
                if event.key == pygame.K_y:
                    
                    fade(bg1, bg2)
                    bg    = bg2
                    stage = 2
                    platforms = scaled_platforms()
                    sp = platforms[0]                        
                    px = sp.left + 10
                    py = sp.top  - PLAYER_H
                    vy = 0.0
                    on_ground = True
                    vy = 0.0
                    npc_visible = False
                    show_dlg    = False
                    dlg_stage   = 0
                elif event.key == pygame.K_n:
                    dialogue  = DLG_NO[:]
                    dlg_stage = 3

    if not won:
        keys = pygame.key.get_pressed()

        vx = 0
        if keys[pygame.K_LEFT]:
            vx = -SPEED
            facing_right = False
        if keys[pygame.K_RIGHT]:
            vx = SPEED
            facing_right = True

        if keys[pygame.K_UP] and on_ground:
            vy = JUMP_VEL
            on_ground = False
            jump_sfx.play()

        
        vy += GRAVITY
        px += vx
        prev_py = py
        py += vy

        
        px = max(0, min(px, W - PLAYER_W))

        p_rect  = pygame.Rect(px, py, PLAYER_W, PLAYER_H)
        on_ground = False

        if stage == 1:
            
            if py + PLAYER_H >= ground_y1 + PLAYER_H:
                py        = ground_y1
                vy        = 0
                on_ground = True

        elif stage == 2:
            
            if vy >= 0:
                for plat in platforms:
                    prev_feet = prev_py + PLAYER_H
                    curr_feet = py      + PLAYER_H
                    horiz_ok  = (px + PLAYER_W > plat.left and px < plat.right)
                    if (horiz_ok and
                        prev_feet <= plat.top and
                        curr_feet >= plat.top):
                        py        = plat.top - PLAYER_H
                        vy        = 0
                        on_ground = True
                        break

            
            if py > H + 50:
                sp = platforms[0]
                px = sp.left + 10
                py = sp.top  - PLAYER_H
                vy = 0.0
                on_ground = True

            
            goal_plat = platforms[-1]
            if (not won and on_ground and
                px + PLAYER_W > goal_plat.left and
                px < goal_plat.right and
                py + PLAYER_H == goal_plat.top):
                won = True

    
    win.blit(bg, (0, 0))

    
    if stage == 1 and npc_visible:
        facing = px + PLAYER_W//2 < NPC_X
        win.blit(npc_img if facing else npc_l, (NPC_X, npc_y_draw))

        # "Press E" hint when player is close
        p_rect = pygame.Rect(px, py, PLAYER_W, PLAYER_H)
        dist = abs((px + PLAYER_W//2) - (NPC_X + 110))
        if dist < NPC_HINT_DIST and not show_dlg:
            hint = font_hint.render("Press E to talk", True, (255, 255, 100))
            hint_x = NPC_X + 110 - hint.get_width()//2
            hint_y = npc_y_draw - 36
            shadow = font_hint.render("Press E to talk", True, (0, 0, 0))
            win.blit(shadow, (hint_x + 2, hint_y + 2))
            win.blit(hint,   (hint_x, hint_y))

    
    sprite = cat if facing_right else cat_l
    win.blit(sprite, (px, py))

    
    p_rect = pygame.Rect(px, py, PLAYER_W, PLAYER_H)
    if show_dlg and stage == 1 and npc_visible and p_rect.colliderect(npc_rect_s1):
        draw_dialogue(dialogue)
    if show_dlg and stage == 1 and npc_visible and not p_rect.colliderect(npc_rect_s1):
        
        show_dlg  = False
        dlg_stage = 0
        dialogue  = DLG_INTRO[:]

    
    if won:
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        win.blit(overlay, (0, 0))
        text = font_lg.render(" You Win! ", True, (255, 215, 0))
        sub  = font_sm.render("Press ESC to quit", True, (255, 255, 255))
        win.blit(text, (W//2 - text.get_width()//2, H//2 - 60))
        win.blit(sub,  (W//2 - sub.get_width()//2,  H//2 + 20))

    pygame.display.flip()

pygame.quit()
sys.exit()