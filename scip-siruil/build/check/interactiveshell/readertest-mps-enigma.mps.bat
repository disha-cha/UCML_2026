read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/enigma.mps"
write problem temp/enigma.mps.mps
presolve
write transproblem temp/enigma.mps_trans.mps
read temp/enigma.mps_trans.mps
optimize
read temp/enigma.mps.mps
optimize
validatesolve "0" "0"
quit
