read /home/disha/UCML_2026/scip-siruil/check/instances/MIP/stein27.fzn
set reoptimization advanced maxsavednodes 100
set reoptimization advanced delay -1
set reoptimization advanced usecuts TRUE
set reoptimization advanced usepscost TRUE
set reoptimization advanced storevarhistory TRUE
set reoptimization globalcons sepainfsubtrees FALSE
set reoptimization advanced saveconsprop TRUE
set reoptimization advanced forceheurrestart 1
set load /home/disha/UCML_2026/scip-siruil/check/coverage/settings/reopt-test-settings-varorderinterdiction-r.set
optimize
read /home/disha/UCML_2026/scip-siruil/check/instances/MIP/stein27_reopt/stein27_1.diff
optimize
validatesolve 0 0
read /home/disha/UCML_2026/scip-siruil/check/instances/MIP/stein27_reopt/stein27_2.diff
optimize
validatesolve 4 4
read /home/disha/UCML_2026/scip-siruil/check/instances/MIP/stein27_reopt/stein27_3.diff
optimize
display reoptstatistic
quit
