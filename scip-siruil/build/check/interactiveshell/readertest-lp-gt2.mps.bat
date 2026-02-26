read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/gt2.mps"
write problem temp/gt2.mps.lp
presolve
write transproblem temp/gt2.mps_trans.lp
read temp/gt2.mps_trans.lp
optimize
read temp/gt2.mps.lp
optimize
validatesolve "21166" "21166"
quit
