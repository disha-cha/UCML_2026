# Install script for directory: /home/disha/UCML_2026/scip-siruil/src

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/home/disha/scipopt")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Release")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

# Set default install directory permissions.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "/usr/bin/objdump")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/lpi" TYPE FILE FILES
    "/home/disha/UCML_2026/scip-siruil/src/lpi/lpi.h"
    "/home/disha/UCML_2026/scip-siruil/src/lpi/type_lpi.h"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/dijkstra" TYPE FILE FILES "/home/disha/UCML_2026/scip-siruil/src/dijkstra/dijkstra.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/nlpi" TYPE FILE FILES
    "/home/disha/UCML_2026/scip-siruil/src/nlpi/exprinterpret.h"
    "/home/disha/UCML_2026/scip-siruil/src/nlpi/intervalarithext.h"
    "/home/disha/UCML_2026/scip-siruil/src/nlpi/nlpi_all.h"
    "/home/disha/UCML_2026/scip-siruil/src/nlpi/nlpi.h"
    "/home/disha/UCML_2026/scip-siruil/src/nlpi/nlpi_filtersqp.h"
    "/home/disha/UCML_2026/scip-siruil/src/nlpi/nlpi_ipopt.h"
    "/home/disha/UCML_2026/scip-siruil/src/nlpi/nlpi_worhp.h"
    "/home/disha/UCML_2026/scip-siruil/src/nlpi/nlpioracle.h"
    "/home/disha/UCML_2026/scip-siruil/src/nlpi/pub_expr.h"
    "/home/disha/UCML_2026/scip-siruil/src/nlpi/struct_expr.h"
    "/home/disha/UCML_2026/scip-siruil/src/nlpi/struct_nlpi.h"
    "/home/disha/UCML_2026/scip-siruil/src/nlpi/type_expr.h"
    "/home/disha/UCML_2026/scip-siruil/src/nlpi/type_exprinterpret.h"
    "/home/disha/UCML_2026/scip-siruil/src/nlpi/type_nlpi.h"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/objscip" TYPE FILE FILES
    "/home/disha/UCML_2026/scip-siruil/src/objscip/objbenders.h"
    "/home/disha/UCML_2026/scip-siruil/src/objscip/objbenderscut.h"
    "/home/disha/UCML_2026/scip-siruil/src/objscip/objbranchrule.h"
    "/home/disha/UCML_2026/scip-siruil/src/objscip/objcloneable.h"
    "/home/disha/UCML_2026/scip-siruil/src/objscip/objconshdlr.h"
    "/home/disha/UCML_2026/scip-siruil/src/objscip/objdialog.h"
    "/home/disha/UCML_2026/scip-siruil/src/objscip/objdisp.h"
    "/home/disha/UCML_2026/scip-siruil/src/objscip/objeventhdlr.h"
    "/home/disha/UCML_2026/scip-siruil/src/objscip/objheur.h"
    "/home/disha/UCML_2026/scip-siruil/src/objscip/objmessagehdlr.h"
    "/home/disha/UCML_2026/scip-siruil/src/objscip/objnodesel.h"
    "/home/disha/UCML_2026/scip-siruil/src/objscip/objpresol.h"
    "/home/disha/UCML_2026/scip-siruil/src/objscip/objpricer.h"
    "/home/disha/UCML_2026/scip-siruil/src/objscip/objprobcloneable.h"
    "/home/disha/UCML_2026/scip-siruil/src/objscip/objprobdata.h"
    "/home/disha/UCML_2026/scip-siruil/src/objscip/objprop.h"
    "/home/disha/UCML_2026/scip-siruil/src/objscip/objreader.h"
    "/home/disha/UCML_2026/scip-siruil/src/objscip/objrelax.h"
    "/home/disha/UCML_2026/scip-siruil/src/objscip/objscipdefplugins.h"
    "/home/disha/UCML_2026/scip-siruil/src/objscip/objscip.h"
    "/home/disha/UCML_2026/scip-siruil/src/objscip/objsepa.h"
    "/home/disha/UCML_2026/scip-siruil/src/objscip/objtable.h"
    "/home/disha/UCML_2026/scip-siruil/src/objscip/objvardata.h"
    "/home/disha/UCML_2026/scip-siruil/src/objscip/type_objcloneable.h"
    "/home/disha/UCML_2026/scip-siruil/src/objscip/type_objprobcloneable.h"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/scip" TYPE FILE FILES
    "/home/disha/UCML_2026/scip-siruil/src/scip/bandit.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/bandit_epsgreedy.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/bandit_exp3.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/bandit_ucb.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/benders.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/benders_default.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/benderscut.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/benderscut_feas.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/benderscut_feasalt.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/benderscut_int.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/benderscut_nogood.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/benderscut_opt.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/bendersdefcuts.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/bitencode.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/boundstore.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/branch_allfullstrong.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/branch_cloud.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/branch_distribution.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/branch_fullstrong.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/branch.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/branch_inference.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/branch_leastinf.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/branch_lookahead.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/branch_mostinf.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/branch_multaggr.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/branch_nodereopt.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/branch_pscost.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/branch_random.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/branch_relpscost.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/branch_vanillafullstrong.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/clock.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/compr.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/compr_largestrepr.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/compr_weakcompr.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/concsolver.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/concsolver_scip.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/concurrent.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/conflict.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/conflictstore.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_abspower.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_and.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_benders.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_benderslp.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_bivariate.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_bounddisjunction.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_cardinality.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_components.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_conjunction.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_countsols.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_cumulative.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_disjunction.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_indicator.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_integral.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_knapsack.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_linear.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_linking.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_logicor.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_nonlinear.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_orbisack.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_orbitope.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_or.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_pseudoboolean.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_quadratic.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_setppc.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_soc.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_sos1.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_sos2.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_superindicator.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_symresack.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_varbound.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cons_xor.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cutpool.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/cuts.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/dbldblarith.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/debug.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/dcmp.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/def.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/dialog_default.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/dialog.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/disp_default.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/disp.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/event_globalbnd.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/event.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/event_estim.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/event_softtimelimit.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/event_solvingphase.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_actconsdiving.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_adaptivediving.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_bound.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_clique.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_coefdiving.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_completesol.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_conflictdiving.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_crossover.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_dins.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_distributiondiving.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_dualval.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_farkasdiving.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_feaspump.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_fixandinfer.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_fracdiving.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_gins.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_guideddiving.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_indicator.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_intdiving.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_intshifting.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heuristics.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_linesearchdiving.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_localbranching.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_locks.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_alns.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_lpface.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_multistart.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_mutation.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_mpec.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_nlpdiving.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_objpscostdiving.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_octane.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_ofins.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_oneopt.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_padm.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_proximity.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_pscostdiving.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_randrounding.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_rens.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_reoptsols.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_repair.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_rins.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_rootsoldiving.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_rounding.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_shiftandpropagate.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_shifting.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_simplerounding.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_subnlp.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_sync.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_trivial.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_trivialnegation.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_trustregion.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_trysol.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_twoopt.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_undercover.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_vbounds.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_veclendiving.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_zeroobj.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/heur_zirounding.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/history.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/implics.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/interrupt.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/intervalarith.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/lp.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/mem.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/message_default.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/message.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/misc.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/nlp.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/nodesel_bfs.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/nodesel_breadthfirst.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/nodesel_dfs.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/nodesel_estimate.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/nodesel.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/nodesel_hybridestim.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/nodesel_restartdfs.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/nodesel_uct.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/paramset.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/presol_boundshift.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/presol_milp.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/presol_convertinttobin.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/presol_domcol.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/presol_dualagg.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/presol_dualcomp.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/presol_dualinfer.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/presol_gateextraction.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/presol.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/presol_implics.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/presol_inttobinary.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/presol_qpkktref.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/presol_redvub.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/presol_sparsify.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/presol_dualsparsify.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/presol_stuffing.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/presol_trivial.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/presol_tworowbnd.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/presolve.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pricer.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pricestore.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/primal.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/prob.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/prop_dualfix.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/prop_genvbounds.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/prop.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/prop_nlobbt.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/prop_obbt.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/prop_probing.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/prop_pseudoobj.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/prop_redcost.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/prop_rootredcost.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/prop_symmetry.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/prop_sync.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/prop_vbounds.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_branch.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_bandit.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_bandit_epsgreedy.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_bandit_exp3.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_bandit_ucb.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_benders.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_benderscut.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_compr.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_conflict.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_cons.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_cutpool.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_dcmp.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_dialog.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_disp.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_event.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_fileio.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_heur.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_history.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_implics.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_lp.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_matrix.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_message.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_misc.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_misc_linear.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_misc_nonlinear.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_misc_select.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_misc_sort.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_nlp.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_nodesel.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_paramset.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_presol.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_pricer.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_prop.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_reader.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_relax.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_reopt.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_sepa.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_sol.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_table.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_tree.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/pub_var.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/rbtree.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/reader_bnd.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/reader_ccg.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/reader_cip.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/reader_cnf.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/reader_cor.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/reader_dec.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/reader_diff.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/reader_fix.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/reader_fzn.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/reader_gms.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/reader.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/reader_lp.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/reader_mps.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/reader_mst.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/reader_opb.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/reader_osil.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/reader_pbm.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/reader_pip.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/reader_ppm.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/reader_rlp.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/reader_sol.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/reader_smps.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/reader_sto.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/reader_tim.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/reader_wbo.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/reader_zpl.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/relax.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/reopt.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/retcode.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scipbuildflags.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scipcoreplugins.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scipdefplugins.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scipgithash.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_bandit.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_benders.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_branch.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_compr.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_concurrent.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_conflict.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_cons.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_copy.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_cut.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_datastructures.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_debug.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_dcmp.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_dialog.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_disp.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_event.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_expr.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_general.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_heur.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_lp.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_mem.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_message.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_nlp.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_nodesel.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_nonlinear.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_numerics.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_param.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_presol.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_pricer.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_prob.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_probing.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_prop.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_randnumgen.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_reader.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_relax.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_reopt.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_sepa.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_sol.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_solve.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_solvingstats.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_table.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_timing.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_tree.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_validation.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scip_var.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/scipshell.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/sepa_cgmip.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/sepa_clique.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/sepa_closecuts.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/sepa_aggregation.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/sepa_convexproj.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/sepa_disjunctive.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/sepa_eccuts.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/sepa_gauge.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/sepa_gomory.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/sepa.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/sepa_impliedbounds.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/sepa_intobj.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/sepa_mcf.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/sepa_oddcycle.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/sepa_rapidlearning.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/sepastore.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/sepa_strongcg.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/sepa_zerohalf.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/set.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/sol.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/solve.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/stat.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_bandit.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_benders.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_benderscut.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_branch.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_clock.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_compr.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_concsolver.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_concurrent.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_conflict.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_conflictstore.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_cons.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_cutpool.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_cuts.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_dcmp.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_dialog.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_disp.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_event.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_heur.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_history.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_implics.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_lp.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_matrix.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_mem.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_message.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_misc.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_nlp.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_nodesel.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_paramset.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_presol.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_pricer.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_pricestore.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_primal.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_prob.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_prop.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_reader.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_relax.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_reopt.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_scip.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_sepa.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_sepastore.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_set.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_sol.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_stat.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_syncstore.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_table.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_tree.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_var.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/struct_visual.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/symmetry.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/syncstore.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/table_default.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/table.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/tree.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/treemodel.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_bandit.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_benders.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_benderscut.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_branch.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_clock.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_compr.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_concsolver.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_concurrent.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_conflict.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_conflictstore.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_cons.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_cutpool.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_cuts.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_dcmp.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_dialog.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_disp.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_event.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_heur.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_history.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_implics.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_interrupt.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_lp.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_matrix.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_mem.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_message.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_misc.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_nlp.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_nodesel.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_paramset.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_presol.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_pricer.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_pricestore.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_primal.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_prob.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_prop.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_reader.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_relax.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_reopt.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_result.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_retcode.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_scip.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_sepa.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_sepastore.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_set.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_sol.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_stat.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_syncstore.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_table.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_timing.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_tree.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_var.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/type_visual.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/var.h"
    "/home/disha/UCML_2026/scip-siruil/src/scip/visual.h"
    "/home/disha/UCML_2026/scip-siruil/build/scip/config.h"
    "/home/disha/UCML_2026/scip-siruil/build/scip/scip_export.h"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/tclique" TYPE FILE FILES
    "/home/disha/UCML_2026/scip-siruil/src/tclique/tclique_coloring.h"
    "/home/disha/UCML_2026/scip-siruil/src/tclique/tclique_def.h"
    "/home/disha/UCML_2026/scip-siruil/src/tclique/tclique.h"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/tinycthread" TYPE FILE FILES "/home/disha/UCML_2026/scip-siruil/src/tinycthread/tinycthread.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/tpi" TYPE FILE FILES
    "/home/disha/UCML_2026/scip-siruil/src/tpi/def_openmp.h"
    "/home/disha/UCML_2026/scip-siruil/src/tpi/tpi.h"
    "/home/disha/UCML_2026/scip-siruil/src/tpi/tpi_none.h"
    "/home/disha/UCML_2026/scip-siruil/src/tpi/tpi_openmp.h"
    "/home/disha/UCML_2026/scip-siruil/src/tpi/tpi_tnycthrd.h"
    "/home/disha/UCML_2026/scip-siruil/src/tpi/type_tpi.h"
    "/home/disha/UCML_2026/scip-siruil/src/tpi/type_tpi_none.h"
    "/home/disha/UCML_2026/scip-siruil/src/tpi/type_tpi_openmp.h"
    "/home/disha/UCML_2026/scip-siruil/src/tpi/type_tpi_tnycthrd.h"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/xml" TYPE FILE FILES
    "/home/disha/UCML_2026/scip-siruil/src/xml/xmldef.h"
    "/home/disha/UCML_2026/scip-siruil/src/xml/xml.h"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/symmetry" TYPE FILE FILES
    "/home/disha/UCML_2026/scip-siruil/src/symmetry/compute_symmetry.h"
    "/home/disha/UCML_2026/scip-siruil/src/symmetry/type_symmetry.h"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/blockmemshell" TYPE FILE FILES "/home/disha/UCML_2026/scip-siruil/src/blockmemshell/memory.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/scip" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/scip")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/scip"
         RPATH "/home/disha/scipopt/lib")
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/bin" TYPE EXECUTABLE FILES "/home/disha/UCML_2026/scip-siruil/build/bin/scip")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/scip" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/scip")
    file(RPATH_CHANGE
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/scip"
         OLD_RPATH ":::::::::::::::::::::::"
         NEW_RPATH "/home/disha/scipopt/lib")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/scip")
    endif()
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  foreach(file
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libscip.so.7.0.2.0"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libscip.so.7.0"
      )
    if(EXISTS "${file}" AND
       NOT IS_SYMLINK "${file}")
      file(RPATH_CHECK
           FILE "${file}"
           RPATH "")
    endif()
  endforeach()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY FILES
    "/home/disha/UCML_2026/scip-siruil/build/lib/libscip.so.7.0.2.0"
    "/home/disha/UCML_2026/scip-siruil/build/lib/libscip.so.7.0"
    )
  foreach(file
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libscip.so.7.0.2.0"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libscip.so.7.0"
      )
    if(EXISTS "${file}" AND
       NOT IS_SYMLINK "${file}")
      if(CMAKE_INSTALL_DO_STRIP)
        execute_process(COMMAND "/usr/bin/strip" "${file}")
      endif()
    endif()
  endforeach()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY FILES "/home/disha/UCML_2026/scip-siruil/build/lib/libscip.so")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/cmake/scip/scip-targets.cmake")
    file(DIFFERENT _cmake_export_file_changed FILES
         "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/cmake/scip/scip-targets.cmake"
         "/home/disha/UCML_2026/scip-siruil/build/src/CMakeFiles/Export/440faded5223945d68a0ef6070a73d3d/scip-targets.cmake")
    if(_cmake_export_file_changed)
      file(GLOB _cmake_old_config_files "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/cmake/scip/scip-targets-*.cmake")
      if(_cmake_old_config_files)
        string(REPLACE ";" ", " _cmake_old_config_files_text "${_cmake_old_config_files}")
        message(STATUS "Old export file \"$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/cmake/scip/scip-targets.cmake\" will be replaced.  Removing files [${_cmake_old_config_files_text}].")
        unset(_cmake_old_config_files_text)
        file(REMOVE ${_cmake_old_config_files})
      endif()
      unset(_cmake_old_config_files)
    endif()
    unset(_cmake_export_file_changed)
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/scip" TYPE FILE FILES "/home/disha/UCML_2026/scip-siruil/build/src/CMakeFiles/Export/440faded5223945d68a0ef6070a73d3d/scip-targets.cmake")
  if(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Rr][Ee][Ll][Ee][Aa][Ss][Ee])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/scip" TYPE FILE FILES "/home/disha/UCML_2026/scip-siruil/build/src/CMakeFiles/Export/440faded5223945d68a0ef6070a73d3d/scip-targets-release.cmake")
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/scip" TYPE FILE FILES
    "/home/disha/UCML_2026/scip-siruil/build/CMakeFiles/scip-config.cmake"
    "/home/disha/UCML_2026/scip-siruil/build/scip-config-version.cmake"
    )
endif()

