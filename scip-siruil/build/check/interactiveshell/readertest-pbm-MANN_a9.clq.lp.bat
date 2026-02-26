read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/MANN_a9.clq.lp"
write problem temp/MANN_a9.clq.lp.pbm
presolve
write transproblem temp/MANN_a9.clq.lp_trans.pbm
read temp/MANN_a9.clq.lp_trans.pbm
optimize
read temp/MANN_a9.clq.lp.pbm
optimize
validatesolve "16" "16"
quit
