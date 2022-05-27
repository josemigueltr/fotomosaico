from tkinter import *
from tkinter import filedialog
from tkinter.messagebox import showinfo
from PIL import Image
from PIL import ImageTk
import cv2
import imutils
import numpy as np
from skimage import io
import matplotlib.pyplot as plt
from skimage.transform import resize
from skimage.util import img_as_ubyte
#Directorio de las imagenes que se usaran para la creacion de el fotomosaico
directorio= './fotos_varias/*jpg'
imagen_original=""


def elegir_imagen():
    # Especificar los tipos de archivos, para elegir solo a las imágenes
    path_image = filedialog.askopenfilename(filetypes = [
        ("image", ".jpeg"),
        ("image", ".png"),
        ("image", ".jpg")])
    if len(path_image) > 0:
        global image
        global imagen_original
        #Leemos la imagen de entrada param ostrarla en la gui
        image = cv2.imread(path_image)
        image= imutils.resize(image, height=380)
        imageToShow= imutils.resize(image, width=180)
        imageToShow = cv2.cvtColor(imageToShow, cv2.COLOR_BGR2RGB)
        im = Image.fromarray(imageToShow )
        img = ImageTk.PhotoImage(image=im)
        lblInputImage.configure(image=img)
        lblInputImage.image = img   
        lblInfo1 = Label(root, text="IMAGEN DE ENTRADA:")
        lblInfo1.grid(column=0, row=1, padx=5, pady=5)
        lblOutputImage.image = ""
        selected.set(0)
        #Asignamos la imagen que se va a procesar
        imagen_original = path_image




def distancia_mas_pequena(color_pixel, directorio_imagenes_promedio_rgb):
    """
    Funcion que encuentra la distancia mas pequeña entre el promedio de colores  de acuerdo a la seccion
    de la imagen que va a sustituir
    """
    distancia = None
    mayor_parecido = None
    for ruta_archivo in directorio_imagenes_promedio_rgb:
        distance = (color_pixel[0] - directorio_imagenes_promedio_rgb[ruta_archivo][0])**2 + (color_pixel[1] - directorio_imagenes_promedio_rgb[ruta_archivo][1])**2 + (color_pixel[2] - directorio_imagenes_promedio_rgb[ruta_archivo][2])**2
        if distancia == None or distance < distancia:
            distancia = distance
            mayor_parecido = ruta_archivo
    return mayor_parecido
        

def calcula_color_promedio(pixel_region):
    return(list(np.mean(pixel_region, axis =(0,1))))


def recortar_directorio_imagenes(imagen):
    """"
    Funcion que redimenciona las imagenes aun tamano mas cuadrado
    """
    #Caso imagn es vertical
    if imagen.shape[0] > imagen.shape[1]:
        corte = imagen.shape[0] - imagen.shape[1]
        nueva_altura = imagen.shape[0] - corte
        imagen = imagen[0:nueva_altura,:]
        return imagen 
    else: # Imagen horizontal
        corte = imagen.shape[1] - imagen.shape[0]
        nuevo_ancho = imagen.shape[1] - corte
        imagen = imagen[:, 0:nuevo_ancho]
        return imagen




