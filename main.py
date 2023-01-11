import pygame
from copy import deepcopy
from random import choice, randrange

W, H = 10, 20                           # кол-во клеток игрового поля
TILE = 45                               # размер клеток игрового поля
GAME_RES = W * TILE, H * TILE           # размер игрового поля
RES = 750, 940                          # размер игрового окна
FPS = 60                                # кадры в секунду
fall = False
first = True
cleared_lines = 0

pygame.init()
sc = pygame.display.set_mode(RES)
game_sc = pygame.Surface(GAME_RES)
clock = pygame.time.Clock()

grid = [pygame.Rect(x * TILE, y * TILE, TILE, TILE) for x in range(W) for y in range(H)]

figures_pos = [[(-1, 0), (-2, 0), (0, 0), (1, 0)],
               [(0, -1), (-1, -1), (-1, 0), (0, 0)],
               [(-1, 0), (-1, 1), (0, 0), (0, -1)],
               [(0, 0), (-1, 0), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, 0)]]

figures = [[pygame.Rect(x + W // 2, y + 1, 1, 1) for x, y in fig_pos] for fig_pos in figures_pos]
figure_rect = pygame.Rect(0, 0, TILE - 2, TILE - 2)
field = [[0 for i in range(W)] for j in range(H)]

anim_count, anim_speed, anim_limit = 0, 60, 2000

bg = pygame.image.load('img/bg.jpg').convert()
game_bg = pygame.image.load('img/bg2.jpg').convert()

main_font = pygame.font.Font('font/font.ttf', 65)
font = pygame.font.Font('font/font.ttf', 45)
main_font_small = pygame.font.Font('font/font.ttf', 40)
font_small = pygame.font.Font('font/font.ttf', 20)

title_tetris = main_font.render('TETRIS', True, pygame.Color('darkorange'))
title_score = font.render('score:', True, pygame.Color('green'))
title_record = font.render('record:', True, pygame.Color('purple'))
title_lines = font.render('lines:', True, pygame.Color('red'))
title_speed = font.render('level:', True, pygame.Color('orange'))

get_color = lambda: (randrange(30, 256), randrange(30, 256), randrange(30, 256))

figure, next_figure = deepcopy(choice(figures)), deepcopy(choice(figures))
color, next_color = get_color(), get_color()

score, lines, bonus_speed = 0, 0, 0
scores = {0: 0, 1: 100, 2: 300, 3: 900, 4: 2700}


def check_borders():
    if figure[i].x < 0 or figure[i].x > W - 1:
        return False
    elif figure[i].y > H - 1 or field[figure[i].y][figure[i].x]:
        return False
    return True


def get_record():
    try:
        with open('record') as f:
            return f.readline()
    except FileNotFoundError:
        with open('record', 'w') as f:
            f.write('0')


def set_record(record, score):
    rec = max(int(record), score)
    with open('record', 'w') as f:
        f.write(str(rec))


def pause_screen():
    pause = pygame.Surface((750, 940), pygame.SRCALPHA)
    pause.fill((0, 0, 255, 127))
    sc.blit(pause, (0, 0))


def show_text(text):
    titleSurf, titleRect = txtObjects(text, main_font_small, (255, 255, 0))
    titleRect.center = (int(RES[0] / 2) - 3, int(RES[1] / 2) - 3)
    sc.blit(titleSurf, titleRect)

    pressKeySurf, pressKeyRect = txtObjects('Нажмите любую клавишу для продолжения', font_small, (255, 255, 0))
    pressKeyRect.center = (int(RES[0] / 2), int(RES[1] / 2) + 100)
    sc.blit(pressKeySurf, pressKeyRect)

    while checkKeys() == None:
        pygame.display.update()
        clock.tick()


def txtObjects(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()


def checkKeys():
    for event in pygame.event.get([pygame.KEYDOWN, pygame.KEYUP]):
        if event.type == pygame.KEYUP:
            continue
        return event.key
    return None


while True:
    if first:
        show_text('Tetris')
    first = False
    record = get_record()
    dx, rotate = 0, False
    sc.blit(bg, (0, 0))
    sc.blit(game_sc, (20, 20))
    game_sc.blit(game_bg, (0, 0))

    # При заполнении линии будет нобольшая пауза
    for i in range(lines):
        pygame.time.wait(200)

    # Игровое управление
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                dx = -1
            elif event.key == pygame.K_RIGHT:
                dx = 1
            elif event.key == pygame.K_DOWN:
                anim_limit = 100
            elif event.key == pygame.K_UP:
                rotate = True
            elif event.key == pygame.K_SPACE:
                fall = True
            elif event.key == pygame.K_ESCAPE:
                pause_screen()
                show_text('Пауза')
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                anim_limit = 2000

    # движение по горизонтали
    figure_old = deepcopy(figure)
    for i in range(4):
        figure[i].x += dx
        if not check_borders():
            figure = deepcopy(figure_old)
            break

    # движение по вертикали
    anim_count += anim_speed + ((cleared_lines // 5) * 5)
    if anim_count > anim_limit or fall:
        anim_count = 0
        figure_old = deepcopy(figure)
        for i in range(4):
            figure[i].y += 1
            if not check_borders():
                for i in range(4):
                    field[figure_old[i].y][figure_old[i].x] = color
                figure, color = next_figure, next_color
                next_figure, next_color = deepcopy(choice(figures)), get_color()
                anim_limit = 2000
                fall = False
                break

    # Вращение фигур
    center = figure[0]
    figure_old = deepcopy(figure)
    if rotate:
        for i in range(4):
            x = figure[i].y - center.y
            y = figure[i].x - center.x
            figure[i].x = center.x - x
            figure[i].y = center.y + y
            if not check_borders():
                figure = deepcopy(figure_old)
                break

    # Проверка на заполнение линий
    line, lines = H - 1, 0
    for row in range(H - 1, -1, -1):
        count = 0
        for i in range(W):
            if field[row][i]:
                count += 1
            field[line][i] = field[row][i]
        if count < W:
            line -= 1
        else:
            lines += 1

    # Начисление очков за заполнение линий
    score += scores[lines]
    cleared_lines += lines

    # Сетка игры
    [pygame.draw.rect(game_sc, (40, 40, 40), i_rect, 1) for i_rect in grid]

    # Отрисовка фигур
    for i in range(4):
        figure_rect.x = figure[i].x * TILE
        figure_rect.y = figure[i].y * TILE
        pygame.draw.rect(game_sc, color, figure_rect)

    # Отрисовка поля
    for y, raw in enumerate(field):
        for x, col in enumerate(raw):
            if col:
                figure_rect.x, figure_rect.y = x * TILE, y * TILE
                pygame.draw.rect(game_sc, col, figure_rect)

    # Отрисовка будующей фигуры
    for i in range(4):
        figure_rect.x = next_figure[i].x * TILE + 380
        figure_rect.y = next_figure[i].y * TILE + 185
        pygame.draw.rect(sc, next_color, figure_rect)

    # Отрисовка текста
    sc.blit(title_tetris, (TILE * 10 + 30, -10))
    sc.blit(title_lines, (TILE * 12 - TILE * 0.5, 350))
    sc.blit(font.render(str(cleared_lines), True, pygame.Color('white')), (TILE * 12, 410))
    sc.blit(title_speed, (TILE * 12 - TILE * 0.5, 480))
    if cleared_lines // 5 + 1 <= 5:
        color_dif = 'green'
    elif cleared_lines // 5 + 1 <= 10:
        color_dif = 'darkorange'
    else:
        color_dif = 'red'
    sc.blit(font.render(str(cleared_lines // 5 + 1), True, pygame.Color(color_dif)), (TILE * 12, 550))
    sc.blit(title_score, (TILE * 12 - TILE * 0.5, 780))
    sc.blit(font.render(str(score), True, pygame.Color('white')), (TILE * 12, 840))
    sc.blit(title_record, (TILE * 12 - TILE * 0.5, 650))
    sc.blit(font.render(record, True, pygame.Color('white')), (TILE * 12, 710))

    # Проверка на проигрыш
    for i in range(W):
        if field[0][i]:
            set_record(record, score)
            field = [[0 for i in range(W)] for i in range(H)]
            anim_count, anim_speed, anim_limit = 0, 60, 2000
            score, cleared_lines = 0, 0
            pygame.time.wait(500)

    pygame.display.flip()
    clock.tick(FPS)