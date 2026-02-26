read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/stein27_inf.lp"
write problem temp/stein27_inf.lp.gms
presolve
write transproblem temp/stein27_inf.lp_trans.gms
read temp/stein27_inf.lp_trans.gms
optimize
read temp/stein27_inf.lp.gms
optimize
validatesolve "+infinity" "+infinity"
quit
