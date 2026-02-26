read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/lseu.mps"
write problem temp/lseu.mps.rlp
presolve
write transproblem temp/lseu.mps_trans.rlp
read temp/lseu.mps_trans.rlp
optimize
read temp/lseu.mps.rlp
optimize
validatesolve "1120" "1120"
quit
