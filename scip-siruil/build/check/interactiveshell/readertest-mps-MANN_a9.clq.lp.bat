read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/MANN_a9.clq.lp"
write problem temp/MANN_a9.clq.lp.mps
presolve
write transproblem temp/MANN_a9.clq.lp_trans.mps
read temp/MANN_a9.clq.lp_trans.mps
optimize
read temp/MANN_a9.clq.lp.mps
optimize
validatesolve "16" "16"
quit
