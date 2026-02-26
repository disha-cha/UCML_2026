read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/enigma.mps"
write problem temp/enigma.mps.pbm
presolve
write transproblem temp/enigma.mps_trans.pbm
read temp/enigma.mps_trans.pbm
optimize
read temp/enigma.mps.pbm
optimize
validatesolve "0" "0"
quit
