read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/stein27.fzn"
write problem temp/stein27.fzn.pbm
presolve
write transproblem temp/stein27.fzn_trans.pbm
read temp/stein27.fzn_trans.pbm
optimize
read temp/stein27.fzn.pbm
optimize
validatesolve "18" "18"
quit
