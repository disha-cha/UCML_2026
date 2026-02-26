# CMake generated Testfile for 
# Source directory: /home/disha/UCML_2026/scip-siruil/applications/MinIISC/check
# Build directory: /home/disha/UCML_2026/scip-siruil/build/applications/MinIISC/check
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(applications-miniisc-build "/usr/bin/cmake" "--build" "/home/disha/UCML_2026/scip-siruil/build" "--target" "miniisc")
set_tests_properties(applications-miniisc-build PROPERTIES  RESOURCE_LOCK "libscip" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/applications/MinIISC/check/CMakeLists.txt;16;add_test;/home/disha/UCML_2026/scip-siruil/applications/MinIISC/check/CMakeLists.txt;0;")
add_test(applications-miniisc-prob.10.30.100.0 "/home/disha/UCML_2026/scip-siruil/build/bin/applications/miniisc" "/home/disha/UCML_2026/scip-siruil/applications/MinIISC/check/../data/prob.10.30.100.0.lp")
set_tests_properties(applications-miniisc-prob.10.30.100.0 PROPERTIES  DEPENDS "applications-miniisc-build" PASS_REGULAR_EXPRESSION "Primal Bound       : \\+(2\\.000000*|1\\.999999*)e\\+00" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/applications/MinIISC/check/CMakeLists.txt;39;add_test;/home/disha/UCML_2026/scip-siruil/applications/MinIISC/check/CMakeLists.txt;0;")
add_test(applications-miniisc-prob.15.40.100.1 "/home/disha/UCML_2026/scip-siruil/build/bin/applications/miniisc" "/home/disha/UCML_2026/scip-siruil/applications/MinIISC/check/../data/prob.15.40.100.1.lp")
set_tests_properties(applications-miniisc-prob.15.40.100.1 PROPERTIES  DEPENDS "applications-miniisc-build" PASS_REGULAR_EXPRESSION "Primal Bound       : \\+(3\\.000000*|2\\.999999*)e\\+00" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/applications/MinIISC/check/CMakeLists.txt;39;add_test;/home/disha/UCML_2026/scip-siruil/applications/MinIISC/check/CMakeLists.txt;0;")
add_test(applications-miniisc-prob.20.50.100.0 "/home/disha/UCML_2026/scip-siruil/build/bin/applications/miniisc" "/home/disha/UCML_2026/scip-siruil/applications/MinIISC/check/../data/prob.20.50.100.0.lp")
set_tests_properties(applications-miniisc-prob.20.50.100.0 PROPERTIES  DEPENDS "applications-miniisc-build" PASS_REGULAR_EXPRESSION "Primal Bound       : \\+(2\\.000000*|1\\.999999*)e\\+00" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/applications/MinIISC/check/CMakeLists.txt;39;add_test;/home/disha/UCML_2026/scip-siruil/applications/MinIISC/check/CMakeLists.txt;0;")
add_test(applications-miniisc-prob.5.030.100.0 "/home/disha/UCML_2026/scip-siruil/build/bin/applications/miniisc" "/home/disha/UCML_2026/scip-siruil/applications/MinIISC/check/../data/prob.5.030.100.0.lp")
set_tests_properties(applications-miniisc-prob.5.030.100.0 PROPERTIES  DEPENDS "applications-miniisc-build" PASS_REGULAR_EXPRESSION "Primal Bound       : \\+(3\\.000000*|2\\.999999*)e\\+00" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/applications/MinIISC/check/CMakeLists.txt;39;add_test;/home/disha/UCML_2026/scip-siruil/applications/MinIISC/check/CMakeLists.txt;0;")
