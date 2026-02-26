read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/egout.mps"
write problem temp/egout.mps.pip
presolve
write transproblem temp/egout.mps_trans.pip
read temp/egout.mps_trans.pip
optimize
read temp/egout.mps.pip
optimize
validatesolve "568.1007" "568.1007"
quit
