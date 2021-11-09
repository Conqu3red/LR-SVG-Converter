from svgelements import *
import os, sys
from typing import List

def standard_prompt(prompt: str, options: List[str]):
	i = None
	while i not in options:
		print(prompt)
		i = input("> ")
	
	return i

print("""--- Line Rider SVG Track generator ---
### Created by Conqu3red (Conqu3red#2054 on discord)""")
file = input("### Enter a file name (example: test.svg): ")
save_format = standard_prompt(
	"### Enter save format\n1: TRK file (small file size)\n2: JSON (linerider.com)",
	["1", "2"]
)

try:
    svg = SVG.parse(file)
except FileNotFoundError:
    print("File Not found!")
    sys.exit(1)
mode = standard_prompt(
	"### Enter mode\n1: Accurate (recommended - default)\n2: approximate",
	["1", "2"]
)
try:
    MODE = int(mode)
except ValueError:
    MODE = 1 # 1: accurate 2: approx
    print("! Set mode to 1")

import json
import math

import lrtools.trkformat as trkformat
import lrtools.jsonformat as jsonformat
from vector_2d import Vector
from lrtools.track import Track, LineType
from lrtools.track import Line as lr_Line
import random


track = Track()
LINE_WIDTH = 0.1

elements = []
for element in svg.elements():
    try:
        if element.values['visibility'] == 'hidden':
            continue
    except (KeyError, AttributeError):
        pass
    if isinstance(element, SVGText):
        elements.append(element)
    elif isinstance(element, Path):
        if len(element) != 0:
            elements.append(element)
    elif isinstance(element, Shape):
        e = Path(element)
        e.reify()  # In some cases the shape could not have reified, the path must.
        if len(e) != 0:
            elements.append(e)
    elif isinstance(element, SVGImage):
        try:
            element.load(os.path.dirname("/"))
            if element.image is not None:
                elements.append(element)
        except OSError:
            pass  


accuracy = 10
z = 1
div = 1
def addLines(item):
    #print(base_pos)

    #shape["m_Pos"]["z"] = z
    #z += -0.05


    item_points_scaled = []
    if MODE == 1: # accurate
        #compute point positions
        for index, point in enumerate(item.segments()[1:]):
            #print(type(point))
            if isinstance(point, (Arc, CubicBezier, QuadraticBezier)): # if curve (arc)
                #print(type(point))
                #print("Approximating curve for ", str(type(point)))
                for i in range(0, accuracy-1):
                    p = point.point(i/(accuracy-1))
                    p2 = point.point((i+1)/(accuracy-1))
                    new_point = lr_Line(LineType.Scenery,
                        Vector((p.x)/div,(p.y)/div),
                        Vector((p2.x)/div,(p2.y)/div),
						width = LINE_WIDTH
                    )
                    item_points_scaled.append(new_point)
            else: # normal straight line
                #print("Parsing line")
                new_point = lr_Line(LineType.Scenery,
                    Vector((point.start.x)/div,(point.start.y)/div),
                    Vector((point.end.x)/div,(point.end.y)/div),
					width = LINE_WIDTH
                )
                item_points_scaled.append(new_point)
    elif MODE == 2: # approximate
        item = Path(item)
        prev = Point(0,0)
        for i in range(100):
            p = item.point(i/100)
            if i == 0: prev = p
            new_point = lr_Line(LineType.Scenery,
                Vector((prev.x)/div,(prev.y)/div),
                Vector((p.x)/div,(p.y)/div),
				width = LINE_WIDTH
            )
            prev = p
            item_points_scaled.append(new_point)
    
    for l in item_points_scaled:
        track.addLine(l)



remaining = len(elements)
for c, item in enumerate(elements):
    if isinstance(item, Shape):
        if isinstance(item, Path):
            for sub_item in item.as_subpaths():
                if sub_item:
                    sub_item.fill = item.fill
                    addLines(sub_item)
            print(f"- Added shape. {len(elements)-c-1} Remaining")
        else:
            print("somehow this shape isn't a path?")
    else:
        print("- Detected item that isn't a shape or path, ignoring")

print("- Saving...")
if save_format == "1":
	trkformat.save_trk(track, file + ".trk")
	print(f"### Saved to track {file}.trk")
else:
	jsonformat.save_json(track, file + ".track.json")
	print(f"### Saved to track {file}.track.json")