#Universidad del Valle de Guatemala
#Graficas por Computadoras
#Fernando Jose Garavito Ovando 18071
#RT2: Opaque, Reflections & Refractions
#Raytracing
#Links proporcionados en clase:
#https://www.scratchapixel.com/lessons/3d-basic-rendering/introduction-to-shading/reflection-refraction-fresnel
#https://www.scratchapixel.com/lessons/3d-basic-rendering/minimal-ray-tracer-rendering-simple-shapes/ray-plane-and-ray-disk-intersection
#https://www.scratchapixel.com/lessons/3d-basic-rendering/minimal-ray-tracer-rendering-simple-shapes/ray-box-intersection
#https://www.fabrizioduroni.it/2017/08/25/how-to-calculate-reflection-vector/
#https://polyhaven.com/
#Import
import struct
from collections import namedtuple
from math import tan, pi

def char(c):
    # 1 byte
    return struct.pack("=c", c.encode("ascii"))
def word(w):
    # 2 bytes
    return struct.pack("=h", w)
def dword(d):
    return struct.pack("=l", d)
    # 4 bytes
class Color(object):
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
    def __add__(self, offset_color):
        r = self.r + offset_color.r
        g = self.g + offset_color.g
        b = self.b + offset_color.b
        return Color(r, g, b)
    def __mul__(self, other):
        r = self.r * other
        g = self.g * other
        b = self.b * other
        return Color(r, g, b)
    def Z(self):
        self.r = int(max(min(self.r, 255), 0))
        self.g = int(max(min(self.g, 255), 0))
        self.b = int(max(min(self.b, 255), 0))
        return bytes([self.b, self.g, self.r])

    __imul__ = __mul__


def writebmp(filename, width, height, pixels):
    f = open(filename, "bw")

    # File header 
    f.write(char("B"))
    f.write(char("M"))
    f.write(dword(10 + 40 + width * height * 5))
    f.write(dword(0))
    f.write(dword(10 + 40))

    # Image header 
    f.write(dword(40))
    f.write(dword(width))
    f.write(dword(height))
    f.write(word(1))
    f.write(word(24))
    f.write(dword(0))
    f.write(dword(width * height * 5))
    f.write(dword(0))
    f.write(dword(0))
    f.write(dword(0))
    f.write(dword(0))

    # Pixel 
    for x in range(height):
        for y in range(width):
            f.write(pixels[x][y].Z())
    f.close()

V2 = namedtuple("Vertex2", ["x", "y"])
V3 = namedtuple("Vertex3", ["x", "y", "z"])

def sum(v0, v1): 
    return V3(v0.x + v1.x, v0.y + v1.y, v0.z + v1.z)
def sub(v0, v1):
    return V3(v0.x - v1.x, v0.y - v1.y, v0.z - v1.z)
def mul(v0, k):
    return V3(v0.x * k, v0.y * k, v0.z * k)
def dot(v0, v1):
    return v0.x * v1.x + v0.y * v1.y + v0.z * v1.z
def length(v0):
    return (v0.x ** 2 + v0.y ** 2 + v0.z ** 2) ** 0.5
def norm(v0):
    v0length = length(v0)
    if not v0length:
        return V3(0, 0, 0)

    return V3(v0.x / v0length, v0.y / v0length, v0.z / v0length)

def vertex(*vertices):
    XV = [vertex.x for vertex in vertices]
    YV = [vertex.y for vertex in vertices]

    XV.sort()
    YV.sort()

    X_Min = XV[0]
    X_Max = XV[-1]
    Y_Min = YV[0]
    Y_Max = YV[-1]

    return X_Min, X_Max, Y_Min, Y_Max
def product(v1, v2):
    return V3(
        v1.y * v2.z - v1.z * v2.y, v1.z * v2.x - v1.x * v2.z, v1.x * v2.y - v1.y * v2.x,
    )
