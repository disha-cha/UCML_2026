read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/enigma.mps"
write problem temp/enigma.mps.ppm
presolve
write transproblem temp/enigma.mps_trans.ppm
read temp/enigma.mps_trans.ppm
optimize
read temp/enigma.mps.ppm
optimize
validatesolve "0" "0"
quit
