read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/egout.mps"
write problem temp/egout.mps.ppm
presolve
write transproblem temp/egout.mps_trans.ppm
read temp/egout.mps_trans.ppm
optimize
read temp/egout.mps.ppm
optimize
validatesolve "568.1007" "568.1007"
quit
