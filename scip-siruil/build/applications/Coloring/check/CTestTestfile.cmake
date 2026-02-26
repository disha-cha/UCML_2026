# CMake generated Testfile for 
# Source directory: /home/disha/UCML_2026/scip-siruil/applications/Coloring/check
# Build directory: /home/disha/UCML_2026/scip-siruil/build/applications/Coloring/check
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(applications-coloring-build "/usr/bin/cmake" "--build" "/home/disha/UCML_2026/scip-siruil/build" "--target" "coloring")
set_tests_properties(applications-coloring-build PROPERTIES  RESOURCE_LOCK "libscip" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/applications/Coloring/check/CMakeLists.txt;16;add_test;/home/disha/UCML_2026/scip-siruil/applications/Coloring/check/CMakeLists.txt;0;")
add_test(applications-coloring-1-FullIns_3 "/home/disha/UCML_2026/scip-siruil/build/bin/applications/coloring" "-f" "/home/disha/UCML_2026/scip-siruil/applications/Coloring/check/../data/1-FullIns_3.col" "-o" "4" "4")
set_tests_properties(applications-coloring-1-FullIns_3 PROPERTIES  DEPENDS "applications-coloring-build" PASS_REGULAR_EXPRESSION "Validation         : Success" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/applications/Coloring/check/CMakeLists.txt;37;add_test;/home/disha/UCML_2026/scip-siruil/applications/Coloring/check/CMakeLists.txt;0;")
add_test(applications-coloring-myciel3 "/home/disha/UCML_2026/scip-siruil/build/bin/applications/coloring" "-f" "/home/disha/UCML_2026/scip-siruil/applications/Coloring/check/../data/myciel3.col" "-o" "4" "4")
set_tests_properties(applications-coloring-myciel3 PROPERTIES  DEPENDS "applications-coloring-build" PASS_REGULAR_EXPRESSION "Validation         : Success" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/applications/Coloring/check/CMakeLists.txt;37;add_test;/home/disha/UCML_2026/scip-siruil/applications/Coloring/check/CMakeLists.txt;0;")
add_test(applications-coloring-queen9_9 "/home/disha/UCML_2026/scip-siruil/build/bin/applications/coloring" "-f" "/home/disha/UCML_2026/scip-siruil/applications/Coloring/check/../data/queen9_9.col" "-o" "10" "10")
set_tests_properties(applications-coloring-queen9_9 PROPERTIES  DEPENDS "applications-coloring-build" PASS_REGULAR_EXPRESSION "Validation         : Success" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/applications/Coloring/check/CMakeLists.txt;37;add_test;/home/disha/UCML_2026/scip-siruil/applications/Coloring/check/CMakeLists.txt;0;")
add_test(applications-coloring-will199GPIA "/home/disha/UCML_2026/scip-siruil/build/bin/applications/coloring" "-f" "/home/disha/UCML_2026/scip-siruil/applications/Coloring/check/../data/will199GPIA.col" "-o" "7" "7")
set_tests_properties(applications-coloring-will199GPIA PROPERTIES  DEPENDS "applications-coloring-build" PASS_REGULAR_EXPRESSION "Validation         : Success" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/applications/Coloring/check/CMakeLists.txt;37;add_test;/home/disha/UCML_2026/scip-siruil/applications/Coloring/check/CMakeLists.txt;0;")
