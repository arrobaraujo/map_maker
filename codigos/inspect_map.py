import tkintermapview
import tkinter as tk

try:
    root = tk.Tk()
    root.withdraw() # Hide the window
    map_widget = tkintermapview.TkinterMapView(root)
    
    print("Children of map_widget:")
    for child in map_widget.winfo_children():
        print(f"Name: {child.winfo_name()}, Class: {child.winfo_class()}")
        # Check if it has internal children
        try:
            for subchild in child.winfo_children():
                 print(f"  Subchild: {subchild.winfo_name()}, Class: {subchild.winfo_class()}")
        except:
            pass
    
    # Check canvas tags
    if hasattr(map_widget, 'canvas'):
        print("\nCanvas tags:")
        for item in map_widget.canvas.find_all():
            print(f"Item: {item}, Tags: {map_widget.canvas.gettags(item)}")

    root.destroy()
except Exception as e:
    print(f"Error: {e}")
