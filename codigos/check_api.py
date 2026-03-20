import tkintermapview
m = tkintermapview.TkinterMapView
for attr in dir(m):
    if any(k in attr.lower() for k in ["pos", "coord", "pixel", "canvas"]):
        print(attr)
