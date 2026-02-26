read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/egout.mps"
write problem temp/egout.mps.pbm
presolve
write transproblem temp/egout.mps_trans.pbm
read temp/egout.mps_trans.pbm
optimize
read temp/egout.mps.pbm
optimize
validatesolve "568.1007" "568.1007"
quit
