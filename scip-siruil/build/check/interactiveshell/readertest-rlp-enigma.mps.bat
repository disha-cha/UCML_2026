read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/enigma.mps"
write problem temp/enigma.mps.rlp
presolve
write transproblem temp/enigma.mps_trans.rlp
read temp/enigma.mps_trans.rlp
optimize
read temp/enigma.mps.rlp
optimize
validatesolve "0" "0"
quit
