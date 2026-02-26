read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/flugpl.mps"
write problem temp/flugpl.mps.ppm
presolve
write transproblem temp/flugpl.mps_trans.ppm
read temp/flugpl.mps_trans.ppm
optimize
read temp/flugpl.mps.ppm
optimize
validatesolve "1201500" "1201500"
quit
