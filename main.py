import wireframe
import pygame
import numpy as np

class ProjectionViewer:
    """Displays 3D objects on a Pygame screen"""

    DRAW_DIST = 25

    TRANSLATION_AMOUNT = 2

    SCALE_AMOUNT = 1.02
    N_SCALE_AMOUNT = 1/SCALE_AMOUNT

    ROTATION_AMOUNT = 0.04
    C_ROTATION_AMOUNT = np.cos(ROTATION_AMOUNT)
    N_C_ROTATION_AMOUNT = np.cos(-ROTATION_AMOUNT)
    S_ROTATION_AMOUNT = np.sin(ROTATION_AMOUNT)
    N_S_ROTATION_AMOUNT = np.sin(-ROTATION_AMOUNT)

    CAMERA_AMOUNT = 1.02
    N_CAMERA_AMOUNT = 1/CAMERA_AMOUNT

    FORWARD = np.array(
        [[1,0,0,0],
         [0,1,0,0],
         [0,0,1,0],
         [0,0,-TRANSLATION_AMOUNT,1]]
    )

    BACKWARD = np.array(
        [[1,0,0,0],
         [0,1,0,0],
         [0,0,1,0],
         [0,0,TRANSLATION_AMOUNT,1]]
    )

    LEFT = np.array(
        [[1,0,0,0],
         [0,1,0,0],
         [0,0,1,0],
         [TRANSLATION_AMOUNT,0,0,1]]
    )

    RIGHT = np.array(
        [[1,0,0,0],
         [0,1,0,0],
         [0,0,1,0],
         [-TRANSLATION_AMOUNT,0,0,1]]
    )

    SCALEUP = np.array(
        [[SCALE_AMOUNT,0,0,0],
         [0,SCALE_AMOUNT,0,0],
         [0,0,SCALE_AMOUNT,0],
         [0,0,0,1]]
    )

    SCALEDOWN = np.array(
        [[N_SCALE_AMOUNT,0,0,0],
         [0,N_SCALE_AMOUNT,0,0],
         [0,0,N_SCALE_AMOUNT,0],
         [0,0,0,1]]
    )

    ROTATE_X = np.array(
        [[1,0,0,0],
         [0,C_ROTATION_AMOUNT,-S_ROTATION_AMOUNT,0],
         [0,S_ROTATION_AMOUNT,C_ROTATION_AMOUNT,0],
         [0,0,0,1]]
    )

    N_ROTATE_X = np.array(
        [[1,0,0,0],
         [0,N_C_ROTATION_AMOUNT,-N_S_ROTATION_AMOUNT,0],
         [0,N_S_ROTATION_AMOUNT,N_C_ROTATION_AMOUNT,0],
         [0,0,0,1]]
    )

    ROTATE_Y = np.array(
        [[C_ROTATION_AMOUNT,0,S_ROTATION_AMOUNT,0],
         [0,1,0,0],
         [-S_ROTATION_AMOUNT,0,C_ROTATION_AMOUNT,0],
         [0,0,0,1]]
    )

    N_ROTATE_Y = np.array(
        [[N_C_ROTATION_AMOUNT,0,N_S_ROTATION_AMOUNT,0],
         [0,1,0,0],
         [-N_S_ROTATION_AMOUNT,0,N_C_ROTATION_AMOUNT,0],
         [0,0,0,1]]
    )

    ROTATE_Z = np.array(
        [[C_ROTATION_AMOUNT,-S_ROTATION_AMOUNT,0,0],
         [S_ROTATION_AMOUNT,C_ROTATION_AMOUNT,0,0],
         [0,0,1,0],
         [0,0,0,1]]
    )

    N_ROTATE_Z = np.array(
        [[N_C_ROTATION_AMOUNT,-N_S_ROTATION_AMOUNT,0,0],
         [N_S_ROTATION_AMOUNT,N_C_ROTATION_AMOUNT,0,0],
         [0,0,1,0],
         [0,0,0,1]]
    )

    KEY_TO_MATRIX = {
        pygame.K_LEFT: N_ROTATE_Y,
        pygame.K_RIGHT: ROTATE_Y,
        pygame.K_DOWN: N_ROTATE_X,
        pygame.K_UP: ROTATE_X,

        pygame.K_EQUALS: SCALEDOWN,
        pygame.K_MINUS: SCALEUP,

        pygame.K_q: N_ROTATE_Z,
        pygame.K_e: ROTATE_Z,

        pygame.K_w: FORWARD,
        pygame.K_s: BACKWARD,
        pygame.K_a: LEFT,
        pygame.K_d: RIGHT
    }

    def __init__(self, width, height):
        self.width = width
        self.halfWidth = width / 2
        self.height = height
        self.halfHeight = height / 2

        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Wireframe Display')
        self.background = (10,10,10)

        self.wireframes = {}
        self.displayNodes = False
        self.displayEdges = True
        self.nodeColor = (255,255,255)
        self.edgeColor = (200,200,200)
        self.nodeRadius = 2

        self.keySet = set()

        self.camDist = np.sqrt(self.halfWidth**2 + self.halfHeight**2)

    def run(self):
        """Create a pygame screen until it is closed."""

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_n:
                        self.displayNodes = not self.displayNodes
                    elif event.key == pygame.K_m:
                        self.displayEdges = not self.displayEdges
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        self.keySet.add(event.key)
                elif event.type == pygame.KEYUP:
                    self.keySet.discard(event.key)

            self.handleKeys()

            self.display()
            pygame.display.flip()
            pygame.time.wait(5)

    def handleKeys(self):
        i = iter(self.keySet)
        matrix = None

        for key in i:
            if key in self.KEY_TO_MATRIX:
                matrix = self.KEY_TO_MATRIX[key]
                break

        for key in i:
            if key in self.KEY_TO_MATRIX:
                matrix = np.dot(matrix, self.KEY_TO_MATRIX[key])

        if matrix is not None:
            self.transformAll(matrix)

        if pygame.K_i in self.keySet:
            self.zoom(self.CAMERA_AMOUNT)

        if pygame.K_o in self.keySet:
            self.zoom(self.N_CAMERA_AMOUNT)

        if pygame.K_EQUALS in self.keySet:
            self.nodeRadius *= self.N_SCALE_AMOUNT

        if pygame.K_MINUS in self.keySet:
            self.nodeRadius *= self.SCALE_AMOUNT

    def transformAll(self, matrix):
        for wireframe in self.wireframes.values():
            wireframe.transform(matrix)

    def zoom(self, d):
        self.camDist *= d

    def addWireframe(self, name, wireframe):
        self.wireframes[name] = wireframe

    def display(self):
        """Draw the wireframes on the screen."""

        self.screen.fill(self.background)

        if self.displayEdges:
            self.de()

        if self.displayNodes:
            self.dn()

    def de(self):
        for wireframe in self.wireframes.values():
            n = wireframe.nodes

            for i1, i2 in wireframe.edges:
                node1 = n[i1]
                node2 = n[i2]

                if node1[2] < 1 or node2[2] < 1:
                    continue

                dist = np.sqrt(node1[0]*node1[0] + node1[1]*node1[1] + node1[2]*node1[2])

                if dist < 1:
                    continue

                incl = np.arccos(node1[2]/dist)
                az = np.arctan2(node1[1], node1[0])

                node2d1 = self.perspective(incl, az)

                dist = np.sqrt(node2[0]*node2[0] + node2[1]*node2[1] + node2[2]*node2[2])

                if dist < 1:
                    continue

                incl = np.arccos(node2[2]/dist)
                az = np.arctan2(node2[1], node2[0])

                node2d2 = self.perspective(incl, az)

                x, y, length = self.calcLen(node2d1, node2d2)

                if (length <= 0 or
                    node2d1[0] <= -x or node2d1[0] >= self.width+x or
                    node2d1[1] <= -y or node2d1[1] >= self.height+y or
                    node2d2[0] <= -x or node2d2[0] >= self.width+x or
                    node2d2[1] <= -y or node2d2[1] >= self.height+y):
                    continue

                pygame.draw.aaline(self.screen, self.edgeColor,
                    node2d1,
                    node2d2
                )

    def calcLen(self, node2d1, node2d2):
        x = abs(node2d2[0] - node2d1[0])
        y = abs(node2d2[1] - node2d1[1])
        return (x, y, np.hypot(y, x))

    def dn(self):
        for wireframe in self.wireframes.values():
            for node in wireframe.nodes:
                if node[2] < 1:
                    continue

                dist = np.sqrt(node[0]*node[0] + node[1]*node[1] + node[2]*node[2])

                if dist < 1:
                    continue

                incl = np.arccos(node[2]/dist)
                az = np.arctan2(node[1], node[0])

                radius = int(self.nodeRadius*self.camDist/dist)

                if radius <= 0 or radius >= self.width:
                    continue

                color = tuple(int(min(c*self.camDist*self.DRAW_DIST/(dist*dist), 255)) for c in self.nodeColor)

                if color[0] <= self.background[0]:
                    continue

                node2d = self.perspective(incl, az)

                if (node2d[0] <= -radius or node2d[0] >= self.width+radius or
                    node2d[1] <= -radius or node2d[1] >= self.height+radius):
                    continue

                pygame.draw.circle(self.screen, color,
                    node2d,
                    radius
                )

    def perspective(self, incl, az):
        return (
            int(self.halfWidth + self.camDist*np.sin(incl)*np.cos(az)),
            int(self.halfHeight + self.camDist*np.sin(incl)*np.sin(az))
        )

if __name__ == '__main__':
    cube = wireframe.Wireframe()
    cube.addNodes(np.array([(x,y,z) for x in (-10,10) for y in (-10,10) for z in (100,120)]))
    cube.addEdges([(n,n+4) for n in range(4)]+[(n,n+1) for n in range(0,7,2)]+[(n,n+2) for n in (0,1,4,5)])

    cube2 = wireframe.Wireframe()
    cube2.addNodes(np.array([(x,y,z) for x in (-10,10) for y in (10,30) for z in (100,120)]))
    cube2.addEdges([(n,n+4) for n in range(4)]+[(n,n+1) for n in range(0,7,2)]+[(n,n+2) for n in (0,1,4,5)])

    dots = wireframe.Wireframe()
    dots.addNodes(np.array([(x,y,z) for x in range(0,100,20) for y in range(0,100,20) for z in range(0,300,20)]))

    pv = ProjectionViewer(800, 600)
    pv.addWireframe('cube', cube)
    pv.addWireframe('cube2', cube2)
    pv.addWireframe('dots', dots)
    pv.run()
