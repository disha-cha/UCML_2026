# CMake generated Testfile for 
# Source directory: /home/disha/UCML_2026/scip-siruil/applications/Ringpacking/check
# Build directory: /home/disha/UCML_2026/scip-siruil/build/applications/Ringpacking/check
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(applications-ringpacking-build "/usr/bin/cmake" "--build" "/home/disha/UCML_2026/scip-siruil/build" "--target" "ringpacking")
set_tests_properties(applications-ringpacking-build PROPERTIES  RESOURCE_LOCK "libscip" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/applications/Ringpacking/check/CMakeLists.txt;13;add_test;/home/disha/UCML_2026/scip-siruil/applications/Ringpacking/check/CMakeLists.txt;0;")
add_test(applications-ringpacking-circle6 "/home/disha/UCML_2026/scip-siruil/build/bin/applications/ringpacking" "-f" "/home/disha/UCML_2026/scip-siruil/applications/Ringpacking/check/../data/circle6.rpa" "-o" "2" "1")
set_tests_properties(applications-ringpacking-circle6 PROPERTIES  DEPENDS "applications-ringpacking-build" PASS_REGULAR_EXPRESSION "Validation         : Success" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/applications/Ringpacking/check/CMakeLists.txt;38;add_test;/home/disha/UCML_2026/scip-siruil/applications/Ringpacking/check/CMakeLists.txt;0;")
add_test(applications-ringpacking-ring1 "/home/disha/UCML_2026/scip-siruil/build/bin/applications/ringpacking" "-f" "/home/disha/UCML_2026/scip-siruil/applications/Ringpacking/check/../data/ring1.rpa" "-o" "1" "1")
set_tests_properties(applications-ringpacking-ring1 PROPERTIES  DEPENDS "applications-ringpacking-build" PASS_REGULAR_EXPRESSION "Validation         : Success" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/applications/Ringpacking/check/CMakeLists.txt;38;add_test;/home/disha/UCML_2026/scip-siruil/applications/Ringpacking/check/CMakeLists.txt;0;")
add_test(applications-ringpacking-ring2 "/home/disha/UCML_2026/scip-siruil/build/bin/applications/ringpacking" "-f" "/home/disha/UCML_2026/scip-siruil/applications/Ringpacking/check/../data/ring2.rpa" "-o" "1" "1")
set_tests_properties(applications-ringpacking-ring2 PROPERTIES  DEPENDS "applications-ringpacking-build" PASS_REGULAR_EXPRESSION "Validation         : Success" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/applications/Ringpacking/check/CMakeLists.txt;38;add_test;/home/disha/UCML_2026/scip-siruil/applications/Ringpacking/check/CMakeLists.txt;0;")
add_test(applications-ringpacking-ring3 "/home/disha/UCML_2026/scip-siruil/build/bin/applications/ringpacking" "-f" "/home/disha/UCML_2026/scip-siruil/applications/Ringpacking/check/../data/ring3.rpa" "-o" "1" "1")
set_tests_properties(applications-ringpacking-ring3 PROPERTIES  DEPENDS "applications-ringpacking-build" PASS_REGULAR_EXPRESSION "Validation         : Success" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/applications/Ringpacking/check/CMakeLists.txt;38;add_test;/home/disha/UCML_2026/scip-siruil/applications/Ringpacking/check/CMakeLists.txt;0;")
