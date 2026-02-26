read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/gt2.mps"
write problem temp/gt2.mps.ppm
presolve
write transproblem temp/gt2.mps_trans.ppm
read temp/gt2.mps_trans.ppm
optimize
read temp/gt2.mps.ppm
optimize
validatesolve "21166" "21166"
quit
