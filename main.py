import wx
from pvlib import pvsystem
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas


global choices
choices=['Canadian Solar Inc  CS5P-220M', 'BYD  Huizhou  Battery BYD 220P6 30',
          'Anhui Rinengzhongtian Semiconductor Development QJM220 60','Custom']
global choice
choice=choices[0]

global alpha_sc
global a_ref
global I_o_ref
global I_L_ref
global Rs_ref
global Rsh_ref
alpha_sc=0.002705
a_ref=1.52658
I_o_ref=3.50757e-10
I_L_ref=8.13928
Rs_ref=0.303753
Rsh_ref=266.124

class parameters():
    
    """
        Parameters of photovoltaic panels
    """
    global alpha_sc
    global a_ref
    global I_o_ref
    global I_L_ref
    global Rs_ref
    global Rsh_ref

    Custom={
        'alpha_sc':alpha_sc,
        'a_ref':a_ref,
        'I_o_ref':I_o_ref,
        'I_L_ref':I_L_ref,
        'R_s':Rs_ref,
        'R_sh_ref':Rsh_ref

    }
    # access database
    CEC_modules=pvsystem.retrieve_sam('CECMod')
    
    # import pv modules from database
    Canadian_Solar_Inc__CS5P_220M = CEC_modules['Canadian_Solar_Inc__CS5P_220M']
    BYD__Huizhou__Battery_BYD_220P6_30=CEC_modules['BYD__Huizhou__Battery_BYD_220P6_30']
    Anhui_Rinengzhongtian_Semiconductor_Development_QJM220_60=CEC_modules['Anhui_Rinengzhongtian_Semiconductor_Development_QJM220_60']

    
class p2(wx.Panel):
    def __init__(self, parent):
        global choice
        wx.Panel.__init__(self,parent,-1,style=wx.SUNKEN_BORDER)
        
        self.temperatureNo=25
        self.irradianceNo=1000
        # sliders

        self.irradianceText=wx.StaticText(self,label='Irradience',pos=(10,500))
        self.irradiance=wx.Slider(parent=self,value=1000,minValue=10, maxValue=1000,style=wx.SL_HORIZONTAL|wx.SL_LABELS,size=(400,100),pos=(140,500))
        self.irradiance.Bind(wx.EVT_SLIDER,self.getIrradiance)
        self.temperatureText=wx.StaticText(self,label='Cell Temperature', pos=(10,550))
        self.temperature=wx.Slider(parent=self,value=25,minValue=-10, maxValue=60,style=wx.SL_HORIZONTAL|wx.SL_LABELS,size=(400,100), pos=(130,550))
        self.temperature.Bind(wx.EVT_SLIDER, self.getTemperature)

        
        self.figure=matplotlib.figure.Figure()
        self.param=choice.replace('-','_')
        self.param=self.param.replace(' ','_')
        
        print('p2'+self.param)
        self.draw(getattr(parameters, self.param))
        
        self.canvas=FigureCanvas(self,0,self.figure)

    def getIrradiance(self,e):
    #  function for irradiance slider
        global choice
        self.irradianceNo= e.GetEventObject().GetValue()
        self.param=choice.replace('-','_')
        self.param=self.param.replace(' ','_')
        print('i'+self.param)
        self.draw(getattr(parameters,self.param))
      

    def getTemperature(self,e):
        global choice
        self.temperatureNo = e.GetEventObject().GetValue()
        self.param=choice.replace('-','_')
        self.param=self.param.replace(' ','_')
        print('t'+self.param)
        self.draw(getattr(parameters,self.param))
       

    def draw(self,param):   
        """
            redraw the plot for every change in sliders
        """     
        IL, I0, Rs, Rsh, nNsVth = pvsystem.calcparams_desoto(
            self.irradianceNo,
            self.temperatureNo,
            alpha_sc=param['alpha_sc'],
            a_ref=param['a_ref'],
            I_L_ref=param['I_L_ref'],
            I_o_ref=param['I_o_ref'],
            R_sh_ref=param['R_sh_ref'],
            R_s=param['R_s'],
            EgRef=1.121,
            dEgdT=-0.0002677
        )

        curve_info = pvsystem.singlediode(
                photocurrent=IL,
                saturation_current=I0,
                resistance_series=Rs,
                resistance_shunt=Rsh,
                nNsVth=nNsVth,
                ivcurve_pnts=100,
                method='lambertw'
            )
        
        # Clear figure 
        self.figure.clear()
        
        #plot i_v
        self.axes=self.figure.add_subplot(2,1,1)
        self.axes.plot(curve_info['v'],curve_info['i'])

        self.axes.set_title(choice)
        self.axes.set_ylabel('Module current')

        #plot p_v
        self.axes=self.figure.add_subplot(2,1,2)
        self.axes.plot(curve_info['v'],curve_info['v']*curve_info['i'])
        #mark MPP coordinates
        self.axes.annotate(( float('{0:.3g}'.format(curve_info['v_mp'])), float('{0:.3g}'.format(curve_info['i_mp']))),
                            (curve_info['v_mp'], curve_info['p_mp']))
        self.axes.set_xlabel('Module voltage')
        self.axes.set_ylabel('Module power')
       
        self.canvas=FigureCanvas(self,-1, self.figure)


