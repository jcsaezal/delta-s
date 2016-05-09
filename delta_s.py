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

def scatter2DTrends(labeledPointsSched,markerSpecs,xlabel,ylabel,mode=0,figSize=[9.0,9.0],filename=None,windowTitle=None,legendLocation='best',axes_labelsize=None,label_offset=(37,5)):
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
        markerSpec=markerSpecs[sched]
        if  len(markerSpec)>1:
            extraArgs=dict(facecolor=markerSpec[1])
        else:
            extraArgs=dict()
        if mode==0:
            plt.plot(X, Y, markersize=10, marker=markerSpec[0],label=sched,linestyle='dashed')  #markerSpec[0])##'--o')
            ## X vs Y
            for x, y, note in zip(X,Y,Labels):
                plt.annotate(
                    note,
                    xy = (x, y), xytext = (offsetx, offsety),
                    textcoords = 'offset points', ha = 'right', va = 'bottom', color='black')
        elif mode==1:
            ## X vs Z
            plt.plot(X, Z, markersize=10, marker=markerSpec[0],label=sched,linestyle='dashed')  #markerSpec[0])##'--o')
            for x, y, note in zip(X,Z,Labels):
                plt.annotate(
                    note,
                    xy = (x, y), xytext = (offsetx, offsety),
                    textcoords = 'offset points', ha = 'right', va = 'bottom', color='black')
        else:
            print "Unsupported mode"
            return 1
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
                field=float(row[1])
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


def delta_s(max_h_idx,temps,fields,samples,min_h_idx=0):
    values=[]

    ## 
    for t in range(0,len(temps)-1):
        val=0.0
        for h in range(min_h_idx,max_h_idx-1):
            (tA,hA,mA)=samples[t][h]
            (tB,hB,mB)=samples[t+1][h+1]
            incr=((mB-mA)/(tB-tA))*(hB-hA)
            val=val+incr
        values.append(val)
    return values

nfields=int(sys.argv[2])

ret=parseInputCSV(sys.argv[1],nfields)

if ret==None:
    exit(1)

##Recuperar componentes individuales de las tuplas
(temps,fields,samples)=ret

## Una curva por cada incremento
results=[]
for i in range(2,nfields+1):
    ret=delta_s(i,temps,fields,samples)
    results.append(ret)

