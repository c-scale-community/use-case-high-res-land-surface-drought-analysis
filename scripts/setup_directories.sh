
project_home=/project/lsda

mkdir -p -m775 $project_home/{Data/{forcing/{converted,downloaded},model_input,model_output,logs},Public,Software,Share/home}

# Git CLONE to $project_home/Software
# Clone to GitHub folder, in order to copy correct files (with project_home) in the Software folder
git clone https://github.com/c-scale-community/use-case-high-res-land-surface-drought-analysis.git $project_home/Software/GitHub

# Copy contents from GitHub folder to Software folder
cp -a $project_home/Software/GitHub/. $project_home/Software

# Replace project home in scripts with real project home
# sed -i "s|^project_home=to_be_modified|project_home=$project_home|" "$project_home/Software/scripts/prepare.sh"
# sed -i "s|^project_home=to_be_modified|project_home=$project_home|" "$project_home/Software/scripts/wflow_catchup.sh"
# sed -i "s|^project_home=to_be_modified|project_home=$project_home|" "$project_home/Software/scripts/wflow_batch.sh"
# sed -i "s|^project_home=to_be_modified|project_home=$project_home|" "$project_home/Software/scripts/plotting.sh"
sed -i "s|^project_home=to_be_modified|project_home=$project_home|" "$project_home/Software/scripts/workflow.sh"

### ADD WFLOW IMAGE

### BUILD PYTHON IMAGE

### ADD CDSKEY FILE IN $project_home/Share/home/.cdsapirc