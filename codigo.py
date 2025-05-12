import pandas as pd
import datetime

lowlimit = 0
highlimit = 1000

muonDataFile = pd.read_csv("muonhunter-data.csv", dtype=str)
print("Cantidad de líneas: ", muonDataFile.shape[0]) #Guarda el número de registros
print("Inicio: ", muonDataFile['Log time'].iloc[0])
 
 
 
first_minute = pd.to_datetime(muonDataFile['Log time'].iloc[0])#Establece el primer y el último minuto
last_minute = pd.to_datetime(muonDataFile['Log time'].iloc[-1])
 
 
time_range = pd.date_range(start=first_minute, end=last_minute, freq='min')#crea un rango de fechas y horas desde el primer minuto hasta el último
 
 
muon = pd.DataFrame({#Crea un DataFrame vacío con columnas time,cpm, cph y missing seconds'
    'time': time_range,
    'cpm': 0,
    'cph': 0,
    'missing_s': 0
})

aux_count = pd.read_csv("aux_count.csv", dtype = str)

#########################################################Sin esto el programa da errores por los formatos de las fechas
for value in aux_count['time']:
    try:
        pd.to_datetime(value)
    except ValueError:
        print("Valor no reconocido como fecha:", value)
aux_count['time'] = pd.to_datetime(aux_count['time'])
############################################################

aux_count = pd.DataFrame({
    'time': aux_count['time'],  
    'totalCount': aux_count['totalCount'], 
    'periodCount': [None] * len(aux_count), 
    'missing_s': [-1] * len(aux_count)  
})
wrongCount_threshold = 20
missing_s_threshold = 10
missing_s_bw_entries_threshold = 30
prev_count = int(aux_count['totalCount'][0])
aux_count.loc[0, 'periodCount'] = 0
aux_count.loc[0, 'missing_s'] = 0


j_last_rec = 0 
j_new_rec = 0


size_aux_count = len(aux_count['time'])
i = 0
while i < size_aux_count and pd.to_datetime(aux_count['time'][i]) < (first_minute + pd.Timedelta(minutes=1)):
    muon['cpm'][0] += aux_count['periodCount'][i]
    muon['missing_s'][0] += aux_count['missing_s'][i]
    i += 1
muon['cph'][0] = round(60 * muon['cpm'][0])

# j=2 is th secon minutt!!!
j = 2


i = 0
j = 0

while i < len(aux_count['time']) and pd.to_datetime(aux_count['time'][i]) < (muon['time'][j] + pd.Timedelta(minutes=1)):
    aux_t = pd.Timestamp("2021-01-01 03:09:59", tz="GMT")
    if pd.Timedelta(aux_count['time'][i] - aux_t).total_seconds() == 0:#NORMAL BEHAVIOUR
        print("To stop")

    muon['cpm'][j] += int(aux_count['periodCount'][i])
    muon['missing_s'][j] += int(aux_count['missing_s'][i])

    i += 1
#cph añade los ÚLTIMOS!!!! minutos
if j > 60:
    if j_new_rec == j:#calcula el cph con los missing minutes
        if pd.isna(muon['cpm'][j-60]):
            muon['cph'][j] = muon['cpm'][j]
        else:#falta menos de una hora
            muon['cph'][j] = muon['cph'][j_last_rec] - muon['cpm'][j-60] + muon['cpm'][j]
    else:
        if pd.isna(muon['cpm'][j-60]):
            muon['cph'][j] = muon['cph'][j-1] + muon['cpm'][j]
        else:#NORMALMENTE quita el minuto anterior y añade el nuevo
            muon['cph'][j] = muon['cph'][j-1] - muon['cpm'][j-60] + muon['cpm'][j]
else:#Si la primera hora ya ha sucedido
    suma_cpm = suma_cpm + muon['cpm'][j]
    muon['cph'][j] = suma_cpm + round((60-j) * suma_cpm / j)

j += 1

#saving
print("Saving file integrating from seconds to minutes/n")
muon.to_csv("muonhunter-data-perMinute.csv", index=False)

#No tengo el de horas, solo el de minutos

#Preview of statistics
aux = muon['cph'].dropna()#Calcula la media, la mediana y la desviacion típica de los missing seconds y de cpm


print("mean(muon$missing_s)=", muon['missing_s'].mean())
print("median(muon$missing_s)=", muon['missing_s'].median())
print("sd(muon$missing_s)=", muon['missing_s'].std())

aux = muon['cpm'].dropna()
print("mean(muon$cpm) without na=", aux.mean())
print("median(muon$cpm) no na=", aux.median())
print("sd(muon$cpm) no na=", aux.std())




