read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/stein27_inf.lp"
write problem temp/stein27_inf.lp.ccg
presolve
write transproblem temp/stein27_inf.lp_trans.ccg
read temp/stein27_inf.lp_trans.ccg
optimize
read temp/stein27_inf.lp.ccg
optimize
validatesolve "+infinity" "+infinity"
quit
