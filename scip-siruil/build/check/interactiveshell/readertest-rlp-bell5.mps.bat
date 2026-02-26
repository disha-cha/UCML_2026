read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/bell5.mps"
write problem temp/bell5.mps.rlp
presolve
write transproblem temp/bell5.mps_trans.rlp
read temp/bell5.mps_trans.rlp
optimize
read temp/bell5.mps.rlp
optimize
validatesolve "8966406.49" "8966406.49"
quit
