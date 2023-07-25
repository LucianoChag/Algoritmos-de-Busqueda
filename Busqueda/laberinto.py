import heapq
from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np

class Nodo():
    def __init__(self,_estado,_padre, costo_acumulado):
        self.estado=_estado   #Entendemos por estado (fila,columna)
        self.padre=_padre     
        #self.accion=_accion    #Accion es simplemente un texto
                                #que diga que accion se realizo, ejemplo (Arriba,Abajo,Izquierda,Derecha)
                                #No es fundamental para el funcionamiento
        self.valor_heuristico = 0  #Atributo para almacenar el valor heurístico
        self.costo_acumulado = costo_acumulado #Atributo para almacenar el costo acumulado durante la ejecución

    def __lt__(self, other): #Compara dos objetos que se encuentran en el montículo heap
        return self.valor_heuristico < other.valor_heuristico


class FronteraStack(): #Algoritmo DFS
    def __init__(self):
        self.frontera=[]

    def agregar_nodo(self,_nodo):
        #Agregar el nodo pasado por parametro a la frontera
        self.frontera.append(_nodo)

    def quitar_nodo(self):
        #Quitar nodo de la frontera (respetar el tipo de frontera)
        return self.frontera.pop()

    def esta_vacia(self):
        #Comprobar si la frontera está vacia o no
        if self.frontera == []:
            return True

    def contiene_estado(self,_estado):
        #Comprobar si el estado pasado por parametro ya se encuentra en la frontera
        for nodo in self.frontera:
            if _estado == nodo.estado:
                return True
        return False


class FronteraQueue(FronteraStack): #Algoritmo BFS
    ''' Aplicar herencia con FronteraStack
        La unica diferencia entre ambas es como
        se quitan los nodos
    '''
    def quitar_nodo(self):
        return self.frontera.pop(0)


class FronteraGreedy(FronteraStack): #Algoritmo GBFS
    def heuristica(self, inicio, meta):
        #Utilizamos la distancia de Manhattan entre dos puntos, Inicio y Meta, del laberinto
        return abs(meta[0] - inicio[0]) + abs(meta[1] - inicio[1])
    def agregar_nodo(self, _nodo, meta):
        # Agregar el nodo pasado por parámetro a la frontera ordenado por su valor heurístico.
        valor_heuristico = self.heuristica(_nodo.estado, meta)
        _nodo.valor_heuristico = valor_heuristico  # Asignamos el valor heurístico al nodo.
        heapq.heappush(self.frontera, _nodo)  # Utilizamos heappush directamente, ya que ahora los nodos son comparables gracias a la función __lt__
    def quitar_nodo(self):
        # Quitar el nodo con menor costo total de la frontera.
        nodo = heapq.heappop(self.frontera)
        return nodo



class FronteraA(FronteraGreedy):
    def agregar_nodo(self, _nodo, meta):
        # Calcular el valor heurístico (h) y el costo acumulado (g) del nodo.
        valor_heuristico = self.heuristica(_nodo.estado, meta)
        costo_acumulado = _nodo.costo_acumulado + 1  # Costo acumulado desde el nodo padre + 1 (movimiento).

        # Asignamos los valores al objeto nodo
        _nodo.valor_heuristico = valor_heuristico
        _nodo.costo_acumulado = costo_acumulado

        # Calcular el costo total (f) y agregar el nodo a la frontera.
        costo_total = costo_acumulado + valor_heuristico
        _nodo.costo_total = costo_total

        # Se agrega al heap la frontera y una tupla que contiene el costo acumulado y el nodo
        heapq.heappush(self.frontera, (_nodo.costo_total, _nodo))
    #Redefinimos esta función para que pueda acceder correctamente al nodo ya que ahora es una tupla
    def contiene_estado(self, _estado):
        for nodo in self.frontera:
            if _estado == nodo[1].estado:
                return True
        
        return False


