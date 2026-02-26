read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/rgn.mps"
write problem temp/rgn.mps.ppm
presolve
write transproblem temp/rgn.mps_trans.ppm
read temp/rgn.mps_trans.ppm
optimize
read temp/rgn.mps.ppm
optimize
validatesolve "82.1999974" "82.1999974"
quit
