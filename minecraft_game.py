from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina(title="Minecraft-Like Game", window_type='onscreen')
camera.position = (0, 10, 0)

# Настройки
TEXTURE_SCALE = 1
BLOCK_SIZE = 1
WORLD_SIZE = 16
HEIGHT = 8

# Текстуры для блоков
grass_texture = load_texture('https://www.minecraftskinstealer.com/skins/render/body/db6b2cdd-98f5-4c8d-a5a3-11bb6c9bb64d.png')
dirt_texture = load_texture('https://www.minecraftskinstealer.com/skins/render/body/db6b2cdd-98f5-4c8d-a5a3-11bb6c9bb64d.png')
stone_texture = load_texture('https://www.minecraftskinstealer.com/skins/render/body/db6b2cdd-98f5-4c8d-a5a3-11bb6c9bb64d.png')

# Словарь для хранения блоков
blocks = {}

def create_block(x, y, z, block_type='grass'):
    """Создание блока в позиции"""
    key = (x, y, z)
    if key in blocks:
        return

    # Выбор цвета в зависимости от типа блока
    if block_type == 'grass':
        color = color.green
    elif block_type == 'dirt':
        color = color.brown
    else:  # stone
        color = color.gray

    block = cube(
        pos=(x, y, z),
        size=BLOCK_SIZE,
        color=color,
        texture='white_cube'
    )
    block.block_type = block_type
    blocks[key] = block

def create_world():
    """Генерирование мира"""
    # Создаём землю
    for x in range(-WORLD_SIZE, WORLD_SIZE):
        for z in range(-WORLD_SIZE, WORLD_SIZE):
            # Высота с небольшой случайностью
            height = random.randint(1, 5) + 2
            for y in range(0, height):
                if y == height - 1:
                    create_block(x, y, z, 'grass')
                else:
                    create_block(x, y, z, 'dirt')

    # Каменные столбы
    for i in range(3):
        x = random.randint(-WORLD_SIZE, WORLD_SIZE)
        z = random.randint(-WORLD_SIZE, WORLD_SIZE)
        for y in range(6, 12):
            create_block(x, y, z, 'stone')

def raycast_from_camera(distance=10):
    """Проверка какой блок находится впереди камеры"""
    camera_pos = camera.position
    forward = camera.forward()

    closest_distance = float('inf')
    closest_block = None

    for distance_step in range(1, distance):
        check_pos = camera_pos + forward * distance_step

        for key, block in blocks.items():
            block_pos = block.position
            dist = distance(check_pos, block_pos)
            if dist < BLOCK_SIZE and dist < closest_distance:
                closest_distance = dist
                closest_block = block

    return closest_block

# Создание контроллера игрока
player = FirstPersonController(model='', speed=8, position=(0, 12, 0))

# Создание мира
create_world()

# Обработка щелчков
def input(key):
    """Обработка входных данных"""
    camera_pos = camera.position
    forward = camera.forward()

    if key == 'left mouse down':
        # Разрушение блока
        hit_info = raycast(origin=camera_pos, direction=forward, max_distance=10)
        if hit_info.hit:
            target_pos = hit_info.entity.position
            key = (int(target_pos.x), int(target_pos.y), int(target_pos.z))
            if key in blocks:
                destroy(blocks[key])
                del blocks[key]

    elif key == 'right mouse down':
        # Размещение блока
        hit_info = raycast(origin=camera_pos, direction=forward, max_distance=10)
        if hit_info.hit:
            normal = hit_info.normal
            # Находим позицию для нового блока
            new_pos = hit_info.world_point + Vec3(normal.x, normal.y, normal.z)
            x, y, z = int(round(new_pos.x)), int(round(new_pos.y)), int(round(new_pos.z))
            create_block(x, y, z, 'grass')

    elif key == 'space':
        # Прыжок
        player.velocity_y = 10

# Гравитация
def update():
    """Обновление физики"""
    global player

    # Простая гравитация
    if camera.y > 0:
        # Проверка коллизий
        camera.y -= 0.2

        # Проверяем есть ли блок внизу
        hit_info = raycast(origin=camera.position, direction=(0, -1, 0), max_distance=1.5)
        if hit_info.hit:
            camera.y = max(camera.y, hit_info.world_point.y + 1.7)

    # Предотвращение падения в ад
    if camera.y < -50:
        camera.position = (0, 15, 0)

# Инструкции
info_text = Text(
    text='ЛКМ - разрушить | ПКМ - строить | WASD - движение | SPACE - прыжок | ESC - выход',
    position=(-0.5, 0.45),
    scale=0.6,
    background=True,
    color=color.white
)

# Запуск
app.run()
