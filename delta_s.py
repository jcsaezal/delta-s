#!/usr/bin/env python
import csv
import sys
import matplotlib 
import matplotlib.pyplot as plt
from matplotlib.markers import *
from math import *
import pandas as pd
import numpy as np
import os

class LabeledPoint:
    def __init__(self, label, x, y, z=0):
        self.label = label
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return repr((self.label, self.x, self.y, self.z))

## Point vector
def buildArrays(labeledPoints):
    X=[]
    Y=[]
    Z=[]
    Labels=[]
    for point in labeledPoints:
        Labels.append(point.label)
        X.append(point.x)
        Y.append(point.y)
        Z.append(point.z)

    return (Labels,X,Y,Z)   


def geomean(numbers):
    product = 1
    for n in numbers:
        product *= n
    return product ** (1.0/len(numbers))

def mean(numbers):
    val = 0.0
    for n in numbers:
        val = val+ n
    return (val/len(numbers))    

def scatter2DTrends(labeledPointsSched,series,xlabel,ylabel,figSize=[9.0,9.0],filename=None,windowTitle=None,axes_labelsize=None,label_offset=(37,5)):
    plt.rcParams["figure.figsize"]=figSize
    offsetx=label_offset[0]
    offsety=label_offset[1]

    plt.figure()
    fig = plt.gcf()
    if windowTitle!=None:
        fig.canvas.set_window_title(windowTitle)

    if axes_labelsize!=None:
        plt.xlabel(xlabel,fontsize=axes_labelsize)
        plt.ylabel(ylabel,fontsize=axes_labelsize)
    else:
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

    for serie in series:
        schedPoints=labeledPointsSched[serie]
        (Labels,X,Y,Z)=buildArrays(schedPoints)

        ## Hack para reconocer el color
        #markerSpec=markerSpecs[sched]
        #if  len(markerSpec)>1:
        #    extraArgs=dict(facecolor=markerSpec[1])
        #else:
        #    extraArgs=dict()
        plt.plot(X, Y, label=serie, marker=(3,0,0), markersize=10, linestyle='dashed')  #markerSpec[0])##'--o')

    lgd=plt.legend(loc='upper left', bbox_to_anchor=(1.02, 1), borderaxespad=0)

    plt.grid(True)
    
    plt.draw()

    if filename!=None:
        plt.savefig(filename,bbox_extra_artists=(lgd,), bbox_inches='tight')
    return 0


def parseInputExcel(filename,nfields):
    table=pd.read_excel(filename) 
    rows=table.values
    temperatures=[]
    increment_h_matrix=[] ## For each t,h value -> M (Magnetizacion) -> Estaria bien guardar tupla entera
    
    ## Lista de listas para guardar muestras correspondientes al mismo mfield (para media)
    mfields=[]
    for i in range(nfields):
        mfields.append([])

    field_cnt=0 ## Modular counter 0..nfields-1
    temp_cnt=0 ## The number of temperatures used is unkown at the beginning
    ## Assume one temperature value (at least)
    samples_same_temp=[]    
    increment_h_matrix.append(samples_same_temp)
    acum_temp=0.0

    for row in rows:
        if len(row)<3:
            print "Not enough columns"
            return None
        ## Valid row
        temperature=row[0]
        field=row[1]/10000.0 ## DIVIDIR ENTRE 10000 > 1T = 10000 Oe
        magnetization=row[2]

        ## Detect new temperature
        if field_cnt == nfields:
            temp_cnt=temp_cnt+1
            field_cnt=0
            ## Temperatura media
            temperatures.append(round(acum_temp/float(nfields),0))
            acum_temp=0.0
            samples_same_temp=[]    
            increment_h_matrix.append(samples_same_temp)

        ## Add new sample (tuple)  
        samples_same_temp.append((temperature,field,magnetization))
        acum_temp=acum_temp+temperature
        mfields[field_cnt].append(field)
        field_cnt=field_cnt+1

    
    ## Add last temperature average    
    temperatures.append(round(acum_temp/float(nfields),0))

    ## Calculate average for fields
    fields=[]
    for field_vs in mfields:
        fields.append(mean(field_vs))

    return (temperatures,fields,increment_h_matrix)

def parseInputCSV(filename,nfields):
    temperatures=[]
    increment_h_matrix=[] ## For each t,h value -> M (Magnetizacion) -> Estaria bien guardar tupla entera
    
    ## Lista de listas para guardar muestras correspondientes al mismo mfield (para media)
    mfields=[]
    for i in range(nfields):
        mfields.append([])

    field_cnt=0 ## Modular counter 0..nfields-1
    temp_cnt=0 ## The number of temperatures used is unkown at the beginning
    ## Assume one temperature value (at least)
    samples_same_temp=[]    
    increment_h_matrix.append(samples_same_temp)
    acum_temp=0.0

    with open(filename,"rb") as in_f: # <-- notice "rb" is used
        reader = csv.reader(in_f,delimiter=',')#delimiter='\t')
        nline=1
        for row in reader:
            if nline>1: ## Skip header
                #print nline,":", 
                if len(row)<3:
                    print "Not enough rows"
                    return None
                ## Valid row
                temperature=float(row[0])
                field=float(row[1])/10000.0 ## DIVIDIR ENTRE 10000 > 1T = 10000 Oe
                magnetization=float(row[2])

                ## Detect new temperature
                if field_cnt == nfields:
                    temp_cnt=temp_cnt+1
                    field_cnt=0
                    ## Temperatura media
                    temperatures.append(round(acum_temp/float(nfields),0))
                    acum_temp=0.0
                    samples_same_temp=[]    
                    increment_h_matrix.append(samples_same_temp)

                ## Add new sample (tuple)  
                samples_same_temp.append((temperature,field,magnetization))
                acum_temp=acum_temp+temperature
                mfields[field_cnt].append(field)
                field_cnt=field_cnt+1
            nline=nline+1
    
    ## Add last temperature average    
    temperatures.append(round(acum_temp/float(nfields),0))

    ## Calculate average for fields
    fields=[]
    for field_vs in mfields:
        fields.append(mean(field_vs))

    return (temperatures,fields,increment_h_matrix)


