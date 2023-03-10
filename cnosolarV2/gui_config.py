###############################
#      CONFIGURATION GUI      #
###############################

import json
import pytz
import pvlib
import requests
import traitlets
import numpy as np
import pandas as pd
import cnosolarV2 as cno
import ipywidgets as widgets
from tkinter import Tk, filedialog
from IPython.display import display

def execute():
    '''
    Graphical user interface for the configuration of the PV plant 
    and download of the corresponding .JSON file.
    
    The JSON file data structure contains the following parameters:
    1. latitude : float
           Latitude based on the location of the PV plant in decimal degrees notation.
        
    2. longitude : float
           Longitude based on the location of the PV plant in decimal degrees notation.
        
    3. tz : string
           Time zone of the location of the PV plant.
    
    4. altitude : float
           Altitude based on the location of the PV plant from sea level in [m].
    
    5. surface_type : string
           Surface type to determine the albedo. Optional if albedo is not known.
    
    6. surface_albedo : float
           Albedo.
    
    7. inverters_database : string
           Repository of inverters arranged by PVlib. Valid options are: 
           CECInverter, SandiaInverter or ADRInverter. If the configuration 
           method is PVsyst or Manual, the value is set to null.
    
    8. inverter_name : string
           Inverter name following the according repository format. If the 
           configuration method is PVsyst or Manual, the value is set to null.
    
    9. inverter : dict
            Set of technical parameters that defines the inverter.
            
            - Main Parameters of SNL PVlib Method
              1. Paco: Inverter rated AC power in W.
              2. Pdco: Inverter rated DC power in W.
              3. Vdco: DC voltage at which the nominal AC Power is reached 
                       with the DC Power input in V.
              4. Pso: DC power required to start the inversion process in W.
              5. C0: Parameter that defines the curvature of the relationship 
                     between AC Power and DC Power in STC condition in 1/W.
              6. C1: Empirical coefficient that allows the Nominal DC Power 
                     to vary linearly with the DC Voltage in 1/V.
              7. C2: Empirical coefficient that allows the DC Starting Power 
                     to vary linearly with the DC Voltage in 1/V.
              8. C3: Empirical coefficient that allows $C_0$ to vary linearly 
                     with the DC Voltage by 1/V.
              9. Pnt: AC power consumed by the inverter during the night in W.
            
            - Main Parameters of NREL PVWatts Method
              1. Pdco: Inverter rated DC power in W.
              2. eta_inv_nom: Dimensionless nominal efficiency of the inverter.
        
    10. ac_model : string
            Inverter modeling method to be used. Valid options are: sandia or
            pvwatts.
    
    11. modules_database : string
            Repository of PV modules arranged by PVlib. Valid options are: pvmodule 
            or cecmodul). If the configuration method is PVFree, PVsyst or Manual, 
            the value is set to null.
    
    12. module_name : string
            PV module name following the according repository format. If the configuration 
            method is PVFree, PVsyst or Manual, the value is set to null.
    
    13. module : dict
            Set of technical parameters that defines the PV module.
            
            - Main Parameters
              1. T_NOCT: Nominal operating cell temperature in ??C.
              2. Technology: PV cell technology. Valid options are: monosi, multisi, 
                             cigs, cdte, asi or None.
              3. N_s: Number of PV cells in series.
              4. I_sc_ref: Short circuit current under STC conditions in A.
              5. V_oc_ref: Open circuit voltage under STC conditions in V.
              6. I_mp_ref: Current at the point of maximum power under STC 
                           conditions in A.
              7. V_mp_ref: Voltage at the point of maximum power under STC 
                           conditions in V.
              8. alpha_sc: Temperature coefficient of the short-circuit 
                           current in A/??C.
              9. beta_oc: Open circuit voltage temperature coefficient in V/??C.
              10. gamma_r: Temperature coefficient of the power at the maximum 
                           point in %/??C.
              11. STC: Nominal power of the PV module under STC conditions in W.
              
    14. bifacial : bool
            Defines if the PV module is bifacial or not.
    
    15. bifaciality : float
            Fraction between the efficiency of the front and rear side 
            of the PV module, measured under STC conditions.
    
    16. row_height : float
            Height of the rows of photovoltaic panels measured at their 
            center in units of meters.
    
    17. row_width : float
            Width of the rows of photovoltaic panels in the 2D plane considered 
            in units of meters (e.g., 1P, 2P, 4L).
    
    18. with_tracker : bool
            Parameter that checks if the mounting of the array is either on 
            fixed-tilt racking or horizontal single axis tracker.
    
    19. surface_azimuth : float or list
            Azimuth angle of the module surface. North = 0, East = 90, 
            South = 180 and West = 270. If with_tracker = true, the value is 
            set to null.
    
    20. surface_tilt : float or list
            Surface tilt angles. The tilt angle is defined as degrees from 
            horizontal (e.g. surface facing up = 0, surface facing 
            horizon = 90). If with_tracker = true, the value is set to null.
        
    21. axis_tilt : float
            Tilt of the axis of rotation with respect to horizontal (e.g. a value of 
            0?? indicates that the support axis of the photovoltaic panels is horizontal)
            in [degrees]. If with_tracker = false, the value is set to null.
    
    22. axis_azimuth : float
            Perpendicular angle to the axis of rotation by right hand rule (e.g., a 
            value of 180?? indicates a rotation from east to west) in [degrees]. If 
            with_tracker = false, the value is set to null.
    
    23. max_angle : float
            Maximum angle of rotation of the tracker from its horizontal position (e.g., a 
            value of 90?? allows the tracker to rotate to and from a vertical position where 
            the panel faces the horizon) in [degrees]. If with_tracker = false, the value 
            is set to null.
    
    24. module_type : string
            PV module mounting and front and back insolation sheets materials. Valid options
            are: open_rack_glass_glass, close_mount_glass_glass or insulated_back_glass_polymer.
    
    25. racking_model : string, optional
            Racking of the PV modules. Valid strings are 'open_rack', 'close_mount', 
            and 'insulated_back'. Used to identify a parameter set for the SAPM cell 
            temperature model.
        
    26. num_arrays : int
            Set of arrangements connected to an inverter. Each subarray consists of modules 
            in series per string, strings in parallel, and the number of inputs to the inverter 
            (either full inputs per inverter or number of MPPT inputs).
    
    27. modules_per_string : int or list
            Number of modules in series per string in each subarray.
    
    28. strings_per_inverter : int or list
            Number of strings in parallel in each subarray.
    
    29. num_inverter : int
            Number of inverters with electrical configuration exactly equal to the one defined. 
            It allows to scale theproduction calculations.
    
    30. loss : float
        Overall DC system losses in percentage.
        Default = 14.6
    
    31. kpc : float
        Transmission losses up to the common coupling point of the inverters.
        Default = 0.0
        
    32. kt : float
        Losses associated with the transformation (voltage rise).
        Default = 0.0
        
    33. kin : float
        Interconnection losses, transmission up to the trade border.
        Default = 0.0
    
    34. name : string
        Suffix to the name of the configuration file (system_config_suffix). 
        Default = 'system_config'
    '''
    
    ###############################
    #      DOCUMENTATION TAB      #
    ###############################
    GUI_LAYOUT = widgets.Layout(display='flex',
                                flex_flow='row',
                                justify_content='space-between')
    
    STYLE = {'description_width': 'initial'}
    
    doc_location = widgets.HTML('''
                                <h5>Informaci??n Geogr??fica</h5>
                                <ul>
                                  <li> <b>Latitud:</b> Utilice la notaci??n de grados decimales; se requieren 5 decimales.</li>
                                  <li> <b>Longitud:</b> Utilice la notaci??n de grados decimales; se requieren 5 decimales.</li>
                                  <li> <b>Altitud:</b> Altitud desde el nivel del mar en metros (m.s.n.m).</li>
                                  <li> <b>Huso Horario:</b> Con referencia a UTC. Por defecto: Am??rica/Bogot?? (UTC-5).</li>
                                  <li> <b>Superficie:</b> Tipo de superficie para determinar el albedo. <span style='color:red'>Opcional si desconoce el albedo</span>.</li>
                                  <li> <b>Albedo:</b> Utilice un valor porcentual en escala entre 0 y 1.</li>
                                </ul>''', layout=widgets.Layout(height='auto'))
    
    doc_inverter = widgets.HTMLMath('''
                                    <h5>M??todo de Configuraci??n: Repositorio</h5>
                                    <ul>
                                      <li> <b>Repositorio:</b> Repositorio de inversores dispuestos por PVlib (CEC).</li>
                                      <li> <b>Fabricantes:</b> Lista de fabricantes del repositorio seleccionado.</li>
                                      <li> <b>Inversores:</b> Lista de equipos disponibles en el repositorio seg??n el fabricante seleccionado.</li>
                                    </ul>

                                    <h5>M??todo de Configuraci??n: PVsyst</h5>
                                    <ul>
                                      <li> Seleccione el archivo del inversor generado por PVsyst (extensi??n .OND) y d?? clic en 'Cargar OND'.</li>
                                    </ul>

                                    <h5>M??todo de Configuraci??n: Manual</h5>
                                    <ul>
                                      <li> <b>Sandia</b> 
                                       <ul class='square'>
                                         <li> <b>$P_{AC}$ Nominal:</b> Potencia AC nominal del inversor en W.</li>
                                         <li> <b>$P_{DC}$ Nominal:</b> Potencia DC nominal del inversor en W.</li>
                                         <li> <b>$V_{DC}$ Nominal:</b> Voltaje DC al que se alcanza la Potencia AC nominal con la entrada de Potencia DC en V.</li>
                                         <li> <b>$P_{DC}$ de Arraque:</b> Potencia DC necesaria para iniciar el proceso de inversi??n en W.</li>
                                         <li> <b>$C_0$:</b> Par??metro que define la curvatura de la relaci??n entre la Potencia AC y Potencia DC en condici??n STC en 1/W.</li>
                                         <li> <b>$C_1$:</b> Coeficiente emp??rico que permite que la Potencia DC Nominal var??e linealmente con el Voltaje DC en 1/V.</li>
                                         <li> <b>$C_2$:</b> Coeficiente emp??rico que permite que la Potencia DC de Arranque var??e linealmente con el Voltaje DC en 1/V.</li>
                                         <li> <b>$C_3$:</b> Coeficiente emp??rico que permite que $C_0$ var??e linealmente con el Voltaje DC en 1/V.</li>
                                         <li> <b>$P_{AC}$ Consumo Nocturno:</b> Potencia AC consumida por el inversor durante la noche en W.</li>
                                         <li> <b>Referencia Inversor:</b> Referencia completa del inversor incluyendo el fabricante y modelo.</li>
                                       </ul>
                                      </li>

                                      <li> <b>PVWatts</b> 
                                       <ul class='square'>
                                         <li> <b>$P_{AC}$ Nominal:</b> Potencia AC nominal del inversor en W.</li>
                                         <li> <b>Eficiencia Nominal:</b> Eficiencia nominal del inversor en magnitud adimensional.</li>
                                         <li> <b>Referencia Inversor:</b> Referencia completa del inversor incluyendo el fabricante y modelo.</li>
                                       </ul>
                                      </li>
                                    </ul>
                                ''', layout=widgets.Layout(height='auto'))

    doc_module = widgets.HTMLMath('''
                                  <h5>M??todo de Configuraci??n: Repositorio</h5>
                                  <ul>
                                    <li> <b>Repositorio:</b> Repositorio de m??dulos fotovoltaicos dispuestos por PVlib (CEC).</li>
                                    <li> <b>PVFree</b> 
                                     <ul class='square'>
                                       <li> <b>Base de Datos:</b> Repositorio de m??dulos fotovoltaicos dispuestos en PVFree.</li>
                                       <li> <b>ID:</b> N??mero de identificaci??n del m??dulo indicado en PVFree.</li>
                                     </ul>
                                    </li>

                                    <li> <b>CEC y Sandia</b> 
                                     <ul class='square'>
                                       <li> <b>Fabricantes:</b> Lista de fabricantes del repositorio seleccionado.</li>
                                       <li> <b>M??dulos:</b> Lista de equipos disponibles en el repositorio seg??n el fabricante seleccionado.</li>
                                     </ul>
                                    </li>
                                  </ul>

                                  <h5>M??todo de Configuraci??n: PVsyst</h5>
                                  <ul>
                                    <li> Seleccione el archivo del m??dulo fotovoltaico generado por PVsyst (extensi??n .PAN) y d?? clic en 'Cargar PAN'.</li>
                                  </ul>

                                  <h5>M??todo de Configuraci??n: Manual</h5>
                                  <ul>
                                    <li> <b>NOCT:</b> Temperatura nominal de funcionamiento (en condiciones NOCT) de la celda en ??C. </li>
                                    <li> <b>Tecnolog??a:</b> Tecnolog??a de la celda fotovoltaica. </li>
                                    <li> <b>N??mero Celdas:</b> N??mero de celdas fotovoltaicas en serie. </li>
                                    <li> <b>$I_{SC}$ en STC:</b> Corriente de corto circuito en condiciones STC en A. </li>
                                    <li> <b>$V_{OC}$ en STC:</b> Voltaje de circuito abierto en condiciones STC en V. </li>
                                    <li> <b>$I_{MP}$ en STC:</b> Corriente en el punto de m??xima potencia en condiciones STC en A. </li>
                                    <li> <b>$V_{MP}$ en STC:</b> Voltaje en el punto de m??xima potencia en condiciones STC en V.</b> </li>
                                    <li> <b>Coef. Temp. $I_{SC}$:</b> Coeficiente de temperatura de la corriente de cortocircuito en %/??C. </li>
                                    <li> <b>Coef. Temp. $V_{OC}$:</b> Coeficiente de temperatura de voltaje de circuito abierto en %/??C. </li>
                                    <li> <b>Coef. Temp. $P_{MP}$:</b> Coeficiente de temperatura de la potencia en el punto m??ximo en %/??C. </li>
                                    <li> <b>$P_{Nominal}$ en STC:</b> Potencia nominal del m??dulo fotovoltaico en condiciones STC en W.</li>
                                    <li> <b>Referencia M??dulo:</b> Referencia completa del m??dulo solar fotovoltaico incluyendo el fabricante y modelo.</li>
                                  </ul>
                                  
                                  <h5>Par??metros Bifacialidad</h5>
                                  <ul>
                                    <li> <b>Panel Bifacial:</b> Si el panel fotovoltaico es bifacial o no. </li>
                                    <li> <b>Bifacialidad:</b> Relaci??n entre la eficiencia del lado frontal y posterior del m??dulo fotovoltaico, medida en condiciones STC. Utilice un valor porcentual en escala entre 0 y 1. </li>
                                    <li> <b>Alto Fila Paneles:</b> Altura de las filas de paneles fotovoltaicos medida en su centro en unidades de metros. </li>
                                    <li> <b>Ancho Fila Paneles:</b> Ancho de las filas de paneles fotovoltaicos en el plano 2D considerado en unidades de metros (e.g., 1P, 2P, 4L). </li>
                                  </ul>
                                ''', layout=widgets.Layout(height='auto'))

    doc_sysdesign = widgets.HTMLMath('''
                                     <h5>Subarrays</h5>
                                     <ul>
                                       <li> <b>Cantidad Subarrays:</b> Conjunto de arreglos conectados a un inversor. Cada subarray se compone de m??dulos en serie por string, strings en paralelo y el n??mero de entradas al inversor (ya sea entradas completas por inversor o n??mero de entradas MPPT).</li>
                                     </ul>

                                     <h5>Configuraci??n El??ctrica</h5>
                                     <ul>
                                       <li> <b>M??dulos por String:</b> Cantidad de m??dulos en serie por string en cada subarray. Para m??ltiples subarrays, separe los valores con una coma de manera ordenada.</li>
                                       <li> <b>Strings por Inversor:</b> Cantidad de strings en paralelo en cada subarray. Para m??ltiples subarrays, separe los valores con una coma de manera ordenada.</li>
                                       <li> <b>N??mero de Inversores:</b> Cantidad de inversores con configuraci??n el??ctrica exactamente igual a la definida. Permite escalar los c??lculos de producci??n.</li>
                                     </ul>

                                      <h5>Seguidores y Orientaci??n</h5>
                                      <ul>
                                        <li> <b>Sin Seguidor</b> 
                                         <ul class='square'>
                                           <li> <b>Azimutal:</b> ??ngulo azimutal en grados decimales <span style='color:blue'>(Norte = 0, Sur = 180, Este = 90, Oeste = 270) </span>. Para m??ltiples subarrays, separe los valores con una coma de manera ordenada (tambi??n aplica si el azimutal es el mismo).</li>
                                           <li> <b>Elevaci??n:</b> ??ngulos de inclinaci??n desde la horizontal en grados decimales. Para m??ltiples subarrays, separe los valores con una coma de manera ordenada (tambi??n aplica si la elevaci??n es la misma).</li>
                                           <li> <b>Racking:</b> Tipo de ventilaci??n del montaje. Se utiliza para identificar un conjunto de par??metros para el modelo de temperatura de la celda.</li>
                                         </ul>
                                        </li>

                                        <li> <b>Seguidor 1-Eje</b><br>
                                        El ??ngulo de rotaci??n se determina en un sistema de coordenadas diestro. El seguidor define el eje-y positivo, el eje-x positivo est?? a 90?? en sentido horario desde el eje-y y es paralelo a la superficie, y el eje-z positivo es normal a ambos ejes (-x y -y), y est?? orientado hacia el cielo. El ??ngulo de rotaci??n es una rotaci??n hacia la derecha alrededor del eje-y en el sistema de coordenadas e indica la posici??n del seguidor en relaci??n con la horizontal. Por ejemplo, si Azimutal Eje es 180?? (orientado al sur) y Elevaci??n Eje es 0??, entonces un ??ngulo del seguidor de 0?? es horizontal, de 30?? es una rotaci??n hacia el oeste, y -90?? es una rotaci??n al plano vertical hacia el este.

                                         <ul class='square'>
                                           <li> <b>Elevaci??n Eje:</b> Elevaci??n del eje de rotaci??n con respecto a la horizontal en grados decimales (e.g., un valor de 0?? indica que el eje de soporte de los paneles fotovoltaicos est?? horizontal). Para m??ltiples subarrays, separe los valores con una coma de manera ordenada (tambi??n aplica si la elevaci??n del eje es la misma).</li>
                                           <li> <b>Azimutal Eje:</b> ??ngulo perpendicular por regla de la mano derecha al eje de rotaci??n en grados decimales (e.g., un valor de 180?? ???i.e., direcci??n sur??? indica una rotaci??n de este a oeste). Para m??ltiples subarrays, separe los valores con una coma de manera ordenada (tambi??n aplica si el azimutal del eje es el mismo).</li>
                                           <li> <b>??ngulo M??ximo:</b> ??ngulo de rotaci??n m??ximo del seguidor desde su posici??n horizontal en grados decimales (e.g., un valor de 90?? permite que el seguidor gire desde y hasta una posici??n vertical en la que el panel mira hacia el horizonte). Para m??ltiples subarrays, separe los valores con una coma de manera ordenada (tambi??n aplica si el ??ngulo m??ximo es el mismo).</li>
                                           <li> <b>Racking:</b> Tipo de ventilaci??n del montaje. Se utiliza para identificar un conjunto de par??metros para el modelo de temperatura de la celda.</li>
                                         </ul>
                                        </li>
                                      </ul>

                                     <h5>Par??metros Globales</h5>
                                     <ul>
                                       <li> <b>P??rdidas DC:</b> Porcentaje de p??rdidas globales DC del sistema. Por defecto: 14.6%.</li>
                                       <li> <b>$k_{pc}$:</b> P??rdidas de transmisi??n hasta el punto com??n de acople de los inversores. Por defecto: 0%.</li>
                                       <li> <b>$k_{t}$:</b> P??rdidas asociadas a la transformaci??n (elevaci??n de tensi??n). Por defecto: 0%.</li>
                                       <li> <b>$k_{in}$:</b> P??rdidas de interconexi??n, transmisi??n hasta la frontera comercial. Por defecto: 0%.</li>
                                       <li> <b>Nombre Planta:</b> Sufijo al nombre del archivo de configuraci??n (system_config_<i>sufijo</i>). Por defecto: system_config.</li>
                                     </ul>
                                 
                                     <h5>Archivo Configuraci??n</h5>
                                     <ul>
                                       <li> <b>Generar Configuraci??n:</b> D?? clic en este bot??n para que el algoritmo genere internamente el archivo de configuraci??n con los par??metros previamente asignados. El ??cono y la descripci??n del bot??n cambiar??n para notificar la ejecuci??n de la configuraci??n.</li>
                                       <li> <b>Descargar Configuraci??n:</b> D?? clic en este bot??n para descargar el archivo de configuraci??n genererado con el bot??n 'Generar Configuraci??n' (una vez este haya notificado su ejecuci??n). Se descargar?? un archivo .JSON que se alojar??n en la carpeta <i>cno_solar/configurations/<span style='color:blue'>system_config.json</span></i>. El ??cono y la descripci??n del bot??n cambiar??n para notificar la descarga del archivo.</li>
                                     </ul>
                                     ''', layout=widgets.Layout(height='auto'))

    ac_documentation = widgets.Accordion(children=[doc_location, doc_inverter, doc_module, doc_sysdesign])
    ac_documentation.set_title(0, 'Tab Ubicaci??n')
    ac_documentation.set_title(1, 'Tab Inversor')
    ac_documentation.set_title(2, 'Tab M??dulo')
    ac_documentation.set_title(3, 'Tab Dise??o Planta')

    tab_doc = widgets.Box([widgets.HTML('<h4>Documentaci??n</h4>', layout=widgets.Layout(height='auto')), 
                           widgets.VBox([widgets.Box([ac_documentation], layout=GUI_LAYOUT)])], 
                           layout=widgets.Layout(display='flex',
                                                 flex_flow='column',
                                                 border='solid 0px',
                                                 align_items='stretch',
                                                 width='100%'))
    
    ###############################
    #        LOCATION TAB         #
    ###############################
    surfaces = {'': None,
                'Urbano': 'urban',
                'C??sped': 'grass',
                'C??sped Fresco': 'fresh grass',
                'Tierra': 'soil',
                'Arena': 'sand',
                'Nieve': 'snow',
                'Nieve Fresca': 'fresh snow',
                'Asfalto': 'asphalt',
                'Hormig??n': 'concrete',
                'Aluminio': 'aluminum',
                'Cobre': 'copper',
                'Acero': 'fresh steel',
                'Acero Sucio': 'dirty steel',
                'Mar': 'sea'}

    w_latitude = widgets.FloatText(value=0,
                                   step=0.00001,
                                   description='',
                                   disabled=False,
                                   style=STYLE)

    w_longitude = widgets.FloatText(value=0,
                                    step=0.00001,
                                    description='',
                                    disabled=False,
                                    style=STYLE)

    w_altitude = widgets.FloatText(value=0,
                                   step=1,
                                   description='',
                                   disabled=False,
                                   style=STYLE)

    w_timezone = widgets.Dropdown(options=pytz.all_timezones,
                                  value='America/Bogota',
                                  description='',
                                  style=STYLE)

    w_surface = widgets.Dropdown(options=surfaces,
                                 value=None,
                                 description='',
                                 style=STYLE)

    w_albedo = widgets.BoundedFloatText(value=None,
                                        step=0.01,
                                        min=0,
                                        max=1,
                                        description='',
                                        disabled=False,
                                        style=STYLE)
    
    def handle_surface_change(change):
        if change.new != None:
            w_albedo.value = pvlib.irradiance.SURFACE_ALBEDOS[change.new]

    w_surface.observe(handle_surface_change, names='value')

    widget_location = [widgets.Box([widgets.HTML('<h4>Informaci??n Geogr??fica</h4>', layout=widgets.Layout(height='auto'))]),
                       widgets.Box([widgets.Label('Latitud'), w_latitude], layout=GUI_LAYOUT),
                       widgets.Box([widgets.Label('Longitud'), w_longitude], layout=GUI_LAYOUT),
                       widgets.Box([widgets.Label('Altitud [m.s.n.m]'), w_altitude], layout=GUI_LAYOUT),
                       widgets.Box([widgets.Label('Huso Horario'), w_timezone], layout=GUI_LAYOUT),
                       widgets.Box([widgets.Label('Superficie'), w_surface], layout=GUI_LAYOUT),
                       widgets.Box([widgets.Label('Albedo [ad.]'), w_albedo], layout=GUI_LAYOUT)]

    tab_location = widgets.Box(widget_location, layout=widgets.Layout(display='flex',
                                                                      flex_flow='column',
                                                                      border='solid 0px',
                                                                      align_items='stretch',
                                                                      width='60%'))

    ###############################
    #        INVERTER TAB         #
    ###############################
    inv_repo = {'CEC': 'CECInverter'}

    inverter_btn = widgets.ToggleButtons(value=None,
                                         options=['Repositorio', 'PVsyst', 'Manual'],
                                         description='',
                                         disabled=False,
                                         button_style='',
                                         tooltips=['Base de datos de PVlib', 
                                                   'Importar desde archivo de PVsyst', 
                                                   'Configuraci??n manual'])

    # REPOSITORY
    # Repository Widgets
    inverter_vbox = widgets.VBox([inverter_btn])

    dropdown_invrepo = widgets.Dropdown(options=inv_repo,
                                        value=None,
                                        description='',
                                        style=STYLE)

    dropdown_manufac = widgets.Dropdown(options='',
                                        value=None,
                                        disabled=True,
                                        description='',
                                        style=STYLE)

    w_dropinvrepo = widgets.VBox([widgets.Box([widgets.Label('Repositorio'), dropdown_invrepo], layout=GUI_LAYOUT)])
    w_dropmanufac = widgets.VBox([widgets.Box([widgets.Label('Fabricantes'), dropdown_manufac], layout=GUI_LAYOUT)])
    
    # PVsyst Widgets
    class SelectFilesButton(widgets.Button):
        '''A file widget that leverages tkinter.filedialog'''
        def __init__(self):
            super(SelectFilesButton, self).__init__()

            # Add the selected_files trait
            self.add_traits(files=traitlets.traitlets.Any()) # List()

            # Create the button
            self.description = 'Seleccionar'
            self.icon = 'square-o'
            self.layout = widgets.Layout(width='35%', height='auto')

            # Set on click behavior
            self.on_click(self.select_files)

        @staticmethod
        def select_files(b):
            '''Generate instance of tkinter.filedialog '''
            # Create Tk root
            root = Tk()

            # Hide the main window
            root.withdraw()

            # Raise the root to the top of all windows
            root.call('wm', 'attributes', '.', '-topmost', True)

            # List of selected fileswill be set to b.value
            b.files = filedialog.askopenfilename(filetypes=(('OND Files', '.OND'),), 
                                                 multiple=False,
                                                 title='Select OND File')

            b.description = 'Seleccionado'
            b.icon = 'check-square-o'

    upload_btn = SelectFilesButton()

    btn = widgets.Button(value=False,
                         description='Cargar OND',
                         disabled=False,
                         button_style='',
                         tooltip='Cargar los archivos .OND',
                         icon='circle',
                         layout=widgets.Layout(width='35%', height='auto'))

    btn.add_traits(files=traitlets.traitlets.Dict())

    w_upload = widgets.VBox([widgets.Box([widgets.HTML('<h5> </h5>', layout=widgets.Layout(height='auto'))]), 
                             widgets.Box([widgets.Label('Archivo Inversor (.OND)'), upload_btn, btn], layout=GUI_LAYOUT)])

    # Manual Widgets
    dropdown_manual = widgets.Dropdown(options=['', 'Sandia', 'PVWatts'],
                                       value=None,
                                       description='')
    
    w_dropmanual = widgets.VBox([widgets.Box([widgets.Label('Formato de Configuraci??n'), dropdown_manual], layout=GUI_LAYOUT)])

    def handle_toggle(change):
        if change['new'] == 'Repositorio':
            inverter_vbox.children = [inverter_btn, w_dropinvrepo, w_dropmanufac]

        elif change['new'] == 'PVsyst':
            inverter_vbox.children = [inverter_btn, w_upload]

        elif change['new'] == 'Manual':
            inverter_vbox.children = [inverter_btn, w_dropmanual]

    def handle_dropdown_manuf(change):
        inverters = pvlib.pvsystem.retrieve_sam(change['new'])

        manufacturers = []
        manufacturers.append('')
        for string in inverters.transpose().index:
            manufacturers.append(string[:string.index('__')])

        manufacturers.append(change['new'])
        dropdown_manufac.options = list(pd.unique(manufacturers))
        dropdown_manufac.disabled = False

        inverter_vbox.children = [inverter_btn, w_dropinvrepo, w_dropmanufac]

    def handle_dropdown_repo(change): 
        inverters = pvlib.pvsystem.retrieve_sam(dropdown_manufac.options[-1])

        matching = [s for s in inverters.transpose().index if change['new'] in s]
        inv_options = list(inverters[matching].transpose().index)
        inv_options.insert(0, '')

        inv_drop = widgets.Dropdown(options=inv_options,
                                    value=None,
                                    description='',
                                    style=STYLE)
        
        w_dropinv = widgets.VBox([widgets.Box([widgets.Label('Inversores'), inv_drop], layout=GUI_LAYOUT)])

        inverter_vbox.children = [inverter_btn, w_dropinvrepo, w_dropmanufac, w_dropinv]

    # PVSYST
    def on_button_clicked(obj):
        btn.description = 'OND Cargado'
        btn.icon = 'check-circle'
        with output:
            output.clear_output()
            ond = cno.pvsyst.ond_to_inverter_param(path=upload_btn.files)
            
            eta_inv_nom = float(ond['pvGInverter']['TConverter']['EfficEuro'])/100
            
            if eta_inv_nom == 0:
                eta_inv_nom = float(ond['pvGInverter']['TConverter']['EfficEuroV'].split(',')[1])/100
            
            try:
                pdco = float(ond['pvGInverter']['TConverter']['PNomDC'])*1000
            except:
                paco = float(ond['pvGInverter']['TConverter']['PNomConv'])*1000
                pdco = paco / eta_inv_nom
                
            try:
                pso = float(ond['pvGInverter']['TConverter']['Pthresh'])*1000
            except:
                if pdco >= 1e06:
                    pso = pdco * 0.005
                else:
                    pso = pdco * 0.01 # https://www.pvsyst.com/help/inverters_general.htm
            
            inverter = {'Vac': float(ond['pvGInverter']['TConverter']['VOutConv']), # Voltaje de red (Par??metros principales)
                        'Pso': np.round(pso, 2), # Pthresh
                        'Paco': float(ond['pvGInverter']['TConverter']['PNomConv'])*1000, # Potencia CA m??xima
                        'Pdco': np.round(pdco, 2), # Potencia FV nominal
                        #'pdc0': float(ond['pvGInverter']['TConverter']['PNomDC'])*1000,
                        'Vdco': float(ond['pvGInverter']['TConverter']['VNomEff'].split(',')[1]), # Voltaje medio
                        'Pnt': float(ond['pvGInverter']['Night_Loss']), # Night Loss
                        #'Vdcmax': float(ond['pvGInverter']['TConverter']['VAbsMax']), # Alto voltaje (Ventrada en curva efic)
                        #'Idcmax': float(ond['pvGInverter']['TConverter']['IMaxDC']),
                        #'Mppt_low': float(ond['pvGInverter']['TConverter']['VMppMin']), # Vm??n@Pnom
                        #'Mppt_high': float(ond['pvGInverter']['TConverter']['VMPPMax']), # Alto Voltaje
                        'eta_inv_nom': np.round(eta_inv_nom, 4),
                        'eta_inv_ref': 0.9637,
                        'Name': '{} {}'.format(ond['pvGInverter']['pvCommercial']['Manufacturer'], ond['pvGInverter']['pvCommercial']['Model'])}
            
            btn.files = {'inv': inverter, 'ond': ond}

    # MANUAL
    def handle_dropdown_manual(change):    
        if change['new'] == 'Sandia':
            w_Paco = widgets.FloatText(value=None, description='', style=STYLE)
            w_Pdco = widgets.FloatText(value=None, description='', style=STYLE)
            w_Vdco = widgets.FloatText(value=None, description='', style=STYLE)
            w_Pso = widgets.FloatText(value=None, description='', style=STYLE)
            w_C0 = widgets.FloatText(value=None, description='', style=STYLE)
            w_C1 = widgets.FloatText(value=None, description='', style=STYLE)
            w_C2 = widgets.FloatText(value=None, description='', style=STYLE)
            w_C3 = widgets.FloatText(value=None, description='', style=STYLE)
            w_Pnt = widgets.FloatText(value=None, description='', style=STYLE)
            w_Name = w_name = widgets.Text(value='', placeholder='Referencia Completa', description='', style=STYLE)

            inv_conf = widgets.VBox([widgets.Box([widgets.HTML('<h5>Configuraci??n Sandia</h5>', layout=widgets.Layout(height='auto'))]),
                                     widgets.Box([widgets.Label('$P_{AC}$ Nominal  [W]'), w_Paco], layout=GUI_LAYOUT),
                                     widgets.Box([widgets.Label('$P_{DC}$ Nominal [W]'), w_Pdco], layout=GUI_LAYOUT),
                                     widgets.Box([widgets.Label('$V_{DC}$ Nominal [V]'), w_Vdco], layout=GUI_LAYOUT),
                                     widgets.Box([widgets.Label('$P_{DC}$ de Arraque [W]'), w_Pso], layout=GUI_LAYOUT),
                                     widgets.Box([widgets.Label('$C_0$ [1/W]'), w_C0], layout=GUI_LAYOUT),
                                     widgets.Box([widgets.Label('$C_1$ [1/V]'), w_C1], layout=GUI_LAYOUT),
                                     widgets.Box([widgets.Label('$C_2$ [1/V]'), w_C2], layout=GUI_LAYOUT),
                                     widgets.Box([widgets.Label('$C_3$ [1/V]'), w_C3], layout=GUI_LAYOUT),
                                     widgets.Box([widgets.Label('$P_{AC}$ Consumo Nocturno [W]'), w_Pnt], layout=GUI_LAYOUT),
                                     widgets.Box([widgets.Label('Referencia Inversor'), w_Name], layout=GUI_LAYOUT)])

            inverter_vbox.children = [inverter_btn, w_dropmanual, inv_conf]

        else:
            w_pdc0 = widgets.FloatText(value=None, description='', style=STYLE)
            w_eta_inv_nom = widgets.BoundedFloatText(value=None, min=0, max=1, step=0.01, description='', style=STYLE)
            w_Name = w_name = widgets.Text(value='', placeholder='Referencia Completa', description='', style=STYLE)

            inv_conf = widgets.VBox([widgets.Box([widgets.HTML('<h5>Configuraci??n PVWatts</h5>', layout=widgets.Layout(height='auto'))]),
                                     widgets.Box([widgets.Label('$P_{AC}$ Nominal [W]'), w_pdc0], layout=GUI_LAYOUT),
                                     widgets.Box([widgets.Label('Eficiencia Nominal [ad.]'), w_eta_inv_nom], layout=GUI_LAYOUT),
                                     widgets.Box([widgets.Label('Referencia Inversor'), w_Name], layout=GUI_LAYOUT)])

            inverter_vbox.children = [inverter_btn, w_dropmanual, inv_conf]

    # OBSERVE
    inverter_btn.observe(handle_toggle, 'value')
    dropdown_invrepo.observe(handle_dropdown_manuf, 'value')
    dropdown_manufac.observe(handle_dropdown_repo, 'value')
    btn.on_click(on_button_clicked)
    dropdown_manual.observe(handle_dropdown_manual, 'value')

    # TAB
    tab_inverter = widgets.Box([widgets.HTML("<h4>M??todo de Configuraci??n</h4>", layout=widgets.Layout(height='auto')), 
                                inverter_vbox], 
                                layout=widgets.Layout(display='flex',
                                                      flex_flow='column',
                                                      border='solid 0px',
                                                      align_items='stretch',
                                                      width='60%'))

    ###############################
    #         MODULE TAB          #
    ###############################
    mod_repo = {'': None,
                'PVFree': 'PVFree',
                'CEC': 'CECMod'}

    module_btn = widgets.ToggleButtons(value=None,
                                       options=['Repositorio', 'PVsyst', 'Manual'],
                                       description='',
                                       disabled=False,
                                       button_style='',
                                       tooltips=['Base de datos de PVlib', 
                                                 'Importar desde archivo de PVsyst', 
                                                 'Configuraci??n manual'])

    # REPOSITORY
    # Repository Widgets
    module_vbox = widgets.VBox([module_btn])

    dropdown_modrepo = widgets.Dropdown(options=mod_repo,
                                        value=None,
                                        description='',
                                        style=STYLE)

    dropdown_modmanu = widgets.Dropdown(options='',
                                        value=None,
                                        disabled=True,
                                        description='',
                                        style=STYLE)

    w_dropmodrepo = widgets.VBox([widgets.Box([widgets.Label('Repositorio'), dropdown_modrepo], layout=GUI_LAYOUT)])
    w_dropmodmanu = widgets.VBox([widgets.Box([widgets.Label('Fabricantes'), dropdown_modmanu], layout=GUI_LAYOUT)])
    
    # PVsyst Widgets
    class SelectPANButton(widgets.Button):
        '''A file widget that leverages tkinter.filedialog'''
        def __init__(self):
            super(SelectPANButton, self).__init__()

            # Add the selected_files trait
            self.add_traits(files=traitlets.traitlets.Any()) # List()

            # Create the button
            self.description = 'Seleccionar'
            self.icon = 'square-o'
            self.layout = widgets.Layout(width='35%', height='auto')

            # Set on click behavior
            self.on_click(self.select_files)

        @staticmethod
        def select_files(b):
            '''Generate instance of tkinter.filedialog '''
            # Create Tk root
            root = Tk()

            # Hide the main window
            root.withdraw()

            # Raise the root to the top of all windows
            root.call('wm', 'attributes', '.', '-topmost', True)

            # List of selected fileswill be set to b.value
            b.files = filedialog.askopenfilename(filetypes=(('PAN Files', '.PAN'),), 
                                                 multiple=False,
                                                 title='Select PAN File')

            b.description = 'Seleccionado'
            b.icon = 'check-square-o'

    upload_modbtn = SelectPANButton()

    modbtn = widgets.Button(value=False,
                            description='Cargar PAN',
                            disabled=False,
                            button_style='',
                            tooltip='Cargar los archivos .PAN',
                            icon='circle',
                            layout=widgets.Layout(width='35%', height='auto'))

    modbtn.add_traits(files=traitlets.traitlets.Dict())
    modbtn_output = widgets.Output()

    w_modupload = widgets.VBox([widgets.Box([widgets.HTML('<h5> </h5>', layout=widgets.Layout(height='auto'))]), 
                                widgets.Box([widgets.Label('Archivo M??dulo (.PAN)'), upload_modbtn, modbtn], layout=GUI_LAYOUT)])

    # Manual Widgets
    dropdown_modmanual = widgets.Dropdown(options=['', 'Sandia', 'PVWatts'],
                                          value=None,
                                          description='M??todo',
                                          style=STYLE)

    # BIFACIAL PARAMETERS
    dropdown_bifacial = widgets.Dropdown(options=[('S??', True), ('No', False)],
                                          value=False,
                                          description='',
                                          style=STYLE)

    w_dropbrifacial = widgets.VBox([widgets.Box([widgets.Label('Panel Bifacial'), dropdown_bifacial], layout=GUI_LAYOUT)])
    bifacial_vbox = widgets.VBox([w_dropbrifacial])
    
    def handle_modtoggle(change):
        if change['new'] == 'Repositorio':
            module_vbox.children = [module_btn, w_dropmodrepo]

        elif change['new'] == 'PVsyst':
            module_vbox.children = [module_btn, w_modupload]

        elif change['new'] == 'Manual':  
            w_T_NOCT = widgets.FloatText(value=None, step=0.1, description='', style=STYLE)
            w_Type = widgets.Dropdown(options=[('Mono-Si', 'monosi'), ('Multi-Si', 'multisi'), ('Poli-Si', 'polysi'), ('CIS', 'cis'), ('CIGS', 'cigs'), ('CdTe', 'cdte'), ('Amorfo', 'amorphous')], value='monosi', description='', style=STYLE)
            w_N_s = widgets.FloatText(value=None, description='', style=STYLE)
            w_I_sc_ref = widgets.FloatText(value=None, step=0.1, description='', style=STYLE)
            w_V_oc_ref = widgets.FloatText(value=None, step=0.1, description='', style=STYLE)
            w_I_mp_ref = widgets.FloatText(value=None, step=0.1, description='', style=STYLE)
            w_V_mp_ref = widgets.FloatText(value=None, step=0.1, description='', style=STYLE)
            w_alpha_sc = widgets.FloatText(value=None, step=0.1, description='', style=STYLE)
            w_beta_oc = widgets.FloatText(value=None, step=0.1, description='', style=STYLE)
            w_gamma_r = widgets.FloatText(value=None, step=0.1, description='', style=STYLE)
            w_STC = widgets.FloatText(value=None, step=0.1, description='', style=STYLE)
            w_Name = w_name = widgets.Text(value='', placeholder='Referencia Completa', description='', style=STYLE)

            mod_conf = widgets.VBox([widgets.Box([widgets.HTML('<h5>Configuraci??n M??dulo</h5>', layout=widgets.Layout(height='auto'))]),
                                     widgets.Box([widgets.Label('NOCT [??C]'), w_T_NOCT], layout=GUI_LAYOUT),
                                     widgets.Box([widgets.Label('Tecnolog??a'), w_Type], layout=GUI_LAYOUT),
                                     widgets.Box([widgets.Label('N??mero Celdas'), w_N_s], layout=GUI_LAYOUT),
                                     widgets.Box([widgets.Label('$I_{SC}$ en STC [A]'), w_I_sc_ref], layout=GUI_LAYOUT),
                                     widgets.Box([widgets.Label('$V_{OC}$ en STC [V]'), w_V_oc_ref], layout=GUI_LAYOUT),
                                     widgets.Box([widgets.Label('$I_{MP}$ en STC [A]'), w_I_mp_ref], layout=GUI_LAYOUT),
                                     widgets.Box([widgets.Label('$V_{MP}$ en STC [A]'), w_V_mp_ref], layout=GUI_LAYOUT),
                                     widgets.Box([widgets.Label('Coef. Temp. $I_{SC}$ [%/??C]'), w_alpha_sc], layout=GUI_LAYOUT),
                                     widgets.Box([widgets.Label('Coef. Temp. $V_{OC}$ [%/??C]'), w_beta_oc], layout=GUI_LAYOUT),
                                     widgets.Box([widgets.Label('Coef. Temp. $P_{MP}$ [%/??C]'), w_gamma_r], layout=GUI_LAYOUT),
                                     widgets.Box([widgets.Label('$P_{Nominal}$ en STC [W]'), w_STC], layout=GUI_LAYOUT),
                                     widgets.Box([widgets.Label('Referencia M??dulo'), w_Name], layout=GUI_LAYOUT)])

            module_vbox.children = [module_btn, mod_conf]

    def handle_dropdown_modmanuf(change):
        if change['new'] == 'PVFree':
            dropdown_pvfree = widgets.Dropdown(options=['', 'cecmodule', 'pvmodule'],
                                           value=None,
                                           description='',
                                           style=STYLE)

            pvfree_id = widgets.VBox([widgets.IntText(value=None, description='', style=STYLE)])     

            w_droppvfree = widgets.VBox([widgets.Box([widgets.Label('Base de Datos'), dropdown_pvfree], layout=GUI_LAYOUT)])
            w_modconf = widgets.VBox([widgets.Box([widgets.Label('ID'), pvfree_id], layout=GUI_LAYOUT)])
            
            module_vbox.children = [module_btn, w_dropmodrepo, w_droppvfree, w_modconf]

        else:    
            modules = pvlib.pvsystem.retrieve_sam(change['new'])

            manufacturers = []
            manufacturers.append('')
            for string in modules.transpose().index:
                manufacturers.append(string[:string.index('_')])

            manufacturers.append(change['new'])

            dropdown_modmanu.options = list(pd.unique(manufacturers))
            dropdown_modmanu.disabled = False

            module_vbox.children = [module_btn, w_dropmodrepo, w_dropmodmanu]

    def handle_dropdown_modrepo(change):
        modules = pvlib.pvsystem.retrieve_sam(dropdown_modmanu.options[-1])

        matching = [s for s in modules.transpose().index if change['new'] in s]
        mod_options = list(modules[matching].transpose().index)
        mod_options.insert(0, '')

        mod_drop = widgets.Dropdown(options=mod_options,
                                    value=None,
                                    description='',
                                    style=STYLE)

        w_dropmod = widgets.VBox([widgets.Box([widgets.Label('M??dulos'), mod_drop], layout=GUI_LAYOUT)])
        
        module_vbox.children = [module_btn, w_dropmodrepo, w_dropmodmanu, w_dropmod]

    # PVSYST
    def on_modbutton_clicked(obj):
        modbtn.description = 'PAN Cargado'
        modbtn.icon = 'check-circle'

        with modbtn_output:
            modbtn_output.clear_output()
            module = cno.pvsyst.pan_to_module_param(path=upload_modbtn.files)
            module['Adjust'] = 0
            module['Technology'] = module['Technol']
            module['T_NOCT'] = module['TRef'] + 20
            module['IAM'] = module['IAM'].tolist()
            modbtn.files = {'mod': module}
            
            if module['T_NOCT'] >= 50:
                module['T_NOCT'] = module['TRef']
    
    # BIFACIAL 
    def handle_dropdown_bifacial(change):
        if change['new'] == True:
            w_bifaciality = widgets.BoundedFloatText(value=None, min=0, max=1, step=0.1, description='', style=STYLE)
            w_rowheight = widgets.BoundedFloatText(value=None, min=0, max=1000, step=0.1, description='', style=STYLE)
            w_rowwidth = widgets.BoundedFloatText(value=None, min=0, max=1000, step=0.1, description='', style=STYLE)

            bif_conf = widgets.VBox([widgets.Box([widgets.Label('Bifacialidad [ad.]'), w_bifaciality], layout=GUI_LAYOUT),
                                     widgets.Box([widgets.Label('Alto Fila Paneles [m]'), w_rowheight], layout=GUI_LAYOUT),
                                     widgets.Box([widgets.Label('Ancho Fila Paneles [m]'), w_rowwidth], layout=GUI_LAYOUT)])

            bifacial_vbox.children = [w_dropbrifacial, bif_conf]

        else:
            bifacial_vbox.children = [w_dropbrifacial]
        
    # OBSERVE
    module_btn.observe(handle_modtoggle, 'value')
    dropdown_modrepo.observe(handle_dropdown_modmanuf, 'value')
    dropdown_modmanu.observe(handle_dropdown_modrepo, 'value')
    modbtn.on_click(on_modbutton_clicked)
    dropdown_bifacial.observe(handle_dropdown_bifacial, 'value')

    # TAB
    tab_module = widgets.Box([widgets.HTML('<h4>M??todo de Configuraci??n</h4>', layout=widgets.Layout(height='auto')), 
                              module_vbox,
                              widgets.HTML('<h4>Par??metros Bifacialidad</h4>', layout=widgets.Layout(height='auto')),
                              bifacial_vbox], 
                              layout=widgets.Layout(display='flex',
                                                    flex_flow='column',
                                                    border='solid 0px',
                                                    align_items='stretch',
                                                    width='60%'))

    ###############################
    #  SYSTEM CONFIGURATION TAB   #
    ###############################

    # SUBARRAYS
    w_subarrays = widgets.BoundedIntText(value=1, min=1, max=1000, description='', style=STYLE)

    conf_subarrays = widgets.VBox([widgets.Box([widgets.HTML('<h4>Subarrays</h4>', layout=widgets.Layout(height='auto'))]),
                                   widgets.Box([widgets.Label('Cantidad Subarrays'), w_subarrays], layout=GUI_LAYOUT)])

    # ELECTRICAL CONFIGURATION
    w_mps = widgets.Text(value='0', description='', style=STYLE)
    w_spi = widgets.Text(value='0', description='', style=STYLE)
    w_numinv = widgets.IntText(value=1, description='', style=STYLE)

    def handle_mppt(change):
        if change['new'] == 1:
            v_mppt = '1'
            v_others = '0'
        else:
            v_mppt = '1, ' * change['new']
            v_mppt = v_mppt[:-2]
            v_others = '0, ' * change['new']
            v_others = v_others[:-2]

        w_mps.value = v_others
        w_spi.value = v_others

    w_subarrays.observe(handle_mppt, 'value')

    conf_elec = widgets.VBox([widgets.Box([widgets.HTML('<h4>Configuraci??n El??ctrica</h4>', layout=widgets.Layout(height='auto'))]),
                              widgets.Box([widgets.Label('M??dulos por String'), w_mps], layout=GUI_LAYOUT),
                              widgets.Box([widgets.Label('Strings por Inversor'), w_spi], layout=GUI_LAYOUT),
                              widgets.Box([widgets.Label('N??mero Inversores'), w_numinv], layout=GUI_LAYOUT)])

    # TRACKING AND ORIENTATION CONFIGURATION
    header_TO = widgets.HTML("<h4>Seguidores y Orientaci??n</h4>", layout=widgets.Layout(height='auto'))

    tracker_btn = widgets.ToggleButtons(value=None,
                                        options=['Sin Seguidor', 'Seguidor 1-Eje'],
                                        description='',
                                        disabled=False,
                                        button_style='',
                                        tooltips=['Montaje con estructura fija', 
                                                  'Montaje con single-axis tracker'])

    sysconfig_vbox = widgets.VBox([header_TO, tracker_btn])

    def handle_toggle(change):
        if change['new'] == 'Sin Seguidor':
            w_Azimuth = widgets.Text(value=None, description='', style=STYLE)
            w_Tilt = widgets.Text(value=None, description='', style=STYLE)
            w_Racking = widgets.Dropdown(options=[('Open Rack', 'open_rack'), ('Close Mount', 'close_mount'), ('Insulated Back', 'insulated_back')], value='open_rack', description='', style=STYLE) # https://sam.nrel.gov/forum/forum-general/1040-mount-types.html#3148

            if w_subarrays.value == 1:
                v_angles = '0.0'
            else:
                v_angles = '0.0, ' * w_subarrays.value
                v_angles = v_angles[:-2]

            w_Azimuth.value = v_angles
            w_Tilt.value = v_angles
            
            no_tracker = widgets.VBox([widgets.Box([widgets.Label('Elevaci??n [??]'), w_Tilt], layout=GUI_LAYOUT),
                                       widgets.Box([widgets.Label('Azimutal [??]'), w_Azimuth], layout=GUI_LAYOUT),
                                       widgets.Box([widgets.Label('Racking'), w_Racking], layout=GUI_LAYOUT)])

            sysconfig_vbox.children = [header_TO, tracker_btn, no_tracker]

        elif change['new'] == 'Seguidor 1-Eje':
            w_AxisTilt = widgets.Text(value=None, description='', style=STYLE)
            w_AxisAzimuth = widgets.Text(value=None, description='', style=STYLE)
            w_MaxAngle = widgets.Text(value=None, description='', style=STYLE)
            w_Racking = widgets.Dropdown(options=[('Open Rack', 'open_rack'), ('Close Mount', 'close_mount'), ('Insulated Back', 'insulated_back')], value='open_rack', description='', style=STYLE) # https://sam.nrel.gov/forum/forum-general/1040-mount-types.html#3148

            if w_subarrays.value == 1:
                v_angles = '0.0'
            else:
                v_angles = '0.0, ' * w_subarrays.value
                v_angles = v_angles[:-2]

            w_AxisTilt.value = v_angles
            w_AxisAzimuth.value = v_angles
            w_MaxAngle.value = v_angles
            
            single_tracker = widgets.VBox([widgets.Box([widgets.Label('Elevaci??n Eje [??]'), w_AxisTilt], layout=GUI_LAYOUT),
                                           widgets.Box([widgets.Label('Azimutal Eje [??]'), w_AxisAzimuth], layout=GUI_LAYOUT),
                                           widgets.Box([widgets.Label('??ngulo M??ximo [??]'), w_MaxAngle], layout=GUI_LAYOUT),
                                           widgets.Box([widgets.Label('Racking'), w_Racking], layout=GUI_LAYOUT)])

            sysconfig_vbox.children = [header_TO, tracker_btn, single_tracker]

    tracker_btn.observe(handle_toggle, 'value')

    # GLOBAL PARAMETERS
    w_loss = widgets.BoundedFloatText(value=14.6, min=0, max=100, step=0.1, description='', style=STYLE)
    w_name = widgets.Text(value='', placeholder='Sufijo extensi??n .JSON', description='', style=STYLE)
    kpc_loss = widgets.BoundedFloatText(value=0.0, min=0, max=100, step=0.1, description='', style=STYLE)
    kt_loss = widgets.BoundedFloatText(value=0.0, min=0, max=100, step=0.1, description='', style=STYLE)
    kin_loss = widgets.BoundedFloatText(value=0.0, min=0, max=100, step=0.1, description='', style=STYLE)
    
    conf_globalparams = widgets.VBox([widgets.Box([widgets.HTML('<h4>Par??metros Globales</h4>', layout=widgets.Layout(height='auto'))]),
                                      widgets.Box([widgets.Label('P??rdidas DC [%]'), w_loss], layout=GUI_LAYOUT),
                                      widgets.Box([widgets.HTML('<h4> </h4>', layout=widgets.Layout(height='auto'))]),
                                      widgets.Box([widgets.Label('$k_{pc}$ [%]'), kpc_loss], layout=GUI_LAYOUT),
                                      widgets.Box([widgets.Label('$k_{t}$ [%]'), kt_loss], layout=GUI_LAYOUT),
                                      widgets.Box([widgets.Label('$k_{in}$ [%]'), kin_loss], layout=GUI_LAYOUT),
                                      widgets.Box([widgets.HTML('<h4> </h4>', layout=widgets.Layout(height='auto'))]),
                                      widgets.Box([widgets.Label('Nombre Planta'), w_name], layout=GUI_LAYOUT)])

    # CONFIGURATION FILE
    # Config Button
    genconfig_btn = widgets.Button(value=False,
                                   description='Generar Configuraci??n',
                                   disabled=False,
                                   button_style='',
                                   tooltip='Generar Configuraci??n del Sistema',
                                   icon='gear',
                                   layout=widgets.Layout(width='60%', height='auto'))

    genconfig_output = widgets.Output()

    # Download Button
    download_btn = widgets.Button(value=False,
                                  description='Descargar Configuraci??n',
                                  disabled=True,
                                  button_style='',
                                  tooltip='Descarga JSON de la Configuraci??n del Sistema',
                                  icon='download',
                                  layout=widgets.Layout(width='60%', height='auto'))
    
    output = widgets.Output()
    
    def on_genconfig_clicked(obj):    
        with genconfig_output:
            genconfig_output.clear_output()

            inverter_status = check_inverter()
            module_status = check_module()
            mount_status = check_mount(num_arrays=w_subarrays.value)
            econfig_status = check_econfig(num_arrays=w_subarrays.value)

            system_configuration = sys_config(inverter_status, module_status, mount_status, econfig_status)

            # JSON verification
            checking_tag = cno.verification.check_json(json_to_check=system_configuration)

            if checking_tag == 'fail':
                genconfig_btn.description = 'Revisar Configuraci??n'
                genconfig_btn.icon = 'warning'
            
            elif checking_tag == 'success':
                genconfig_btn.description = 'Configuraci??n Generada'
                genconfig_btn.icon = 'check'

                download_btn.disabled = False
                
    genconfig_btn.on_click(on_genconfig_clicked)

    def on_button_clicked(obj):
        with output:
            output.clear_output()

            inverter_status = check_inverter()
            module_status = check_module()
            mount_status = check_mount(num_arrays=w_subarrays.value)
            econfig_status = check_econfig(num_arrays=w_subarrays.value)
            system_configuration = sys_config(inverter_status, module_status, mount_status, econfig_status)

            if w_name.value != '':
                json_file = f'./configurations/system_config_{w_name.value}.json'
            else:
                json_file = './configurations/system_config.json'

            with open(json_file, 'w') as f:
                json.dump(system_configuration, f, indent=2)

            download_btn.description = 'Configuraci??n Descargada'
            download_btn.icon = 'check'

    download_btn.on_click(on_button_clicked)
    
    conf_json = widgets.VBox([widgets.Box([widgets.HTML('<h4>Archivo Configuraci??n</h4>', layout=widgets.Layout(height='auto'))]),
                              widgets.HBox([genconfig_btn, download_btn]),
                              widgets.HBox([genconfig_output, output])])
    
    # TAB
    tab_sysconfig = widgets.Box([conf_subarrays,
                                 conf_elec,
                                 sysconfig_vbox,
                                 conf_globalparams,
                                 conf_json], 
                                 layout=widgets.Layout(display='flex',
                                                       flex_flow='column',
                                                       border='solid 0px',
                                                       align_items='stretch',
                                                       width='60%'))

    ###############################
    #            GUI              #
    ###############################

    # Str to List
    def str_to_list(string):
        l = []
        l.append('[')
        l.append(string) # l.append(string.value)
        l.append(']')
        return json.loads(''.join(l))

    # Status Check
    ## Inverter
    def check_inverter():
        if inverter_btn.value == 'Repositorio':
            inverters_database = dropdown_invrepo.value
            inverter_name = inverter_vbox.children[3].children[0].children[1].value
            inverter = dict(pvlib.pvsystem.retrieve_sam(inverters_database)[inverter_name])
            
            ac_model = 'sandia'
                 
            inverter = {'Paco': inverter['Paco'],
                        'Pdco': inverter['Pdco'],
                        'Vdco': inverter['Vdco'],
                        'Pso': inverter['Pso'],
                        'C0': inverter['C0'],
                        'C1': inverter['C1'],
                        'C2': inverter['C2'],
                        'C3': inverter['C3'],
                        'Pnt': inverter['Pnt']}

        if inverter_btn.value == 'PVsyst':
            inverter = btn.files['inv']

            inverters_database = None
            inverter_name = inverter['Name'] 
            
            # Sandia
            try:
                # Curve inputs
                n = 6

                # Voltaje level (Vmin, Vnom and Vmax)
                dc_voltage_level = ['Vmin']*n
                dc_voltage_level.extend(v for v in ['Vnom']*n)
                dc_voltage_level.extend(v for v in ['Vmax']*n)

                # Voltaje values (Vmin, Vnom and Vmax)
                volts = btn.files['ond']['pvGInverter']['TConverter']['VNomEff'].split(',')

                dc_voltage = [float(volts[0])]*n
                dc_voltage.extend(v for v in [float(volts[1])]*n)
                dc_voltage.extend(v for v in [float(volts[2])]*n)

                # Power values
                dc_power = []
                ac_power = []

                for i in range(1, 4):
                    profile = f'ProfilPIOV{i}'
                    for j in range(2, 8):
                        aux = list(map(float, btn.files['ond']['pvGInverter']['TConverter'][profile][f'Point_{j}'].split(',')))
                        dc_power.append(aux[0])
                        ac_power.append(aux[1])

                # Fit Sandia                
                data = pd.DataFrame({'dc_power': dc_power, # W
                                     'ac_power': ac_power, # W
                                     'dc_voltage': dc_voltage, # V
                                     'dc_voltage_level': dc_voltage_level})

                params = pvlib.inverter.fit_sandia(ac_power=data['ac_power'], # W 
                                                   dc_power=data['dc_power'], # W 
                                                   dc_voltage=data['dc_voltage'], # V 
                                                   dc_voltage_level=data['dc_voltage_level'], 
                                                   p_ac_0=inverter['Paco'], # W 
                                                   p_nt=inverter['Pnt']) # W

                # Inverter
                ac_model = 'sandia'

                inverter = {'Paco': inverter['Paco'],
                            'Pdco': inverter['Pdco'],
                            'Vdco': inverter['Vdco'],
                            'Pso': inverter['Pso'],
                            'C0': float('{:0.6e}'.format(params['C0'])),
                            'C1': float('{:0.6e}'.format(params['C1'])),
                            'C2': np.round(params['C2'], 6),
                            'C3': np.round(params['C3'], 6),
                            'Pnt': inverter['Pnt']}

            # PVWatts
            except:
                ac_model = 'pvwatts'

                inverter = {'Pdco': inverter['Pdco'],
                            'eta_inv_nom': inverter['eta_inv_nom']}

        if inverter_btn.value == 'Manual':
            if dropdown_manual.value == 'Sandia':
                ac_model = 'sandia'
                    
                inverter = {'Paco': inverter_vbox.children[2].children[1].children[1].value,
                            'Pdco': inverter_vbox.children[2].children[2].children[1].value,
                            'Vdco': inverter_vbox.children[2].children[3].children[1].value,
                            'Pso': inverter_vbox.children[2].children[4].children[1].value,
                            'C0': inverter_vbox.children[2].children[5].children[1].value,
                            'C1': inverter_vbox.children[2].children[6].children[1].value,
                            'C2': inverter_vbox.children[2].children[7].children[1].value,
                            'C3': inverter_vbox.children[2].children[8].children[1].value,
                            'Pnt': inverter_vbox.children[2].children[9].children[1].value}
                
                inverter_name = inverter_vbox.children[2].children[10].children[1].value
                
                if inverter_name == '':
                    inverter_name = None

            elif dropdown_manual.value == 'PVWatts':
                ac_model = 'pvwatts'
                
                paco = inverter_vbox.children[2].children[1].children[1].value
                eta_inv_nom = inverter_vbox.children[2].children[2].children[1].value
                
                pdco = np.round(paco/eta_inv_nom, 2)
                
                inverter = {'Pdco': pdco,
                            'eta_inv_nom': eta_inv_nom}
                
                inverter_name = inverter_vbox.children[2].children[3].children[1].value

                if inverter_name == '':
                    inverter_name = None
                
            else:
                inverter_name = None
                
            inverters_database = None

        return [inverters_database, inverter_name, inverter, ac_model]

    ## Module
    def check_module():
        if module_btn.value == 'Repositorio':
            if dropdown_modrepo.value != 'PVFree':
                modules_database = dropdown_modrepo.value
                modules_name = module_vbox.children[3].children[0].children[1].value
                module = dict(pvlib.pvsystem.retrieve_sam(modules_database)[modules_name])

                if modules_database == 'CECMod':
                    module = {'T_NOCT': module['T_NOCT'],
                              'Technology': module['Technology'],
                              'N_s': module['N_s'],
                              'I_sc_ref': module['I_sc_ref'],
                              'V_oc_ref': module['V_oc_ref'],
                              'I_mp_ref': module['I_mp_ref'],
                              'V_mp_ref': module['V_mp_ref'],
                              'alpha_sc': np.round(module['alpha_sc']*100/module['I_sc_ref'], 6), # %/??C (?? 100 * Isc -> A/??C)
                              'beta_oc': np.round(module['beta_oc']*100/module['V_oc_ref'], 6), # %/??C (?? 100 * Voc -> V/??C)
                              'gamma_r': module['gamma_r'], # %/??C
                              'STC': module['STC']}
                
                # https://www.osti.gov/servlets/purl/919131 (pp.16-17)
                elif modules_database == 'SandiaMod': 
                    module = {'T_NOCT': 45,
                              'Technology': module['Material'],
                              'N_s': module['Cells_in_Series'],
                              'I_sc_ref': module['Isco'],
                              'V_oc_ref': module['Voco'],
                              'I_mp_ref': module['Impo'],
                              'V_mp_ref': module['Vmpo'],
                              'alpha_sc': np.round(module['Aisc']*100, 6), # %/??C (?? 100 * Isc -> A/??C)
                              'beta_oc': np.round(module['Bvoco']*100/module['Voco'], 6), # %/??C (?? 100 * Voc -> V/??C)
                              'gamma_r': 0,
                              'STC': np.round(module['Impo']*module['Vmpo'], 2)}
                
            else:
                modules_database = dropdown_modrepo.value
                module = dict(requests.get(f'https://pvfree.herokuapp.com/api/v1/{module_vbox.children[2].children[0].children[1].value}/{module_vbox.children[3].children[0].children[1].children[0].value}/').json())
                modules_name = module['Name']        
            
                if module_vbox.children[2].children[0].children[1].value == 'cecmodule':
                    module = {'T_NOCT': module['T_NOCT'],
                              'Technology': module['Technology'],
                              'N_s': module['N_s'],
                              'I_sc_ref': module['I_sc_ref'],
                              'V_oc_ref': module['V_oc_ref'],
                              'I_mp_ref': module['I_mp_ref'],
                              'V_mp_ref': module['V_mp_ref'],
                              'alpha_sc': module['alpha_sc'],
                              'beta_oc': module['beta_oc'],
                              'gamma_r': module['gamma_r'],
                              'STC': module['STC']}
                
                # https://www.osti.gov/servlets/purl/919131 (pp.16-17)
                elif module_vbox.children[2].children[0].children[1].value == 'pvmodule':
                    module = {'T_NOCT': 45,
                              'Technology': module['Material'],
                              'N_s': module['Cells_in_Series'],
                              'I_sc_ref': module['Isco'],
                              'V_oc_ref': module['Voco'],
                              'I_mp_ref': module['Impo'],
                              'V_mp_ref': module['Vmpo'],
                              'alpha_sc': np.round(module['Aisc']*100, 6), # %/??C (?? 100 * Isc -> A/??C)
                              'beta_oc': np.round(module['Bvoco']*100/module['Voco'], 6), # %/??C (?? 100 * Voc -> V/??C)
                              'gamma_r': 0,
                              'STC': np.round(module['Impo']*module['Vmpo'], 2)}
                
        if module_btn.value == 'PVsyst':
            module = modbtn.files['mod']

            module['a_ref'] = module['Gamma'] * module['NCelS'] * (1.38e-23 * (273.15 + 25) / 1.6e-19)

            modules_database = None
            modules_name = '{} {}'.format(module['manufacturer'], module['module_name'])   
            
            module = {'T_NOCT': module['TRef']+20,
                      'Technology': module['Technol'],
                      'N_s': module['NCelS'],
                      'I_sc_ref': module['Isc'],
                      'V_oc_ref': module['Voc'],
                      'I_mp_ref': module['Imp'],
                      'V_mp_ref': module['Vmp'],
                      'alpha_sc': np.round(module['mIsc_percent'], 6), # %/??C (?? 100 * Isc -> A/??C)
                      'beta_oc': np.round(module['mVoc_percent'], 6), # %/??C (?? 100 * Voc -> V/??C)
                      'gamma_r': module['mPmpp'], # %/??C
                      'STC': module['Pmpp']}
                      
            if module['T_NOCT'] >= 50:
                module['T_NOCT'] = module['TRef']

        if module_btn.value == 'Manual':
            module = {'T_NOCT': module_vbox.children[1].children[1].children[1].value,
                      'Technology': module_vbox.children[1].children[2].children[1].value,
                      'N_s': module_vbox.children[1].children[3].children[1].value,
                      'I_sc_ref': module_vbox.children[1].children[4].children[1].value,
                      'V_oc_ref': module_vbox.children[1].children[5].children[1].value,
                      'I_mp_ref': module_vbox.children[1].children[6].children[1].value,
                      'V_mp_ref': module_vbox.children[1].children[7].children[1].value,
                      'alpha_sc': module_vbox.children[1].children[8].children[1].value,
                      'beta_oc': module_vbox.children[1].children[9].children[1].value,
                      'gamma_r': module_vbox.children[1].children[10].children[1].value,
                      'STC': module_vbox.children[1].children[11].children[1].value}

            modules_database = None
            modules_name = module_vbox.children[1].children[12].children[1].value
        
            if modules_name == '':
                modules_name = None
        
        t = module['Technology']
        if t in ['Mono-c-Si', 'monoSi', 'monosi', 'c-Si', 'xsi', 'mtSiMono']:
            module_tec = 'monosi'
        elif t in ['Multi-c-Si', 'multiSi',  'multisi', 'mc-Si', 'EFG mc-Si', 'polySi',  'polysi', 'mtSiPoly']:
            module_tec = 'multisi'
        elif t in ['CIS',  'cis', 'CIGS', 'cigs']:
            module_tec = 'cigs'
        elif t in ['CdTe', 'cdte', 'Thin Film',  'GaAs']:
            module_tec = 'cdte'
        elif t in ['amorphous', 'asi', 'a-Si / mono-Si', '2-a-Si',  '3-a-Si',  'Si-Film', 'HIT-Si']:
            module_tec = 'amorphous'
        else:
            module_tec = None
            
        module['Technology'] = module_tec
        
        if bifacial_vbox.children[0].children[0].children[1].value == False:
            bifacial = False
            bifaciality = None
            row_height = None
            row_width = None
        else:
            bifacial = True
            bifaciality = bifacial_vbox.children[1].children[0].children[1].value
            row_height = bifacial_vbox.children[1].children[1].children[1].value
            row_width = bifacial_vbox.children[1].children[2].children[1].value
        
        return [modules_database, modules_name, module, bifacial, bifaciality, row_height, row_width]

    ## Mount
    def check_mount(num_arrays):
        if tracker_btn.value == 'Sin Seguidor': 
            with_tracker = False
            axis_tilt = None
            axis_azimuth = None
            max_angle = None
            racking_model = sysconfig_vbox.children[2].children[2].children[1].value

            if num_arrays == 1:
                surface_tilt = [float(sysconfig_vbox.children[2].children[0].children[1].value)]
                surface_azimuth = [float(sysconfig_vbox.children[2].children[1].children[1].value)]

            elif num_arrays > 1:
                surface_tilt = list(map(float, str_to_list(sysconfig_vbox.children[2].children[0].children[1].value)))
                surface_azimuth = list(map(float, str_to_list(sysconfig_vbox.children[2].children[1].children[1].value)))
                
            if racking_model == 'open_rack':
                module_type = 'glass_glass'

            elif racking_model == 'close_mount':
                module_type = 'glass_glass'

            elif racking_model == 'insulated_back':
                module_type = 'glass_polymer'

        elif tracker_btn.value == 'Seguidor 1-Eje':
            with_tracker = True
            surface_azimuth = None
            surface_tilt = None
            racking_model = sysconfig_vbox.children[2].children[3].children[1].value

            if num_arrays == 1:
                axis_tilt = [float(sysconfig_vbox.children[2].children[0].children[1].value)]
                axis_azimuth = [float(sysconfig_vbox.children[2].children[1].children[1].value)]
                max_angle = [float(sysconfig_vbox.children[2].children[2].children[1].value)]

            elif num_arrays > 1:
                axis_tilt = list(map(float, str_to_list(sysconfig_vbox.children[2].children[0].children[1].value)))
                axis_azimuth = list(map(float, str_to_list(sysconfig_vbox.children[2].children[1].children[1].value)))
                max_angle = list(map(float, str_to_list(sysconfig_vbox.children[2].children[2].children[1].value)))  

            if racking_model == 'open_rack':
                module_type = 'glass_glass'

            elif racking_model == 'close_mount':
                module_type = 'glass_glass'

            elif racking_model == 'insulated_back':
                module_type = 'glass_polymer'

        return [with_tracker, surface_azimuth, surface_tilt, axis_tilt, axis_azimuth, max_angle, module_type, racking_model]

    ## Electric Configuration
    def check_econfig(num_arrays):
        num_inverters = int(w_numinv.value)
        if num_arrays == 1:
            modules_per_string = [int(w_mps.value)] #Modules Per String
            strings_per_inverter = [int(w_spi.value)] #Strings Per Inverter

        elif num_arrays > 1:
            modules_per_string = list(map(int, str_to_list(w_mps.value))) #Modules Per String
            strings_per_inverter = list(map(int, str_to_list(w_spi.value))) #Strings Per Inverter

        return [modules_per_string, strings_per_inverter, num_inverters]

    ## System Configuration
    def sys_config(inverter_status, module_status, mount_status, econfig_status):
        system_configuration = {# Geographic Info
                                'latitude': w_latitude.value,
                                'longitude': w_longitude.value,
                                'tz': w_timezone.value,
                                'altitude': w_altitude.value,
                                #'surface_type': w_surface.value,
                                'surface_albedo': w_albedo.value,

                                # Inverter
                                #'inverters_database': inverter_status[0],
                                'inverter_name': inverter_status[1],
                                'ac_model': inverter_status[3],
                                'inverter': dict(inverter_status[2]),

                                # PV Module
                                #'modules_database': module_status[0],
                                'module_name': module_status[1],
                                'module': dict(module_status[2]),
                                'bifacial': module_status[3],
                                'bifaciality': module_status[4],
                                'row_height': module_status[5],
                                'row_width': module_status[6],
            
                                # Subarrays
                                'num_arrays': w_subarrays.value,
            
                                # Electric Configuration
                                'modules_per_string': econfig_status[0],
                                'strings_per_inverter': econfig_status[1],
                                'num_inverter': econfig_status[2],
            
                                # Mount
                                'with_tracker': mount_status[0],
                                'surface_tilt': mount_status[2],
                                'surface_azimuth': mount_status[1],
                                'axis_tilt': mount_status[3],
                                'axis_azimuth': mount_status[4],
                                'max_angle': mount_status[5],
                                'module_type': mount_status[6],
                                #'racking_model': mount_status[7],

                                # Global Parameters
                                'loss': w_loss.value,
                                'kpc': kpc_loss.value,
                                'kt': kt_loss.value,
                                'kin': kin_loss.value,
                                'name': w_name.value}

        return system_configuration

    # GUI - Dashboard
    item_layout = widgets.Layout(margin='0 0 25px 0')

    tab = widgets.Tab([tab_doc, tab_location, tab_inverter, tab_module, tab_sysconfig], 
                      layout=item_layout)
    
    tab.set_title(0, 'Documentaci??n')
    tab.set_title(1, 'Ubicaci??n')
    tab.set_title(2, 'Inversor')
    tab.set_title(3, 'M??dulo')
    tab.set_title(4, 'Dise??o Planta')

    dashboard = widgets.VBox([tab])
    display(dashboard)