class Laberinto():
    def  __init__(self,_algoritmo):
        ''' Dentro del init podemos ejecutar funciones
            para ir definiendo los atributos de la clase.
            Les dejo lista la parte de leer el laberinto
            del archivo de texto, y la detección del inicio,
            meta y paredes.
        '''
        

        with open('laberinto.txt','r') as archivo:
            contenido=archivo.read()     #Con read() leemos todo el archivo y lo guardamos en contenido

        contenido=contenido.splitlines() #Con splitlines() separamos el contenido en lineas, eliminando el \n

        self.ancho=len(contenido[0])    #El ancho del laberinto es la cantidad 
                                        #de caracteres de la primer linea 
                                        #(O de cualquiera suponiendo que todas tienen el mismo ancho)
        self.alto=len(contenido)        #El alto del laberinto es la cantidad de lineas
        self.paredes=[]                 #Lista de paredes

        for fila in range(self.alto):   #Recorremos todas las filas
            fila_paredes=[]             #Creamos una lista vacia para las paredes de la fila actual
                                        #para cada fila se vuelve a limpiar la lista
            for columna in range(self.ancho): #Recorremos todas las columnas
                if contenido[fila][columna]==' ': #Si el caracter esta vacio es camino
                    fila_paredes.append(False) #Agregamos el camino a la lista de paredes de la fila actual
                elif contenido[fila][columna]=='I':   #Si el caracter es I es el inicio
                    self.inicio=(fila,columna)        #Guardamos el inicio
                    fila_paredes.append(False)         
                elif contenido[fila][columna]=='M':   #Si el caracter es M es la meta
                    self.meta=(fila,columna)          #Guardamos la meta
                    fila_paredes.append(False)
                else:
                    fila_paredes.append(True)  #Si no es ninguna de las anteriores, es una pared         
            self.paredes.append(fila_paredes)  #Agregamos la lista de paredes de la fila actual a la lista de paredes
        #De este modo ya tenemos identificadas las paredes, el inicio y la meta
        self.solucion=[] #Creamos una lista vacía que contiene la solución al laberinto
        self.algoritmo=_algoritmo #String en el que pasamos el nombre del algoritmo a utilizar

    def expandir_nodo(self,_nodo):
        ''' Dentro de _nodo.estado tenemos la posicion actual del nodo
            Debemos comprobar en todas las direcciones si podemos movernos
            descartando las que sean paredes o esten fuera del laberinto                 (i-1,j)
            Utilicen el grafico que está en el Notion para guiarse                (i,j-1) (i,j) (i,j+1)
            Devolver una lista de vecinos posibles (nodos hijo)                          (i+1,j)
        '''
        fila, columna = _nodo.estado
        #Creamos la lista de movimientos por defecto
        posiciones = [(fila - 1, columna),
                    (fila, columna -1),
                    (fila + 1, columna),
                    (fila, columna + 1)]
        
        vecinos = [] #Creamos una lista vacia con los movimientos posibles/validos/vecinos

        for fila, columna in posiciones:
            if fila >= 0 and fila < self.alto and columna >= 0 and columna < self.ancho and not self.paredes[fila][columna]: #Recordar que la lista de paredes tiene True si hay una pared y False si hay un camino, por ello se usa el operado NOT
                vecinos.append((fila,columna))
        
        return vecinos
                


    def resolver(self):
        '''
        Acá tienen que implementar el algoritmo de busqueda
        La idea es intentar replicar el pseudocodigo que vimos en clase
        1- Inicializar la frontera con el nodo inicial
        2- Inicializar el conjunto de explorados como vacio
        3- Repetimos:
            3.1- Si la frontera esta vacia, no hay solucion
            3.2- Quitamos un nodo de la frontera
            3.3- Si el nodo contiene un estado que es meta, devolver la solucion
            3.4- Agregar el nodo a explorados
            3.5- Expandir el nodo, agregando los nodos hijos a la frontera
        '''
        #Determinamos los algoritmos existentes y a utilizar
        if self.algoritmo=='BFS': #Breadth-First Search
            frontera = FronteraQueue()
        elif self.algoritmo=='DFS': #Depth-First Search 
            frontera = FronteraStack()
        elif self.algoritmo == 'GBFS': #Greedy Best-First Search
            frontera = FronteraGreedy()
        elif self.algoritmo == 'A': #A*
            frontera = FronteraA()
            
        #------------------------------------------------------------------------
        nodo_inicial = Nodo(self.inicio, None, 0) #Nodo inicial, sin un padre y sin costo acumulado
        ''' En los algoritmos de Busqueda Informada (BI) se tiene en cuenta la distancia que hay entre
            el inicio y la meta, es por ello que se realiza esta condición que varía los argumentos 
            que se le pasan a la función agregar_nodo() ya que NECESITA calcular dicha distancia. 
            En cambio, los algoritmos de Busqueda No Informada (BNI) NO lo necesitan, por lo que solo se 
            pasa el nodo
        '''
        if self.algoritmo == "GBFS" or self.algoritmo == "A":
            frontera.agregar_nodo(nodo_inicial, self.meta) #Agregamos el nodo a la frontera de BI
        else:
            frontera.agregar_nodo(nodo_inicial) #Agregamos el nodo a la frontera de BNI
            
        self.estados_explorados = [] #Esta lista contiene los estados, es decir la fila y columna
        self.nodos_explorados = [] #Esta lista contiene los objetos tipo Nodo

        while (True):
            if frontera.esta_vacia(): #Comprobamos si la la frontera está vacía
                raise Exception("No hay solucion") 
            
            #Si usamos el algoritmo A* la forma de quitar el nodo es distinta
            if self.algoritmo == "A":
                nodo_actual = frontera.quitar_nodo()[1]
            else:
                nodo_actual = frontera.quitar_nodo()
            
            if nodo_actual.estado == self.meta: #Chequeamos si llegó a la meta

                print("Algoritmo utilizado: ", self.algoritmo)
                
                nodo_aux = nodo_actual #Creamos un objeto auxiliar para no interferir con el actual
                
                self.nodos_explorados.reverse() #Damos vuelta la lista para poder trabajar en el orden correcto

                for nodo in self.nodos_explorados: #Bucle para recorrer todos los nodos explorados
                    estado = nodo_aux.padre.estado 
                    if estado == nodo.estado: #Chequeamos si el padre del actual es igual al primer nodo explorado
                        self.solucion.append(estado) #Si es correcto, significa que ese nodo es su predecesor
                        nodo_aux = nodo #Cambiamos el auxiliar al actual 

                self.solucion.reverse() #Damos vuelta la lista ya que se ingresaron los valores desde el último al primero
                self.solucion.append(nodo_actual.estado) #Agregamos la meta a la solución
                print("Recorrido: ", self.solucion)
                
                costo = len(self.nodos_explorados) #Determinamos cuantos nodos exploró
                print("Nodos explorados: ", costo)
                return #Finalizamos el bucle

            #Continuamos el bucle
            self.estados_explorados.append(nodo_actual.estado) #Agregamos el estado a la lista de estados explorados
            self.nodos_explorados.append(nodo_actual) #Agregamos el Nodo a la lista de nodos explorados

            vecinos = self.expandir_nodo(nodo_actual) #Expandimos el nodo y agregamos los movimientos posibles

            for vecino in vecinos:
                #Chequeamos si la frontera está vacia y si los vecinos no han sido explorados 
                if not frontera.contiene_estado(vecino) and vecino not in self.estados_explorados:
                    #Creamos un nuevo objeto nodo
                    nuevo_nodo = Nodo(vecino, nodo_actual, nodo_actual.costo_acumulado + 1)
                    if self.algoritmo == "GBFS" or self.algoritmo == "A":
                        frontera.agregar_nodo(nuevo_nodo, self.meta)
                    else:
                        frontera.agregar_nodo(nuevo_nodo)
                
    
    def generar_imagen(self, ruta_camino, nodos_explorados):
        # Crear una matriz numérica para representar el laberinto en la imagen.
        imagen_laberinto = np.zeros((self.alto, self.ancho))

        for fila in range(self.alto):
            for columna in range(self.ancho):
                if self.paredes[fila][columna]:
                    imagen_laberinto[fila][columna] = 1  # Paredes (valor 1)

        # Marcar los nodos explorados en la imagen.
        for nodo in nodos_explorados:
            fila, columna = nodo.estado
            imagen_laberinto[fila][columna] = 2  # Nodos explorados (valor 2)

        # Marcar el camino recorrido en la imagen.
        for fila, columna in ruta_camino:
            imagen_laberinto[fila][columna] = 3  # Camino recorrido (valor 3)

        # Marcar el inicio en la imagen.
        inicio_fila, inicio_columna = self.inicio
        imagen_laberinto[inicio_fila][inicio_columna] = 4  # Inicio (valor 4)

        # Marcar la meta en la imagen.
        meta_fila, meta_columna = self.meta
        imagen_laberinto[meta_fila][meta_columna] = 5  # Meta (valor 5)

        # Utilizar un colormap personalizado para visualizar los valores numéricos con colores.
        cmap = cm.colors.ListedColormap(['lightblue', 'gray', 'pink', 'lightgreen', 'white', 'black'])
        plt.imshow(imagen_laberinto, cmap=cmap, interpolation='none')
        plt.axis('off')
        plt.show()


laberinto = Laberinto("A") 
laberinto.resolver()       
laberinto.generar_imagen(laberinto.solucion, laberinto.nodos_explorados)


