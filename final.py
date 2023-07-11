import cv2
from  matplotlib import pyplot as plt
import numpy as np 
import queue
import streamlit as st
from streamlit_cropper import st_cropper
from PIL import Image

#titulo do app
st.title("Selecione a Imagem")

#upload de arquivos de imagem
img_file = st.file_uploader(label="Envie uma Imagem", type=['png','jpg', 'jpeg'])
# usaremos essa variavel dps
file = img_file

#gera check box para atualização em tempo real
realtime_update = st.sidebar.checkbox("Atualização em Tempo Real", value=True)

#cor do quadro de seleção
box_color = st.sidebar.color_picker(label="Grupo de Cores", value='#0000FF')

#radiobuttons sobre a proporsão da tela
aspect_choice = st.sidebar.radio(label="Proporção da Tela", options=["1:1","16:9", "4:3"])

aspect_dict = {
	"1:1":(1,1),
	"16:9":(16,9),
	"4:3":(4,3)
}

aspect_ratio = aspect_dict[aspect_choice]

# se o arquivo existir
if img_file:
	img = Image.open(img_file)

	if not realtime_update:
		st.write("Duplo clique para cortar a imagem")
    
    #corta a imagem
	imagem_cortada = st_cropper(img, realtime_update=realtime_update, box_color=box_color, aspect_ratio=aspect_ratio)
    
    #escreve na tela
	st.write("Resultado")
    
    #mostrando o resultado
	corte = imagem_cortada.thumbnail((350,350))
	st.image(imagem_cortada)


if (file): 
    #lendo imagem
    file = imagem_cortada
    file = np.array(file)
    img_rgb = cv2.cvtColor(file, cv2.COLOR_BGR2RGB)
    
   
    #preparando imagem
    img_preparada = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2HSV)
    
    #tira ruidos
    img_med = cv2.medianBlur(img_preparada, 5)
    
    #binarização por hsv
    minimo =(160, 10, 10)
    maximo =(180, 255, 255)
    img_binaria = cv2.inRange(img_med, minimo, maximo)
    
    #dilatação
    element_estr = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7,7))
    img_process = cv2.dilate(img_binaria, element_estr, iterations = 1)
    
    #adiciona borda
    img_borda = cv2.copyMakeBorder(img_process, 10, 10, 10, 10, cv2.BORDER_CONSTANT, None, value = 0)
    
    #contagem
    img = img_borda.copy()

    #thresholding basico
    img[img > 127] = 255
    img[img <= 127] = 0



    altura  = img.shape[0]
    largura = img.shape[1]
    print ("altura  ",  altura)
    print ("largura ", largura)
    print ("pixels  ", altura*largura)
    st.write (" ## Contando Sementes")

    def conheceVizinhanca(img, q, cont, visitado):
        while (q.qsize() > 0):
            pixel = q.get()
            x     = pixel[0]
            y     = pixel[1]
            if(x > 0 and x < altura and y > 0 and y < largura):
                if(not visitado[x, y]):
                    img[x, y]      = 200 - cont*2;		
                    visitado[x, y] = True
                    q.put([x+1, y])
                    q.put([x-1, y])
                    q.put([x  , y+1])
                    q.put([x  , y-1])

    def contar(img):
        contador = 0
        visitado = img < 255 

        for x in range (0, altura):
            for y in range (0, largura):
                if not visitado[x, y]:
                    contador += 1
                    q = queue.Queue()
                    q.put([x, y])
                    conheceVizinhanca(img, q, contador, visitado)
                    cv2.putText(img, str(contador), (y,x), cv2.FONT_ITALIC, 0.5, 255,2)				
                    print (contador)
        st.write ("Total: ", contador, "objeto(s)")

    def areas(img):
        hist, bin = np.histogram(img.ravel(), 256, [1,254])
        contador = 0
        for i in range (254, 1, -1):
            if hist[i] > 0:
                contador += 1
        return contador

    contar(img)
    contador = areas(img) 
    histograma(img)

    
    #mostrar resultado
    st.image(img, caption='Imagem Contada', width=300)
