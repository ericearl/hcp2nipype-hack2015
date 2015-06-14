# HCP FREESURFER PIPELINE WRAPPING PART 1
#
# This takes the first portion of the HCP Freesurfer preprocessing pipeline
# wraps it into nipype nodes
# this is incomplete!
#
# OHBM HACKATHON PROJECT
# this code is by marianne reddan (so blame her becaus she doesn't know py syntax)
# www.appliedmarianne.com
#####

#####
## TO DO: 	confirm bash to py var passing is working
##			get dev access to freesurfer  https://surfer.nmr.mgh.harvard.edu/fswiki/ReadOnlyCVS
##			then build missing interfaces!!
#####


### setting up and running the node
# import FreeSurfer
import os
import nipype.pipeline.engine as pe
import nipype.interfaces.io as nio
import nipype.interfaces.utility as ut
from nipype.interfaces.freesurfer.preprocess import ReconAll
from nipype.interfaces.utility import Rename
import nipype.interfaces.freesurfer.preprocess as fs  
import sys
#from nipype.interfaces.freesurfer.utils import MakeAverageSubject

# Variable translation from bash to py
#$SubjectID = subID
subID = sys.argv[1]
#$SubjectDIR = subDIR
subDIR = sys.argv[2]
#$T1wImageFile = T1w
T1w = sys.argv[3]


##### NODE 1: RECON_ALL STEP 1
# HCP line:
#		recon-all -i "$T1wImageFile"_1mm.nii.gz -subjid $SubjectID -sd $SubjectDIR -motioncor -talairach -nuintensitycor -normalization
recon_pre = pe.Node(interface=fs.ReconAll(),
                    name='FreeSurf_Recon_Part1')
# INFORMATION: Recon-all performs cortical reconstruction of an anatomical mri
# -i 			specifies input image
#				"$T1wImageFile"_1mm.nii.gz
#				this is run  with PreFreeSurfer masked data, because HCP people thing it is ureliable to use phase II data
# -subjid 		give it the subj id variable#
#				$SubjectID 
# -sd 			give it the subj dir
#				$SubjectDIR 
# -motioncor 	When there are multiple source volumes, this step will correct for small motions between them and then average them together. 
#				The input are the volumes found in file(s) mri/orig/XXX.mgz. The output will be the volume mri/orig.mgz. If no runs are found, then it 
#				looks for a volume in mri/orig (or mri/orig.mgz). If that volume is there, then it is used in subsequent processes 
#				as if it was the motion corrected volume. If no volume is found, then the process exits with errors.
# -talairach 	This computes the affine transform from the orig volume to the MNI305 atlas using the MINC program mritotal (see Collins, et al, 1994) 
#				through a FreeSurfer script called talairach. Several of the downstream programs use talairach coordinates as seed points. You can/should 
#				check how good the talairach registration is using tkregister2 --s subjid --fstal. tkregister2 allows you to compare the orig volume against 
#				the talairach volume resampled into the orig space. Run "tkregister2 --help" for more information. Creates the files mri/transform/talairach.auto.xfm 
#				and talairach.xfm.
# -nuintensitycor Non-parametric Non-uniform intensity Normalization (N3), corrects for intensity non-uniformity in MR data, making relatively few assumptions about 
#				the data. This runs the MINC tool 'nu_correct'. By default, four iterations of nu_correct are run. The flag -nuiterations specification of 
#				some other number of iterations.
# -Normalization Performs intensity normalization of the orig volume and places the result in mri/T1.mgz. Attempts to correct for fluctuations in intensity 
#				that would otherwise make intensity-based segmentation much more difficult. Intensities for all voxels are scaled so 
#				that the mean intensity of the white matter is 110. If there are problems with the normalization, users can add control points. 
recon_pre.inputs.subject_id = subID
#recon_pre.inputs.directive = 'all'
recon_pre.inputs.subjects_dir = subDIR
recon_pre.inputs.T1_files = T1w + '_1mm.nii.gz' #FIX SYNTAX, pass the var in a string
recon_pre.inputs.flags = '-motioncor -talairach -nuintensitycor -normalization'

##### NODE 2: MRI_CONVERT
# HCP line:
#	mri_convert "$T1wImageBrainFile"_1mm.nii.gz "$SubjectDIR"/"$SubjectID"/mri/brainmask.mgz --conform
# INFORMATION:
#	mri_convert is a general purpose utility for converting between different file formats
mc = pe.Node(interface=fs.MRIConvert(),
                    name='Convert_nii2mgz')
