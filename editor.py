import tkinter as tk

# INTITIALIZE GUI
app = tk.Tk()
app.geometry(f'900x600')
app.resizable(width=False, height=True)
canvas = tk.Canvas(app, bg=CANVAS_BACKGROUND_COLOR, height=BACKGROUD_HEIGHT, width=BACKGROUD_WIDTH)
canvas.pack(fill=tk.BOTH, expand=True)

app.mainloop()