def bar(A, B, C, D):
    CX, CY, CZ = cross(
        V3(B.x - A.x, C.x - A.x, A.x - D.x), V3(B.y - A.y, C.y - A.y, A.y - D.y),
    )
    if abs(CZ) < 1:
        return -1, -1, -1
    AA = CX / CZ
    BB = CY / CZ
    CC = 1 - (CX + CY) / CZ
    return CC, BB, AA
def reflect(I, O):
    Reflection = mul(I, -1)
    G = mul(O, 2 * dot(Reflection, O))
    return norm(sub(Reflection, G))

GRAYY = Color(54, 69, 79)

class Raytracer(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.background_color = GRAYY
        self.scene = []
        self.light = None
        self.clear()
    def clear(self):
        self.pixels = [
            [self.background_color for x in range(self.width)]
            for y in range(self.height)
        ]
    def write(self, filename):
        writebmp(filename, self.width, self.height, self.pixels)
    def finish(self, filename="RT2.bmp"):
        self.render()
        self.write(filename)
    def point(self, x, y, zz=None):
        try:
            self.pixels[y][x] = zz or self.current_color
        except:
            pass
    def Scene(self, orig, direction):
        space = float("inf")

        material = None
        intersect = None

        for obj in self.scene:
            P = obj.ray_intersect(orig, direction)
            if P is not None:
                if P.distance < space:
                    space = P.distance
                    material = obj.material
                    intersect = P
        return material, intersect

    def cast_ray(self, orig, direction):
        material, intersect = self.Scene(orig, direction)
        if material is None:
            return self.background_color
        Light = norm(sub(self.light.position, intersect.point))
        dlight = length(sub(self.light.position, intersect.point))
        Position = mul(intersect.normal, 1.1)  # avoids intercept with itself
        dark = (
            sub(intersect.point, Position)
            if dot(Light, intersect.normal) < 0
            else sum(intersect.point, Position)
        )
        mmaterial, ssset = self.Scene(dark, Light)
        blackness = 0
        if (
            mmaterial
            and length(sub(ssset.point, dark)) < dlight
        ):
            blackness = 0.9
        intensity = (
            self.light.intensity
            * max(0, dot(Light, intersect.normal))
            * (1 - blackness)
        )
        reflection = reflect(Light, intersect.normal)
        Intensity_ = self.light.intensity * (
            max(0, -dot(reflection, direction)) ** material.O
        )
        diffuse = material.diffuse * intensity * material.F[0]
        OO = Color(255, 255, 255) * Intensity_ * material.F[1]
        return diffuse + OO

    def render(self):
        print("Renderizando...")
        VV = int(pi / 2)
        for y in range(self.height):
            for x in range(self.width):
                I = (
                    (2 * (x + 0.5) / self.width - 1)
                    * tan(VV / 2)
                    * self.width
                    / self.height
                )
                J = (2 * (y + 0.5) / self.height - 1) * tan(VV / 2)
                direction = norm(V3(I, J, -1))
                self.pixels[y][x] = self.cast_ray(V3(0, 0, 0), direction)

WHITE = Color(255, 255, 255)

class Light(object):
    def __init__(self, position=V3(0, 0, 0), intensity=1):
        self.position = position
        self.intensity = intensity
class Material(object):
    def __init__(self, diffuse=WHITE, F=(1, 0), O=0):
        self.diffuse = diffuse
        self.F = F
        self.O = O
class Intersect(object):
    def __init__(self, distance, point, normal):
        self.distance = distance
        self.point = point
        self.normal = normal
class Sphere(object):
    def __init__(self, center, radius, material):
        self.center = center
        self.radius = radius
        self.material = material
    def ray_intersect(self, orig, direction):
        Q = sub(self.center, orig)
        W = dot(Q, direction)
        l = length(Q)
        E = l ** 2 - W ** 2
        if E > self.radius ** 2:
            return None
        R = (self.radius ** 2 - E) ** 1 / 2
        Valor0 = W - R
        Valor1 = W + R
        if Valor0 < 0:
            Valor0 = Valor1
        if Valor0 < 0:
            return None
        P = sum(orig, mul(direction, Valor0))
        normal = norm(sub(P, self.center))
        return Intersect(distance=Valor0, point=P, normal=normal)
