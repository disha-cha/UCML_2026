read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/lseu.mps"
write problem temp/lseu.mps.ppm
presolve
write transproblem temp/lseu.mps_trans.ppm
read temp/lseu.mps_trans.ppm
optimize
read temp/lseu.mps.ppm
optimize
validatesolve "1120" "1120"
quit
