import pandas as pd
from fastapi import FastAPI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


app = FastAPI()

@app.get("/")
def read_root():
    return {"NO TE OLVIDES DE AGREGAR /docs"}


@app.get("/cantidad_filmaciones_mes/{Mes}")

def cantidad_filmaciones_mes( Mes ):

    #Importamos el csv final
    movies_credits_final = pd.read_csv('dataset_final.csv', index_col=0)

    #Nos aseguramos que la columna "release_date" este en formato datetime para cumplir los endpoints
    movies_credits_final['release_date'] = pd.to_datetime(movies_credits_final['release_date'])

    #Convertimos el nombre del mes en español a número
    meses = {
        'enero': 1,
        'febrero': 2,
        'marzo': 3,
        'abril': 4,
        'mayo': 5,
        'junio': 6,
        'julio': 7,
        'agosto': 8,
        'septiembre': 9,
        'octubre': 10,
        'noviembre': 11,
        'diciembre': 12
    }
    mes_a_numero = meses.get(Mes.lower())
    
    #Si no se ha ingresado un mes valido en español retornaremos el mensaje de advertencia
    if mes_a_numero not in [1,2,3,4,5,6,7,8,9,10,11,12] :
        return f"El mes '{Mes}' no es válido. Por favor ingresa un mes en español."
    
    #Si se ha ingresado un mes valido en español retornaremos la cantidad de filmaciones aplicando el siguiente filtro
    cantidad_pelis = movies_credits_final[movies_credits_final['release_date'].dt.month == mes_a_numero].shape[0]
    
    return f"En {Mes} fueron estrenadas {cantidad_pelis} películas."

@app.get("/cantidad_filmaciones_dia/{Dia}")

def cantidad_filmaciones_dia(Dia):

    #Importamos el csv final
    movies_credits_final = pd.read_csv('dataset_final.csv', index_col=0)
    
    #Nos aseguramos que la columna "release_date" este en formato datetime para cumplir los endpoints
    movies_credits_final['release_date'] = pd.to_datetime(movies_credits_final['release_date'])
    
    #Si el dia se debe ingresar en español tendremos que usar el metodo dayofweek en la consulta, para eso debemos mapear
    #los dias de la semana en su nombre en español a sus índices
    semanaDia = {"lunes": 0,"martes": 1,"miércoles": 2,"jueves": 3,"viernes": 4,"sábado": 5,"domingo": 6}

    #Pasamos a minuscula el dia ingresado en español en la consulta
    dia_minuscula = Dia.lower()

    #Si no se ha ingresado un día valido en español retornaremos el mensaje de advertencia
    if dia_minuscula not in semanaDia:
        return f"El día '{Dia}' no es válido. Por favor ingresar un día de la semana en español."
    
    #Nos quedamos con el indice del dia correspondiente
    indiceDia = semanaDia[dia_minuscula]

    #Ahora filtramos la cantidad de peliculas que se estrenaron en el dia ingresado aplicando el siguiente filtro
    cantidad_pelis = movies_credits_final[movies_credits_final['release_date'].dt.dayofweek == indiceDia].shape[0]

    return f"En los días {Dia} fueron estrenadas {cantidad_pelis} peliculas"

@app.get("/votos_titulo/{titulo_de_la_filmacion}")

def votos_titulo(titulo_de_la_filmacion):
  
   #Importamos el csv final
   movies_credits_final = pd.read_csv('dataset_final.csv', index_col=0)

   #Guardaremos en una variable los datos del df correpondiente al titulo ingresado. Aplicaremos minuscula
   pelicula = movies_credits_final[movies_credits_final['title'].str.lower() == titulo_de_la_filmacion.lower()]

   #Si no se ha encontrado la pelicula, devolvemos un mensaje de advertencia
   if pelicula.empty:
      return f"El nombre de la película '{titulo_de_la_filmacion}' no se encontró en la consulta. Por favor intente otro nombre."
   
   #Si la pelicula encontrada no tiene 2000 valoraciones o mas, informamos eso con un mensaje y pedimos otro titulo.
   if pelicula['vote_count'].values[0] < 2000:
      return f"La película '{titulo_de_la_filmacion}' no tiene al menos 2000 votos. Intente con otra pelicula por favor."
   
   #Creamos las variables que filtran la consulta para luego mostrar en el resultado de la funcion
   cant_votos = pelicula['vote_count'].values[0]
   promedio_votos = pelicula['vote_average'].values[0]
   titulo = pelicula['title'].values[0]

   return f"La pelicula {titulo} tiene {promedio_votos} en promedio de votos y cuenta con un total de {cant_votos} valoraciones"

@app.get("/score_titulo/{titulo_de_la_filmacion}")

def score_titulo(titulo_de_la_filmacion):
   
   #Importamos el csv final
   movies_credits_final = pd.read_csv('dataset_final.csv', index_col=0)
   
   #Guardaremos en una variable los datos del df correpondiente al titulo ingresado. Aplicaremos minuscula
   pelicula = movies_credits_final[movies_credits_final['title'].str.lower() == titulo_de_la_filmacion.lower()]
   
   #Si no se ha encontrado la pelicula, devolvemos un mensaje de advertencia
   if pelicula.empty:
    return f"El nombre de la película '{titulo_de_la_filmacion}' no se encontró en la consulta. Por favor intente otro nombre."
    
   #Si la pelicula se ha encontrado, retornamos los datos solicitados, crearemos las variables que filtran la consulta para luego
   #mostrar en el resultado de la funcion
   año_estreno = pelicula['release_year'].values[0]
   titulo = pelicula['title'].values[0]
   score = pelicula['popularity'].values[0]
   
   return f"La película '{titulo}' se ha estrenado el año {año_estreno} y cuenta con {score} de puntaje de popularidad asignado por TMDB"

