function nfbSave(indVol)
% Function to clear workspase and save the necessary information.
%
% input:
% indVol - volume(scan) index
% Workspace variables.
%
% output:
% Output is a storage into the neurofeedback run directory.
%__________________________________________________________________________
% Copyright (C) 2016-2019 OpenNFT.org
%
% Written by Yury Koush, Artem Nikonorov

disp('Save...')

P = evalin('base', 'P');
mainLoopData = evalin('base', 'mainLoopData');
rtQA_matlab = evalin('base', 'rtQA_matlab');
rtQA_python = evalin('base', 'rtQA_python');
% evalin('base', 'clear mmImgViewTempl;');
% evalin('base', 'clear mmStatVol;');
% evalin('base', 'clear mmOrthView;');
[isPSC, isDCM, isSVM, isIGLM] = getFlagsType(P);

folder = P.nfbDataFolder;

% save rtqa data
save([folder '\rtQA_matlab.mat'], '-struct', 'rtQA_matlab');
save([folder '\rtQA_python.mat'], '-struct', 'rtQA_python');

% save last volume stat data for offline access
slNrImg2DdimX = mainLoopData.slNrImg2DdimX;
slNrImg2DdimY = mainLoopData.slNrImg2DdimY;
img2DdimX = mainLoopData.img2DdimX;
img2DdimY = mainLoopData.img2DdimY;
dimVol = mainLoopData.dimVol;
tn = mainLoopData.tn;
indVolNorm = mainLoopData.indVolNorm;
indVolNorm = double(indVolNorm);
idxActVoxIGLM = mainLoopData.idxActVoxIGLM{indVolNorm};
statMap3D = mainLoopData.statMap3D;

maskedStatMapVect = tn(idxActVoxIGLM);
maxTval = max(maskedStatMapVect);
if isempty(maxTval)
    maxTval = 1;
end
statMapVect = maskedStatMapVect;
statMap3D(idxActVoxIGLM) = statMapVect;

statMap2D = vol3Dimg2D(statMap3D, slNrImg2DdimX, slNrImg2DdimY, img2DdimX, img2DdimY, dimVol) / maxTval;
statMap2D = statMap2D * 255;

mainLoopData.statMap2D = statMap2D;
mainLoopData.statMap3D = statMap3D;
m = evalin('base', 'mmStatVol');
m.Data.statVol = statMap3D;
assignin('base', 'mainLoopData', mainLoopData);

% save feedback values
if ~P.isRestingState
    save([folder filesep P.SubjectID '_' ...
        num2str(P.NFRunNr) '_NFBs' '.mat'], ...
        '-struct', 'mainLoopData', 'vectNFBs');
end

% save time-series
if P.NrROIs >0
    save([folder filesep P.SubjectID '_' ...
        num2str(P.NFRunNr) '_raw_tsROIs' '.mat'], ...
        '-struct', 'mainLoopData', 'rawTimeSeries');
    save([folder filesep P.SubjectID '_' ...
        num2str(P.NFRunNr) '_proc_tsROIs' '.mat'], ...
        '-struct', 'mainLoopData', 'kalmanProcTimeSeries');
end

% save parameters
save([folder filesep P.SubjectID '_' ...
    num2str(P.NFRunNr) '_mainLoopData' '.mat'],'-struct','mainLoopData');
save([folder filesep P.SubjectID '_' ...
    num2str(P.NFRunNr) '_P' '.mat'], '-struct', 'P');

% save reward values
if strcmp(P.Prot, 'Inter') && strcmp(P.Type, 'PSC')
    % save reward vector for subsequent NF run, i.e. it becomes previous
    if isfield(P, 'actValue')
        prev_actValue = P.actValue;
    else
        prev_actValue = 0;
        fprintf('\nCheck Reward algorithm!\n');
    end;
    save([folder filesep 'reward_' sprintf('%02d',P.NFRunNr) '.mat'], ...
        'prev_actValue');
end

% save activation map(s)
folder = [P.WorkFolder filesep 'NF_Data_' num2str(P.NFRunNr)];
if ~isempty(mainLoopData.statMap3D_iGLM)
    if ~isDCM
        statVolData = mainLoopData.statMap3D_iGLM;
        save([folder filesep 'statVolData_' ...
            sprintf('%02d',P.NFRunNr) '.mat'], 'statVolData');
    else
        for iDcmBlock = 1: size(mainLoopData.statMap3D_iGLM,4)
            statVolData = ...
                squeeze(mainLoopData.statMap3D_iGLM(:,:,:, iDcmBlock));
            save([folder filesep 'statVolData_' ...
                sprintf('%02d',iDcmBlock) '.mat'],'statVolData');
        end
    end
end

% save ROIs
if isPSC || isSVM
    roiData.ROIs = evalin('base', 'ROIs');
end
if isDCM
    roiData.ROIsAnat = evalin('base', 'ROIsAnat');
    roiData.ROIsGroup = evalin('base', 'ROIsGroup');
    roiData.ROIsGlmAnat = evalin('base', 'ROIsGlmAnat');
    roiData.ROIoptimGlmAnat = evalin('base', 'ROIoptimGlmAnat');
end
if ~P.isRestingState
    save([folder filesep P.SubjectID '_' ...
        num2str(P.NFRunNr) '_roiData' '.mat'], 'roiData');
end

% concatenate two TimeVector event files
fileTimeVectors_display = [folder filesep 'TimeVectors_display_' ...
    sprintf('%02d', P.NFRunNr) '.txt'];

if ~isSVM && exist(fileTimeVectors_display, 'file')
    recs = load([folder filesep 'TimeVectors_' ...
        sprintf('%02d', P.NFRunNr) '.txt']);
    recsDisplay = load(fileTimeVectors_display);
    sz = size(recs);
    % Times.t9 and Times.t10
    tmpVect = 1:size(recsDisplay,1);
    recs(tmpVect, 10:11) = recsDisplay(:,1:2);
    % Abs Matlab PTB Helper times for display
    recs(tmpVect, sz(2)+1:sz(2)+2) = recsDisplay(:,3:4);
    save([folder filesep 'TimeVectors_' ...
        sprintf('%02d', P.NFRunNr) '.txt'], 'recs', '-ascii', '-double');
end

disp('Saving done')


