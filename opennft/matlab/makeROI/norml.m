function norml(def,res,vox)
%-----------------------------------------------------------------------
% Job saved on 09-Mar-2023 15:43:19 by cfg_util (rev $Rev: 7345 $)
% spm SPM - SPM12 (7771)
% cfg_basicio BasicIO - Unknown
%-----------------------------------------------------------------------
matlabbatch{1}.spm.spatial.normalise.write.subj.def = {def};
matlabbatch{1}.spm.spatial.normalise.write.subj.resample = {strcat(res,',1')};
matlabbatch{1}.spm.spatial.normalise.write.woptions.bb = [NaN NaN NaN; NaN NaN NaN];
matlabbatch{1}.spm.spatial.normalise.write.woptions.vox = vox;
matlabbatch{1}.spm.spatial.normalise.write.woptions.interp = 0;
matlabbatch{1}.spm.spatial.normalise.write.woptions.prefix = 'w';
spm('defaults', 'FMRI');
spm_jobman('run', matlabbatch);