read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/enigma.mps"
write problem temp/enigma.mps.gms
presolve
write transproblem temp/enigma.mps_trans.gms
read temp/enigma.mps_trans.gms
optimize
read temp/enigma.mps.gms
optimize
validatesolve "0" "0"
quit
