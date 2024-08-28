import pyray as pr
import random
import math

WIDTH = 800
HEIGHT = 600

NUM_FISH = 100
FISH_LENGTH = 20
MAX_LIFETIME = 60 
LIFETIME_INCREASE = 2
ENABLE_BREEDING = True
BREEDING_CHANCE = 0.001
MUTATION_RANGE = 0.1 
BREEDING_WINDOW = 10  

MIN_SPEED = 4
MAX_SPEED = 8.0
MIN_DETECTION_RANGE = 100
MAX_DETECTION_RANGE = 300

MAX_PELLETS = 200
PELLET_SPAWN_RATE = 0.4
PELLET_SIZE = 2
PELLET_EAT_DISTANCE = 5

class Pellet:
    def __init__(self, x=None, y=None):
        self.x = x if x is not None else random.randint(0, WIDTH)
        self.y = y if y is not None else random.randint(0, HEIGHT)
        self.color = pr.YELLOW

    def draw(self):
        pr.draw_circle(int(self.x), int(self.y), PELLET_SIZE, self.color)

class Fish:
    def __init__(self, detection_range=None, speed=None):
        self.speed = speed if speed is not None else random.uniform(MIN_SPEED, MAX_SPEED)
        self.detection_range = detection_range if detection_range is not None else random.uniform(MIN_DETECTION_RANGE, MAX_DETECTION_RANGE)
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.angle = random.uniform(0, 2 * math.pi)
        self.color = pr.Color(
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255),
            255
        )
        self.lifetime = MAX_LIFETIME

    def move(self, pellets):
        nearest_pellet = self.find_nearest_pellet(pellets)
        if nearest_pellet:
            dx, dy = self.calculate_shortest_distance(self.x, self.y, nearest_pellet.x, nearest_pellet.y)
            target_angle = math.atan2(dy, dx)
            angle_diff = (target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
            self.angle += max(min(angle_diff, 0.1), -0.1)

        self.x = (self.x + self.speed * math.cos(self.angle)) % WIDTH
        self.y = (self.y + self.speed * math.sin(self.angle)) % HEIGHT

        self.lifetime -= pr.get_frame_time()

    def draw(self):
        end_x = self.x + FISH_LENGTH * math.cos(self.angle)
        end_y = self.y + FISH_LENGTH * math.sin(self.angle)

        if 0 <= end_x < WIDTH and 0 <= end_y < HEIGHT:
            pr.draw_line(int(self.x), int(self.y), int(end_x), int(end_y), self.color)
        else:
            if end_x < 0:
                t = -self.x / (end_x - self.x)
                y_intersect = self.y + t * (end_y - self.y)
                pr.draw_line(int(self.x), int(self.y), 0, int(y_intersect), self.color)
                pr.draw_line(int(WIDTH-1), int(y_intersect), int((end_x + WIDTH) % WIDTH), int(end_y % HEIGHT), self.color)
            elif end_x >= WIDTH:
                t = (WIDTH - self.x) / (end_x - self.x)
                y_intersect = self.y + t * (end_y - self.y)
                pr.draw_line(int(self.x), int(self.y), int(WIDTH-1), int(y_intersect), self.color)
                pr.draw_line(0, int(y_intersect), int(end_x % WIDTH), int(end_y % HEIGHT), self.color)
            elif end_y < 0:
                t = -self.y / (end_y - self.y)
                x_intersect = self.x + t * (end_x - self.x)
                pr.draw_line(int(self.x), int(self.y), int(x_intersect), 0, self.color)
                pr.draw_line(int(x_intersect), int(HEIGHT-1), int(end_x % WIDTH), int((end_y + HEIGHT) % HEIGHT), self.color)
            elif end_y >= HEIGHT:
                t = (HEIGHT - self.y) / (end_y - self.y)
                x_intersect = self.x + t * (end_x - self.x)
                pr.draw_line(int(self.x), int(self.y), int(x_intersect), int(HEIGHT-1), self.color)
                pr.draw_line(int(x_intersect), 0, int(end_x % WIDTH), int(end_y % HEIGHT), self.color)

    def calculate_shortest_distance(self, x1, y1, x2, y2):
        dx = min((x2 - x1) % WIDTH, (x1 - x2) % WIDTH)
        dy = min((y2 - y1) % HEIGHT, (y1 - y2) % HEIGHT)
        if x2 < x1 and dx == (x2 - x1) % WIDTH:
            dx = -dx
        if y2 < y1 and dy == (y2 - y1) % HEIGHT:
            dy = -dy
        return dx, dy

    def find_nearest_pellet(self, pellets):
        nearest_pellet = None
        min_distance = float('inf')
        for pellet in pellets:
            dx, dy = self.calculate_shortest_distance(self.x, self.y, pellet.x, pellet.y)
            distance = math.sqrt(dx**2 + dy**2)
            angle_to_pellet = math.atan2(dy, dx)
            angle_diff = abs((angle_to_pellet - self.angle + math.pi) % (2 * math.pi) - math.pi)
            if distance < self.detection_range and distance < min_distance and angle_diff < math.pi/2:
                nearest_pellet = pellet
                min_distance = distance
        return nearest_pellet

    def is_dead(self):
        return self.lifetime <= 0

    def can_breed(self):
        return self.lifetime > MAX_LIFETIME - BREEDING_WINDOW

def check_fish_collision(fish1, fish2):
    dx, dy = fish1.calculate_shortest_distance(fish1.x, fish1.y, fish2.x, fish2.y)
    distance = math.sqrt(dx**2 + dy**2)
    return distance < FISH_LENGTH

def breed(fish1, fish2):
    avg_speed = (fish1.speed + fish2.speed) / 2
    speed_mutation = random.gauss(0, avg_speed * MUTATION_RANGE)
    new_speed = max(MIN_SPEED, min(MAX_SPEED, avg_speed + speed_mutation))

    avg_range = (fish1.detection_range + fish2.detection_range) / 2
    range_mutation = random.gauss(0, avg_range * MUTATION_RANGE)
    new_detection_range = max(MIN_DETECTION_RANGE, min(MAX_DETECTION_RANGE, avg_range + range_mutation))

    return Fish(speed=new_speed, detection_range=new_detection_range)

def main():
    pr.init_window(WIDTH, HEIGHT, "Fish")
    pr.set_target_fps(60)

    fish_population = [Fish() for _ in range(NUM_FISH)]
    pellets = [Pellet() for _ in range(MAX_PELLETS // 2)]

    while not pr.window_should_close():
        pr.begin_drawing()
        pr.clear_background(pr.BLACK)

        if pr.is_mouse_button_pressed(pr.MOUSE_LEFT_BUTTON):
            mouse_x = pr.get_mouse_x()
            mouse_y = pr.get_mouse_y()
            if len(pellets) < MAX_PELLETS:
                pellets.append(Pellet(mouse_x, mouse_y))

        for fish in fish_population:
            fish.move(pellets)
            fish.draw()

        for pellet in pellets:
            pellet.draw()

        pellets_to_remove = set()
        for fish in fish_population:
            for pellet in pellets:
                dx, dy = fish.calculate_shortest_distance(fish.x, fish.y, pellet.x, pellet.y)
                if math.sqrt(dx**2 + dy**2) < PELLET_EAT_DISTANCE:
                    pellets_to_remove.add(pellet)
                    fish.lifetime += LIFETIME_INCREASE
                    break

        pellets = [p for p in pellets if p not in pellets_to_remove]

        if len(pellets) < MAX_PELLETS and random.random() < PELLET_SPAWN_RATE:
            pellets.append(Pellet())

        new_fish = []
        if ENABLE_BREEDING:
            for i, fish1 in enumerate(fish_population):
                for fish2 in fish_population[i+1:]:
                    if check_fish_collision(fish1, fish2) and random.random() < BREEDING_CHANCE:
                        new_fish.append(breed(fish1, fish2))

        fish_population = [fish for fish in fish_population if not fish.is_dead()]
        fish_population.extend(new_fish)

        if fish_population:
            avg_speed = sum(fish.speed for fish in fish_population) / len(fish_population)
            min_speed = min(fish.speed for fish in fish_population)
            max_speed = max(fish.speed for fish in fish_population)
            avg_range = sum(fish.detection_range for fish in fish_population) / len(fish_population)
            min_range = min(fish.detection_range for fish in fish_population)
            max_range = max(fish.detection_range for fish in fish_population)

            pr.draw_text(f"Fish: {len(fish_population)}", 10, 10, 20, pr.WHITE)
            pr.draw_text(f"Average Speed: {avg_speed:.2f}", 10, 40, 20, pr.WHITE)
            pr.draw_text(f"Speed Range: {min_speed:.2f} - {max_speed:.2f}", 10, 70, 20, pr.WHITE)
            pr.draw_text(f"Average Detection: {avg_range:.2f}", 10, 100, 20, pr.WHITE)
            pr.draw_text(f"Detection Range: {min_range:.2f} - {max_range:.2f}", 10, 130, 20, pr.WHITE)
        else:
            pr.draw_text("No fish remaining", 10, 10, 20, pr.WHITE)

        pr.end_drawing()

    pr.close_window()

if __name__ == "__main__":
    main()