read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/enigma.mps"
write problem temp/enigma.mps.pip
presolve
write transproblem temp/enigma.mps_trans.pip
read temp/enigma.mps_trans.pip
optimize
read temp/enigma.mps.pip
optimize
validatesolve "0" "0"
quit
