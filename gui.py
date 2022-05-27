from tkinter import *
from tkinter import filedialog
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



# Función que calcula el color rgb promedio
def calcula_color_promedio(pixel_region):
    return(list(np.mean(pixel_region, axis =(0,1))))

# Función que encuentra la distancia más pequeña entre el promedio de colores de las imágenes de nuestro directorio
# y la sección del píxel de nuestra imagen a procesar, encontrando los que tengan el mayor parecido
def mejor_parecido(color_pixel, directorio_imagenes_promedio_rgb):
    distancia = None
    mayor_parecido = None
    for ruta_archivo in directorio_imagenes_promedio_rgb:
        distance = (color_pixel[0] - directorio_imagenes_promedio_rgb[ruta_archivo][0])**2 + (color_pixel[1] - directorio_imagenes_promedio_rgb[ruta_archivo][1])**2 + (color_pixel[2] - directorio_imagenes_promedio_rgb[ruta_archivo][2])**2
        if distancia == None or distance < distancia:
            distancia = distance
            mayor_parecido = ruta_archivo
    return mayor_parecido
        
# Función que hace que las imágenes sean cuadradas
def recortar_directorio_imagenes(imagen):
    # Corta en función del valor más pequeño, por ejemplo si tenemos 1120 * 700
    # la imagen será de 700 * 700
    # Si hay más filas que columnas
    if imagen.shape[0] > imagen.shape[1]:
        corte = imagen.shape[0] - imagen.shape[1]
        nueva_altura = imagen.shape[0] - corte
        imagen = imagen[0:nueva_altura,:]
        return imagen 
    else: # Si hay más columnas que filas
        corte = imagen.shape[1] - imagen.shape[0]
        nuevo_ancho = imagen.shape[1] - corte
        imagen = imagen[:, 0:nuevo_ancho]
        return imagen




def fotomosaico(valor_pixel, imagen_entrada, imagen_salida):
    # Valor que afectará el tamaño de pixeleado de nuestro fotomosaico.
    valor_pixel = valor_pixel

    # Convertimos la dirección de la imagen a procesar en una matriz 2D (imagen binaria o en escala de grises) o 3D (imagen en color).
    imagen_a_procesar = io.imread(imagen_entrada)

    # Directorio de donde se sacarán las fotos para generar nuestro fotomosaico
    directorio= './fotos_varias/*jpg'

    # Diccionario donde las llaves son las rutas de los archivos (de nuestro 
    # directorio) y los valores son la imagen convertida en una matriz 2D o 3D.
    directorio_imagenes = {}

    # Diccionario donde las llaves son las rutas de los archivos (de nuestro
    # directorio) y los valores son los valores rgb promedio.
    directorio_imagenes_promedio_rgb = {}
   
    print('Cargando imágenes...')

    # Procesamos todas las imagenes de nuestro directorio
    coleccion_imagenes = io.imread_collection(directorio)

    # Iteramos sobre las imagenes ya procesadas recabadas de nuestro directorio
    for ruta_archivo in coleccion_imagenes.files:
        try:
            imagen_actual = io.imread(ruta_archivo)
            # Guardamos como llave la ruta del archivo y como valor la imagen procesada y recortada en forma cuadrada
            directorio_imagenes[ruta_archivo] = recortar_directorio_imagenes(imagen_actual)
            img = recortar_directorio_imagenes(imagen_actual)
            # Guardamos como llave la ruta del archivo y como valor guardamos el valor rgb promedio de la imagen
            directorio_imagenes_promedio_rgb[ruta_archivo] = calcula_color_promedio(img)
        except:
            continue

    # Esto permitirá que todos los cuadrados de "píxeles" quepan por igual en el marco
    ajustar_filas = imagen_a_procesar.shape[0] % valor_pixel
    ajustar_columns = imagen_a_procesar.shape[1] % valor_pixel
    imagen_a_procesar = imagen_a_procesar[0:imagen_a_procesar.shape[0]-ajustar_filas, 0:imagen_a_procesar.shape[1]-ajustar_columns]
    # print('La altura y el ancho de su foto son: ', imagen_a_procesar.shape) 
    # print('Estamos creando su fotomosaico. La espera es de alrededor de 5 minutos, si su imagen no se termina de procesar en ese tiempo, cambie el tamaño de su imagen o aumente el tamaño de los píxeles.')
    fila = []
    imagen_temporal = []

    # this will iterate through each pixel_region and move to the next region by value in valor_pixel
    # the fotomosaico will be created fila by fila

    # El fotomosaico será creado fila por fila
    for i in range(0, imagen_a_procesar.shape[0], valor_pixel):
        for j in range(0, imagen_a_procesar.shape[1], valor_pixel):

            pixel_region = imagen_a_procesar[i:i+valor_pixel, j:j+valor_pixel]

            # calculamos el color promedio de la región en nuestra imagen a procesar o imagen de entrada
            color_pixel = calcula_color_promedio(pixel_region)

            # calculamos el valor que más se asemeje al valor del píxel de nuestra imagen a procesar
            mayor_parecido = mejor_parecido(color_pixel, directorio_imagenes_promedio_rgb)

            img = io.imread(mayor_parecido)

            # cambiamos el tamaño de la imagen que más se asemejó al tamaño del pixel cuadrado.
            img = resize(img, (valor_pixel,valor_pixel), anti_aliasing=True)
            
            # insertamos la imagen en la fila
            fila.append(img)
        imagen_temporal.append(np.hstack(fila))
        fila = []
    fotomosaico = np.vstack(imagen_temporal)  

    # Nos ayuda a suprimir la advertencia de que hay hubo una perdida en la conversión.
    fotomosaico = img_as_ubyte(fotomosaico)

    # Tomamos el nombre de archivo que tendrá nuestro fotomosaico
    mostrar = "static/uploads/" + imagen_salida
    io.imsave(mostrar, fotomosaico)



root = Tk()


# Label donde se presentará la imagen de entrada
lblInputImage = Label(root)
lblInputImage.grid(column=0, row=2)

# Label donde se presentará la imagen de salida
lblOutputImage = Label(root)
lblOutputImage.grid(column=1, row=1, rowspan=6)

# Label ¿Qué color te gustaría resaltar?
lblInfo2 = Label(root, text="FILTROS", width=25)
lblInfo2.grid(column=0, row=3, padx=5, pady=5)

# Creamos los radio buttons y la ubicación que estos ocuparán
selected = IntVar()

btnFotomosaico= Button(root, text="Aplicar Fotomosaico", command=fotomosaico(20,imagen_original, 'fotomosaico.jpg'))
btnFotomosaico.grid(column=0,row=4)
# Creamos el botón para elegir la imagen de entrada
btn = Button(root, text="Escoge una imagen", width=25, command=elegir_imagen)
btn.grid(column=0, row=0, padx=5, pady=5)
root.mainloop()