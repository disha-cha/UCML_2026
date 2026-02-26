# CMake generated Testfile for 
# Source directory: /home/disha/UCML_2026/scip-siruil/examples/VRP/check
# Build directory: /home/disha/UCML_2026/scip-siruil/build/examples/VRP/check
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(examples-vrp-build "/usr/bin/cmake" "--build" "/home/disha/UCML_2026/scip-siruil/build" "--target" "vrp")
set_tests_properties(examples-vrp-build PROPERTIES  RESOURCE_LOCK "libscip" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/examples/VRP/check/CMakeLists.txt;18;add_test;/home/disha/UCML_2026/scip-siruil/examples/VRP/check/CMakeLists.txt;0;")
add_test(examples-vrp-eil13 "/home/disha/UCML_2026/scip-siruil/build/bin/examples/vrp" "/home/disha/UCML_2026/scip-siruil/examples/VRP/check/../data/eil13.vrp")
set_tests_properties(examples-vrp-eil13 PROPERTIES  DEPENDS "examples-vrp-build" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/examples/VRP/check/CMakeLists.txt;38;add_test;/home/disha/UCML_2026/scip-siruil/examples/VRP/check/CMakeLists.txt;0;")
add_test(examples-vrp-eil7 "/home/disha/UCML_2026/scip-siruil/build/bin/examples/vrp" "/home/disha/UCML_2026/scip-siruil/examples/VRP/check/../data/eil7.vrp")
set_tests_properties(examples-vrp-eil7 PROPERTIES  DEPENDS "examples-vrp-build" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/examples/VRP/check/CMakeLists.txt;38;add_test;/home/disha/UCML_2026/scip-siruil/examples/VRP/check/CMakeLists.txt;0;")
