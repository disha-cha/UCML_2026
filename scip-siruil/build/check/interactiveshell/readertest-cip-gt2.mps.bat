read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/gt2.mps"
write problem temp/gt2.mps.cip
presolve
write transproblem temp/gt2.mps_trans.cip
read temp/gt2.mps_trans.cip
optimize
read temp/gt2.mps.cip
optimize
validatesolve "21166" "21166"
quit
