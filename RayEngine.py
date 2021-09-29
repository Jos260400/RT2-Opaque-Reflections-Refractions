#Universidad del Valle de Guatemala
#Graficas por Computadoras
#Fernando Jose Garavito Ovando 18071
#RT2: Opaque, Reflections & Refractions
#RayEngine
#Links proporcionados en clase:
#https://www.scratchapixel.com/lessons/3d-basic-rendering/introduction-to-shading/reflection-refraction-fresnel
#https://www.scratchapixel.com/lessons/3d-basic-rendering/minimal-ray-tracer-rendering-simple-shapes/ray-plane-and-ray-disk-intersection
#https://www.scratchapixel.com/lessons/3d-basic-rendering/minimal-ray-tracer-rendering-simple-shapes/ray-box-intersection
#https://www.fabrizioduroni.it/2017/08/25/how-to-calculate-reflection-vector/
#https://polyhaven.com/
#Import
from Raytracing import Raytracer
from Raytracing import Material
from Raytracing import Light
from Raytracing import Sphere
from Raytracing import Color
from Raytracing import V3

BLACK = Color(0, 0, 0)
WHITE = Color(255, 255, 255)
GRAY = Color(5, 5, 5)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)

Partenegra = Material(diffuse=BLACK, F=(0.5, 0.5), O=5)
Partegris = Material(diffuse=GRAY, F=(1, 1), O=30)
Esferablanca = Material(diffuse=WHITE, F=(1, 1), O=20)
Esferaverde = Material(diffuse=GREEN, F=(0.5, 0.5), O=10)

# Render
render = Raytracer(500, 500)
render.light = Light(position=V3(-5, 0, 10), intensity=2)
render.background_color = BLUE
render.scene = [

    Sphere(V3(-2, 0, -5), 1, Esferablanca),

    Sphere(V3(0, 0, -5), 0.25, Esferaverde),
]

render.finish()
