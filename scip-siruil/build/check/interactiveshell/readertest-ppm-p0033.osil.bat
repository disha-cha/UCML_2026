read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/p0033.osil"
write problem temp/p0033.osil.ppm
presolve
write transproblem temp/p0033.osil_trans.ppm
read temp/p0033.osil_trans.ppm
optimize
read temp/p0033.osil.ppm
optimize
validatesolve "3089" "3089"
quit
