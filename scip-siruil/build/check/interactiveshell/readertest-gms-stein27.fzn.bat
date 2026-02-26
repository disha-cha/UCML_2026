read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/stein27.fzn"
write problem temp/stein27.fzn.gms
presolve
write transproblem temp/stein27.fzn_trans.gms
read temp/stein27.fzn_trans.gms
optimize
read temp/stein27.fzn.gms
optimize
validatesolve "18" "18"
quit
