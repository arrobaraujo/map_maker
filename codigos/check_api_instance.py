import tkinter
import tkintermapview
import os

# Create a hidden root
root = tkinter.Tk()
root.withdraw()

m = tkintermapview.TkinterMapView(root)
print("Methods for TkinterMapView instance:")
for attr in sorted(dir(m)):
    if not attr.startswith("__"):
        print(attr)

root.destroy()
