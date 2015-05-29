# -*- coding: utf-8 -*-
import numpy as np
import scipy as sp
import os

import matplotlib as mpl
mpl.use("Qt4Agg")
#mpl.rcParams['text.usetex']=True
#mpl.rcParams['text.latex.unicode']=True
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D as line

from processing_gui import PostProcessingModule
import settings as st

#define your own functions here
class eval_A1(PostProcessingModule):
    '''
    create diagrams for evaluation step A1
    '''

    name = 'A1'

    line_color = '#aaaaaa'
    line_style = '-'
    font_size = 20
#    epsPercent = 2./5
    spacing = 0.01
    counter = 0
    
    def __init__(self):
        PostProcessingModule.__init__(self)
        return

    def run(self, data):
        print 'processing ',data['regime name']
        
        #dict for calculated values
        output = {}

        #reset counter
        self.counter = 0
        
        #calculate datasets
        t = data['results']['simTime']
        y = data['results']['model_output.0']
        yd = data['results']['trajectory_output.0'][-1]

        self.posLabel = np.arange(np.min(y) + 0.1*yd, yd, (yd-np.min(y))/4)
            
        #create plot
        fig = Figure()
        axes = fig.add_subplot(111)
        axes.set_title(r'\textbf{Sprungantwort}')
        axes.plot(t, y, c='k')
        axes.set_xlim(left=0, right=t[-1])
        axes.set_ylim(0,3.5)
        axes.set_xlabel(r'\textit{Zeit [s]}')
        axes.set_ylabel(r'\textit{Ballposition r(t) [m]}')
        
        #create desired line
        desiredLine = line([0, t[-1]], [yd, yd], lw=1, ls=self.line_style, c='k')
        axes.add_line(desiredLine)

        #calc rise-time (Anstiegszeit)
        try:            
            tr = t[y.index([x for x in y if x > yd*0.9][0])]
            #create and add line
            self.createTimeLine(axes, t, y, tr, r'$T_r$')
            output.update({'tr': tr})
        except IndexError:
            output.update({'tr': None})
            #print 'AttackLine is not defined'
        
        #calc correction-time (Anregelzeit)
        try:
            tanr = t[y.index([x for x in y if x > yd][0])]
            #create and add line
            self.createTimeLine(axes, t, y, tanr, r'$T_{anr}$')
            output.update({'tanr': tanr})
        except IndexError:
            #print 'RiseLine is not defined'
            output.update({'tanr': None})
        
        #calc overshoot-time and overshoot in percent (Überschwingzeit und Überschwingen)
        if output['tanr']:
            if yd > 0:
                y_max = np.max(y[t.index(tanr):])
            else:
                y_max = np.min(y[t.index(tanr):])
#            lastval = 0
#            for val in y[t.index(tanr):]:
#                y_max = (val - yd)*yd
                
#                if val < lastval:
#                    break
#                else:
#                    lastval = val
            to = t[y.index(y_max)]
#            to = t[y.index(val)]
            do = y_max - yd
            doPercent = do/yd * 100
            #create and add line
            self.createTimeLine(axes, t, y, to, r'$T_o$')
            output.update({'to': to, 'do': do, 'doPercent': doPercent})
        else:
            #print 'OvershootLine is not defined'
            output.update({'to': None, 'do': None, 'doPercent': None})

        #calc damping-time (Beruhigungszeit)
        try:                
#            eps = self.epsPercent*yd/100
            eps = st.R
            enterIdx = -1
            for idx, val in enumerate(y):
                if enterIdx == -1:
                    if abs(val - yd) < eps:
                        enterIdx = idx
                else:
                    if abs(val - yd) >= eps:
                        enterIdx = -1
            teps = t[enterIdx]
            #create and add line
            self.createTimeLine(axes, t, y, teps, r'$T_{\epsilon}$')
            output.update({'teps': teps})
        except IndexError:
            #print 'DampingLine is not defined'
            output.update({'teps': None})
        
        #create epsilon tube
        upperBoundLine = line([0, t[-1]], [yd+eps, yd+eps], ls='--', c=self.line_color)
        axes.add_line(upperBoundLine)
        lowerBoundLine = line([0, t[-1]], [yd-eps, yd-eps], ls='--', c=self.line_color)
        axes.add_line(lowerBoundLine)
        
        #calc control deviation
        control_deviation = y[-1] - yd
        output.update({'control_deviation': control_deviation})
        
        # print time data
        #print str(output) + '\n'    
        
        self.calcMetrics(data, output)

        #check for sim succes
        if not data['results']['finished']:
            for key in output.keys():
                output[key] = None

        #add settings and metrics to dictionary results
        results = {}
        results.update({'metrics': output})
        results.update({'modules': data['modules']})
        
        canvas = FigureCanvas(fig)
        
        self.writeOutputFiles(self.name, data['regime name'], fig, results)
        
        return {'name':'_'.join([data['regime name'], self.name]),\
                    'figure': canvas}
        
    def createTimeLine(self, axes, t, y, time_value, label):
        if time_value != t[-1]:
            #create timeLine
            timeLine = line([time_value, time_value],\
                            [np.min(y), y[t.index(time_value)]],\
                            ls = self.line_style,\
                            c = self.line_color) 
            axes.add_line(timeLine)
            #create label
            axes.text(time_value + self.spacing,\
                        self.posLabel[self.counter],\
                        label,\
                        size = self.font_size)
            self.counter = self.counter + 1

    def calcMetrics(self, data, output):
        '''
        calculate metrics for comaprism
        '''
        
        L1NormITAE = self.calcL1NormITAE(data)            
        L1NormAbs = self.calcL1NormAbs(data)
#                    
#        print 'ITAE score: ', errorIntegral
        print 'L1NormITAE: ', L1NormITAE
        print 'L1NormAbs: ', L1NormAbs
        print '\n'
        output.update({'L1NormITAE': L1NormITAE, 'L1NormAbs': L1NormAbs})
#        output.update({'ITAE': errorIntegral})
