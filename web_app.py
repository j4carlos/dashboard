import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import requests
import pandas as pd
import datetime

api_url='https://ftx.us/api'
#api = '/markets'
#url = api_url + api

cryptos=['BTC/USD','ETH/USD','USDT/USD','DOGE/USD','SHIB/USD',
         'AAVE/USD','LTC/USD','LINK/USD','DAI/USD','UNI/USD']

option = st.sidebar.selectbox('Select one symbol', (cryptos))

today = datetime.date.today()
before = today - datetime.timedelta(days=500)
start_date = st.sidebar.date_input('Start date', before)
end_date = st.sidebar.date_input('End date', today)

market_name = option

resolution = 60 * 60 * 24
start = datetime.datetime(2021,1,1).timestamp()

path = f'/markets/{market_name}/candles?resolution={resolution}&start={start}'
url = api_url + path

grafico = requests.get(url).json()
graf = pd.DataFrame(grafico['result'])
graf = graf[graf['startTime']>str(start_date)]
graf['date'] = pd.to_datetime(graf['startTime'])
graf = graf.set_index('date')
graf = graf.drop(columns=['startTime','time'])

varianza = graf['close'].var()
volumen= graf['volume'][-1]+graf['volume'][-2]
volumenAnt = (graf['volume'][-2]-graf['volume'][-3])/graf['volume'][-2]

col1, col2, col3,col4 = st.columns(4)
col1.image('https://help.ftx.com/hc/article_attachments/4410000944788/mceclip3.png',width=110)
col2.metric(f'Cryto:{option}',f'{(graf["close"][-1])}',f'{(graf["close"][-1]-graf["close"][-2]):.2f}')
col3.metric("Varianza",f'{varianza:.3g}', '')
col4.metric("Volumen 24h",f'{volumen}',f'{volumenAnt:1%}')


#x = graf.index()
y = graf['close']

fig1, ax1 = plt.subplots()
ax1.plot(y)

ax1.set(xlabel='Fecha', ylabel='Precio',
       title=f'Precio {option}')
ax1.grid()


barras = []
for i in range(0,len(cryptos)):
    market_name = cryptos[i]
    
    path = f'/markets/{market_name}'
    url = api_url + path
    
    salida = requests.get(url).json()
    #salida = dict(salida)
    salida = salida['result']
    df1 = pd.DataFrame([salida])
    
    barras.append(df1['volumeUsd24h'][0])
    
barras = pd.DataFrame(barras)
barras['volumen24h']=barras[0]
barras.drop(columns=[0])


fig, ax = plt.subplots()

y_pos = np.arange(len(cryptos))

ax.barh(y_pos, barras['volumen24h'], align='center')
ax.set_yticks(y_pos, labels=cryptos)
ax.invert_yaxis()  # labels read top-to-bottom
ax.set_xlabel('u$d')
ax.set_title('Volumen 24 horas en mill u$d')


barras,lineas = st.columns(2)
barras.pyplot(fig)
lineas.pyplot(fig1)


#--------------------Medias moviles-----------------#


valores = graf['close']
valores = valores.reset_index()
valores = valores.drop(columns=['date'])
abd=list(valores['close'])


def moving_average(d, w):
   d=pd.DataFrame(d)
   return d.rolling(w).mean()

def extraer(x):
   dataB=[]
   for item in abd[:-x:-1]:
      dataB.append(item)
   dataR=[]
   for item in dataB[::-1]:
      dataR.append(item)
   return np.array(dataR)


if st.checkbox('Medias moviles'):
   medias = [30,50,120,150,200,250]
   m = st.selectbox('Medias',medias)
   datos = extraer(1.1*m)

   datosX = moving_average(datos,m)

   mva = pd.DataFrame(datos,columns=['Datos'])
   mva[f'Media de {m}'] = datosX
   st.line_chart(mva)

########### Calculadora ##############

opcCalc = st.sidebar.selectbox('Divisa de origen',('Crypto','USD'))
calculadora = st.sidebar.number_input('Monto')
A = graf['close'][-1]
if opcCalc == 'Crypto':
   wallet = str(float(calculadora)*A)
   out=f'{wallet} $'
else:
   wallet = float(calculadora)/A
   out = wallet

st.sidebar.write(out)
