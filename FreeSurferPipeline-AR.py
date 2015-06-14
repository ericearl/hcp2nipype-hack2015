
# # HCP preprocessing pipeline
# 
# Product of 2015 OHBM hackathon
#
# nipype conversion of FreeSurfer/FreeSurferPipeline.sh
#
# Andrew Reinenberg
#

# ## Load modules:

# In[1]:

from nipype.interfaces import fsl
import nipype.interfaces.io as nio           # Data i/o
import nipype.interfaces.utility as util     # utility
import nipype.pipeline.engine as pe
from nipype.interfaces.base import BaseInterface, TraitedSpec, File, traits
import os
import sys
import nibabel as nib
#from IPython.display import Image
import glob
import numpy as np


# In[2]:
# need fsl path, virtalmachine's path set here
FSLDIR = '/usr/share/fsl/5.0'#!echo $FSLDIR #'/usr/local/fsl' #!echo $FSLDIR
fsl.FSLCommand.set_default_output_type('NIFTI')


# ## Create Nodes & Workflow:

# In[12]:

wflow = pe.Workflow(name='hcp_preprocess_freesurfer')

# May also need: 'subjectid', 'subjetdir', 't2wimage'
input_node = pe.Node(util.IdentityInterface(fields=['t1wimage',
                                                    't1wimagebrain']),
                     name='input_node')

# 1. Mean=`fslstats $T1wImageBrain -M`
# outputs = 'mean_stat'
meaner_node = pe.Node(fsl.utils.ImageStats(),
                      name='get_mean')

# 2. flirt -interp spline -in "$T1wImage" -ref "$T1wImage" -applyisoxfm 1 -out "$T1wImageFile"_1mm.nii.gz
flirt_node = pe.Node(fsl.FLIRT(apply_isoxfm = 1),
                     name='flirt')

# 3. applywarp --rel --interp=spline -i "$T1wImage" -r "$T1wImageFile"_1mm.nii.gz --premat=$FSLDIR/etc/flirtsch/ident.mat -o "$T1wImageFile"_1mm.nii.gz
applywarp_spline_node = pe.Node(fsl.ApplyWarp(relwarp=True,
                                              interp = 'spline',
                                              premat = FSLDIR + '/etc/flirtsch/ident.mat'),
                                name='warp_spline')

# 4. applywarp --rel --interp=nn -i "$T1wImageBrain" -r "$T1wImageFile"_1mm.nii.gz --premat=$FSLDIR/etc/flirtsch/ident.mat -o "$T1wImageBrainFile"_1mm.nii.gz
applywarp_nn_node = pe.Node(fsl.ApplyWarp(relwarp = True,
                                          interp = 'nn',
                                          premat = FSLDIR + '/etc/flirtsch/ident.mat'
                                         ),
                            name='warp_nn')

# 5. fslmaths "$T1wImageFile"_1mm.nii.gz -div $Mean -mul 150 -abs "$T1wImageFile"_1mm.nii.gz
fslmaths_node = pe.Node(fsl.MultiImageMaths(op_string = '-div %s -mul 150 -abs',
                                            operand_files = meaner_node.outputs.out_stat
                                            ),
                        name='fslmaths')

## Marianne's portion of the conversion
# # 6. recon-all -i "$T1wImageFile"_1mm.nii.gz -subjid $SubjectID -sd $SubjectDIR -motioncor -talairach -nuintensitycor -normalization
# reconall_1_node = pe.Node(interface=fs.ReconAll(inputs),
#                           name='FreeSurf_Recon_Part1')
# recon_pre.inputs.subject_id = '$SubjectID'
# #recon_pre.inputs.directive = 'all'
# recon_pre.inputs.subjects_dir = '$SubjectDIR'
# recon_pre.inputs.T1_files = '"$T1wImageFile"_1mm.nii.gz'
# recon_pre.inputs.flags = '-motioncor -talairach -nuintensitycor -normalization'

