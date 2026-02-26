read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/vpm2.fzn"
write problem temp/vpm2.fzn.ppm
presolve
write transproblem temp/vpm2.fzn_trans.ppm
read temp/vpm2.fzn_trans.ppm
optimize
read temp/vpm2.fzn.ppm
optimize
validatesolve "13.75" "13.75"
quit
