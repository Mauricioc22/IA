import tkinter as tk
import os
import PIL.Image, PIL.ImageTk
import cv2
import camera
import model
import playsound
import time

class App:
    import time
    
    def get_rep_limit(self):
        self.rep_limit = int(self.rep_limit_entry.get())
        self.rep_limit_entry.pack_forget()
        self.rep_limit_btn.pack_forget()


    # def reinicio(self):
    #     self.btn_toggleauto.invoke()
    #     print("Entro a reinicio")


    def countdown(self, seconds):
        self.status = False

        self.counting_enabled = False
        for i in range(seconds, -1, -1):
            self.countdown_label.config(text=f"Descansando: {i} segundos restantes")
            self.window.after(1000, self.countdown, i-1)
            if i >0 and self.rep_counter > 0:
                self.countdown_label.config(text=f"Alto, descansa un poco") 
                self.rep_counter = 0               
            #if i == 0:
                
                # self.status = True
                # print(self.status)
                #self.reinicio()
            if i == 0:
                self.countdown_label.config(text=f"Continua tu entrenamiento!") 


            break
        self.btn_toggleauto.invoke()
        #self.window.after(1000*seconds, self.btn_toggleauto.invoke)

        

            

    
    # def get_rep_limit(self):
    #     self.rep_limit = int(input("Ingresa el límite de repeticiones: "))

    def __init__(self):
        self.window = tk.Tk()
        self.window.title = "Contador de repeticiones de curl de biceps"
        #limite
        self.rep_limit = 0
        
        #Estado
        self.status = False

        self.counters = [1, 1]
        self.rep_counter = 0
        self.rep_counter_temp = 0
        self.set_counter = 0
        
        self.extended = False
        self.contracted = False
        self.last_prediction = 0
        
        self.model = model.Model()
        
        self.counting_enabled = False

        self.camera = camera.Camera()
        
        #limite
        #self.get_rep_limit()
        
        
        self.init_gui()
        
        self.delay = 15
        self.update()
        
        self.window.attributes("-topmost", True)
        self.window.mainloop()
        
    def init_gui(self):
        self.canvas = tk.Canvas(self.window, width=self.camera.width*0.8, height=self.camera.height*0.8)
        self.canvas.pack()
        
        self.btn_toggleauto = tk.Button(self.window, text="Iniciar conteo", width=50, command=self.counting_toggle)
        self.btn_toggleauto.pack(anchor=tk.CENTER, expand=True)
    
        self.btn_class_one = tk.Button(self.window, text="Extendido", width=50, command=lambda: self.save_for_class(1))
        self.btn_class_one.pack(anchor=tk.CENTER, expand=True)
    
        self.btn_class_two = tk.Button(self.window, text="Contraido", width=50, command=lambda: self.save_for_class(2))
        self.btn_class_two.pack(anchor=tk.CENTER, expand=True)
    
        self.btn_train = tk.Button(self.window, text="Entrenar modelo", width=50, command=lambda: self.model.train_model(self.counters))
        self.btn_train.pack(anchor=tk.CENTER, expand=True)
    
        self.btn_reset = tk.Button(self.window, text="Reiniciar/Parar", width=50, command=self.reset)
        self.btn_reset.pack(anchor=tk.CENTER, expand=True)
    
        self.counter_label = tk.Label(self.window, text=f"{self.rep_counter}")
        self.counter_label.config(font=("Arial", 24))
        self.counter_label.pack(anchor=tk.CENTER, expand=True)
    
        #ingresar limite en interfaz grafica
        self.rep_limit_entry = tk.Entry(self.window)
        self.rep_limit_entry.pack(anchor=tk.CENTER, expand=True)

        self.rep_limit_btn = tk.Button(self.window, text="Confirmar límite", width=50, command=self.get_rep_limit)
        self.rep_limit_btn.pack(anchor=tk.CENTER, expand=True)
    
        self.countdown_label = tk.Label(self.window, text="")
        self.countdown_label.config(font=("Arial", 24))
        self.countdown_label.pack(anchor=tk.CENTER, expand=True)

    
    
    def update(self):
        if self.counting_enabled:
            # self.predict()
            try:
                self.predict()
            except Exception as e:
                print(e)
            
        if self.extended and self.contracted:
            self.extended, self.contracted = False, False
            self.rep_counter += 1
                
            if self.rep_counter % self.rep_limit == 0:
                playsound.playsound("sound/up.mp3")
                
                self.set_counter += 1
                
            else:
                playsound.playsound("sound/beep2.mp3")
            
        
        self.counter_label.config(text=f"Sets: {self.set_counter} | Reps: {self.rep_counter}")
            
        ret, frame = self.camera.get_frame()
        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
                
        self.window.after(self.delay, self.update)
                
    def predict(self):
        frame = self.camera.get_frame()
        prediction = self.model.predict(frame)
        
        if prediction != self.last_prediction:
            if prediction == 1:
                self.extended = True
                self.last_prediction = 1
            if prediction == 2:
                self.contracted = True
                self.last_prediction = 2
        
        #limite
        if self.rep_counter == self.rep_limit:
            self.rep_counter = 0
            self.countdown(15)

    def counting_toggle(self):
        self.counting_enabled = not self.counting_enabled
    
    def save_for_class(self, class_num):
        ret, frame = self.camera.get_frame()
        if not os.path.exists("1"):
            os.mkdir("1")
        if not os.path.exists("2"):
            os.mkdir("2")
            
        cv2.imwrite(f"{class_num}/frame{self.counters[class_num-1]}.jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY))
        img = PIL.Image.open(f"{class_num}/frame{self.counters[class_num-1]}.jpg")
        img.thumbnail((150, 150), PIL.Image.ANTIALIAS)
        img.save(f"{class_num}/frame{self.counters[class_num-1]}.jpg")
    
        # self.counters[class_num-1] += 1
        if isinstance(class_num, int):
            self.counters[class_num - 1] += 1
        else:
            print("class_num debe ser un entero")        
    
    def reset(self):
        self.rep_counter = 0