@app.get("/get_actor/{nombre_actor}")

def get_actor(nombre_actor):

    #Importamos el csv final
    movies_credits_final = pd.read_csv('dataset_final.csv', index_col=0)
    
    #Primero nos aseguramos que en "cast" no hayan quedado nulos luego del merge, y si hay nulos cambiar por "no cast information"
    movies_credits_final['cast'] = movies_credits_final['cast'].fillna('[no cast information]')
    nombre_actor = [nombre_actor]

    #Guardamos en una variable las filas o las peliculas del df donde se encuentre al actor
    peliculas_actor = movies_credits_final[movies_credits_final['cast'].apply(lambda x: any(d in x for d in nombre_actor))]

    #Si el actor ingresado no esta en la consulta devolvemos un mensaje de advertencia
    if peliculas_actor.empty:
        return f"El actor {nombre_actor} no se ha encontrado. Por favor intente con otro nombre o intente escribiendo las primeras letras con mayuscula."

    #Creamos las variables que filtran la consulta para luego mostrar en el resultado de la funcion
    retorno_actor = round(peliculas_actor['return'].sum(),2)
    retorno_promedio = round(peliculas_actor['return'].mean(),2)
    pelis_cantidad =  peliculas_actor['id'].shape[0]
    nombre_actor = nombre_actor[0]

    return f"El actor {nombre_actor} participó en {pelis_cantidad} peliculas con un retorno total de {retorno_actor} en millones de dolares, y ha tenido un promedio de {retorno_promedio} en millones de dolares de retorno por pelicula."

@app.get("/get_director/{nombre_director}")

def get_director( nombre_director ):

    #Importamos el csv final
    movies_credits_final = pd.read_csv('dataset_final.csv', index_col=0)
    
    #Primero nos aseguradmos que en "director" no hayan quedado nulos luego del merge, y si hay nulos cambiar por "no director information"
    movies_credits_final['director'] = movies_credits_final['director'].fillna('[no director information]')

    #Guardamos en una variable las filas o las peliculas del df donde se encuentre al director
    peliculas_director = movies_credits_final[movies_credits_final['director'] == nombre_director]

    #Si el director ingresado no esta en la consulta devolvemos un mensaje de advertencia
    if peliculas_director.empty:
        return f"El director {nombre_director} no se ha encontrado. Por favor intente con otro nombre o intente escribiendo las primeras letras con mayuscula."
    
    #Creamos las variables que filtran la consulta para luego mostrar en el resultado de la funcion
    retorno_director = round(peliculas_director['return'].sum(),2)
    exito_director = f"El director {nombre_director} en sus peliculas tuvo un retorno total de {retorno_director} en millones de dolares"

    return exito_director, peliculas_director[['title', 'release_date', 'budget', 'return']]

#A continuación desarrollaremos en endpoint de machine learning

#Importamos el csv final
movies_credits_final = pd.read_csv('dataset_final.csv', index_col=0)

#Comenzaremos eligiendo una muestra filtrando el dataframe con las películas que se hayan estrendo a partir del año 1987
movies_muestra = movies_credits_final[(movies_credits_final['release_year'] >= 1987)].sample(n=5000, random_state=42)

#Hacemos el preprocesamiento de los datos, convertimos a strig los datos de las columnas que usaremos para vectorizar
movies_muestra['director'] = movies_muestra['director'].astype(str)
movies_muestra['genres'] = movies_muestra['genres'].apply(lambda x: ' '.join(map(str, x)) if isinstance(x, list) else '')

#Se crea una columna que combine los valores de las que serán vectorizadas
movies_muestra['vectorizable'] = movies_muestra['director'] + ' ' + movies_muestra['genres']

#Se pasa a minúsculas todos los textos para no influir en la cantidad generada
movies_muestra['vectorizable'] = movies_muestra['vectorizable'].str.lower()

#Creamos una instancia de TfidfVectorizer para vectorizar el texto en una matriz de características
tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=3000)

#Transformar los datos
tfidf_matrix = tfidf_vectorizer.fit_transform(movies_muestra['vectorizable'])

#Se calcula la similitud coseno
matriz_de_similitud2 = cosine_similarity(tfidf_matrix)

@app.get("/recomendacion/{titulo}")

def recomendacion(titulo):
   
    #Obtenemos el índice de la película
    indice_pelicula = movies_credits_final[movies_credits_final['title'].str.lower() == titulo.lower()].index
    
    #Si no está la película ingresada, enviamos un mensaeje
    if indice_pelicula.empty:
        return f"No se encontró la película con el título: {titulo}. Intente con el nombre original"
    
    # Obtener los índices de las películas más similares
    peliculas_similares = matriz_de_similitud2[indice_pelicula[0]].argsort()[::-1]

    # Obtener los títulos de las películas recomendadas
    recomendaciones = movies_credits_final[['release_year','title']].iloc[peliculas_similares[1:6]]

    recomendaciones = recomendaciones['title'].tolist()

    return recomendaciones
