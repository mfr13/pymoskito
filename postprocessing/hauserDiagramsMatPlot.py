# -*- coding: utf-8 -*-
import numpy as np
import scipy as sp

import matplotlib as mpl
mpl.use("Qt4Agg")
mpl.rcParams['text.usetex']=True
mpl.rcParams['text.latex.unicode']=True
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.figure import Figure

from postprocessing import PostProcessingModule
import settings as st

#define your own functions here
class hauserDiagramsMatPlot(PostProcessingModule):
    '''
    create diagrams like hauser did
    '''

    def __init__(self):
        PostProcessingModule.__init__(self)
        return

    def run(self, data):
        print 'processing ', data['regime name']
        
        # vectorise skalar functions
        vSubt = np.vectorize(self.subt)
        vMul = np.vectorize(self.mul)
        vAdd = np.vectorize(self.add)
          
        #calculate datasets
        t = data['results']['simTime']
        yd = data['results']['trajectory_output.0']
        y = []
        for i in range(4):
            y.append(data['results']['model_output.'+str(i)]  )
            
        eps = vSubt(yd[0], y[0])

        u = data['results']['controller_output.0']
        
        # Parameter from Controller -> make modelling (estimate/meausre paramters)
        # and then neglect psi therm
        # you are interested in the error through the negligence 
        B = st.B
        G = st.G

        
        if data['modules']['controller']['type'] == 'FController':
            psi = vMul(np.dot(B, y[0]), np.power(y[3],2))
        elif data['modules']['controller']['type'] == 'GController':
            psi = vMul(vMul(np.dot(2*B, y[0]), y[3]), u)
        elif data['modules']['controller']['type'] == 'JController':
            psi = vAdd(vMul(np.dot(B,y[0]), np.power(y[3], 2)),\
                       np.dot(B*G, vSubt(y[2] - np.sin(y[2]))))
        else:
            raise Exception('psi is useless')
            psi = np.dot(0, t)

        # plots
        fig = Figure()
        #fig.tight_layout()
        #fig.subplots_adjust(left=0.1, right=1.3, top=1.3, bottom=0.1)
        fig.subplots_adjust(wspace=0.3, hspace=0.25)

        axes1 = fig.add_subplot(2, 2, 1)
        #axes1.set_title(r'\textbf{output error = yd - x0}')
        axes1.plot(t, eps, c='k')
        axes1.set_xlim(left=0, right=t[-1])
        axes1.set_xlabel(r'$t /s$')
        axes1.set_ylabel(r'$e$')
        
        axes2 = fig.add_subplot(2, 2, 2)
        #axes2.set_title(r'\textbf{Beam Angle}')
        axes2.plot(t, y[2], c='k')
        axes2.set_xlim(left=0, right=t[-1])
        axes2.set_xlabel(r'$t /s$')
        axes2.set_ylabel(r'$\theta$')
        
        axes3 = fig.add_subplot(2, 2, 3)
        #axes3.set_title(r'\textbf{neglected nonlinearity}')
        axes3.plot(t, psi, c='k')
        axes3.set_xlim(left=0, right=t[-1])
        axes3.set_xlabel(r'$t /s$')
        axes3.set_ylabel(r'$\psi$')
        
        axes4 = fig.add_subplot(2, 2, 4)
        #axes4.set_title(r'\textbf{Beam Torque}')
        axes4.plot(t, u, c='k')
        axes4.set_xlim(left=0, right=t[-1])
        axes4.set_xlabel(r'$t /s$')
        axes4.set_ylabel(r'$\tau$')
        
        canvas = FigureCanvas(fig)
        fig.savefig('testc.svg')
        
        return canvas