mc.inputs.in_file =  T1w + '_1mm.nii.gz'
mc.inputs.out_file = subID + '/' + subDIR + '/' + 'mri/brainmask.mgz' #FIX SYNTAX
mc.inputs.out_type = 'mgz'

##### NODE 3: MRI_EM_REGISTER
# HCP line:
#	mri_em_register -mask "$SubjectDIR"/"$SubjectID"/mri/brainmask.mgz "$SubjectDIR"/"$SubjectID"/mri/nu.mgz $FREESURFER_HOME/average/RB_all_2008-03-26.gca "$SubjectDIR"/"$SubjectID"/mri/transforms/talairach_with_skull.lta
# INFORMATION:
#	creates a transform in lta format
#	for more: https://surfer.nmr.mgh.harvard.edu/fswiki/mri_em_register

##### NODE 4: SKULL STRIPPING
# HCP line:
#	mri_watershed -T1 -brain_atlas $FREESURFER_HOME/average/RB_all_withskull_2008-03-26.gca "$SubjectDIR"/"$SubjectID"/mri/transforms/talairach_with_skull.lta "$SubjectDIR"/"$SubjectID"/mri/T1.mgz "$SubjectDIR"/"$SubjectID"/mri/brainmask.auto.mgz 
# INFORMATION:
#	strip skull and other outer non-brain tissue
#	for more: https://surfer.nmr.mgh.harvard.edu/fswiki/mri_watershed

##### NODE 5: MAKE COPY FOR A RENAME
# HCP line:
#	cp "$SubjectDIR"/"$SubjectID"/mri/brainmask.auto.mgz "$SubjectDIR"/"$SubjectID"/mri/brainmask.mgz 
# INFORMATION:
#	copies image to new name
#	for more: http://nipy.sourceforge.net/nipype/interfaces/generated/nipype.interfaces.utility.html
rename1 = = pe.Node(interface=ut.Rename(),
                    name='RenameBrainMask')
rename1.inputs.in_file = subDIR + '/' + subID + '/mri/brainmask.auto.mgz' #FIX SYNTAX
rename1.inputs.format_string = subDIR + '/' + subID '/' + 'mri/brainmask.mgz' #FIX SYNTAX
# test it
res = rename1.run()          
print res.outputs.out_file     

##### NODE 6: RECON PART II
# HCP line:
#	recon-all -subjid $SubjectID -sd $SubjectDIR -autorecon2 -nosmooth2 -noinflate2 -nocurvstats -nosegstats -openmp 8
recon_post = pe.Node(interface=fs.ReconAll(),
                    name='FreeSurf_Recon_Part1')
# INFORMATION: Recon-all performs cortical reconstruction of an anatomical mri
# -autorecon2 	process steps 6-23
#				after autorecon2, check final surfaces:
#				a. if wm edit was required, then run -autorecon2-wm
#				b. if control points added, then run -autorecon2-cp
#				c. if edits made to correct pial, then run -autorecon2-pial
#				d. proceed to run -autorecon3
# -nosmooth2 	After tesselation, the orig surface is very jagged because each triangle is on the edge of a voxel 
#				face and so are at right angles to each other. The vertex positions are adjusted slightly here to reduce 
#				the angle. This is only necessary for the inflation processes. Creates surf/?h.smoothwm(.nofix). Calls 
#				mris_smooth. Smooth1 is the step just after tessellation, and smooth2 is the step just after topology fixing.
# -noinflate2 	Inflation of the surf/?h.smoothwm(.nofix) surface to create surf/?h.inflated. The inflation attempts to minimize 
#				metric distortion so that distances and areas are perserved (ie, the surface is not stretched). In this sense, 
#				it is like inflating a paper bag and not a balloon. Inflate1 is the step just after tessellation, and inflate2 is 
#				the step just after topology fixing. Calls mris_inflate. Creates ?h.inflated, ?h.sulc, ?h.curv, and ?h.area.
# -nocurvstats 	?? can't find documentation
# -nosegstats 	Computes statistics on the segmented subcortical structures found in mri/aseg.mgz. Writes output to file stats/aseg.stats.
# -openmp 8		?? can't find documentation	
recon_post.inputs.subject_id = subID
recon_post.inputs.subjects_dir = subDIR
recon_post.inputs.flags = '-autorecon2 -nosmooth2 -noinflate2 -nocurvstats -nosegstats -openmp 8'
