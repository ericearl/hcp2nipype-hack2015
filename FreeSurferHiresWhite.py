#beginnings of nipype conversion of FreeSurferHiresWhite.sh
#OHBM hackathon 2015
#NK - 6/14/15


SubjectID="100307"
SubjectDIR='100307/'
T1wImage= SubjectDIR + "T1w/T1w.nii.gz" #T1w FreeSurfer Input (Full Resolution)
T2wImage= SubjectDIR + 'T2w/T2w.nii.gz' #T2w FreeSurfer Input (Full Resolution)
#
#export SUBJECTS_DIR="$SubjectDIR"
#
mridir= SubjectDIR + '/' + SubjectID + '/mri'
surfdir= SubjectDIR + '/' + SubjectID + '/surf'
reg = mridir + '/transforms/hires21mm.dat'
regII = mridir + '/transforms/1mm2hires.dat'
#


InputFile = T1wImage

import nipype.pipeline.engine as pe         # the workflow and node wrapper
import nipype.interfaces.fsl as fsl
import nipype.interfaces.freesurfer as freesurfer

wf = pe.Workflow(name='testing')
wf.base_dir = '.'

############
##fslmaths "$T1wImage" -abs -add 1 "$mridir"/T1w_hires.nii.gz
fslmath_Node = pe.Node(interface=fsl.maths.MultiImageMaths(), name='fslmath') 
fslmath_Node.inputs.in_file=InputFile
fslmath_Node.inputs.op_string="-abs -add 1"
fslmath_Node.name = 'fslmath'
fslmath_out_file='T1w_hires.nii.gz'


############ 
##tkregister2 --mov "$mridir"/T1w_hires.nii.gz --targ $mridir/orig.mgz --noedit --regheader --reg $reg
tkregister2_Node = pe.Node(interface=freesurfer.Tkregister2(), name='tkregister2')
#tkregister2_moving_image = 'T1w_hires.nii.gz'
tkregister2_Node.inputs.target_image = 'T1w.nii.gz'
tkregister2_Node.inputs.reg_header   = True
tkregister2_Node.inputs.reg_file     = 'regfile'
tkregister2_Node.inputs.noedit       = True


#connect math and tkregister nodes
wf.add_nodes([fslmath_Node, tkregister2_Node])
wf.connect(fslmath_Node, 'out_file', tkregister2_Node, 'moving_image')
############

#copy files?
## map white and pial to hires coords (pial is only for visualization - won't be used later)
##cp $SubjectDIR/$SubjectID/surf/lh.white $SubjectDIR/$SubjectID/surf/lh.sphere.reg
##cp $SubjectDIR/$SubjectID/surf/rh.white $SubjectDIR/$SubjectID/surf/rh.sphere.reg

############ not yet working, needs nipype adjustment of freesurfer.utils.SurfaceTransform
##mri_surf2surf --s $SubjectID --sval-xyz white --reg $reg "$mridir"/T1w_hires.nii.gz --tval-xyz --tval white.hires --hemi lh
mri_surf2surf_lh_Node = pe.Node(interface=freesurfer.utils.SurfaceTransform(),name='mri_surf2surf-lh')
mri_surf2surf_lh_Node.inputs.subjects_dir= SubjectDIR
mri_surf2surf_lh_Node.inputs.hemi='lh'
mri_surf2surf_lh_Node.inputs.args.tval='white.hires'
mri_surf2surf_lh_Node.inputs.args='--sval-xyz white --tval-xyz'
# Missing part: --reg $reg "$mridir"/T1w_hires.nii.gz'

##mri_surf2surf --s $SubjectID --sval-xyz white --reg $reg "$mridir"/T1w_hires.nii.gz --tval-xyz --tval white.hires --hemi rh
mri_surf2surf_rh_Node = pe.Node(interface=freesurfer.utils.SurfaceTransform(),name='mri_surf2surf-rh')
mri_surf2surf_rh_Node.inputs.subjects_dir= SubjectDIR #Not Sure
mri_surf2surf_rh_Node.inputs.hemi='rh'
mri_surf2surf_rh_Node.inputs.args.tval='white.hires'
mri_surf2surf_rh_Node.inputs.args='--sval-xyz white --tval-xyz'
# Missing part: --reg $reg "$mridir"/T1w_hires.nii.gz’ 

#connect tkregister to left and right surf nodes
#reg needs to be added to nipype as input to SurfaceTransform?
wf.add_nodes([tkregister2_Node, mri_surf2surf_lh_Node]) 
wf.connect(tkregister2_Node, 'reg_file', mri_surf2surf_lh_Node, 'reg')

wf.add_nodes([tkregister2_Node, mri_surf2surf_rh_Node]) 
wf.connect(tkregister2_Node, 'reg_file', mri_surf2surf_rh_Node, 'reg')
############


############ not yet working , 
#mri_convert $mridir/aseg.hires.mgz $mridir/aseg.hires.nii.gz
mri_convert_Node = pe.Node(interface=freesurfer.MRIsConvert(),name='mri_convert')
mri_convert_Node.inputs.rescale=True
#mri_convert_Node.inputs.label_file='T1w_hires.nii.gz'
mri_convert_Node.inputs.args='-rt nearest $mridir/$v $mridir/$basename.hires.mgz'

wf.add_nodes([mri_surf2surf_rh_Node, mri_convert_Node])
wf.connect(mri_surf2surf_rh_Node, 'out_file', mri_surf2surf_rh_Node, 'reg')

#
# ends around line 51 of FreeSurferHiresWhite.sh
#