# # 7. mri_convert "$T1wImageBrainFile"_1mm.nii.gz "$SubjectDIR"/"$SubjectID"/mri/brainmask.mgz --conform
# nifti_to_mgz_node = pe.Node(interface=fs.MRIConvert(),
#                     name='Convert_nii2mgz')
# mc.inputs.in_file = '"$T1wImageBrainFile"_1mm.nii.gz'
# mc.inputs.out_file = '"$SubjectDIR"/"$SubjectID"/mri/brainmask.mgz'
# mc.inputs.out_type = 'mgz'

# # 8. mri_em_register -mask "$SubjectDIR"/"$SubjectID"/mri/brainmask.mgz "$SubjectDIR"/"$SubjectID"/mri/nu.mgz $FREESURFER_HOME/average/RB_all_2008-03-26.gca "$SubjectDIR"/"$SubjectID"/mri/transforms/talairach_with_skull.lta
# # transform_to_lta_node = pe.Node()

# # 9. mri_watershed -T1 -brain_atlas $FREESURFER_HOME/average/RB_all_withskull_2008-03-26.gca "$SubjectDIR"/"$SubjectID"/mri/transforms/talairach_with_skull.lta "$SubjectDIR"/"$SubjectID"/mri/T1.mgz "$SubjectDIR"/"$SubjectID"/mri/brainmask.auto.mgz 
# # mri_watershed_node = pe.Node()

# # 10. cp "$SubjectDIR"/"$SubjectID"/mri/brainmask.auto.mgz "$SubjectDIR"/"$SubjectID"/mri/brainmask.mgz 
# rename1 = = pe.Node(interface=ut.Rename(),
#                     name='RenameBrainMask')
# rename1.inputs.in_file = ""$SubjectDIR"/"$SubjectID"/mri/brainmask.auto.mgz"
# rename1.inputs.format_string = ""$SubjectDIR"/"$SubjectID"/mri/brainmask.mgz"
# # test it
# res = rename1.run()          
# print res.outputs.out_file

# # 11. recon-all -subjid $SubjectID -sd $SubjectDIR -autorecon2 -nosmooth2 -noinflate2 -nocurvstats -nosegstats -openmp 8
# # reconall_2_node = pe.Node()
# recon_post = pe.Node(interface=fs.ReconAll(),
#                     name='FreeSurf_Recon_Part1')
# recon_post.inputs.subject_id = '$SubjectID'
# recon_post.inputs.subjects_dir = '$SubjectDIR'
# recon_post.inputs.flags = '-autorecon2 -nosmooth2 -noinflate2 -nocurvstats -nosegstats -openmp 8'

# Output:
# outputspec = pe.Node(util.IdentityInterface(fields=['subject',
#                                                     'regressors']),
#                      name='outputspec')


# In[13]:

# Connect pieces of workflow
wflow.connect(input_node, 't1wimage',
              meaner_node, 'in_file')
wflow.connect(input_node, 't1wimage',
              flirt_node, 'in_file')
wflow.connect(input_node, 't1wimage',
              flirt_node, 'reference')
# wflow.connect(meaner_node, 'mean_stat',
#               fslmaths_node, 'Mean')
wflow.connect(input_node, 't1wimage',
              applywarp_spline_node, 'in_file')
wflow.connect(flirt_node, 'out_file',
              applywarp_spline_node, 'ref_file')
wflow.connect(input_node, 't1wimagebrain',
              applywarp_nn_node, 'in_file')
wflow.connect(flirt_node, 'out_file',
              applywarp_nn_node, 'ref_file')
wflow.connect(flirt_node, 'out_file',
              fslmaths_node, 'in_file')

# inputs
wflow.base_dir = '.'
input_node.inputs.t1wimage='T1w/T1w_acpc_dc_restore.nii.gz' #T1w FreeSurfer Input (Full Resolution)
input_node.inputs.t1wimagebrain='T1w/T1w_acpc_dc_restore_brain.nii.gz' #T1w FreeSurfer Input (Full Resolution)
meaner_node.inputs.op_string = '-M'
meaner_node.inputs.terminal_output = 'none'                               
# flirt_node.inputs.output_type


# In[18]:

wflow.write_graph("workflow_graph.dot")
# Image(filename="./hcp_preprocess_freesurfer/workflow_graph.dot.png")


# In[16]:

# wf.run(plugin='MultiProc', plugin_args={'n_procs' : 2})
wflow.run()