def fotomosaico():
   
    """
        Funcion que se encarga de construir una nueva imagen aplicando el filtro de fotomosaico
        A partir de un banco de imagenes local se  revisa cada una de ellas para que se ajuste a la seccion de la
        imagen que se busque construir y con ello dar forma al fotomosaico
    """
    global imagen_original
    global text
    global name
    if(imagen_original==""):
        popup_showinfo("Debes Seleccionar una imagen!")
        return
    if(text.get()=="" or not text.get().isdigit()):
        popup_showinfo("Ingresa un numero valido en el tamaño del pixel")
        return
    if(name.get()==""):
        popup_showinfo("Ingresa nombre para la imagen de salida valido")
        return
    #Valor de cada pixel
    valor_pixel = int(text.get())

    #Imagen que se procesara
    imagen_a_procesar = io.imread(imagen_original)

    #Carpeta con las imagenes que usaremos para cotruir el fotoosaico
    directorio= './varios/*jpg'
    directorio_imagenes = {}
    directorio_imagenes_promedio_rgb = {}   
    print('Cargando imágenes...')
    #Carcamos todas las imagenes de la carpeta de imagenes variadas
    coleccion_imagenes = io.imread_collection(directorio)
    for ruta_archivo in coleccion_imagenes.files:
        try:
            imagen_actual = io.imread(ruta_archivo)
            directorio_imagenes[ruta_archivo] = recortar_directorio_imagenes(imagen_actual)
            img = recortar_directorio_imagenes(imagen_actual)
            directorio_imagenes_promedio_rgb[ruta_archivo] = calcula_color_promedio(img)
        except:
            continue

    # Redimecionamos todas laa imagenes que formaran parte del fotomosaico para que quepan dentro de las dimensines
    #de la imagen original
    ajustar_filas = imagen_a_procesar.shape[0] % valor_pixel
    ajustar_columns = imagen_a_procesar.shape[1] % valor_pixel
    imagen_a_procesar = imagen_a_procesar[0:imagen_a_procesar.shape[0]-ajustar_filas, 0:imagen_a_procesar.shape[1]-ajustar_columns]
    fila = []
    imagen_temporal = []
    #Creamos el fotomosaico
    for i in range(0, imagen_a_procesar.shape[0], valor_pixel):
        for j in range(0, imagen_a_procesar.shape[1], valor_pixel):
            pixel_region = imagen_a_procesar[i:i+valor_pixel, j:j+valor_pixel]
            color_pixel = calcula_color_promedio(pixel_region)
            mayor_parecido = distancia_mas_pequena(color_pixel, directorio_imagenes_promedio_rgb)
            img = io.imread(mayor_parecido)
            img = resize(img, (valor_pixel,valor_pixel), anti_aliasing=True)
            fila.append(img)
        imagen_temporal.append(np.hstack(fila))
        fila = []
    fotomosaico = np.vstack(imagen_temporal)  
    fotomosaico = img_as_ubyte(fotomosaico)
    mostrar = "resultados/" + f'{name.get()}.jpg'
    io.imsave(mostrar, fotomosaico)
    print("TErminbeeeeeee")
    #Visualizamos la imagen resultante en la interfaz grafica
    salida = cv2.imread(mostrar)
    imageToShowOutput = cv2.cvtColor(salida, cv2.COLOR_BGR2RGB)
    im = Image.fromarray(imageToShowOutput)
    img = ImageTk.PhotoImage(image=im)
    lblOutputImage.configure(image=img)
    lblOutputImage.image = img
    lblInfo3 = Label(root, text="IMAGEN RESULTANTE", font="bold")
    lblInfo3.grid(column=1, row=0, padx=5, pady=5)

def popup_showinfo(msg):
    showinfo("Advertencia",msg)

#Interfaz grafica

root = Tk()

# Imagen de entrada
lblInputImage = Label(root)
lblInputImage.grid(column=0, row=2)

# Imagen  resusltante
lblOutputImage = Label(root)
lblOutputImage.grid(column=1, row=1, rowspan=6)

# Filtros disponibles
lblInfo2 = Label(root, text="FILTROS", width=25)
lblInfo2.grid(column=0, row=7, padx=5, pady=5)
selected = IntVar()


#Tamaño del fotomosaico
text=StringVar()
lblInfo3 = Label(root, text="Ingresa el tamaño de los fotomosaicos", width=40)
lblInfo3.grid(column=0, row=3, padx=60, pady=5)
entrada=Entry(textvariable=text)
entrada.grid(column=0,row=4)

#Nombre de la imagen resultante
name=StringVar()
lblInfo4 = Label(root, text="Ingresa nombre de la imagen resultante", width=40)
lblInfo4.grid(column=0, row=5, padx=60, pady=5)
e=Entry(textvariable=name)
e.grid(column=0,row=6)

#Boton con el cual se aplicara el filtro de fotomosaico
btnFotomosaico= Button(root, text="Aplicar Fotomosaico", command=fotomosaico)
btnFotomosaico.grid(column=0,row=8)
#Boton par seleciona
btn = Button(root, text="Escoge una imagen", width=25, command=elegir_imagen)
btn.grid(column=0, row=0, padx=5, pady=5)
root.mainloop()