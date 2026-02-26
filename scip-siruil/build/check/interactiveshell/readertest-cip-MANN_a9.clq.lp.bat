read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/MANN_a9.clq.lp"
write problem temp/MANN_a9.clq.lp.cip
presolve
write transproblem temp/MANN_a9.clq.lp_trans.cip
read temp/MANN_a9.clq.lp_trans.cip
optimize
read temp/MANN_a9.clq.lp.cip
optimize
validatesolve "16" "16"
quit
