# CMake generated Testfile for 
# Source directory: /home/disha/UCML_2026/scip-siruil/applications/STP/check
# Build directory: /home/disha/UCML_2026/scip-siruil/build/applications/STP/check
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(applications-scipstp-build "/usr/bin/cmake" "--build" "/home/disha/UCML_2026/scip-siruil/build" "--target" "scipstp")
set_tests_properties(applications-scipstp-build PROPERTIES  RESOURCE_LOCK "libscip" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/applications/STP/check/CMakeLists.txt;19;add_test;/home/disha/UCML_2026/scip-siruil/applications/STP/check/CMakeLists.txt;0;")
add_test(applications-scipstp-cc3-4u "/home/disha/UCML_2026/scip-siruil/build/bin/applications/scipstp" "-f" "/home/disha/UCML_2026/scip-siruil/applications/STP/check/../data/short/cc3-4u.stp" "-o" "23" "23")
set_tests_properties(applications-scipstp-cc3-4u PROPERTIES  DEPENDS "applications-scipstp-build" PASS_REGULAR_EXPRESSION "Validation         : Success" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/applications/STP/check/CMakeLists.txt;40;add_test;/home/disha/UCML_2026/scip-siruil/applications/STP/check/CMakeLists.txt;0;")
add_test(applications-scipstp-d18 "/home/disha/UCML_2026/scip-siruil/build/bin/applications/scipstp" "-f" "/home/disha/UCML_2026/scip-siruil/applications/STP/check/../data/short/d18.stp" "-o" "223" "223")
set_tests_properties(applications-scipstp-d18 PROPERTIES  DEPENDS "applications-scipstp-build" PASS_REGULAR_EXPRESSION "Validation         : Success" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/applications/STP/check/CMakeLists.txt;40;add_test;/home/disha/UCML_2026/scip-siruil/applications/STP/check/CMakeLists.txt;0;")
add_test(applications-scipstp-hc6u "/home/disha/UCML_2026/scip-siruil/build/bin/applications/scipstp" "-f" "/home/disha/UCML_2026/scip-siruil/applications/STP/check/../data/short/hc6u.stp" "-o" "39" "39")
set_tests_properties(applications-scipstp-hc6u PROPERTIES  DEPENDS "applications-scipstp-build" PASS_REGULAR_EXPRESSION "Validation         : Success" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/applications/STP/check/CMakeLists.txt;40;add_test;/home/disha/UCML_2026/scip-siruil/applications/STP/check/CMakeLists.txt;0;")
