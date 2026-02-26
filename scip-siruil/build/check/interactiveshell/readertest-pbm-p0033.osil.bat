read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/p0033.osil"
write problem temp/p0033.osil.pbm
presolve
write transproblem temp/p0033.osil_trans.pbm
read temp/p0033.osil_trans.pbm
optimize
read temp/p0033.osil.pbm
optimize
validatesolve "3089" "3089"
quit
