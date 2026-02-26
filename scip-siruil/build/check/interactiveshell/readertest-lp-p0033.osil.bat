read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/p0033.osil"
write problem temp/p0033.osil.lp
presolve
write transproblem temp/p0033.osil_trans.lp
read temp/p0033.osil_trans.lp
optimize
read temp/p0033.osil.lp
optimize
validatesolve "3089" "3089"
quit
