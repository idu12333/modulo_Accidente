# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AccidenteDockWidget
                                 A QGIS plugin
 Análisis de accidentes en Madrid
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2022-04-23
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Francisco Javier Holguera Illera
        email                : idu12333@usal.es
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import processing

from qgis.PyQt import QtGui, QtWidgets, uic

from qgis.PyQt.QtCore import pyqtSignal

from qgis.core import QgsProject, QgsVectorLayer,QgsField, QgsFeature,QgsGeometry,QgsPointXY,QgsVectorFileWriter

from PyQt5.QtCore import QVariant

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'accidente_modulo_dockwidget_base.ui'))


class AccidenteDockWidget(QtWidgets.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(AccidenteDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://doc.qt.io/qt-5/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
        self.btn_actualizar.clicked.connect(self.actualizar)

        #Coloco los filtro y le digo el tipo de archivos que permita cargar:
        self.qfw_selector.setFilter("Archivos csv(*.csv)")        
        self.qfw_selectorcapa.setFilter("Archivos shp(*.shp)")     
        #botón cargar fichero
        self.btn_cargar.clicked.connect(self.cargar_fichero)             
        #a partir de aqui importo las librerias QgsProject, 
        #QgsVectorLayer,QgsField, QgsFeature,QgsGeometry,QgsPointXY
        #,QgsVectorFileWriter:
        self.btn_crearcapa.clicked.connect(self.crear_capa)
        #botón cargar capa shape
        self.btn_cargacapa.clicked.connect(self.cargar_capa)
        #a partir de aqui importo processing
        self.btn_analisis.clicked.connect(self.capa_analisis)
   

   
    def actualizar(self):
        global lista_capas
        capas=QgsProject.instance().mapLayers().values()
        lista_capas=[]
        lista_capas=[capa.name() for capa in capas]
        self.cmb_capas.clear()
        self.cmb_capas.addItems(lista_capas)   
                
    def cargar_fichero(self,event):
        ruta=str(self.qfw_selector.filePath())#ruta seleccionada       
        #abro el archivo para leer y lo manejo con alias leer_csv:
        with open(ruta,'r') as leer_csv:  
         lineas=leer_csv.read().splitlines()#Separo por lineas
         contar=0
         #lineas es el vector y linea cada uno de los renglones del vector lineas
         #recorro los renglones con un for
         #Leemos y almacenamos la tabla
         for linea in lineas:
            if contar>0:#para que no coga los títulos
              campos=linea.split(';')#separo los campos de cada fila 
              self.qtw_tabla.insertRow(self.qtw_tabla.rowCount())
              #codigo distrito
              self.qtw_tabla.setItem(self.qtw_tabla.rowCount()-1,0,QtWidgets.QTableWidgetItem((campos[5])))
              #nombre distrito
              self.qtw_tabla.setItem(self.qtw_tabla.rowCount() - 1, 1, QtWidgets.QTableWidgetItem((campos[6])))
              #coordenada X
              self.qtw_tabla.setItem(self.qtw_tabla.rowCount() - 1, 2, QtWidgets.QTableWidgetItem((campos[15])))
              #coordenada Y
              self.qtw_tabla.setItem(self.qtw_tabla.rowCount() - 1, 3, QtWidgets.QTableWidgetItem((campos[16])))
              self.qtw_tabla.setItem(self.qtw_tabla.rowCount() - 1, 4, QtWidgets.QTableWidgetItem((campos[7])))
              self.qtw_tabla.setItem(self.qtw_tabla.rowCount() - 1, 5, QtWidgets.QTableWidgetItem((campos[9])))
              self.qtw_tabla.setItem(self.qtw_tabla.rowCount() - 1, 6, QtWidgets.QTableWidgetItem((campos[17])))
            contar=contar+1


    def crear_capa(self, event):
        #creo una capa tipo punto, le digo el sistema de coordenadas de los datos, 
        #creamos la capa en memoria(temporal)
        vlayer = QgsVectorLayer('Point?crs=EPSG:25830', 'Accidentes en Ciudad', 'memory')
        #proveedor de la capa 
        provider = vlayer.dataProvider()
        #añado los campos tipo string
        provider.addAttributes([QgsField('Cod_Distrito', QVariant.String),QgsField('Nombre_Distrito', QVariant.String),QgsField('Tipo_accidente', QVariant.String),QgsField('Tipo_vehiculo', QVariant.String),QgsField('alcohol', QVariant.String)])
        #actualizo los campos de la capa
        vlayer.updateFields()
    
        for fila in range(0,self.qtw_tabla.rowCount()-1):
          #creo una entidad
          f = QgsFeature()
          #con propiedades de geometría con las coordenadas indicadas
          f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(float(self.qtw_tabla.item(fila,2).text()),float(self.qtw_tabla.item(fila,3).text()))))
          #añado atributos
          f.setAttributes([self.qtw_tabla.item(fila,0).text(), self.qtw_tabla.item(fila,1).text(), self.qtw_tabla.item(fila,4).text(), self.qtw_tabla.item(fila,5).text(), self.qtw_tabla.item(fila,6).text()])
          #añado al proveedor el registro creado
          provider.addFeature(f)
          #actualizo la capa         
          vlayer.updateExtents()
        #Añado la capa al proyecto actual
        QgsProject.instance().addMapLayer(vlayer)
        #vlayer.setOpacity(0.1)
        
        #rutas relativas
        #En el directorio raiz del plugin me creo las carpetas templates(estilos) y salida(ficheros creados)
        thisFilePath = os.path.dirname(os.path.realpath(__file__))
        self.templatePath = thisFilePath 
        
        rutaESTILO1=self.templatePath+'//templates/estilo1.qml'
        #guardo la capa en una ruta para poder llamarla desde proccesing
        thisFilePath = os.path.dirname(os.path.realpath(__file__))
        self.templatePath = thisFilePath 
                
        rutaSHAPEfile=self.templatePath+'//salida/accidentes.shp'  
        #cargo estilo y escribo fichero        
        QgsVectorFileWriter.writeAsVectorFormat(vlayer,rutaSHAPEfile,"utf-8",vlayer.crs(),"ESRI Shapefile")
        vlayer.loadNamedStyle(rutaESTILO1) 

    def cargar_capa(self,event):
        ruta=str(self.qfw_selectorcapa.filePath())     
        #creo una capa a partir del fichero que indico en la ruta 
        layer = QgsVectorLayer(ruta,"distritos")
        #Añado la capa al proyecto actual
        QgsProject.instance().addMapLayer(layer)        
        layer.setOpacity(0.5)              
        
        thisFilePath = os.path.dirname(os.path.realpath(__file__))
        self.templatePath = thisFilePath

        rutaESTILO2=self.templatePath+'//templates/estilo2.qml'
        #guardo la capa en una ruta para poder llamarla desde proccesing
        rutaSHAPEfile=self.templatePath+'//salida/distritos.shp'
        #cargo estilo y escribo fichero
        layer.loadNamedStyle(rutaESTILO2) 
        QgsVectorFileWriter.writeAsVectorFormat(layer,rutaSHAPEfile,"utf-8",layer.crs(),"ESRI Shapefile")
        
    def capa_analisis(self,event):       

       thisFilePath = os.path.dirname(os.path.realpath(__file__))
       self.templatePath = thisFilePath

       #ruta del fichero estilo
       rutaESTILO=self.templatePath+'\\templates\estilo.qml'
       #ruta de la capa de polígonos
       layer=self.templatePath+'//salida/distritos.shp'                    
       #ruta de la capa de puntos
       layerP = self.templatePath+'//salida/accidentes.shp'       
       #ruta del fichero de salida
       fileOutput=self.templatePath+'//salida/accidentesDistritoContar.shp'
       
       #geoproceso nativo de QGIS: "Contar puntos en polígono"
       processing.run("qgis:countpointsinpolygon", {'POLYGONS': layer,'POINTS': layerP,'OUTPUT': fileOutput})
       #creo una capa a partir del fichero creado en el geoproceso
       lyrcountpointsinpolygon = QgsVectorLayer(fileOutput, 'AccidentesPorDistrito', "ogr")     
       #Añado la capa al proyecto actual
       QgsProject.instance().addMapLayer(lyrcountpointsinpolygon)        
       #Añado el estilo de una leyenda guardada en una ruta
       lyrcountpointsinpolygon.loadNamedStyle(rutaESTILO) 
       lyrcountpointsinpolygon.setOpacity(0.5)
       lyrcountpointsinpolygon.updateExtents()
     
    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()





