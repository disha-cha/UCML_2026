read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/MANN_a9.clq.lp"
write problem temp/MANN_a9.clq.lp.pip
presolve
write transproblem temp/MANN_a9.clq.lp_trans.pip
read temp/MANN_a9.clq.lp_trans.pip
optimize
read temp/MANN_a9.clq.lp.pip
optimize
validatesolve "16" "16"
quit
