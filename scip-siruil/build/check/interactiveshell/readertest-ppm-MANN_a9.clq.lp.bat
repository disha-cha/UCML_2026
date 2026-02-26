read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/MANN_a9.clq.lp"
write problem temp/MANN_a9.clq.lp.ppm
presolve
write transproblem temp/MANN_a9.clq.lp_trans.ppm
read temp/MANN_a9.clq.lp_trans.ppm
optimize
read temp/MANN_a9.clq.lp.ppm
optimize
validatesolve "16" "16"
quit
