read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/MANN_a9.clq.lp"
write problem temp/MANN_a9.clq.lp.ccg
presolve
write transproblem temp/MANN_a9.clq.lp_trans.ccg
read temp/MANN_a9.clq.lp_trans.ccg
optimize
read temp/MANN_a9.clq.lp.ccg
optimize
validatesolve "16" "16"
quit
