read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/flugpl.mps"
write problem temp/flugpl.mps.pbm
presolve
write transproblem temp/flugpl.mps_trans.pbm
read temp/flugpl.mps_trans.pbm
optimize
read temp/flugpl.mps.pbm
optimize
validatesolve "1201500" "1201500"
quit
