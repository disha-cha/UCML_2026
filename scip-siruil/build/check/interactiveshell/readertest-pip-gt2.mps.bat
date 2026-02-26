read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/gt2.mps"
write problem temp/gt2.mps.pip
presolve
write transproblem temp/gt2.mps_trans.pip
read temp/gt2.mps_trans.pip
optimize
read temp/gt2.mps.pip
optimize
validatesolve "21166" "21166"
quit
