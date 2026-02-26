read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/vpm2.fzn"
write problem temp/vpm2.fzn.pip
presolve
write transproblem temp/vpm2.fzn_trans.pip
read temp/vpm2.fzn_trans.pip
optimize
read temp/vpm2.fzn.pip
optimize
validatesolve "13.75" "13.75"
quit
