# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import uic

import numpy as np
import multiprocessing as mp
import pyqtgraph as pg
import itertools

from opennft import utils
from opennft import config
from opennft.rtqa_fdm import FD


class RTQAWindow(QtWidgets.QWidget):
    """Real-time quality assessment GUI and methods application class
    """

    # --------------------------------------------------------------------------
    def __init__(self, input, output, rtqa_calc):
        super(RTQAWindow, self).__init__(flags=QtCore.Qt.Window)
        mp.Process.__init__(self)

        uic.loadUi(utils.get_ui_file('rtqa.ui'), self)

        self.rtqa_calc = rtqa_calc

        self.rtqa_calc.input = input
        self.rtqa_calc.output = output

        # parent data transfer block
        sz = int(input["nr_rois"])
        self.nrROIs = sz
        self.musterInfo = input["muster_info"]

        if input["is_auto_rtqa"]:
            self.comboBox.model().item(2).setEnabled(False)
            self.comboBox.model().item(6).setEnabled(False)
        else:
            self.computeMusterPlotData(config.MUSTER_Y_LIMITS)

        xrange = self.rtqa_calc.xrange

        # Additional GUI elements connection and initialization
        groupBoxLayout = self.roiGroupBox.layout()
        for i in range(sz):
            if i == sz-1:
                name = 'Whole brain ROI'
            else:
                name = 'ROI_' + str(i + 1)
            label = QtWidgets.QLabel(name)
            label.setStyleSheet("color: " + config.ROI_PLOT_COLORS[i].name())
            label.setVisible(False)
            groupBoxLayout.addWidget(label)
        self.selectedRoiLabels = self.roiGroupBox.findChildren(QtWidgets.QLabel)
        self.mcrRadioButton.toggled.connect(self.onRadioButtonStateChanged)

        # Plots initialization
        self.snrPlot = pg.PlotWidget(self)
        self.snrPlot.setBackground((255, 255, 255))
        self.snrPlotLayout.addWidget(self.snrPlot)
        p = self.snrPlot.getPlotItem()
        self.plotsSetup(p, "SNR [a.u.]", xrange)
        self.drawMusterPlot(p)
        p.setYRange(-1, 1, padding=0.0)

        self.noRegSnrPlot = pg.PlotWidget(self)
        self.noRegSnrPlot.setBackground((255, 255, 255))
        self.noRegSnrPlotLayout.addWidget(self.noRegSnrPlot)
        p = self.noRegSnrPlot.getPlotItem()
        self.plotsSetup(p, "SNR [a.u.]", xrange)
        self.drawMusterPlot(p)
        p.setYRange(-1, 1, padding=0.0)

        self.msePlot = pg.PlotWidget(self)
        self.msePlot.setBackground((255, 255, 255))
        self.msePlotLayout.addWidget(self.msePlot)
        p = self.msePlot.getPlotItem()
        self.plotsSetup(p, "Mean squared error [a.u.]", xrange)
        self.drawMusterPlot(p)
        p.setYRange(-1, 1, padding=0.0)

        self.trendPlot = pg.PlotWidget(self)
        self.trendPlot.setBackground((255, 255, 255))
        self.linearTreandPlotLayout.addWidget(self.trendPlot)
        p = self.trendPlot.getPlotItem()
        self.plotsSetup(p, "Beta regressor amplitude [a.u.]", xrange)
        self.drawMusterPlot(p)
        p.setYRange(-1, 1, padding=0.0)

        self.fdPlot = pg.PlotWidget(self)
        self.fdPlot.setBackground((255, 255, 255))
        self.fdPlotLayout.addWidget(self.fdPlot)
        p = self.fdPlot.getPlotItem()
        self.plotsSetup(p, "FD [mm]", xrange)

        self.translatPlot = pg.PlotWidget(self)
        self.translatPlot.setBackground((255, 255, 255))
        self.tdPlotLayout.addWidget(self.translatPlot)
        p = self.translatPlot.getPlotItem()
        self.plotsSetup(p, "Amplitude [mm]", xrange)

        self.rotatPlot = pg.PlotWidget(self)
        self.rotatPlot.setBackground((255, 255, 255))
        self.rdPlotLayout.addWidget(self.rotatPlot)
        p = self.rotatPlot.getPlotItem()
        self.plotsSetup(p, "Amplitude [mm]", xrange)

        self.dvarsPlot = pg.PlotWidget(self)
        self.dvarsPlot.setBackground((255, 255, 255))
        self.dvarsPlotLayout.addWidget(self.dvarsPlot)
        p = self.dvarsPlot.getPlotItem()
        self.plotsSetup(p, "DVARS [a.u.]", xrange)

        self.spikesPlot = pg.PlotWidget(self)
        self.spikesPlot.setBackground((255, 255, 255))
        self.spikesPlotLayout.addWidget(self.spikesPlot)
        p = self.spikesPlot.getPlotItem()
        self.plotsSetup(p, "Amplitude [a.u.]", xrange)
        self.drawMusterPlot(p)
        p.setYRange(-1, 1, padding=0.0)

        # CNR, means and variances plots and labels
        if not input["is_auto_rtqa"]:

            self.cnrPlot = pg.PlotWidget(self)
            self.cnrPlot.setBackground((255, 255, 255))
            self.cnrPlotLayout.addWidget(self.cnrPlot)
            p = self.cnrPlot.getPlotItem()
            self.plotsSetup(p, "CNR [a.u.]", xrange)
            self.drawMusterPlot(p)
            p.setYRange(-1, 1, padding=0.0)

            self.meanPlot = pg.PlotWidget(self)
            self.meanPlot.setBackground((255, 255, 255))
            self.meanPlotLayout.addWidget(self.meanPlot)
            p = self.meanPlot.getPlotItem()
            self.plotsSetup(p, "Mean [a.u.]", xrange)
            self.drawMusterPlot(p)
            p.setYRange(-1, 1, padding=0.0)

            self.varPlot = pg.PlotWidget(self)
            self.varPlot.setBackground((255, 255, 255))
            self.varPlotLayout.addWidget(self.varPlot)
            p = self.varPlot.getPlotItem()
            self.plotsSetup(p, "Variance [a.u.]", xrange)
            self.drawMusterPlot(p)
            p.setYRange(-1, 1, padding=0.0)

            names = ['ROI_1 rMean', ' bas', ' cond']
            color = [config.ROI_PLOT_COLORS[0], config.ROI_PLOT_COLORS[0], config.ROI_PLOT_COLORS[0]]
            for i in range(sz - 1):
                if i == sz - 2:
                    name = 'Whole brain ROI'
                else:
                    name = 'ROI_' + str(i + 2)
                names.append(name + ' rMean')
                names.append(' bas')
                names.append(' cond')
                color = color + [config.ROI_PLOT_COLORS[i + 1]] + [config.ROI_PLOT_COLORS[i + 1]] + [
                    config.ROI_PLOT_COLORS[i + 1]]
            pens = []
            for i in range(sz * 3):
                pens = pens + [pg.mkPen(color[i], width=1.2)]
            self.makeTextValueLabel(self.labelMean, names, pens)

            names = ['ROI_1 rVariance', ' bas', ' cond']
            for i in range(sz - 1):
                if i == sz - 2:
                    name = 'Whole brain ROI'
                else:
                    name = 'ROI_' + str(i + 2)
                names.append(name + ' rVariance')
                names.append(' bas')
                names.append(' cond')
            self.makeTextValueLabel(self.labelVar, names, pens)

        # Other labels initialization
        names = ['Translationals: ']
        pens = [config.PLOT_PEN_COLORS[6]]
        for i in range(3):
            names.append(self.names[i])
            pens.append(config.PLOT_PEN_COLORS[i])
        self.makeTextValueLabel(self.tdLabel, names, pens)

        names = ['Rotations: ']
        pens = [config.PLOT_PEN_COLORS[6]]
        for i in range(3):
            names.append(self.names[i + 3])
            pens.append(config.PLOT_PEN_COLORS[i + 3])
        self.makeTextValueLabel(self.rdLabel, names, pens)

        names = ['Framewise Displacement']
        pens = [config.PLOT_PEN_COLORS[0]]
        for i in range(len(config.DEFAULT_FD_THRESHOLDS) - 1):
            names.append('Threshold ' + str(i + 1))
            pens.append(config.PLOT_PEN_COLORS[i + 1])
        self.makeTextValueLabel(self.fdLabel, names, pens)

        self.onComboboxChanged()
        self.volumeCheckBox.stateChanged.connect(self.onShowRtqaVol)

    # --------------------------------------------------------------------------
    def closeEvent(self, event):

        self.hide()
        event.accept()

    # --------------------------------------------------------------------------
    def plotsSetup(self, p, yName, xrange):

        p.setLabel('left', yName)
        p.setMenuEnabled(enableMenu=False)
        p.setMouseEnabled(x=False, y=False)
        p.showGrid(x=True, y=True, alpha=1)
        p.installEventFilter(self)
        p.disableAutoRange(axis=pg.ViewBox.XAxis)
        p.setXRange(1, xrange, padding=0.0)

    # --------------------------------------------------------------------------
    def onShowRtqaVol(self):

        state = self.comboBox.currentIndex()
        if state == 0:
            self.rtqa_calc.output["rtqa_vol"] = self.rtqa_calc.volume_data["snr_vol"]
        elif state == 2:
            self.rtqa_calc.output["rtqa_vol"] = self.rtqa_calc.volume_data["cnr_vol"]

    # --------------------------------------------------------------------------
    def onComboboxChanged(self):
        """  SNR/CNR label switching. Both modes use the same label
        """

        state = self.comboBox.currentIndex()

        # SNR state
        if state == 0:

            names = ['SNR ']
            pens = [config.PLOT_PEN_COLORS[6]]
            sz = len(self.rtqa_calc.rSNR)
            for i in range(sz):
                if i == sz - 1:
                    name = 'Whole brain ROI'
                else:
                    name = 'ROI_' + str(i + 1)
                names.append(name + ':  ' + '{0:.3f}'.format(float(self.rtqa_calc.rSNR[i][self.rtqa_calc.iteration])))
                pens.append(pg.mkPen(color=config.ROI_PLOT_COLORS[i], width=1.2))
            self.makeTextValueLabel(self.valuesLabel, names, pens, lineBreak='<br>')
            self.currentMode = 0

        # CNR state
        elif state == 2:

            self.stackedWidgetOptions.setCurrentIndex(0)

            names = ['СNR ']
            pens = [config.PLOT_PEN_COLORS[6]]
            sz = len(self.rtqa_calc.rCNR)
            for i in range(sz):
                if i == sz - 1:
                    name = 'Whole brain ROI'
                else:
                    name = 'ROI_' + str(i + 1)
                names.append(name + ':  ' + '{0:.3f}'.format(float(self.rtqa_calc.rCNR[i][self.rtqa_calc.iteration])))
                pens.append(pg.mkPen(color=config.ROI_PLOT_COLORS[i], width=1.2))
            self.makeTextValueLabel(self.valuesLabel, names, pens, lineBreak='<br>')
            self.currentMode = 2

        if state == 1 or state == 7:
            self.roiGroupBox.setVisible(False)
        else:
            self.roiGroupBox.setVisible(True)

    # --------------------------------------------------------------------------
    def onRadioButtonStateChanged(self):
        """ FD and MD mode change. Mode changing switch plots and plot title
        """

        if self.mcrRadioButton.isChecked():
            names = ['Micro Displacement']
            pens = [config.PLOT_PEN_COLORS[0]]
            names.append('Threshold')
            pens.append(config.PLOT_PEN_COLORS[2])
            self.makeTextValueLabel(self.fdLabel, names, pens)

        else:
            names = ['Framewise Displacement']
            pens = [config.PLOT_PEN_COLORS[0]]
            for i in range(len(config.DEFAULT_FD_THRESHOLDS) - 1):
                names.append('Threshold ' + str(i + 1))
                pens.append(config.PLOT_PEN_COLORS[i + 1])
            self.makeTextValueLabel(self.fdLabel, names, pens)

        self.draw_mc_plots(self.mcrRadioButton.isChecked())

    # --------------------------------------------------------------------------
    def makeTextValueLabel(self, label, names, pens, lineBreak=' '):
        """ Dynamic generation of titles and value labels

        :param label: label for text update
        :param names: set of names
        :param pens: set of pens for each name
        :param lineBreak: line break for value labels, space by default for title labels
        """

        label.setText('')
        legendText = '<html><head/><body><p>'

        for n, c in zip(names, pens):
            cname = c.color().name()
            legendText += (
                    '<span style="font-weight:600;color:{};">'.format(cname) + '{}</span>'.format(n) + lineBreak)

        legendText += '</p></body></html>'

        label.setText(legendText)

    # --------------------------------------------------------------------------
    def roiChecked(self):
        """ Redrawing plots when the set of selected ROIs is changed even if run is stopped
        """

        self.checkedBoxesInd = self.rtqa_calc.input["roi_checked"]
        for i in range(len(self.selectedRoiLabels)):
            if i in self.checkedBoxesInd:
                self.selectedRoiLabels[i].setVisible(True)
            else:
                self.selectedRoiLabels[i].setVisible(False)

        self.init = True
        if self.rtqa_calc.input["is_stopped"] and self.rtqa_calc.iteration!=1:
            self.plotRTQA(self.rtqa_calc.iteration+1)

    # --------------------------------------------------------------------------
    def computeMusterPlotData(self, ylim):
        singleY = np.array([ylim[0], ylim[1], ylim[1], ylim[0]])

        def computeConds(nrCond, tmpCond):
            xCond = np.zeros(nrCond * 4, dtype=np.float64)
            yCond = np.zeros(nrCond * 4, dtype=np.float64)

            for k in range(nrCond):
                i = slice(k * 4, (k + 1) * 4)

                xCond[i] = np.array([
                    tmpCond[k][0] - 1,
                    tmpCond[k][0] - 1,
                    tmpCond[k][1],
                    tmpCond[k][1],
                ])

                yCond[i] = singleY

            return xCond, yCond

        for cond in range(self.musterInfo['condTotal']):
            xCond, yCond = computeConds(self.musterInfo['nrCond' + str(cond + 1)],
                                        self.musterInfo['tmpCond' + str(cond + 1)])
            self.musterInfo['xCond' + str(cond + 1)] = xCond
            self.musterInfo['yCond' + str(cond + 1)] = yCond

    # --------------------------------------------------------------------------
    def drawMusterPlot(self, plotitem):

        ylim = config.MUSTER_Y_LIMITS

        if self.comboBox.model().item(2).isEnabled():

            muster = []

            for i in range(self.musterInfo['condTotal']):
                muster.append(
                    plotitem.plot(x=self.musterInfo['xCond' + str(i + 1)],
                                  y=self.musterInfo['yCond' + str(i + 1)],
                                  fillLevel=ylim[0],
                                  pen=config.MUSTER_PEN_COLORS[i],
                                  brush=config.MUSTER_BRUSH_COLORS[i])
                )

        else:
            muster = [
                plotitem.plot(x=[1, self.rtqa_calc.xrange],
                              y=[-1000, 1000],
                              fillLevel=ylim[0],
                              pen=config.MUSTER_PEN_COLORS[9],
                              brush=config.MUSTER_BRUSH_COLORS[9])
            ]

        return muster

    # --------------------------------------------------------------------------
    def plotTs(self, init, plotitem, data, checkedBoxesInd):
        """ Time-series plot method

        :param init: flag for plot initializtion
        :param plotitem: time-series plotitem
        :param data: time-series value for drawing
        :param checkedBoxesInd: indexes of selected ROIs
        """

        if self.tsCheckBox.isChecked():

            sz, l = data.shape

            if init:

                plotitem.clear()
                plots = []

                muster = self.drawMusterPlot(plotitem)

                plot_colors = np.array(config.ROI_PLOT_COLORS)[checkedBoxesInd]
                for i, c in zip(range(sz), plot_colors):
                    pen = pg.mkPen(color=c, width=config.ROI_PLOT_WIDTH)
                    p = plotitem.plot(pen=pen)
                    plots.append(p)

                self.plotTs.__dict__[plotitem] = plots, muster

            x = np.arange(1, l + 1, dtype=np.float64)

            plotitems = self.plotTs.__dict__[plotitem][0]
            for p, y in zip(plotitems, data):
                p.setData(x=x, y=np.array(y))

            items = plotitem.listDataItems()

            for m in self.plotTs.__dict__[plotitem][1]:
                items.remove(m)

            if data.any():
                if plotitem.vb.state["targetRange"][1] == [-1, 1]:
                    plotitem.enableAutoRange(enable=True, x=False, y=True)
                plotitem.setYRange(np.min(data).astype(np.float32), np.max(data).astype(np.float32), padding=0.0)

    # --------------------------------------------------------------------------
    def plotRTQA(self, n):
        """ Encapsulated plots drawing

        :param n: last volume index
        """

        self.labelsUpdate()

        # SNR plot
        plotitem = self.snrPlot.getPlotItem()
        data = self.rtqa_calc.rSNR[self.rtqa_calc.checkedBoxesInd, 0:n]
        self.plotTs(self.init, plotitem, data, self.checkedBoxesInd)

        if self.comboBox.model().item(2).isEnabled():
            # CNR plot
            plotitem = self.cnrPlot.getPlotItem()
            data = self.rtqa_calc.rCNR[self.checkedBoxesInd, 0:n]
            self.plotTs(self.init, plotitem, data, self.checkedBoxesInd)

            # Means plot
            plotitem = self.meanPlot.getPlotItem()
            data = np.append(self.rtqa_calc.rMean[self.checkedBoxesInd, 0:n], self.rtqa_calc.meanBas[self.checkedBoxesInd, 0:n], axis=0)
            data = np.append(data, self.rtqa_calc.meanCond[self.checkedBoxesInd, 0:n], axis=0)
            color = np.array(config.ROI_PLOT_COLORS)[self.checkedBoxesInd]
            color = np.append(color, np.array(config.ROI_PLOT_COLORS)[self.checkedBoxesInd])
            color = np.append(color, np.array(config.ROI_PLOT_COLORS)[self.checkedBoxesInd])
            style = [QtCore.Qt.SolidLine, QtCore.Qt.DashLine, QtCore.Qt.DashDotDotLine]
            self.plotStatValues(self.init, plotitem, data, color, style)

            # Variances plot
            plotitem = self.varPlot.getPlotItem()
            data = np.append(self.rtqa_calc.rVar[self.checkedBoxesInd, 0:n], self.rtqa_calc.varBas[self.checkedBoxesInd, 0:n], axis=0)
            data = np.append(data, self.rtqa_calc.varCond[self.checkedBoxesInd, 0:n], axis=0)
            self.plotStatValues(self.init, plotitem, data, color, style)

        # Spikes plot
        plotitem = self.spikesPlot.getPlotItem()
        data = self.rtqa_calc.glmProcTimeSeries[self.checkedBoxesInd, 0:n]
        self.plotSpikes(self.init, plotitem, data, self.checkedBoxesInd)

        # Kalman filter MSE plot
        plotitem = self.msePlot.getPlotItem()
        data = self.rtqa_calc.rMSE[self.checkedBoxesInd, 0:n]
        self.plotTs(self.init, plotitem, data, self.checkedBoxesInd)

        # Linear trend coefficients plot
        plotitem = self.trendPlot.getPlotItem()
        data = self.rtqa_calc.linTrendCoeff[self.checkedBoxesInd, 0:n]
        self.plotTs(self.init, plotitem, data, self.checkedBoxesInd)

        # No regulation SNR plot
        plotitem = self.noRegSnrPlot.getPlotItem()
        data = self.rtqa_calc.rNoRegSNR[self.checkedBoxesInd, 0:n]
        self.plotTs(self.init, plotitem, data, self.checkedBoxesInd)

        # DVARS plot
        plotitem = self.dvarsPlot.getPlotItem()
        plotitem.clear()
        plotitem.plot(y=self.rtqa_calc.DVARS, pen=config.PLOT_PEN_COLORS[0], name='DVARS')
        plotitem.plot(x=np.arange(1, self.rtqa_calc.xrange+1, dtype=np.float64), y=config.DEFAULT_DVARS_THRESHOLD * np.ones(self.rtqa_calc.xrange),
                        pen=config.PLOT_PEN_COLORS[2], name='thr')

        self.init = False

    # --------------------------------------------------------------------------
    def plotStatValues(self, init, plotitem, data, color, style):
        """ Drawing method for mean and variance statistics

        :param init: flag for plot initializtion
        :param plotitem: mean or variance plotitem
        :param data: signal values for drawing
        :param color: color of each ROI line
        :param style: style of each ROI line
        """

        if self.tsCheckBox.isChecked():

            sz, l = data.shape

            if init:

                plotitem.clear()
                plots = []

                muster = self.drawMusterPlot(plotitem)

                style = np.repeat(style, sz / 3)

                for i, c, s in zip(range(sz), color, style):
                    pen = pg.mkPen(c, width=3.0, style=QtCore.Qt.PenStyle(s))
                    p = plotitem.plot(pen=pen)
                    plots.append(p)

                self.plotTs.__dict__[plotitem] = plots, muster

            x = np.arange(1, l + 1, dtype=np.float64)

            for p, y in zip(self.plotTs.__dict__[plotitem][0], data):
                p.setData(x=x, y=np.array(y))

            items = plotitem.listDataItems()

            for m in self.plotTs.__dict__[plotitem][1]:
                items.remove(m)

            if data.any():
                plotitem.setYRange(np.min(data[np.nonzero(data)]), np.max(data), padding=0.0)

    # --------------------------------------------------------------------------
    def plotDisplacements(self):
        """ Drawing of Framewise and Micro Displacements

        """

        self.rtqa_calc.draw_mc_plots(self.mcrRadioButton.isChecked())

    # --------------------------------------------------------------------------
    def plotSpikes(self, init, plotitem, data, checkedBoxesInd):
        """ Spikes plot drawing

        :param init: flag for plot initializtion
        :param plotitem: spikes plotitem
        :param data: signal values for drawing
        :param checkedBoxesInd: indexes of selected ROIs
        """

        # First part - line drawing
        sz, l = data.shape
        x = np.arange(1, l + 1, dtype=np.float64)

        if init:
            plotitem.clear()
            plots = []

            muster = self.drawMusterPlot(plotitem)

            for i, c in zip(range(sz), np.array(config.ROI_PLOT_COLORS)[checkedBoxesInd]):
                pen = pg.mkPen(color=c, width=config.ROI_PLOT_WIDTH)
                p = plotitem.plot(pen=pen)
                plots.append(p)

            self.plotSpikes.__dict__[plotitem] = plots, muster

        plots = self.plotSpikes.__dict__[plotitem][0]
        for p, y in zip(plots, data):
            p.setData(x=x, y=np.array(y))

        # Second part - spikes marking
        for i, c in zip(range(sz), np.array(config.ROI_PLOT_COLORS)[checkedBoxesInd]):

            roiInd = checkedBoxesInd[i]
            if self.posSpikes[str(roiInd)].any():
                brush = pg.mkBrush(color=c)
                p = plotitem.scatterPlot(symbol='o', size=20, brush=brush)
                plots.append(p)
                plots[-1].setData(x=self.rtqa_calc.posSpikes[str(roiInd)] + 1,
                                  y=self.rtqa_calc.glmProcTimeSeries[roiInd, self.rtqa_calc.posSpikes[str(roiInd)]])

                pen = pg.mkPen(color=pg.mkColor(0, 0, 0), width=1.5 * config.ROI_PLOT_WIDTH)
                p = plotitem.plot(pen=pen)
                plots.append(p)

                inds = self.posSpikes[str(roiInd)]
                indX = np.array(list(itertools.chain.from_iterable(zip(inds, inds + 1))))
                indY = np.array(list(itertools.chain.from_iterable(zip(inds - 1, inds))))

                y = np.array(self.glmProcTimeSeries[roiInd, indY])
                x1 = indX

                plots[-1].setData(x=x1, y=y, connect='pairs')

            if self.negSpikes[str(roiInd)].any():
                brush = pg.mkBrush(color=c)
                p = plotitem.scatterPlot(symbol='d', size=20, brush=brush)
                plots.append(p)
                plots[-1].setData(x=self.rtqa_calc.negSpikes[str(roiInd)] + 1,
                                  y=self.rtqa_calc.glmProcTimeSeries[roiInd, self.rtqa_calc.negSpikes[str(roiInd)]])

                pen = pg.mkPen(color=pg.mkColor(0, 0, 0), width=1.5 * config.ROI_PLOT_WIDTH)
                p = plotitem.plot(pen=pen)
                plots.append(p)

                inds = self.rtqa_calc.negSpikes[str(roiInd)]
                indX = np.array(list(itertools.chain.from_iterable(zip(inds, inds + 1))))
                indY = np.array(list(itertools.chain.from_iterable(zip(inds - 1, inds))))

                y = np.array(self.rtqa_calc.glmProcTimeSeries[roiInd, indY])
                x1 = indX

                plots[-1].setData(x=x1, y=y, connect='pairs')

        items = plotitem.listDataItems()

        for m in self.plotSpikes.__dict__[plotitem][1]:
            items.remove(m)

        if data.any():
            plotitem.setYRange(np.min(self.rtqa_calc.glmProcTimeSeries) - 1, np.max(self.rtqa_calc.glmProcTimeSeries) + 1, padding=0.0)

    # --------------------------------------------------------------------------
    def draw_mc_plots(self, mdFlag):

        x = np.arange(1, self.data.shape[0] + 1, dtype=np.float64)

        self.translatPlot.clear()
        self.rotatPlot.clear()
        self.fdPlot.clear()

        for i in range(0, 3):
            self.translatPlot.plot(x=x, y=self.data[:, i], pen=config.PLOT_PEN_COLORS[i], name=self.names[i])

        for i in range(3, 6):
            self.rotatPlot.plot(x=x, y=self.data[:, i]*50, pen=config.PLOT_PEN_COLORS[i], name=self.names[i])

        x = np.arange(1, self.data.shape[0], dtype=np.float64)

        if mdFlag:
            self.fdPlot.setLabel('left', "MD [mm]")
            self.fdPlot.plot(x=x, y=self.MD, pen=config.PLOT_PEN_COLORS[0], name='MD')
            self.fdPlot.plot(x=np.arange(0, self.xmax, dtype=np.float64), y=self.threshold[0] * np.ones(self.xmax),
                            pen=config.PLOT_PEN_COLORS[2], name='thr')
        else:
            self.fdPlot.setLabel('left', "FD [mm]")
            self.fdPlot.plot(x=x, y=self.FD, pen=config.PLOT_PEN_COLORS[0], name='FD')
            thresholds = self.threshold[1:3]
            for i, t in enumerate(thresholds):
                self.fdPlot.plot(x=np.arange(0, self.xmax, dtype=np.float64), y=float(t) * np.ones(self.xmax),
                                pen=config.PLOT_PEN_COLORS[i + 1], name='thr' + str(i))

    # --------------------------------------------------------------------------
    def labelsUpdate(self):

        sz = self.nrROIs
        indexVolume = self.rtqa_calc.iteration

        # SNR
        if self.comboBox.currentIndex() == 0:
            names = ['SNR ']
            pens = [config.PLOT_PEN_COLORS[6]]
            for i in range(sz):
                if i == sz - 1:
                    name = 'Whole brain ROI'
                else:
                    name = 'ROI_' + str(i + 1)
                names.append(name + ': ' + '{0:.3f}'.format(float(self.rtqa_calc.rSNR[i, indexVolume])))
                pens.append(pg.mkPen(color=config.ROI_PLOT_COLORS[i], width=1.2))

            self.makeTextValueLabel(self.valuesLabel, names, pens, lineBreak='<br>')
        elif self.comboBox.currentIndex() == 2:
            # CNR
            names = ['СNR ']
            pens = [config.PLOT_PEN_COLORS[6]]
            for i in range(self.nrROIs):
                if i == sz - 1:
                    name = 'Whole brain ROI'
                else:
                    name = 'ROI_' + str(i + 1)
                names.append(name + ': ' + '{0:.3f}'.format(float(self.rtqa_calc.rCNR[i][indexVolume - 1])))
                pens.append(pg.mkPen(color=config.ROI_PLOT_COLORS[i], width=1.2))

            if self.comboBox.currentIndex() == 2:
                names.append('<br><br>Baseline values   --- ')
                pens.append(config.PLOT_PEN_COLORS[6])
                names.append('Condition values -··-··- ')
                pens.append(config.PLOT_PEN_COLORS[6])

            self.makeTextValueLabel(self.valuesLabel, names, pens, lineBreak='<br>')

        # MCMD
        names = ['<u>FD</u> ']
        pens = [config.PLOT_PEN_COLORS[6]]
        names.append('Threshold 1: ' + str(int(self.rtqa_calc.excFD[0])))
        pens.append(config.PLOT_PEN_COLORS[1])
        names.append('Threshold 2: ' + str(int(self.rtqa_calc.excFD[1])))
        pens.append(config.PLOT_PEN_COLORS[2])
        names.append('<br><u>MD</u> ')
        pens.append(config.PLOT_PEN_COLORS[6])
        names.append('Threshold: ' + str(int(self.rtqa_calc.excVD)))
        pens.append(config.PLOT_PEN_COLORS[2])
        names.append('<br><u>Mean FD</u> ')
        pens.append(config.PLOT_PEN_COLORS[6])
        names.append('{0:.3f}'.format(self.rtqa_calc.meanFD))
        pens.append(config.PLOT_PEN_COLORS[6])
        names.append('<br><u>Mean MD</u> ')
        pens.append(config.PLOT_PEN_COLORS[6])
        names.append('{0:.3f}'.format(self.rtqa_calc.meanMD))
        pens.append(config.PLOT_PEN_COLORS[6])
        names.append('<br><u>Offset MC parameters</u> ')
        pens.append(config.PLOT_PEN_COLORS[6])
        for i in range(6):
            names.append('{0:.3e}'.format(self.rtqa_calc.offsetMCParam[0][i]))
            pens.append(config.PLOT_PEN_COLORS[6])
        self.makeTextValueLabel(self.mcmdValuesLabel, names, pens, lineBreak='<br>')

        # Spikes
        cnt = 0
        for i in range(sz):
            cnt = cnt + np.count_nonzero(self.rtqa_calc.posSpikes[str(i)])
        names = ['( Circles ) <br>Positive spikes: ' + str(int(cnt))]

        cnt = 0
        for i in range(sz):
            cnt = cnt + np.count_nonzero(self.rtqa_calc.negSpikes[str(i)])
        names.append('<br>( Diamonds )<br>Negative spikes: ' + str(int(cnt)))
        pens = [config.PLOT_PEN_COLORS[6],
                config.PLOT_PEN_COLORS[6]]
        self.makeTextValueLabel(self.spikesLabel, names, pens, lineBreak='<br>')

        # Linear trend
        names = ['Linear trend beta ']
        pens = [config.PLOT_PEN_COLORS[6]]
        sz = self.rtqa_calc.linTrendCoeff.shape[0]
        for i in range(sz):
            if i == sz - 1:
                name = 'Whole brain ROI'
            else:
                name = 'ROI_' + str(i + 1)
            names.append(name + ': ' + '{0:.3f}'.format(float(self.rtqa_calc.linTrendCoeff[i, indexVolume - 1])))
            pens.append(pg.mkPen(color=config.ROI_PLOT_COLORS[i], width=1.2))
        self.makeTextValueLabel(self.trendLabel, names, pens, lineBreak='<br>')

        # MSE
        names = ['MSE ']
        pens = [config.PLOT_PEN_COLORS[6]]
        for i in range(sz):
            if i == sz - 1:
                name = 'Whole brain ROI'
            else:
                name = 'ROI_' + str(i + 1)
            names.append(name + ': ' + '{0:.3f}'.format(float(self.rtqa_calc.rMSE[i, indexVolume])))
            pens.append(pg.mkPen(color=config.ROI_PLOT_COLORS[i], width=1.2))

        self.makeTextValueLabel(self.mseLabel, names, pens, lineBreak='<br>')

        # no reg SNR
        names = ['no reg SNR ']
        pens = [config.PLOT_PEN_COLORS[6]]
        for i in range(sz):
            if i == sz - 1:
                name = 'Whole brain ROI'
            else:
                name = 'ROI_' + str(i + 1)
            names.append(name + ': ' + '{0:.3f}'.format(float(self.rtqa_calc.rNoRegSNR[i, indexVolume])))
            pens.append(pg.mkPen(color=config.ROI_PLOT_COLORS[i], width=1.2))

        self.makeTextValueLabel(self.noRegSnrValueLabel, names, pens, lineBreak='<br>')

        # DVARS
        names = ['DVARS ']
        pens = [config.PLOT_PEN_COLORS[6]]
        names.append('{0:.3f} '.format(float(self.rtqa_calc.DVARS[-1])))
        pens.append(config.PLOT_PEN_COLORS[6])
        names.append('<br>Threshold : ' + str(int(self.rtqa_calc.excDVARS)))
        pens.append(config.PLOT_PEN_COLORS[6])

        self.makeTextValueLabel(self.dvarsLabel, names, pens, lineBreak='<br>')


