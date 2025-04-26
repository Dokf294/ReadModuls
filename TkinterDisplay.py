import tkinter as tk 
def _Call_Tkinter_():
    root = tk.Tk() 
    root.title('Я родился!') 
    root.geometry("800x600") 

    lable = tk.Label(root, text='Я вызван!', font=('Arial', 14)) 
    lable.pack()
    tk.mainloop()  
if __name__ == '__main__': 
    _Call_Tkinter_()
