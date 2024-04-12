function makeROI(func,anat,roi)
    patharr = strsplit(anat,'\\');
    anatDir =char(join(patharr(1:end-1),'\\'));
    anatName = char(patharr(end));
    if ~exist([anatDir,'\\',strcat('r',anatName)],'file')
        coreg(func,anat);
    end
    if ~exist([anatDir,'\\',strcat('iy_r',anatName)],'file')
        seg([anatDir,'\\',strcat('r',anatName)]);
    end
    norml([anatDir,'\\',strcat('iy_r',anatName)],roi,[2.5,2.5,2.5]);
