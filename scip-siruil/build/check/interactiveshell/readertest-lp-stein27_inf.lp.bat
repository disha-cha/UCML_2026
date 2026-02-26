read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/stein27_inf.lp"
write problem temp/stein27_inf.lp.lp
presolve
write transproblem temp/stein27_inf.lp_trans.lp
read temp/stein27_inf.lp_trans.lp
optimize
read temp/stein27_inf.lp.lp
optimize
validatesolve "+infinity" "+infinity"
quit
