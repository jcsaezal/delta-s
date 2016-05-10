#!/usr/bin/python
import csv
import sys
import matplotlib 
import matplotlib.pyplot as plt
from matplotlib.markers import *
from math import *

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

def scatter2DTrends(labeledPointsSched,xlabel,ylabel,figSize=[9.0,9.0],filename=None,windowTitle=None,legendLocation='best',axes_labelsize=None,label_offset=(37,5)):
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

    for sched in labeledPointsSched.keys():
        schedPoints=labeledPointsSched[sched]
        (Labels,X,Y,Z)=buildArrays(schedPoints)

        ## Hack para reconocer el color
        #markerSpec=markerSpecs[sched]
        #if  len(markerSpec)>1:
        #    extraArgs=dict(facecolor=markerSpec[1])
        #else:
        #    extraArgs=dict()
        plt.plot(X, Y, marker=(3,0,0), markersize=10, linestyle='dashed')  #markerSpec[0])##'--o')

    plt.legend(loc=legendLocation) # scatterpoints=1)
    plt.grid(True)
    plt.draw()
    if filename!=None:
        plt.savefig(filename)
    return 0


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
        fields.append(round(mean(field_vs),0))

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

nfields=int(sys.argv[2])
mass=float(sys.argv[3])
ret=parseInputCSV(sys.argv[1],nfields)

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



data={}

for i in range(len(results)):
    curve=results[i]
    name=str(i)
    data[name]=[]
    for j in range(len(curve)):
        x=temps[j]
        y=curve[j]
        z=i ## Rango
        data[name].append(LabeledPoint("nada",x,y,z))
             
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
rcParams['font.family'] = 'Helvetica'
rcParams['xtick.labelsize'] = fsize
rcParams['ytick.labelsize'] = fsize
rcParams['legend.fontsize'] = fsize
rcParams['grid.linewidth']= 1.0

figSize=[10.0,9.0]
scatter2DTrends(data,"T(K)","DeltaS",figSize,filename="figure.pdf",windowTitle="EDP",legendLocation='upper right',axes_labelsize=fsize,label_offset=(10,5))

#Uncomment to display the chart windows
plt.show()



