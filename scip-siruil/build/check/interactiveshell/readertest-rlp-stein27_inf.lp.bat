read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/stein27_inf.lp"
write problem temp/stein27_inf.lp.rlp
presolve
write transproblem temp/stein27_inf.lp_trans.rlp
read temp/stein27_inf.lp_trans.rlp
optimize
read temp/stein27_inf.lp.rlp
optimize
validatesolve "+infinity" "+infinity"
quit
