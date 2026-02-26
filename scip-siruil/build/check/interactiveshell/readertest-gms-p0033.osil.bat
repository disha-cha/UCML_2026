read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/p0033.osil"
write problem temp/p0033.osil.gms
presolve
write transproblem temp/p0033.osil_trans.gms
read temp/p0033.osil_trans.gms
optimize
read temp/p0033.osil.gms
optimize
validatesolve "3089" "3089"
quit
