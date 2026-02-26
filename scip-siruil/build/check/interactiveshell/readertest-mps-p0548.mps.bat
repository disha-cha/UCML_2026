read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/p0548.mps"
write problem temp/p0548.mps.mps
presolve
write transproblem temp/p0548.mps_trans.mps
read temp/p0548.mps_trans.mps
optimize
read temp/p0548.mps.mps
optimize
validatesolve "8691" "8691"
quit
