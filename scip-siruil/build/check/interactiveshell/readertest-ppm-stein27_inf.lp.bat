read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/stein27_inf.lp"
write problem temp/stein27_inf.lp.ppm
presolve
write transproblem temp/stein27_inf.lp_trans.ppm
read temp/stein27_inf.lp_trans.ppm
optimize
read temp/stein27_inf.lp.ppm
optimize
validatesolve "+infinity" "+infinity"
quit
