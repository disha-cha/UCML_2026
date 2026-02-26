read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/egout.mps"
write problem temp/egout.mps.cip
presolve
write transproblem temp/egout.mps_trans.cip
read temp/egout.mps_trans.cip
optimize
read temp/egout.mps.cip
optimize
validatesolve "568.1007" "568.1007"
quit
