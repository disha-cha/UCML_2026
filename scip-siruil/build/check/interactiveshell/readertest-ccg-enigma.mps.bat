read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/enigma.mps"
write problem temp/enigma.mps.ccg
presolve
write transproblem temp/enigma.mps_trans.ccg
read temp/enigma.mps_trans.ccg
optimize
read temp/enigma.mps.ccg
optimize
validatesolve "0" "0"
quit
