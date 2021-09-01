import time, math, pygame

GAIN = 0.1
PARKING_BAY_POSITION = 0.7, 0.1
PARKING_BAY_VELOCITY = 0.00005, -0.00001
CAR_IMAGE_FILENAME = './dot.png'
PARKING_BAY_IMAGE_FILENAME = './circle.png'
DISPLAY_DIMENSIONS = 800, 800
LEFT_KEYS = (pygame.K_LEFT, pygame.K_a, pygame.K_KP4, )
RIGHT_KEYS = (pygame.K_RIGHT, pygame.K_d, pygame.K_KP6, )
UP_KEYS = (pygame.K_UP, pygame.K_w, pygame.K_KP2, )
DOWN_KEYS = (pygame.K_DOWN, pygame.K_s, pygame.K_KP8, )
QUIT_KEYS = (pygame.K_ESCAPE, pygame.K_q, pygame.K_x, pygame.K_BREAK, pygame.K_END, )
ONE_MINUS_GAIN = 1.0 - GAIN


class Figure(object):
    def __init__(self, carpark, imageFilename, position, velocity=(0.0, 0.0)):
        self.image = pygame.image.load(imageFilename)
        self.width, self.height = self.image.get_size()
        self.originalPosition = self.px, self.py = position
        self.originalVelocity = self.vx, self.vy = velocity
        self.carpark = carpark
        self.parkwidth, self.parkheight = carpark.get_size()
        self.parkcolour = self.carpark.get_at((0, 0), )
        self.halfwidth, self.halfheight = self.width / 2, self.height / 2

    def reset(self):
        self.px, self.py = self.originalPosition
        self.vx, self.vy = self.originalVelocity

    def tick(self, erase=False):
        if erase:
            self.erase()
        self.updateVelocity()
        self.updatePosition()
        self.draw()

    def updatePosition(self):
        self.px += self.vx
        self.py += self.vy
        self.bounce()

    def bounce(self):
        if self.px < 0.0 or self.px > 1.0:
            self.vx *= -1
        if self.py < 0.0 or self.py > 1.0:
            self.vy *= -1

    def updateVelocity(self):
        pass

    def draw(self):
        self.carpark.blit(self.image, self.pixelCoords())

    def erase(self):
        self.carpark.fill(self.parkcolour, (*self.pixelCoords(), self.width, self.height))

    def pixelCoords(self, x=None, y=None):
        if x is None:
            x = self.px
        if y is None:
            y = self.py
        return (int(x * self.parkwidth - self.halfwidth),
                int(y * self.parkheight - self.halfheight))


class Car(Figure):
    def __init__(self, carpark, speed=0.0001, maxParkingSpeed=0.002, imageFilename=CAR_IMAGE_FILENAME, coords=(0.5, 0.5)):
        Figure.__init__(self, carpark, imageFilename, coords)
        self.reset()
        self.speed = speed
        self.image = pygame.image.load(imageFilename)
        self.width, self.height = self.image.get_size()
        self.px, self.py = coords
        self.maxParkingSpeedSquare = maxParkingSpeed * maxParkingSpeed
        shortEdge = min(self.width / self.parkwidth, self.height / self.parkheight)
        self.radiusSquare = shortEdge * shortEdge
        self.halfwidth, self.halfheight = self.width / 2, self.height / 2
        self.halfParkWidth = self.parkwidth / 2
        self.halfParkHeight = self.parkheight / 2
        self.quarterParkWidth = self.parkwidth / 4
        self.quarterParkHeight = self.parkheight / 4
        self.threeQuarterParkWidth = self.parkwidth - self.quarterParkWidth

    def reset(self):
        Figure.reset(self)
        self.topX, self.topY = 0.5, math.sqrt(3) / 2
        self.startTime = time.perf_counter()

    def bounce(self):
        if self.px < 0.0 or self.px > 1.0 or self.py < 0.0 or self.py > 1.0:
            self.reset()

    def updateVelocity(self):
        xSquared, ySquared = self.topX * self.topX, self.topY * self.topY
        self.vx = self.speed * (self.topX - 0.5)
        self.vy = self.speed * (((self.topX - xSquared) / self.topY) -
                                ((xSquared + ySquared - self.topX) / (2 * self.topY)))

    def draw(self, showTriangle=True, triangleColour=(255, 255, 252)):
        if showTriangle:
            tx, ty = (int(self.topX * self.halfParkWidth + self.quarterParkWidth),
                             int(self.topY * self.halfParkHeight + self.quarterParkHeight))
            pixelThird = ((self.quarterParkWidth, self.quarterParkHeight),
                          (tx, ty),
                          (self.threeQuarterParkWidth, self.quarterParkHeight))
            pygame.draw.polygon(self.carpark, triangleColour, pixelThird, 2)
        Figure.draw(self)


if __name__ == '__main__':
    screen = pygame.display.set_mode(DISPLAY_DIMENSIONS)
    car = Car(screen)
    parkingBay = Figure(screen, PARKING_BAY_IMAGE_FILENAME, PARKING_BAY_POSITION,
                        velocity=PARKING_BAY_VELOCITY)
    while True:
        screen.fill((0, 0, 0),)
        parkingBay.tick()
        car.tick()
        xDist, yDist = car.px - parkingBay.px, car.py - parkingBay.py
        squareDist = xDist * xDist + yDist * yDist
        if squareDist < car.radiusSquare:
            if ((abs(car.vx - parkingBay.vx) + abs(car.vy - parkingBay.vy))
                    < car.maxParkingSpeedSquare):
                print(time.perf_counter() - car.startTime)
                car.reset()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key in QUIT_KEYS:
                    exit()
                if event.key in LEFT_KEYS:
                    car.topX -= GAIN
                elif event.key in RIGHT_KEYS:
                    car.topX += GAIN
                elif event.key in UP_KEYS:
                    car.topY -= GAIN
                elif event.key in DOWN_KEYS:
                    car.topY += GAIN