def delta_s(max_h_idx,temps,fields,samples,mass,min_h_idx=0):
    values=[]

    ## 
    for i in range(0,len(temps)-1):
        sum1=0.0
        for j in range(min_h_idx,max_h_idx-1):
            (tA,hA,mA)=samples[i][j]
            (tB,hB,mB)=samples[i][j+1]
            #Suma1=Suma1+0.5*(M(i,j+1)+M(i,j))*(B(i,j+1)-B(i,j))
            incr=(mB+mA)*(hB-hA)
            sum1=sum1+0.5*incr
        sum2=0.0
        for j in range(min_h_idx,max_h_idx-1):
            (tA,hA,mA)=samples[i+1][j]
            (tB,hB,mB)=samples[i+1][j+1]
            #Suma2=Suma2+0.5*(M(i+1,j+1)+M(i+1,j))*(B(i+1,j+1)-B(i+1,j))
            incr=(mB+mA)*(hB-hA)
            sum2=sum2+0.5*incr                                
        #DST(k)= -(Suma2-Suma1)/(T(i+1)-T(i))/rmasa
        val=-((sum2-sum1)/(temps[i+1]-temps[i]))/mass
        values.append(val)
    return values

if len(sys.argv)<4 or len(sys.argv)>5:
    print "Usage: %s <data_file> <nfield_values> <mass> [output_file]" % sys.argv[0]
    exit(0)


input_file=sys.argv[1]
nfields=int(sys.argv[2])
mass=float(sys.argv[3])


if len(sys.argv)==5:
    output_file=sys.argv[4]

basename, file_extension = os.path.splitext(input_file)
pdf_file="%s.pdf" % basename

## Start processing
if file_extension=='.csv' or file_extension=='.dat':
    ret=parseInputCSV(sys.argv[1],nfields)
    csv_format=True
elif file_extension=='.xls' or file_extension=='.xlsx':
    ret=parseInputExcel(sys.argv[1],nfields)
    csv_format=False
else:
    print "Unrecognized file extension: %s" % (file_extension)
    exit(1)

## Build output file name if necessary
if len(sys.argv)==5:
    output_file=sys.argv[4]
    basename, file_extension = os.path.splitext(output_file)
    if file_extension=='.csv' or file_extension=='.dat':
        csv_format=True
    else:
        csv_format=False
else:
    output_file="%s_out%s" % (basename,file_extension)



if ret==None:
    exit(1)

##Recuperar componentes individuales de las tuplas
(temps,fields,samples)=ret

## Una curva por cada incremento
results=[]
#for i in range(2,4):
for i in range(2,nfields+1):
#for i in range(1,nfields-1):
    ret=delta_s(i,temps,fields,samples,mass)
    results.append(ret)


## Prepare unitary rows (one row per temperature (minus one) -> last temperature does not apply )
output_rows=[] ## To generate output panda table
for i in range(len(temps)-1):
    output_rows.append([temps[i]]) # (Temperature field)

data={}
series=[]
for i in range(len(results)):
    curve=results[i]
    name="H=%.2f T" % fields[i+1] # "H=%i" % i
    data[name]=[]
    series.append(name)
    for j in range(len(curve)):
        x=temps[j]
        y=curve[j]
        z=i ## Rango
        data[name].append(LabeledPoint(name,x,y,z))
        ## Fill corresponding value
        output_rows[j].append(curve[j])

header=list(series)

series.reverse()
             
# Formato: Lista de listas
# en cada lista -> pos 0 es el tipo de marker
# TipoDeMarker: caracter o tupla (numsides, style, angle)
#  http://matplotlib.org/1.4.1/api/markers_api.html#module-matplotlib.markers
# pos 1 de la lista es el descriptor de color (acepta caracteres con colores predefinidos)
# , colores HTML, escala de grises (num. entre 0 y 1)
# http://matplotlib.org/1.4.1/api/colors_api.html
# markersRaw=[['o'],[(4,0,0),'k'],['^'],[(7,2,0)],[(3,0,0),'k']]

# ## Prepare markers (for each workload)
# markerSpecs={}
# marker_cnt=0
# nr_markers=len(markersRaw)
# for wname in selectedWorkloads:
#     markerSpecs[wname] = markersRaw[marker_cnt%nr_markers]
#     marker_cnt = marker_cnt + 1


fsize=16
rcParams['font.family'] = 'Arial'
rcParams['xtick.labelsize'] = fsize
rcParams['ytick.labelsize'] = fsize
rcParams['legend.fontsize'] = fsize
rcParams['grid.linewidth']= 1.0
#rcParams['text.usetex']= 1

figSize=[8.0,7.0]
scatter2DTrends(data,series,r'$T(K)$',r'$\Delta S$',figSize,filename=pdf_file,windowTitle="DeltaS",axes_labelsize=fsize,label_offset=(10,5))

#Uncomment to display the chart windows
#plt.show()

##Generate output panda table
nparray=np.array(output_rows)
outputTable=pd.DataFrame(nparray)
header.insert(0,"Temp (K)")
if csv_format:
    outputTable.to_csv(output_file,header=header,index=False,sep=',',encoding='utf-8')
else:
    outputTable.to_excel(output_file,header=header,index=False)



