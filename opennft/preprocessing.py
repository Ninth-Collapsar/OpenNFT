# coding=utf-8

import codecs
import os
import subprocess

import pydicom
import matlab
import matlab.engine
import nibabel as nib
import shutil
import json
from PyQt5.QtCore import QSettings
import nilearn.image as nil


def dcm2nii(dcm_dir, out_dir, filename):
    print('--------------------------')
    print('dcm2nii: %s' % filename)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    p = subprocess.Popen('dcm2niix -z n -f %s -o "%s" "%s"' % (filename, out_dir, dcm_dir), shell=True,
                         stdout=subprocess.PIPE)
    out, err = p.communicate()
    for line in out.splitlines():
        print(codecs.decode(line, 'UTF-8'))


def makeROI(func, anat, stdRoiDir, subjectDir):
    eng = matlab.engine.start_matlab()
    eng.addpath(r'F:\Codes\Python\OpenNFT\opennft\matlab\makeROI')
    for roi in os.listdir(stdRoiDir):
        print('--------------------------')
        print('makeROI: %s' % roi)
        dstDir = os.path.join(subjectDir, 'ROI', roi.split('.')[0].split('_')[-1])
        eng.makeROI(func, anat, os.path.join(stdRoiDir, roi), nargout=0)
        if not os.path.exists(dstDir):
            os.makedirs(dstDir)
        resmp = nil.resample_to_img(os.path.join(stdRoiDir, 'w' + roi), func, interpolation='nearest')
        resmp.to_filename(os.path.join(dstDir, roi))
        del resmp
        os.remove(os.path.join(stdRoiDir, 'w' + roi))
    eng.quit()


def getDCMParam(dcmDir):
    print('--------------------------')
    print('getDCMParam: %s' % dcmDir)
    dcms = [dcm for dcm in os.listdir(dcmDir) if '.dcm' in dcm]
    dcm = pydicom.dcmread(os.path.join(dcmDir, dcms[0]))
    name = str(dcm.get('PatientName'))
    date = dcm.get('AcquisitionDate')
    matrix = dcm.get('AcquisitionMatrix')
    while 0 in matrix:
        matrix.remove(0)
    slices = int(dcm.get('NumberOfSlices') / len(dcms))
    TR = int(dcm.get('RepetitionTime'))
    print('subjectName: %s' % name)
    print('slices: %d' % slices)
    print('matrix: %s' % str(matrix))
    print('TR: %d' % TR)
    return slices, matrix, TR, name, date


def run():
    ################################################################

    # path setting
    t1Dir = r"E:\RT\preprocess\t1w"
    restDir = r"E:\RT\preprocess\rest"

    ################################################################

    subjectDirRoot = r"E:\RT\data\subjects"
    stdRoiDir = r"E:\RT\make_ROI\mask"
    srcCfgPath = r"F:\Codes\Python\OpenNFT\opennft\configs\NF_PSC_cont_155.ini"
    srcJsonPath = r"F:\Codes\Python\OpenNFT\opennft\configs\NF_PSC_cont_155.json"

    activeNumber = 6  # block number
    activeTime = 40  # 单位为s,每个block的时间

    # run
    slices, matrix, TR, subjectName, date = getDCMParam(restDir)
    subjectDir = '\\'.join([subjectDirRoot, subjectName + '_' + date])
    if not os.path.exists(subjectDir):
        os.makedirs(subjectDir)

    if not os.path.exists(os.path.join(subjectDir, 'USF', 'T1.nii')):
        dcm2nii(t1Dir, os.path.join(subjectDir, 'USF'), 'T1')
    if not os.path.exists(os.path.join(subjectDir, 'MCT', 'MOTION.nii')):
        dcm2nii(restDir, os.path.join(subjectDir, 'MCT'), 'MOTION')
    motion = nib.load(os.path.join(subjectDir, 'MCT', 'MOTION.nii'))
    nib.Nifti1Image(motion.get_data()[:, :, :, 0], motion.affine).to_filename(
        os.path.join(subjectDir, 'MCT', 'MOTION_first.nii'))
    motionPath = os.path.join(subjectDir, 'MCT', 'MOTION_first.nii')
    t1Path = os.path.join(subjectDir, 'USF', 'T1.nii')
    makeROI(motionPath, t1Path, stdRoiDir, subjectDir)

    subCfgDir = os.path.join(subjectDir, 'config')
    if not os.path.exists(subCfgDir):
        os.makedirs(subCfgDir)

    cfgPath = os.path.join(subCfgDir, 'config.ini')
    jsonPath = os.path.join(subCfgDir, 'config.json')
    shutil.copy(srcCfgPath, cfgPath)
    shutil.copy(srcJsonPath, jsonPath)
    watchFolder = os.path.join(subjectDir, 'watch')
    if not os.path.exists(watchFolder):
        os.makedirs(watchFolder)
    workFolder = os.path.join(subjectDir, 'work')
    if not os.path.exists(workFolder):
        os.makedirs(workFolder)
    roiFolder = os.path.join(subjectDir, 'ROI', 'HIP')
    settings = QSettings(cfgPath, QSettings.IniFormat)
    nrOfVolumes = 0
    with open(jsonPath, 'rb') as f:
        srcJson = json.load(f)
        srcJson['ConditionIndex'][0]['OnOffsets'] = []
        blockLength = int(activeTime * 1000 / TR)
        start = blockLength + 1
        for i in range(activeNumber):
            srcJson['ConditionIndex'][0]['OnOffsets'].append([start, start + blockLength - 1])
            nrOfVolumes = start + blockLength - 1
            start += 2 * blockLength
        dstJson = srcJson
        f.close()
    with open(jsonPath, 'w') as f:
        json.dump(dstJson, f)
        f.close()

    # new added.
    roi_dir = os.path.join(subjectDir, "ROI")
    os.mkdir(os.path.join(roi_dir, "LHIP"))
    shutil.copyfile(os.path.join(roi_dir, "HIP", "L_HIP.nii"), 
                    os.path.join(roi_dir, "LHIP", "L_HIP.nii"))
    shutil.copyfile(os.path.join(r'..\setup\screen\db_reg\config.json'), os.path.join(subCfgDir, 'config_dbrg.json'))
    shutil.copyfile(os.path.join(r'..\setup\screen\rest\config.json'), os.path.join(subCfgDir, 'config_rest.json'))

    print('--------------------------')
    print('setting: %s' % subjectDir.split('\\')[-1])
    settings.setValue('SubjectID', subjectDir.split('\\')[-1])
    settings.setValue('FirstFileNameTxt', '_.dcm')
    settings.setValue('FirstFileName', '_.dcm')
    settings.setValue('StimulationProtocol', jsonPath)
    settings.setValue('WatchFolder', watchFolder)
    settings.setValue('WorkFolder', workFolder)
    settings.setValue('RoiFilesFolder', roiFolder)
    settings.setValue('MCTempl', motionPath)
    settings.setValue('StructBgFile', t1Path)
    settings.setValue('NrOfSlices', slices)
    settings.setValue('MatrixSizeX', matrix[0])
    settings.setValue('MatrixSizeY', matrix[1])
    settings.setValue('TR', TR)
    settings.setValue('NrOfVolumes', nrOfVolumes + int(settings.value('nrSkipVol')))
    settings.setValue('NegFeedback', 'true')
    print('----------DONE------------')


if __name__ == '__main__':
    run()
