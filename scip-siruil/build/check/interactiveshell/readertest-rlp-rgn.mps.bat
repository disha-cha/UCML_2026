read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/rgn.mps"
write problem temp/rgn.mps.rlp
presolve
write transproblem temp/rgn.mps_trans.rlp
read temp/rgn.mps_trans.rlp
optimize
read temp/rgn.mps.rlp
optimize
validatesolve "82.1999974" "82.1999974"
quit
