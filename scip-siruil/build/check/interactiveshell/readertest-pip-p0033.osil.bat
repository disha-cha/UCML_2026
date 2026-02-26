read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/p0033.osil"
write problem temp/p0033.osil.pip
presolve
write transproblem temp/p0033.osil_trans.pip
read temp/p0033.osil_trans.pip
optimize
read temp/p0033.osil.pip
optimize
validatesolve "3089" "3089"
quit
