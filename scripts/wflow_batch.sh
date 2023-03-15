#!/bin/bash
#
#SBATCH --job-name=wflow-batch
#
#SBATCH -N 1
#SBATCH -c 1
#SBATCH -t 48:00:00
#SBATCH -p normal
#
#SBATCH --array=0-50
#
#SBTACH --ntasks-per-node=1

# Usage wflow_batch <start_forecast> <start_input>
# start_forecast start time of the forecast in YYYY_MM format
# start_input start time of the data in YYYY_MM format

project_home=to_be_modified
# project_home=/project/hrlsa
image=$project_home/Software/images/wflow_063.sif

output_dir=$project_home/Data/model_output/run_SEAS5_ens${SLURM_ARRAY_TASK_ID}_$1
input_dir=$project_home/Data/model_output/run_ERA5_$2

c_fname="forcing/converted"
forcing_name=$(ls $project_home/Data/$c_fname | grep forcing_SEAS5_ens${SLURM_ARRAY_TASK_ID}_`echo $1 | sed 's/_/-/g'`)

# create output dir if not exists
mkdir -p -m770 $output_dir

# Run Wflow
srun --nodes 1 --ntasks 1 singularity exec \
	--bind $project_home/Data:/data \
	--bind $input_dir:/tempdata/input \
        --bind $output_dir:/tempdata/output \
        --bind $project_home/Data/$c_fname/$forcing_name:/tempdata/forcing/forcing.nc \
       	--pwd /data \
       	$image \
	/opt/wflow_cli/bin/wflow_cli /data/model_input/wflow_sbm_static.toml
	# --output_dir "/data/model_output/run_SEAS5_ens${SLURM_ARRAY_TASK_ID}_$1" \
       	# --instates_filename "/data/model_output/run_ERA5_$2" \
	# --forcing_filename "/data/${c_fname}/$(ls ${project_home}/Data/${c_fname} | grep forcing_SEAS5_ens${SLURM_ARRAY_TASK_ID}_`echo $1 | sed 's/_/-/g'`)"