class main(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self,parent,title=title,size=(1050,650))

        # frame color
        self.colours()

        #configure splitter
        self.sp=wx.SplitterWindow(self)
        self.p1=wx.Panel(self.sp, style=wx.SUNKEN_BORDER)
        self.p2=p2(self.sp)
        self.sp.SplitVertically(self.p1,self.p2,400)
        
        # configure ComboBox
        pvPanel=wx.StaticText(self.p1,label='Alege panoul fotovoltaic',pos = (20,50))
       
        self.combo=wx.ComboBox(self.p1,-1, style= wx.CB_READONLY, choices=choices,pos = (20,80),value=choices[0])
        self.combo.Bind(wx.EVT_COMBOBOX, self.onCombo)

        # Labels
        self.alpha_scLabel=wx.StaticText(self.p1,label='alpha_sc',pos = (20,110))
        self.a_refLabel=wx.StaticText(self.p1,label='a_ref',pos = (20,140))
        self.I_Lref_Label=wx.StaticText(self.p1,label='I_L_ref',pos = (20,170))
        self.I_0_refLabel=wx.StaticText(self.p1,label='I_0_ref',pos = (20,200))
        self.Rsh_refLabel=wx.StaticText(self.p1,label='Rsh_ref',pos = (20,230))
        self.Rs_refLabel=wx.StaticText(self.p1,label='Rs_ref',pos = (20,260))


        # TextBoxes
        # create
        self.alpha_scText=wx.TextCtrl(self.p1,pos = (70,110))
        self.a_refText=wx.TextCtrl(self.p1,pos = (70,140))
        self.I_L_refText=wx.TextCtrl(self.p1,pos = (70,170))
        self.I_0_refText=wx.TextCtrl(self.p1,pos = (70,200))
        self.Rsh_refText=wx.TextCtrl(self.p1,pos = (70,230))
        self.Rs_refText=wx.TextCtrl(self.p1,pos = (70,260))

        # add event
        self.alpha_scText.Bind(wx.EVT_CHAR, self.checkNumeric)
        self.a_refText.Bind(wx.EVT_CHAR, self.checkNumeric)
        self.a_refText.Bind(wx.EVT_CHAR, self.checkNumeric)
        self.I_L_refText.Bind(wx.EVT_CHAR, self.checkNumeric)
        self.I_0_refText.Bind(wx.EVT_CHAR, self.checkNumeric)
        self.Rsh_refText.Bind(wx.EVT_CHAR, self.checkNumeric)
        self.Rs_refText.Bind(wx.EVT_CHAR, self.checkNumeric)

        
        # button
        #create
        self.calculate=wx.Button(self.p1,label='Calculeaza',pos=(50,300))
        self.updated=wx.Button(self.p1,label='Actualizeaza',pos=(50,120))

        #add event
        self.calculate.Bind(wx.EVT_BUTTON, self.getValues)
        self.updated.Bind(wx.EVT_BUTTON, self.update)

        self.hideCustom()

    def update(self,e):
        global choice
        
        print('u')
        param=choice.replace('-','_')
        param=param.replace(' ','_')
        # print(choice)
        self.p2.draw(getattr(parameters,param))
        

    def getValues(self,e):
        global alpha_sc
        global a_ref
        global I_o_ref
        global I_L_ref
        global Rs_ref
        global Rsh_ref
        global choice
        # parameters.Custom[alpha_sc]=self.alpha_scText.GetValue()
        alpha_sc=float(self.alpha_scText.GetValue())
        parameters.Custom['alpha_sc']=alpha_sc
        a_ref=float(self.a_refText.GetValue())
        parameters.Custom['a_ref']=a_ref
        I_o_ref=float(self.I_0_refText.GetValue())
        parameters.Custom['I_o_ref']=I_o_ref
        I_L_ref=float(self.I_L_refText.GetValue())
        parameters.Custom['I_L_ref']=I_L_ref
        Rs_ref=float(self.Rs_refText.GetValue())
        parameters.Custom['R_s']=Rs_ref
        Rsh_ref=float(self.Rsh_refText.GetValue())
        parameters.Custom['R_sh_ref']=Rsh_ref
        print(parameters.Custom)
        self.p2.draw(parameters.Custom)


    def checkNumeric(self, e):
        raw_value =  e.GetEventObject().GetValue().strip()
        keycode = e.GetKeyCode()
        if keycode < 255:
            # print('keycode:',keycode,'chr(keycode) ', chr(keycode))
            if chr(keycode).isdigit() or chr(keycode)=='.' and '.'  not in raw_value:
                # print('skip')
                e.Skip()
            else: 
                if chr(keycode)=='-':
                    wx.MessageBox("Must be positive", "Error" ,wx.OK | wx.ICON_INFORMATION) 
                else:
                    wx.MessageBox("Not numeric", "Error" ,wx.OK | wx.ICON_INFORMATION)  


    def hideCustom(self):
         # hide elements
        self.alpha_scLabel.Hide()
        self.a_refLabel.Hide()
        self.I_Lref_Label.Hide()
        self.I_0_refLabel.Hide()
        self.Rsh_refLabel.Hide()
        self.Rs_refLabel.Hide()

        # TextBoxes
        self.alpha_scText.Hide()
        self.a_refText.Hide()
        self.I_L_refText.Hide()
        self.I_0_refText.Hide()
        self.Rsh_refText.Hide()
        self.Rs_refText.Hide()
        
        # button
        self.calculate.Hide()   
        self.updated.Show()
        
   
    def colours(self):
        self.SetBackgroundColour(wx.Colour(191, 128, 255,255))
    

    def showCustom(self):
        self.alpha_scLabel.Show()
        self.a_refLabel.Show()
        self.I_Lref_Label.Show()
        self.I_0_refLabel.Show()
        self.Rsh_refLabel.Show()
        self.Rs_refLabel.Show()

        # TextBoxes
        self.alpha_scText.Show()
        self.a_refText.Show()
        self.I_L_refText.Show()
        self.I_0_refText.Show()
        self.Rsh_refText.Show()
        self.Rs_refText.Show()
        
        # button
        self.calculate.Show()
        self.updated.Hide()

        # clear TextBoxes
        self.alpha_scText.Clear()
        self.a_refText.Clear()
        self.I_L_refText.Clear()
        self.I_0_refText.Clear()
        self.Rsh_refText.Clear()
        self.Rs_refText.Clear()
    
    
    def onCombo(self,e):
        global choice
        global choices
        print("You selected"+self.combo.GetValue()+" from Combobox")
        choice=choices[choices.index(self.combo.GetValue())]
        print('c'+choice)
        if(choice=='Custom'):
            self.showCustom()
        else:
            self.hideCustom()

    
app=wx.App(redirect=False)
frame=main(None,"You can do it!!!")
frame.Show()

app.MainLoop()
