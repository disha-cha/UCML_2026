read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/rgn.mps"
write problem temp/rgn.mps.pbm
presolve
write transproblem temp/rgn.mps_trans.pbm
read temp/rgn.mps_trans.pbm
optimize
read temp/rgn.mps.pbm
optimize
validatesolve "82.1999974" "82.1999974"
quit
