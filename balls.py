import pyray as ray
import random
class Shape:
    shapes = []

    def __init__(self, position, velocity):
        self.position = position
        self.velocity = velocity
        Shape.shapes.append(self)

    def move(self):
        self.position = (self.position[0] + self.velocity[0], self.position[1] + self.velocity[1])

    @staticmethod
    def check_collisions():
        num_shapes = len(Shape.shapes)
        for i in range(num_shapes):
            shape1 = Shape.shapes[i]
            for j in range(i+1, num_shapes):
                shape2 = Shape.shapes[j]
                if isinstance(shape1, Circle) and isinstance(shape2, Circle):
                    dx = shape1.position[0] - shape2.position[0]
                    dy = shape1.position[1] - shape2.position[1]
                    distance = (dx**2 + dy**2)**0.5
                    if distance < shape1.radius + shape2.radius:
                        overlap = (shape1.radius + shape2.radius) - distance
                        overlap_dx = (dx / distance) * overlap
                        overlap_dy = (dy / distance) * overlap
                        shape1.position = (shape1.position[0] + overlap_dx, shape1.position[1] + overlap_dy)
                        shape2.position = (shape2.position[0] - overlap_dx, shape2.position[1] - overlap_dy)
                        shape1.velocity, shape2.velocity = shape2.velocity, shape1.velocity

class Circle(Shape):
    def __init__(self, position, velocity, radius):
        super().__init__(position, velocity)
        self.radius = radius

    def draw(self):
        ray.draw_circle_v(self.position, self.radius, ray.WHITE)
    def bounce(self, screen_width, screen_height):
        if self.position[0] - self.radius <= 0 or self.position[0] + self.radius >= screen_width:
            self.velocity = (-self.velocity[0], self.velocity[1])
            self.position = (max(self.radius, min(self.position[0], screen_width - self.radius)), self.position[1])
        if self.position[1] - self.radius <= 0 or self.position[1] + self.radius >= screen_height:
            self.velocity = (self.velocity[0], -self.velocity[1])
            self.position = (self.position[0], max(self.radius, min(self.position[1], screen_height - self.radius)))
def main():
    screen_width = 800
    screen_height = 600

    ray.init_window(screen_width, screen_height, "Balls")
    ray.set_target_fps(60)

    for i in range(random.randint(30, 40)):
        Circle((random.randint(0, screen_width), random.randint(0, screen_height)),
                              (random.randint(-10, 10), random.randint(-10, 10)),
                              random.randint(10, 20))

    while not ray.window_should_close():
        Shape.check_collisions()
        for shape in Shape.shapes:
            shape.move()
            shape.bounce(screen_width, screen_height)
        ray.begin_drawing()
        ray.clear_background(ray.BLACK)

        for circle in Shape.shapes:
            circle.draw()
        ray.end_drawing()

    ray.close_window()
if __name__ == "__main__":
    main()
