read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/vpm2.fzn"
write problem temp/vpm2.fzn.mps
presolve
write transproblem temp/vpm2.fzn_trans.mps
read temp/vpm2.fzn_trans.mps
optimize
read temp/vpm2.fzn.mps
optimize
validatesolve "13.75" "13.75"
quit
