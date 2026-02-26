read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/MANN_a9.clq.lp"
write problem temp/MANN_a9.clq.lp.rlp
presolve
write transproblem temp/MANN_a9.clq.lp_trans.rlp
read temp/MANN_a9.clq.lp_trans.rlp
optimize
read temp/MANN_a9.clq.lp.rlp
optimize
validatesolve "16" "16"
quit
