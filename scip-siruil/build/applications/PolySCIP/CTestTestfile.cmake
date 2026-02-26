# CMake generated Testfile for 
# Source directory: /home/disha/UCML_2026/scip-siruil/applications/PolySCIP
# Build directory: /home/disha/UCML_2026/scip-siruil/build/applications/PolySCIP
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(applications-polyscip-build "/usr/bin/cmake" "--build" "/home/disha/UCML_2026/scip-siruil/build" "--target" "polyscip")
set_tests_properties(applications-polyscip-build PROPERTIES  RESOURCE_LOCK "libscip" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/applications/PolySCIP/CMakeLists.txt;62;add_test;/home/disha/UCML_2026/scip-siruil/applications/PolySCIP/CMakeLists.txt;0;")
add_test(applications-polyscip-AP_p-3_n-5 "/home/disha/UCML_2026/scip-siruil/build/bin/applications/polyscip" "/home/disha/UCML_2026/scip-siruil/applications/PolySCIP/data/AP_p-3_n-5.mop")
set_tests_properties(applications-polyscip-AP_p-3_n-5 PROPERTIES  DEPENDS "applications-polyscip-build" PASS_REGULAR_EXPRESSION "PolySCIP Status: Successfully finished" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/applications/PolySCIP/CMakeLists.txt;85;add_test;/home/disha/UCML_2026/scip-siruil/applications/PolySCIP/CMakeLists.txt;0;")
add_test(applications-polyscip-mobp_2_30_1_knapsack "/home/disha/UCML_2026/scip-siruil/build/bin/applications/polyscip" "/home/disha/UCML_2026/scip-siruil/applications/PolySCIP/data/mobp_2_30_1_knapsack.mop")
set_tests_properties(applications-polyscip-mobp_2_30_1_knapsack PROPERTIES  DEPENDS "applications-polyscip-build" PASS_REGULAR_EXPRESSION "PolySCIP Status: Successfully finished" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/applications/PolySCIP/CMakeLists.txt;85;add_test;/home/disha/UCML_2026/scip-siruil/applications/PolySCIP/CMakeLists.txt;0;")
add_test(applications-polyscip-tenfelde_podehl "/home/disha/UCML_2026/scip-siruil/build/bin/applications/polyscip" "/home/disha/UCML_2026/scip-siruil/applications/PolySCIP/data/tenfelde_podehl.mop")
set_tests_properties(applications-polyscip-tenfelde_podehl PROPERTIES  DEPENDS "applications-polyscip-build" PASS_REGULAR_EXPRESSION "PolySCIP Status: Successfully finished" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/applications/PolySCIP/CMakeLists.txt;85;add_test;/home/disha/UCML_2026/scip-siruil/applications/PolySCIP/CMakeLists.txt;0;")
